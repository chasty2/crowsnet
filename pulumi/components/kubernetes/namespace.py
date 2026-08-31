"""Namespaces that enforce the restricted Pod Security Standard."""

import pulumi
import pulumi_kubernetes as kubernetes

# Pod Security Admission is driven by namespace labels, not RBAC, so a workload
# that never calls the API server still needs these to be sandboxed.
RESTRICTED_PSA_LABELS = {
    "pod-security.kubernetes.io/enforce": "restricted",
    "pod-security.kubernetes.io/enforce-version": "latest",
    "pod-security.kubernetes.io/audit": "restricted",
    "pod-security.kubernetes.io/warn": "restricted",
}


def restricted_namespace(
    name: str,
    extra_labels: dict[str, str] | None = None,
    opts: pulumi.ResourceOptions | None = None,
) -> kubernetes.core.v1.Namespace:
    """Create a namespace that enforces the restricted Pod Security Standard.

    Args:
        name: Namespace name, used as the Pulumi resource name too.
        extra_labels: Additional labels merged over the Pod Security ones.
        opts: Pulumi resource options.

    Returns:
        The Namespace resource.
    """
    return kubernetes.core.v1.Namespace(
        name,
        metadata=kubernetes.meta.v1.ObjectMetaArgs(
            name=name,
            labels={**RESTRICTED_PSA_LABELS, **(extra_labels or {})},
        ),
        opts=opts,
    )
