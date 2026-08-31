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

from components.kubernetes.deployment import single_container_deployment
from components.kubernetes.namespace import restricted_namespace
from components.kubernetes.persistent_volume import nfs_volume
from components.kubernetes.persistent_volume_claim import volume_claim
from components.kubernetes.service import node_port_service

APP_NAME = "foundry"
APP_LABELS = {"app": APP_NAME}
NAMESPACE = "foundry"
IMAGE = "docker.io/felddy/foundryvtt:14.367.0"
CONTAINER_PORT = 30000
NODE_PORT = 30000
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
    namespace = restricted_namespace(NAMESPACE)

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

    volume = nfs_volume(
        VOLUME_NAME,
        server=NFS_SERVER,
        path=NFS_PATH,
        size=STORAGE_SIZE,
        storage_class=STORAGE_CLASS,
        labels=APP_LABELS,
    )

    claim = volume_claim(
        VOLUME_NAME,
        namespace=NAMESPACE,
        size=STORAGE_SIZE,
        storage_class=STORAGE_CLASS,
        opts=pulumi.ResourceOptions(parent=namespace, depends_on=[volume]),
    )

    deployment = single_container_deployment(
        APP_NAME,
        namespace=NAMESPACE,
        image=IMAGE,
        labels=APP_LABELS,
        container_port=CONTAINER_PORT,
        env=_container_env(),
        # Foundry binds its license signature to the host identity. Without a
        # fixed hostname every replacement pod arrives as a new install and the
        # license needs re-confirming
        hostname=APP_NAME,
        run_as=(PODMAN_UID, PODMAN_GID),
        claim_name=VOLUME_NAME,
        mount_path="/data",
        # Mount only the subdirectory the container owns.
        sub_path=DATA_SUBPATH,
        opts=pulumi.ResourceOptions(parent=namespace, depends_on=[claim, secret]),
    )

    service = node_port_service(
        APP_NAME,
        namespace=NAMESPACE,
        selector=APP_LABELS,
        port=CONTAINER_PORT,
        node_port=NODE_PORT,
        labels=APP_LABELS,
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
