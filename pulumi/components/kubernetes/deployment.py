"""Deployments for the single-container workloads the homelab runs."""

from collections.abc import Sequence

import pulumi
import pulumi_kubernetes as kubernetes


def single_container_deployment(
    name: str,
    namespace: str,
    image: str,
    labels: dict[str, str],
    container_port: int,
    env: Sequence[kubernetes.core.v1.EnvVarArgs] | None = None,
    hostname: str | None = None,
    replicas: int = 1,
    run_as: tuple[int, int] | None = None,
    claim_name: str | None = None,
    mount_path: str | None = None,
    sub_path: str | None = None,
    opts: pulumi.ResourceOptions | None = None,
) -> kubernetes.apps.v1.Deployment:
    """Create a Deployment running one hardened container.

    Args:
        name: Workload name, used as the Pulumi resource name too.
        namespace: Namespace to deploy into.
        image: Container image reference.
        labels: Pod labels; also the Deployment's selector.
        container_port: Port the container listens on.
        env: Container environment variables.
        hostname: Fixed pod hostname, for images that tie an identity to it.
        replicas: Pod count.
        run_as: (uid, gid) to run as, which also becomes the volume fs group.
        claim_name: PersistentVolumeClaim to mount, if any.
        mount_path: Where to mount that claim in the container.
        sub_path: Subdirectory of the volume to mount, rather than its root.
        opts: Pulumi resource options.

    Returns:
        The Deployment resource.
    """
    return kubernetes.apps.v1.Deployment(
        name,
        metadata=kubernetes.meta.v1.ObjectMetaArgs(
            name=name,
            namespace=namespace,
            labels=labels,
        ),
        spec=kubernetes.apps.v1.DeploymentSpecArgs(
            replicas=replicas,
            selector=kubernetes.meta.v1.LabelSelectorArgs(match_labels=labels),
            template=kubernetes.core.v1.PodTemplateSpecArgs(
                metadata=kubernetes.meta.v1.ObjectMetaArgs(labels=labels),
                spec=kubernetes.core.v1.PodSpecArgs(
                    hostname=hostname,
                    # The workload never calls the API server.
                    automount_service_account_token=False,
                    security_context=_pod_security_context(run_as),
                    containers=[
                        _container(
                            name=name,
                            image=image,
                            container_port=container_port,
                            env=env,
                            claim_name=claim_name,
                            mount_path=mount_path,
                            sub_path=sub_path,
                        )
                    ],
                    volumes=_claim_volumes(claim_name),
                ),
            ),
        ),
        opts=opts,
    )


def _pod_security_context(
    run_as: tuple[int, int] | None,
) -> kubernetes.core.v1.PodSecurityContextArgs:
    """Build the pod security context, pinning the uid/gid when one is given."""
    uid, gid = run_as if run_as else (None, None)
    return kubernetes.core.v1.PodSecurityContextArgs(
        run_as_non_root=True,
        run_as_user=uid,
        run_as_group=gid,
        fs_group=gid,
        fs_group_change_policy="OnRootMismatch" if gid is not None else None,
        seccomp_profile=kubernetes.core.v1.SeccompProfileArgs(
            type="RuntimeDefault",
        ),
    )


def _container(
    name: str,
    image: str,
    container_port: int,
    env: Sequence[kubernetes.core.v1.EnvVarArgs] | None,
    claim_name: str | None,
    mount_path: str | None,
    sub_path: str | None,
) -> kubernetes.core.v1.ContainerArgs:
    """Build the container spec, with privileges dropped."""
    mounts = None
    if claim_name:
        mounts = [
            kubernetes.core.v1.VolumeMountArgs(
                name=claim_name,
                mount_path=mount_path,
                sub_path=sub_path,
            )
        ]

    return kubernetes.core.v1.ContainerArgs(
        name=name,
        image=image,
        security_context=kubernetes.core.v1.SecurityContextArgs(
            allow_privilege_escalation=False,
            capabilities=kubernetes.core.v1.CapabilitiesArgs(drop=["ALL"]),
        ),
        env=list(env) if env else None,
        ports=[
            kubernetes.core.v1.ContainerPortArgs(container_port=container_port)
        ],
        volume_mounts=mounts,
    )


def _claim_volumes(
    claim_name: str | None,
) -> list[kubernetes.core.v1.VolumeArgs] | None:
    """Back the pod's volume with the claim, when the workload has one."""
    if not claim_name:
        return None

    return [
        kubernetes.core.v1.VolumeArgs(
            name=claim_name,
            persistent_volume_claim=kubernetes.core.v1.PersistentVolumeClaimVolumeSourceArgs(
                claim_name=claim_name,
            ),
        )
    ]
