"""
Provision CrowsNet infrastructure for the selected Pulumi stack.
"""

import pulumi
from pulumi_proxmoxve import Provider

from apps.foundry import deploy_foundry
from apps.jellyfin import deploy_jellyfin
from apps.virtual_machines import select_vms
from components.proxmox.virtual_machine import ProxmoxVM


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
    value, which the default kubernetes provider reads on its own. The Foundry
    account lives in the same stack config, as `foundry:username` and the
    encrypted `foundry:password`.
    """
    config = pulumi.Config("foundry")
    *_, foundry_service = deploy_foundry(
        username=config.require("username"),
        password=config.require_secret("password"),
    )
    pulumi.export("foundry_node_port", foundry_service.spec.ports[0].node_port)

    *_, jellyfin_service = deploy_jellyfin()
    pulumi.export("jellyfin_node_port", jellyfin_service.spec.ports[0].node_port)


stack = pulumi.get_stack()

if stack == "k8s":
    deploy_k8s()
else:
    deploy_proxmox_vms(stack)
