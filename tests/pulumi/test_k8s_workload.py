"""Tests for the nginx smoke-test workload in pulumi/test_k8s.py."""

import pulumi


class _Mocks(pulumi.runtime.Mocks):
    def new_resource(self, args: pulumi.runtime.MockResourceArgs):
        return [args.name + "_id", args.inputs]

    def call(self, args: pulumi.runtime.MockCallArgs):
        return {}


pulumi.runtime.set_mocks(_Mocks())

from test_k8s import (  # noqa: E402  (must follow set_mocks)
    APP_LABELS,
    IMAGE,
    NODE_PORT,
    deploy_test_nginx,
)


@pulumi.runtime.test
def test_deployment_runs_one_labelled_nginx_replica():
    deployment, _ = deploy_test_nginx()

    def check(spec):
        assert spec["replicas"] == 1
        assert spec["selector"]["match_labels"] == APP_LABELS
        assert spec["template"]["metadata"]["labels"] == APP_LABELS
        container = spec["template"]["spec"]["containers"][0]
        assert container["image"] == IMAGE
        assert container["ports"][0]["container_port"] == 80

    return deployment.spec.apply(check)


@pulumi.runtime.test
def test_service_exposes_the_deployment_on_a_nodeport():
    _, service = deploy_test_nginx()

    def check(spec):
        assert spec["type"] == "NodePort"
        assert spec["selector"] == APP_LABELS
        port = spec["ports"][0]
        assert port["node_port"] == NODE_PORT
        assert port["port"] == 80
        assert port["target_port"] == 80

    return service.spec.apply(check)
