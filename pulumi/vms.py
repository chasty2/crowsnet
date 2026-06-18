"""VM definitions and stack selection for CrowsNet infrastructure.

Kept free of Pulumi runtime side effects so it can be imported and unit-tested
without a live Pulumi engine.
"""

STAGE_VMS = [
    {"name": "lab",    "vmid": 200, "cpu": 2, "ram": 4096,  "ip": "192.168.4.200", "mac": "CA:9B:F1:85:90:C0", "clone": True, "template": "small"},
]

PROD_VMS = [
    {"name": "gate",   "vmid": 100, "cpu": 2, "ram": 4096,  "ip": "192.168.4.100", "mac": "82:08:61:78:5A:6C", "clone": False, "template": "small"},
    {"name": "proxy",  "vmid": 101, "cpu": 2, "ram": 8192,  "ip": "192.168.4.101", "mac": "BC:24:11:88:D8:67", "clone": False, "template": "small"},
    {"name": "bailey", "vmid": 125, "cpu": 4, "ram": 12288, "ip": "192.168.4.125", "mac": "02:26:85:4A:AC:52", "clone": False, "template": "small"},
    {"name": "kube-1", "vmid": 126, "cpu": 2, "ram": 8192,  "ip": "192.168.4.126", "mac": "BC:24:11:91:7B:19", "clone": False, "template": "large"},
]


def select_vms(stack: str) -> list[dict]:
    """Return the VM definitions for a stack, rejecting unknown stacks."""
    if stack == "stage":
        return STAGE_VMS
    if stack == "prod":
        return PROD_VMS
    raise ValueError(f"Unknown stack '{stack}'. Expected 'stage' or 'prod'.")
