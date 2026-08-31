"""Reusable Kubernetes building blocks for CrowsNet workloads.

Each module wraps a single Kubernetes resource behind a factory function that
carries the homelab's defaults — restricted Pod Security Admission, retained
storage, dropped capabilities — so every application does not restate them.

The functions return the native `pulumi_kubernetes` resource rather than a
`ComponentResource`: a component wrapper would add a URN layer without grouping
anything, and would force a replacement of every resource already deployed.
"""
