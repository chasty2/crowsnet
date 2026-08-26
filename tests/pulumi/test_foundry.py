"""Tests for the Foundry workload in pulumi/foundry.py."""

import pulumi


class _Mocks(pulumi.runtime.Mocks):
    def new_resource(self, args: pulumi.runtime.MockResourceArgs):
        return [args.name + "_id", args.inputs]

    def call(self, args: pulumi.runtime.MockCallArgs):
        return {}


pulumi.runtime.set_mocks(_Mocks())

from foundry import (  # noqa: E402  (must follow set_mocks)
    APP_LABELS,
    IMAGE,
    NAMESPACE,
    NODE_PORT,
    PODMAN_GID,
    PODMAN_UID,
    SECRET_NAME,
    STORAGE_CLASS,
    VOLUME_NAME,
    deploy_foundry,
)

USERNAME = "test-account"
PASSWORD = "test-password"


def _deploy():
    return deploy_foundry(username=USERNAME, password=PASSWORD)


@pulumi.runtime.test
def test_namespace_enforces_the_restricted_pod_security_standard():
    namespace, _, _, _, _, _ = _deploy()

    def check(metadata):
        assert metadata["name"] == NAMESPACE
        labels = metadata["labels"]
        assert labels["pod-security.kubernetes.io/enforce"] == "restricted"
        assert labels["pod-security.kubernetes.io/audit"] == "restricted"
        assert labels["pod-security.kubernetes.io/warn"] == "restricted"
        assert labels["pod-security.kubernetes.io/enforce-version"] == "latest"

    return namespace.metadata.apply(check)


@pulumi.runtime.test
def test_volume_reads_the_nfs_export_and_is_never_reclaimed():
    _, _, volume, _, _, _ = _deploy()

    def check(spec):
        assert spec["persistent_volume_reclaim_policy"] == "Retain"
        assert spec["storage_class_name"] == STORAGE_CLASS
        assert spec["access_modes"] == ["ReadWriteOnce"]
        assert spec["nfs"]["server"] == "192.168.4.11"
        assert spec["nfs"]["path"] == "/ssd_mirror/foundry"

    return volume.spec.apply(check)


@pulumi.runtime.test
def test_claim_binds_to_the_nfs_volume_by_storage_class():
    _, _, _, claim, _, _ = _deploy()

    def check(spec):
        assert spec["storage_class_name"] == STORAGE_CLASS
        assert spec["access_modes"] == ["ReadWriteOnce"]
        assert spec["resources"]["requests"]["storage"] == "50Gi"

    return claim.spec.apply(check)


@pulumi.runtime.test
def test_deployment_runs_one_replica_as_the_podman_user():
    _, _, _, _, deployment, _ = _deploy()

    def check(spec):
        assert spec["replicas"] == 1
        assert spec["selector"]["match_labels"] == APP_LABELS
        pod = spec["template"]["spec"]
        security = pod["security_context"]
        assert security["run_as_user"] == PODMAN_UID
        assert security["run_as_group"] == PODMAN_GID
        assert security["fs_group"] == PODMAN_GID
        assert security["run_as_non_root"] is True
        # A recursive chown would fail against the root_squash export.
        assert security["fs_group_change_policy"] == "OnRootMismatch"
        assert security["seccomp_profile"]["type"] == "RuntimeDefault"

    return deployment.spec.apply(check)


@pulumi.runtime.test
def test_pod_drops_privileges_and_mounts_no_service_account_token():
    _, _, _, _, deployment, _ = _deploy()

    def check(spec):
        pod = spec["template"]["spec"]
        assert pod["automount_service_account_token"] is False
        container = pod["containers"][0]
        assert container["image"] == IMAGE
        assert container["security_context"]["allow_privilege_escalation"] is False
        assert container["security_context"]["capabilities"]["drop"] == ["ALL"]

    return deployment.spec.apply(check)


@pulumi.runtime.test
def test_credentials_reach_the_container_only_through_the_secret():
    _, _, _, _, deployment, _ = _deploy()

    def check(spec):
        env = spec["template"]["spec"]["containers"][0]["env"]
        by_name = {var["name"]: var for var in env}

        for name in ("FOUNDRY_USERNAME", "FOUNDRY_PASSWORD"):
            secret_ref = by_name[name]["value_from"]["secret_key_ref"]
            assert secret_ref["name"] == SECRET_NAME
            assert secret_ref["key"] == name
            assert "value" not in by_name[name]

        assert by_name["FOUNDRY_PROTOCOL"]["value"] == "4"
        assert by_name["CONTAINER_PRESERVE_CONFIG"]["value"] == "true"

    return deployment.spec.apply(check)


@pulumi.runtime.test
def test_world_data_mounts_from_the_data_subdirectory_of_the_export():
    _, _, _, _, deployment, _ = _deploy()

    def check(spec):
        pod = spec["template"]["spec"]
        mount = pod["containers"][0]["volume_mounts"][0]
        assert mount["name"] == VOLUME_NAME
        assert mount["mount_path"] == "/data"
        assert mount["sub_path"] == "data"

        volume = pod["volumes"][0]
        assert volume["persistent_volume_claim"]["claim_name"] == VOLUME_NAME

    return deployment.spec.apply(check)


@pulumi.runtime.test
def test_service_exposes_foundry_on_its_nodeport():
    _, _, _, _, _, service = _deploy()

    def check(spec):
        assert spec["type"] == "NodePort"
        assert spec["selector"] == APP_LABELS
        port = spec["ports"][0]
        assert port["node_port"] == NODE_PORT
        assert port["port"] == 30000
        assert port["target_port"] == 30000

    return service.spec.apply(check)
