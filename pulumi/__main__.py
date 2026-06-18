"""Provision CrowsNet virtual machines"""

import pulumi
from pulumi_proxmoxve import Provider

from components import ProxmoxVM
from vms import select_vms

config = pulumi.Config("proxmox")
endpoint = config.require("endpoint")
api_token = config.require("api-token")
api_name = config.require("api-name")

provider = Provider(
    "proxmoxve",
    endpoint=endpoint,
    api_token=f"{api_name}={api_token}",
    insecure=True
)

vms = select_vms(pulumi.get_stack())

for vm in vms:
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
