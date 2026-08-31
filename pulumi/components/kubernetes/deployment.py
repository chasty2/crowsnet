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
    mount: ClaimMount | None = None,
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
        mount: PersistentVolumeClaim to mount, and where, if any.
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
                            mount=mount,
                        )
                    ],
                    volumes=_claim_volumes(mount),
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
    mount: ClaimMount | None,
) -> kubernetes.core.v1.ContainerArgs:
    """Build the container spec, with privileges dropped."""
    mounts = None
    if mount:
        mounts = [
            kubernetes.core.v1.VolumeMountArgs(
                name=mount.claim_name,
                mount_path=mount.mount_path,
                sub_path=mount.sub_path,
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
    mount: ClaimMount | None,
) -> list[kubernetes.core.v1.VolumeArgs] | None:
    """Back the pod's volume with the claim, when the workload has one."""
    if not mount:
        return None

    return [
        kubernetes.core.v1.VolumeArgs(
            name=mount.claim_name,
            persistent_volume_claim=kubernetes.core.v1.PersistentVolumeClaimVolumeSourceArgs(
                claim_name=mount.claim_name,
            ),
        )
    ]
