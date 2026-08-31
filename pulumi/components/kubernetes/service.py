"""Services that expose a workload on a node port."""

import pulumi
import pulumi_kubernetes as kubernetes


def node_port_service(
    name: str,
    namespace: str,
    selector: dict[str, str],
    port: int,
    node_port: int,
    target_port: int | None = None,
    labels: dict[str, str] | None = None,
    opts: pulumi.ResourceOptions | None = None,
) -> kubernetes.core.v1.Service:
    """Create a NodePort Service in front of a workload.

    Args:
        name: Service name, used as the Pulumi resource name too.
        namespace: Namespace to place the service in.
        selector: Pod labels the service routes to.
        port: Port the service listens on.
        node_port: Port opened on every node.
        target_port: Container port to route to; defaults to `port`.
        labels: Labels for the service metadata.
        opts: Pulumi resource options.

    Returns:
        The Service resource.
    """
    return kubernetes.core.v1.Service(
        name,
        metadata=kubernetes.meta.v1.ObjectMetaArgs(
            name=name,
            namespace=namespace,
            labels=labels,
        ),
        spec=kubernetes.core.v1.ServiceSpecArgs(
            type="NodePort",
            selector=selector,
            ports=[
                kubernetes.core.v1.ServicePortArgs(
                    port=port,
                    target_port=target_port if target_port is not None else port,
                    node_port=node_port,
                )
            ],
        ),
        opts=opts,
    )
