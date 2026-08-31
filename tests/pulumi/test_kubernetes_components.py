"""Tests for the reusable components in pulumi/components/kubernetes/.

These cover the defaults the components carry on their own. What Foundry does
with them is covered by tests/pulumi/test_foundry.py.
"""

import pulumi


class _Mocks(pulumi.runtime.Mocks):
    def new_resource(self, args: pulumi.runtime.MockResourceArgs):
        return [args.name + "_id", args.inputs]

    def call(self, args: pulumi.runtime.MockCallArgs):
        return {}


pulumi.runtime.set_mocks(_Mocks())

from components.kubernetes.deployment import (  # noqa: E402  (must follow set_mocks)
    ClaimMount,
    single_container_deployment,
)
from components.kubernetes.namespace import restricted_namespace  # noqa: E402
from components.kubernetes.persistent_volume import nfs_volume  # noqa: E402
from components.kubernetes.persistent_volume_claim import volume_claim  # noqa: E402
from components.kubernetes.service import node_port_service  # noqa: E402

LABELS = {"app": "demo"}


def _deployment(**overrides):
    kwargs = dict(
        name="demo",
        namespace="demo",
        image="demo:1",
        labels=LABELS,
        container_port=8080,
    )
    kwargs.update(overrides)
    return single_container_deployment(**kwargs)


@pulumi.runtime.test
def test_namespace_enforces_the_restricted_pod_security_standard():
    namespace = restricted_namespace("demo")

    def check(metadata):
        assert metadata["name"] == "demo"
        labels = metadata["labels"]
        assert labels["pod-security.kubernetes.io/enforce"] == "restricted"
        assert labels["pod-security.kubernetes.io/audit"] == "restricted"
        assert labels["pod-security.kubernetes.io/warn"] == "restricted"
        assert labels["pod-security.kubernetes.io/enforce-version"] == "latest"

    return namespace.metadata.apply(check)


@pulumi.runtime.test
def test_namespace_keeps_its_security_labels_alongside_extra_ones():
    namespace = restricted_namespace("demo", extra_labels={"team": "homelab"})

    def check(metadata):
        labels = metadata["labels"]
        assert labels["team"] == "homelab"
        assert labels["pod-security.kubernetes.io/enforce"] == "restricted"

    return namespace.metadata.apply(check)


@pulumi.runtime.test
def test_nfs_volume_retains_its_data_by_default():
    volume = nfs_volume(
        "demo-data",
        server="10.0.0.1",
        path="/export/demo",
        size="5Gi",
        storage_class="nfs-demo",
    )

    def check(spec):
        # The data outlives the cluster: never reclaim it.
        assert spec["persistent_volume_reclaim_policy"] == "Retain"
        assert spec["capacity"]["storage"] == "5Gi"
        assert spec["access_modes"] == ["ReadWriteOnce"]
        assert spec["mount_options"] == ["hard"]
        assert spec["nfs"]["server"] == "10.0.0.1"
        assert spec["nfs"]["path"] == "/export/demo"

    return volume.spec.apply(check)


@pulumi.runtime.test
def test_claim_requests_storage_of_the_named_class():
    claim = volume_claim(
        "demo-data",
        namespace="demo",
        size="5Gi",
        storage_class="nfs-demo",
    )

    def check(spec):
        assert spec["storage_class_name"] == "nfs-demo"
        assert spec["access_modes"] == ["ReadWriteOnce"]
        assert spec["resources"]["requests"]["storage"] == "5Gi"

    return claim.spec.apply(check)


@pulumi.runtime.test
def test_deployment_drops_privileges_and_mounts_no_service_account_token():
    deployment = _deployment()

    def check(spec):
        assert spec["replicas"] == 1
        assert spec["selector"]["match_labels"] == LABELS
        assert spec["template"]["metadata"]["labels"] == LABELS
        pod = spec["template"]["spec"]
        assert pod["automount_service_account_token"] is False
        assert pod["security_context"]["run_as_non_root"] is True
        assert pod["security_context"]["seccomp_profile"]["type"] == "RuntimeDefault"
        container = pod["containers"][0]
        assert container["image"] == "demo:1"
        assert container["ports"][0]["container_port"] == 8080
        assert container["security_context"]["allow_privilege_escalation"] is False
        assert container["security_context"]["capabilities"]["drop"] == ["ALL"]

    return deployment.spec.apply(check)


@pulumi.runtime.test
def test_deployment_runs_as_the_given_uid_without_chowning_the_volume():
    deployment = _deployment(run_as=(2004, 2004))

    def check(spec):
        security = spec["template"]["spec"]["security_context"]
        assert security["run_as_user"] == 2004
        assert security["run_as_group"] == 2004
        assert security["fs_group"] == 2004
        # A recursive chown would fail against a squashed NFS export.
        assert security["fs_group_change_policy"] == "OnRootMismatch"

    return deployment.spec.apply(check)


@pulumi.runtime.test
def test_deployment_without_a_run_as_leaves_the_uid_to_the_image():
    deployment = _deployment()

    def check(spec):
        security = spec["template"]["spec"]["security_context"]
        assert security.get("run_as_user") is None
        assert security.get("fs_group") is None
        assert security.get("fs_group_change_policy") is None

    return deployment.spec.apply(check)


@pulumi.runtime.test
def test_deployment_mounts_the_claim_at_the_requested_subdirectory():
    deployment = _deployment(
        mount=ClaimMount(
            claim_name="demo-data",
            mount_path="/data",
            sub_path="worlds",
        )
    )

    def check(spec):
        pod = spec["template"]["spec"]
        mount = pod["containers"][0]["volume_mounts"][0]
        assert mount["name"] == "demo-data"
        assert mount["mount_path"] == "/data"
        assert mount["sub_path"] == "worlds"
        assert pod["volumes"][0]["persistent_volume_claim"]["claim_name"] == "demo-data"

    return deployment.spec.apply(check)


@pulumi.runtime.test
def test_deployment_without_a_claim_declares_no_volumes():
    deployment = _deployment()

    def check(spec):
        pod = spec["template"]["spec"]
        assert pod.get("volumes") is None
        assert pod["containers"][0].get("volume_mounts") is None

    return deployment.spec.apply(check)


@pulumi.runtime.test
def test_service_routes_its_node_port_to_the_selected_pods():
    service = node_port_service(
        "demo",
        namespace="demo",
        selector=LABELS,
        port=8080,
        node_port=30080,
        labels=LABELS,
    )

    def check(spec):
        assert spec["type"] == "NodePort"
        assert spec["selector"] == LABELS
        port = spec["ports"][0]
        assert port["port"] == 8080
        assert port["node_port"] == 30080
        # Unspecified, so it follows the service port.
        assert port["target_port"] == 8080

    return service.spec.apply(check)


@pulumi.runtime.test
def test_service_can_target_a_container_port_of_its_own():
    service = node_port_service(
        "demo",
        namespace="demo",
        selector=LABELS,
        port=80,
        node_port=30080,
        target_port=8080,
    )

    def check(spec):
        assert spec["ports"][0]["port"] == 80
        assert spec["ports"][0]["target_port"] == 8080

    return service.spec.apply(check)
