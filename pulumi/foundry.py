"""Foundry Virtual Tabletop, running on the MicroK8s cluster.

World data lives on the NFS export served by the hypervisor, so it survives a
destroy/rebuild of the node. The container runs as the `podman` uid/gid, which
keeps every file it writes owned the way the rest of the homelab expects.

Kept free of Pulumi runtime side effects at import time so it can be imported
and unit-tested without a live Pulumi engine; credentials are passed in rather
than read from config here.
"""

import pulumi
import pulumi_kubernetes as kubernetes

APP_NAME = "foundry"
APP_LABELS = {"app": APP_NAME}
NAMESPACE = "foundry"
# Pinned: Foundry licenses are tied to a major version, so a floating tag can
# silently upgrade the cluster into an unlicensed state.
IMAGE = "docker.io/felddy/foundryvtt:14.367.0"
CONTAINER_PORT = 30000
NODE_PORT = 30000

# The `podman` service account, as created by the common role. Running as this
# uid/gid is the Kubernetes equivalent of the rootless `userns: keep-id` setup
# the container used under Podman.
PODMAN_UID = 2004
PODMAN_GID = 2004

NFS_SERVER = "192.168.4.11"
NFS_PATH = "/ssd_mirror/foundry"
DATA_SUBPATH = "data"
SECRET_NAME = "foundry-credentials"
VOLUME_NAME = "foundry-data"
# No StorageClass object carries this name; it exists only to bind this PV to
# this PVC, and to keep a dynamic provisioner from answering the claim instead.
STORAGE_CLASS = "nfs-foundry"
STORAGE_SIZE = "50Gi"

# The felddy image fetches the licensed build with these credentials on boot.
CONTAINER_ENV = {
    "FOUNDRY_PROTOCOL": "4",
    "CONTAINER_CACHE_SIZE": "3",
    "CONTAINER_PRESERVE_CONFIG": "true",
}


