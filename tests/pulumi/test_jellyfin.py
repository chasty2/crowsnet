"""Tests for the Jellyfin workload in pulumi/jellyfin.py."""

import pulumi


class _Mocks(pulumi.runtime.Mocks):
    def new_resource(self, args: pulumi.runtime.MockResourceArgs):
        return [args.name + "_id", args.inputs]

    def call(self, args: pulumi.runtime.MockCallArgs):
        return {}


pulumi.runtime.set_mocks(_Mocks())

from jellyfin import (  # noqa: E402  (must follow set_mocks)
    APP_LABELS,
    CONTAINER_PORT,
    DATA_STORAGE_CLASS,
    DATA_VOLUME_NAME,
    IMAGE,
    MEDIA_STORAGE_CLASS,
    MEDIA_VOLUME_NAME,
    NAMESPACE,
    NODE_PORT,
    PODMAN_GID,
    PODMAN_UID,
    deploy_jellyfin,
)


def _deploy():
    return deploy_jellyfin()


@pulumi.runtime.test
def test_namespace_enforces_the_restricted_pod_security_standard():
    namespace, *_ = _deploy()

    def check(metadata):
        assert metadata["name"] == NAMESPACE
        labels = metadata["labels"]
        assert labels["pod-security.kubernetes.io/enforce"] == "restricted"
        assert labels["pod-security.kubernetes.io/audit"] == "restricted"
        assert labels["pod-security.kubernetes.io/warn"] == "restricted"
        assert labels["pod-security.kubernetes.io/enforce-version"] == "latest"

    return namespace.metadata.apply(check)


@pulumi.runtime.test
def test_config_volume_reads_the_ssd_export_and_is_never_reclaimed():
    _, data_volume, _, _, _, _, _ = _deploy()

    def check(spec):
        assert spec["persistent_volume_reclaim_policy"] == "Retain"
        assert spec["storage_class_name"] == DATA_STORAGE_CLASS
        assert spec["nfs"]["server"] == "192.168.4.11"
        assert spec["nfs"]["path"] == "/ssd_mirror/jellyfin"

    return data_volume.spec.apply(check)


@pulumi.runtime.test
def test_media_volume_reads_the_library_export_and_is_never_reclaimed():
    _, _, _, media_volume, _, _, _ = _deploy()

    def check(spec):
        assert spec["persistent_volume_reclaim_policy"] == "Retain"
        assert spec["storage_class_name"] == MEDIA_STORAGE_CLASS
        assert spec["nfs"]["server"] == "192.168.4.11"
        assert spec["nfs"]["path"] == "/hdd_mirror/media"

    return media_volume.spec.apply(check)


@pulumi.runtime.test
def test_each_claim_binds_to_its_own_volume_by_storage_class():
    _, _, data_claim, _, media_claim, _, _ = _deploy()

    def check(specs):
        data, media = specs
        # Distinct classes, or either claim could bind to the wrong export.
        assert data["storage_class_name"] == DATA_STORAGE_CLASS
        assert media["storage_class_name"] == MEDIA_STORAGE_CLASS
        assert data["resources"]["requests"]["storage"] == "50Gi"
        assert media["resources"]["requests"]["storage"] == "8Ti"

    return pulumi.Output.all(data_claim.spec, media_claim.spec).apply(check)


@pulumi.runtime.test
def test_deployment_runs_one_replica_as_the_podman_user():
    *_, deployment, _ = _deploy()

    def check(spec):
        assert spec["replicas"] == 1
        assert spec["selector"]["match_labels"] == APP_LABELS
        security = spec["template"]["spec"]["security_context"]
        assert security["run_as_user"] == PODMAN_UID
        assert security["run_as_group"] == PODMAN_GID
        assert security["fs_group"] == PODMAN_GID
        assert security["run_as_non_root"] is True
        # A recursive chown of the media library would take hours over NFS.
        assert security["fs_group_change_policy"] == "OnRootMismatch"
        assert security["seccomp_profile"]["type"] == "RuntimeDefault"

    return deployment.spec.apply(check)


@pulumi.runtime.test
def test_pod_drops_privileges_and_mounts_no_service_account_token():
    *_, deployment, _ = _deploy()

    def check(spec):
        pod = spec["template"]["spec"]
        assert pod["automount_service_account_token"] is False
        container = pod["containers"][0]
        assert container["image"] == IMAGE
        assert container["ports"][0]["container_port"] == CONTAINER_PORT
        assert container["security_context"]["allow_privilege_escalation"] is False
        assert container["security_context"]["capabilities"]["drop"] == ["ALL"]

    return deployment.spec.apply(check)


@pulumi.runtime.test
def test_config_and_cache_mount_as_subdirectories_of_one_claim():
    *_, deployment, _ = _deploy()

    def check(spec):
        pod = spec["template"]["spec"]
        mounts = {m["mount_path"]: m for m in pod["containers"][0]["volume_mounts"]}

        assert mounts["/config"]["name"] == DATA_VOLUME_NAME
        assert mounts["/config"]["sub_path"] == "config"
        assert mounts["/cache"]["name"] == DATA_VOLUME_NAME
        assert mounts["/cache"]["sub_path"] == "cache"

        # The library is the whole export, so it takes no sub_path.
        assert mounts["/media"]["name"] == MEDIA_VOLUME_NAME
        assert mounts["/media"].get("sub_path") is None

    return deployment.spec.apply(check)


@pulumi.runtime.test
def test_three_mounts_are_backed_by_two_pod_volumes():
    *_, deployment, _ = _deploy()

    def check(spec):
        pod = spec["template"]["spec"]
        assert len(pod["containers"][0]["volume_mounts"]) == 3
        # Duplicating the data volume would be rejected by the API server.
        claims = [v["persistent_volume_claim"]["claim_name"] for v in pod["volumes"]]
        assert claims == [DATA_VOLUME_NAME, MEDIA_VOLUME_NAME]

    return deployment.spec.apply(check)


@pulumi.runtime.test
def test_service_exposes_jellyfin_on_its_nodeport():
    *_, service = _deploy()

    def check(spec):
        assert spec["type"] == "NodePort"
        assert spec["selector"] == APP_LABELS
        port = spec["ports"][0]
        assert port["node_port"] == NODE_PORT
        assert port["port"] == CONTAINER_PORT
        assert port["target_port"] == CONTAINER_PORT

    return service.spec.apply(check)
