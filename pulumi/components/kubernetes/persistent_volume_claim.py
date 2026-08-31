"""PersistentVolumeClaims that bind to a named storage class."""

from collections.abc import Sequence

import pulumi
import pulumi_kubernetes as kubernetes


def volume_claim(
    name: str,
    namespace: str,
    size: str,
    storage_class: str,
    access_modes: Sequence[str] = ("ReadWriteOnce",),
    opts: pulumi.ResourceOptions | None = None,
) -> kubernetes.core.v1.PersistentVolumeClaim:
    """Create a PersistentVolumeClaim for a volume of the given storage class.

    Args:
        name: Claim name, used as the Pulumi resource name too.
        namespace: Namespace to place the claim in.
        size: Requested storage, as a Kubernetes quantity (e.g. "50Gi").
        storage_class: Class of the volume to bind to.
        access_modes: Access modes the claim requires.
        opts: Pulumi resource options. Pass `depends_on` the volume when the
            claim is meant to bind to a specific one.

    Returns:
        The PersistentVolumeClaim resource.
    """
    return kubernetes.core.v1.PersistentVolumeClaim(
        name,
        metadata=kubernetes.meta.v1.ObjectMetaArgs(
            name=name,
            namespace=namespace,
        ),
        spec=kubernetes.core.v1.PersistentVolumeClaimSpecArgs(
            access_modes=list(access_modes),
            storage_class_name=storage_class,
            resources=kubernetes.core.v1.VolumeResourceRequirementsArgs(
                requests={"storage": size},
            ),
        ),
        opts=opts,
    )
