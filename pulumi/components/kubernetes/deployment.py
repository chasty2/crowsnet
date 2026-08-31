"""Deployments for the single-container workloads the homelab runs."""

from collections.abc import Sequence
from typing import NamedTuple

import pulumi
import pulumi_kubernetes as kubernetes


class ClaimMount(NamedTuple):
    """A PersistentVolumeClaim and where the container mounts it.

    Kubernetes has no mount without a path, so the two travel together rather
    than as separate optional arguments.
    """

    claim_name: str
    mount_path: str
    sub_path: str | None = None


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
    mounts: Sequence[ClaimMount] = (),
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
        mounts: PersistentVolumeClaims to mount, and where. The same claim may
            appear more than once, mounted at a different path or sub_path.
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
                            mounts=mounts,
                        )
                    ],
                    volumes=_claim_volumes(mounts),
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
    mounts: Sequence[ClaimMount],
) -> kubernetes.core.v1.ContainerArgs:
    """Build the container spec, with privileges dropped."""
    volume_mounts = [
        kubernetes.core.v1.VolumeMountArgs(
            name=mount.claim_name,
            mount_path=mount.mount_path,
            sub_path=mount.sub_path,
        )
        for mount in mounts
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
        volume_mounts=volume_mounts or None,
    )


def _claim_volumes(
    mounts: Sequence[ClaimMount],
) -> list[kubernetes.core.v1.VolumeArgs] | None:
    """Back the pod's volumes with the claims the container mounts.

    A claim mounted at several paths is still one volume, so names are deduped
    while keeping the order they were requested in.
    """
    if not mounts:
        return None

    claim_names = dict.fromkeys(mount.claim_name for mount in mounts)

    return [
        kubernetes.core.v1.VolumeArgs(
            name=claim_name,
            persistent_volume_claim=kubernetes.core.v1.PersistentVolumeClaimVolumeSourceArgs(
                claim_name=claim_name,
            ),
        )
        for claim_name in claim_names
    ]
