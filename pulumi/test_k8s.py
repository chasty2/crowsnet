"""Throwaway nginx workload used to smoke-test the k8s stack.

Kept free of Pulumi runtime side effects at import time so it can be imported
and unit-tested without a live Pulumi engine.
"""

import pulumi_kubernetes as kubernetes

APP_NAME = "nginx-test"
APP_LABELS = {"app": APP_NAME}
IMAGE = "nginx:stable"
CONTAINER_PORT = 80
NODE_PORT = 30080


def deploy_test_nginx():
    """Create an nginx Deployment and the NodePort Service that exposes it.

    Returns:
        A (deployment, service) tuple.
    """
    deployment = kubernetes.apps.v1.Deployment(
        APP_NAME,
        metadata=kubernetes.meta.v1.ObjectMetaArgs(
            name=APP_NAME,
            labels=APP_LABELS,
        ),
        spec=kubernetes.apps.v1.DeploymentSpecArgs(
            replicas=1,
            selector=kubernetes.meta.v1.LabelSelectorArgs(
                match_labels=APP_LABELS,
            ),
            template=kubernetes.core.v1.PodTemplateSpecArgs(
                metadata=kubernetes.meta.v1.ObjectMetaArgs(
                    labels=APP_LABELS,
                ),
                spec=kubernetes.core.v1.PodSpecArgs(
                    containers=[
                        kubernetes.core.v1.ContainerArgs(
                            name=APP_NAME,
                            image=IMAGE,
                            ports=[
                                kubernetes.core.v1.ContainerPortArgs(
                                    container_port=CONTAINER_PORT,
                                )
                            ],
                        )
                    ],
                ),
            ),
        ),
    )

    service = kubernetes.core.v1.Service(
        APP_NAME,
        metadata=kubernetes.meta.v1.ObjectMetaArgs(
            name=APP_NAME,
            labels=APP_LABELS,
        ),
        spec=kubernetes.core.v1.ServiceSpecArgs(
            type="NodePort",
            selector=APP_LABELS,
            ports=[
                kubernetes.core.v1.ServicePortArgs(
                    port=CONTAINER_PORT,
                    target_port=CONTAINER_PORT,
                    node_port=NODE_PORT,
                )
            ],
        ),
    )

    return deployment, service
