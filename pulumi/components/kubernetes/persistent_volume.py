"""PersistentVolumes backed by an NFS export."""

from collections.abc import Sequence

import pulumi
import pulumi_kubernetes as kubernetes


def nfs_volume(
    name: str,
    server: str,
    path: str,
    size: str,
    storage_class: str,
    labels: dict[str, str] | None = None,
    access_modes: Sequence[str] = ("ReadWriteOnce",),
    reclaim_policy: str = "Retain",
    mount_options: Sequence[str] = ("hard",),
    opts: pulumi.ResourceOptions | None = None,
) -> kubernetes.core.v1.PersistentVolume:
    """Create a PersistentVolume that reads from an NFS export.

    Args:
        name: Volume name, used as the Pulumi resource name too.
        server: NFS server address.
        path: Exported path on that server.
        size: Capacity, as a Kubernetes quantity (e.g. "50Gi").
        storage_class: Class that pairs this volume with its claim. No
            StorageClass object need carry the name; a private one keeps a
            dynamic provisioner from answering the claim instead.
        labels: Labels for the volume metadata.
        access_modes: Access modes the volume supports.
        reclaim_policy: Defaults to retaining the data, which outlives the
            cluster in this homelab.
        mount_options: NFS mount options.
        opts: Pulumi resource options.

    Returns:
        The PersistentVolume resource.
    """
    return kubernetes.core.v1.PersistentVolume(
        name,
        metadata=kubernetes.meta.v1.ObjectMetaArgs(
            name=name,
            labels=labels,
        ),
        spec=kubernetes.core.v1.PersistentVolumeSpecArgs(
            capacity={"storage": size},
            access_modes=list(access_modes),
            persistent_volume_reclaim_policy=reclaim_policy,
            storage_class_name=storage_class,
            mount_options=list(mount_options),
            nfs=kubernetes.core.v1.NFSVolumeSourceArgs(
                server=server,
                path=path,
            ),
        ),
        opts=opts,
    )