def deploy_foundry(username: pulumi.Input[str], password: pulumi.Input[str]):
    """Create the namespace, storage, and workload that serve Foundry.

    Args:
        username: Foundry account used to fetch the licensed build.
        password: Password for that account.

    Returns:
        A (namespace, secret, volume, claim, deployment, service) tuple.
    """
    namespace = kubernetes.core.v1.Namespace(
        NAMESPACE,
        metadata=kubernetes.meta.v1.ObjectMetaArgs(
            name=NAMESPACE,
            labels={
                # Pod Security Admission is namespace labels, not RBAC. The pod
                # never calls the API server, so it needs no Role binding.
                "pod-security.kubernetes.io/enforce": "restricted",
                "pod-security.kubernetes.io/enforce-version": "latest",
                "pod-security.kubernetes.io/audit": "restricted",
                "pod-security.kubernetes.io/warn": "restricted",
            },
        ),
    )

    child = pulumi.ResourceOptions(parent=namespace)

    secret = kubernetes.core.v1.Secret(
        SECRET_NAME,
        metadata=kubernetes.meta.v1.ObjectMetaArgs(
            name=SECRET_NAME,
            namespace=NAMESPACE,
        ),
        string_data={
            "FOUNDRY_USERNAME": username,
            "FOUNDRY_PASSWORD": password,
        },
        opts=child,
    )

    volume = kubernetes.core.v1.PersistentVolume(
        VOLUME_NAME,
        metadata=kubernetes.meta.v1.ObjectMetaArgs(
            name=VOLUME_NAME,
            labels=APP_LABELS,
        ),
        spec=kubernetes.core.v1.PersistentVolumeSpecArgs(
            capacity={"storage": STORAGE_SIZE},
            access_modes=["ReadWriteOnce"],
            # The data outlives the cluster: never reclaim it.
            persistent_volume_reclaim_policy="Retain",
            storage_class_name=STORAGE_CLASS,
            mount_options=["hard"],
            nfs=kubernetes.core.v1.NFSVolumeSourceArgs(
                server=NFS_SERVER,
                path=NFS_PATH,
            ),
        ),
    )

    claim = kubernetes.core.v1.PersistentVolumeClaim(
        VOLUME_NAME,
        metadata=kubernetes.meta.v1.ObjectMetaArgs(
            name=VOLUME_NAME,
            namespace=NAMESPACE,
        ),
        spec=kubernetes.core.v1.PersistentVolumeClaimSpecArgs(
            access_modes=["ReadWriteOnce"],
            storage_class_name=STORAGE_CLASS,
            resources=kubernetes.core.v1.VolumeResourceRequirementsArgs(
                requests={"storage": STORAGE_SIZE},
            ),
        ),
        opts=pulumi.ResourceOptions(parent=namespace, depends_on=[volume]),
    )

    deployment = kubernetes.apps.v1.Deployment(
        APP_NAME,
        metadata=kubernetes.meta.v1.ObjectMetaArgs(
            name=APP_NAME,
            namespace=NAMESPACE,
            labels=APP_LABELS,
        ),
        spec=kubernetes.apps.v1.DeploymentSpecArgs(
            replicas=1,
            selector=kubernetes.meta.v1.LabelSelectorArgs(
                match_labels=APP_LABELS,
            ),
            template=kubernetes.core.v1.PodTemplateSpecArgs(
                metadata=kubernetes.meta.v1.ObjectMetaArgs(
                    labels=APP_LABELS,
                ),
                spec=kubernetes.core.v1.PodSpecArgs(
                    # Foundry binds its license signature to the host identity.
                    # Without a fixed hostname every replacement pod arrives as
                    # a new install and the license needs re-confirming, so pin
                    # it the way the podman container used to.
                    hostname=APP_NAME,
                    automount_service_account_token=False,
                    security_context=kubernetes.core.v1.PodSecurityContextArgs(
                        run_as_non_root=True,
                        run_as_user=PODMAN_UID,
                        run_as_group=PODMAN_GID,
                        fs_group=PODMAN_GID,
                        # The data is already podman-owned, so skip kubelet's
                        # recursive chown over the whole NFS export.
                        fs_group_change_policy="OnRootMismatch",
                        seccomp_profile=kubernetes.core.v1.SeccompProfileArgs(
                            type="RuntimeDefault",
                        ),
                    ),
                    containers=[
                        kubernetes.core.v1.ContainerArgs(
                            name=APP_NAME,
                            image=IMAGE,
                            security_context=kubernetes.core.v1.SecurityContextArgs(
                                allow_privilege_escalation=False,
                                capabilities=kubernetes.core.v1.CapabilitiesArgs(
                                    drop=["ALL"],
                                ),
                            ),
                            env=_container_env(),
                            ports=[
                                kubernetes.core.v1.ContainerPortArgs(
                                    container_port=CONTAINER_PORT,
                                )
                            ],
                            volume_mounts=[
                                kubernetes.core.v1.VolumeMountArgs(
                                    name=VOLUME_NAME,
                                    mount_path="/data",
                                    # The export root holds more than the world
                                    # data; mount only the subdirectory the
                                    # container owns.
                                    sub_path=DATA_SUBPATH,
                                )
                            ],
                        )
                    ],
                    volumes=[
                        kubernetes.core.v1.VolumeArgs(
                            name=VOLUME_NAME,
                            persistent_volume_claim=kubernetes.core.v1.PersistentVolumeClaimVolumeSourceArgs(
                                claim_name=VOLUME_NAME,
                            ),
                        )
                    ],
                ),
            ),
        ),
        opts=pulumi.ResourceOptions(parent=namespace, depends_on=[claim, secret]),
    )

    service = kubernetes.core.v1.Service(
        APP_NAME,
        metadata=kubernetes.meta.v1.ObjectMetaArgs(
            name=APP_NAME,
            namespace=NAMESPACE,
            labels=APP_LABELS,
        ),
        spec=kubernetes.core.v1.ServiceSpecArgs(
            type="NodePort",
            selector=APP_LABELS,
            ports=[
                kubernetes.core.v1.ServicePortArgs(
                    port=CONTAINER_PORT,
                    target_port=CONTAINER_PORT,
                    node_port=NODE_PORT,
                )
            ],
        ),
        opts=child,
    )

    return namespace, secret, volume, claim, deployment, service


def _container_env() -> list[kubernetes.core.v1.EnvVarArgs]:
    """Build the container environment, sourcing credentials from the Secret."""
    credentials = [
        kubernetes.core.v1.EnvVarArgs(
            name=name,
            value_from=kubernetes.core.v1.EnvVarSourceArgs(
                secret_key_ref=kubernetes.core.v1.SecretKeySelectorArgs(
                    name=SECRET_NAME,
                    key=name,
                ),
            ),
        )
        for name in ("FOUNDRY_USERNAME", "FOUNDRY_PASSWORD")
    ]
    settings = [
        kubernetes.core.v1.EnvVarArgs(name=name, value=value)
        for name, value in CONTAINER_ENV.items()
    ]
    return credentials + settings
