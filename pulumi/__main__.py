"""A Python Pulumi program"""

import pulumi
from pulumi_proxmoxve import Provider

from components import ProxmoxVM

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

STAGE_VMS = [
    {"name": "lab",    "vmid": 200, "cpu": 2, "ram": 4096,  "ip": "192.168.4.200", "mac": "CA:9B:F1:85:90:C0", "clone": False, "template": "small"},
]

PROD_VMS = [
    {"name": "gate",   "vmid": 100, "cpu": 2, "ram": 4096,  "ip": "192.168.4.100", "mac": "82:08:61:78:5A:6C", "clone": False, "template": "small"},
    {"name": "proxy",  "vmid": 101, "cpu": 2, "ram": 8192,  "ip": "192.168.4.101", "mac": "BC:24:11:88:D8:67", "clone": False, "template": "small"},
    {"name": "bailey", "vmid": 125, "cpu": 4, "ram": 12288, "ip": "192.168.4.125", "mac": "02:26:85:4A:AC:52", "clone": False, "template": "small"},
    {"name": "kube-1", "vmid": 126, "cpu": 2, "ram": 8192,  "ip": "192.168.4.126", "mac": "BC:24:11:91:7B:19", "clone": False, "template": "large"},
]

stack = pulumi.get_stack()
vms = STAGE_VMS if stack == "stage" else PROD_VMS

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
