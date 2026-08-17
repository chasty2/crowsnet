"""Provision CrowsNet infrastructure for the selected Pulumi stack.

The stack name selects what kind of infrastructure is deployed: `k8s` deploys
workloads onto the MicroK8s cluster, every other stack deploys Proxmox VMs.
"""

import pulumi
from pulumi_proxmoxve import Provider

from components.proxmox import ProxmoxVM
from test_k8s import deploy_test_nginx
from vms import select_vms


def deploy_proxmox_vms(stack: str) -> None:
    """Deploy the VMs belonging to a Proxmox stack."""
    config = pulumi.Config("proxmox")
    provider = Provider(
        "proxmoxve",
        endpoint=config.require("endpoint"),
        api_token=f"{config.require('api-name')}={config.require('api-token')}",
        insecure=True
    )

    for vm in select_vms(stack):
        ProxmoxVM(
            name=vm["name"],
            vmid=vm["vmid"],
            cpu=vm["cpu"],
            ram=vm["ram"],
            ip=vm["ip"],
            mac=vm["mac"],
            clone=vm["clone"],
            template=vm["template"],
            opts=pulumi.ResourceOptions(provider=provider),
        )


def deploy_k8s() -> None:
    """Deploy workloads onto the MicroK8s cluster.

    Cluster credentials come from the stack's `kubernetes:kubeconfig` config
    value, which the default kubernetes provider reads on its own.
    """
    _, service = deploy_test_nginx()
    pulumi.export("test_nginx_service", service.metadata.name)
    pulumi.export("test_nginx_node_port", service.spec.ports[0].node_port)


stack = pulumi.get_stack()

if stack == "k8s":
    deploy_k8s()
else:
    deploy_proxmox_vms(stack)
