"""Jellyfin media server, running on the MicroK8s cluster.

Two NFS exports back the workload: the server's own config and transcode cache
live on the SSD pool, the library itself on the spinning pool. Both survive a
destroy/rebuild of the node. The container runs as the `podman` uid/gid, which
keeps every file it writes owned the way the rest of the homelab expects.

Kept free of Pulumi runtime side effects at import time so it can be imported
and unit-tested without a live Pulumi engine.
"""

import pulumi

from components.kubernetes.deployment import ClaimMount, single_container_deployment
from components.kubernetes.namespace import restricted_namespace
from components.kubernetes.persistent_volume import nfs_volume
from components.kubernetes.persistent_volume_claim import volume_claim
from components.kubernetes.service import node_port_service

APP_NAME = "jellyfin"
APP_LABELS = {"app": APP_NAME}
NAMESPACE = "jellyfin"
IMAGE = "docker.io/jellyfin/jellyfin:10.11.6"
# Jellyfin listens on 8096, but the cluster only exposes the NodePort range.
CONTAINER_PORT = 8096
NODE_PORT = 30096
PODMAN_UID = 2004
PODMAN_GID = 2004
NFS_SERVER = "192.168.4.11"

DATA_VOLUME_NAME = "jellyfin-data"
DATA_NFS_PATH = "/ssd_mirror/jellyfin"
CONFIG_SUBPATH = "config"
CACHE_SUBPATH = "cache"
DATA_STORAGE_SIZE = "50Gi"

MEDIA_VOLUME_NAME = "jellyfin-media"
MEDIA_NFS_PATH = "/hdd_mirror/media"
MEDIA_STORAGE_SIZE = "8Ti"

# No StorageClass objects carry these names; they exist only to bind each PV to
# its own PVC, and to keep a dynamic provisioner from answering the claims.
DATA_STORAGE_CLASS = "nfs-jellyfin-data"
MEDIA_STORAGE_CLASS = "nfs-jellyfin-media"


def deploy_jellyfin():
    """Create the namespace, storage, and workload that serve Jellyfin.

    Returns:
        A (namespace, data_volume, data_claim, media_volume, media_claim,
        deployment, service) tuple.
    """
    namespace = restricted_namespace(NAMESPACE)

    child = pulumi.ResourceOptions(parent=namespace)

    data_volume, data_claim = _volume_and_claim(
        DATA_VOLUME_NAME,
        path=DATA_NFS_PATH,
        size=DATA_STORAGE_SIZE,
        storage_class=DATA_STORAGE_CLASS,
        namespace_resource=namespace,
    )

    media_volume, media_claim = _volume_and_claim(
        MEDIA_VOLUME_NAME,
        path=MEDIA_NFS_PATH,
        size=MEDIA_STORAGE_SIZE,
        storage_class=MEDIA_STORAGE_CLASS,
        namespace_resource=namespace,
    )

    deployment = single_container_deployment(
        APP_NAME,
        namespace=NAMESPACE,
        image=IMAGE,
        labels=APP_LABELS,
        container_port=CONTAINER_PORT,
        run_as=(PODMAN_UID, PODMAN_GID),
        mounts=[
            # Config and cache are subdirectories of the one export, so the
            # claim is mounted twice rather than split into two volumes.
            ClaimMount(
                claim_name=DATA_VOLUME_NAME,
                mount_path="/config",
                sub_path=CONFIG_SUBPATH,
            ),
            ClaimMount(
                claim_name=DATA_VOLUME_NAME,
                mount_path="/cache",
                sub_path=CACHE_SUBPATH,
            ),
            # The library is the whole export, and stays writable so Jellyfin
            # can save metadata alongside the media.
            ClaimMount(
                claim_name=MEDIA_VOLUME_NAME,
                mount_path="/media",
            ),
        ],
        opts=pulumi.ResourceOptions(
            parent=namespace,
            depends_on=[data_claim, media_claim],
        ),
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

    return (
        namespace,
        data_volume,
        data_claim,
        media_volume,
        media_claim,
        deployment,
        service,
    )


def _volume_and_claim(
    name: str,
    path: str,
    size: str,
    storage_class: str,
    namespace_resource,
):
    """Create an NFS PersistentVolume and the claim that binds to it."""
    volume = nfs_volume(
        name,
        server=NFS_SERVER,
        path=path,
        size=size,
        storage_class=storage_class,
        labels=APP_LABELS,
    )

    claim = volume_claim(
        name,
        namespace=NAMESPACE,
        size=size,
        storage_class=storage_class,
        opts=pulumi.ResourceOptions(
            parent=namespace_resource,
            depends_on=[volume],
        ),
    )

    return volume, claim
