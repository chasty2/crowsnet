"""A Python Pulumi program"""

import pulumi
import pulumi_proxmoxve as proxmox
from pulumi_proxmoxve import Provider
from pulumi_proxmoxve.vm import VirtualMachine

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


virtual_machine = proxmox.vm.VirtualMachine(
    opts=pulumi.ResourceOptions(provider=provider),
    name="lab",             # Name in Proxmox
    resource_name="lab",    # Name in Pulumi config
    node_name="esper", 
    vm_id=200,
    agent=proxmox.vm.VirtualMachineAgentArgs(
        enabled=True, # toggles checking for ip addresses through qemu-guest-agent
        trim=True,
        type="virtio"
    ),
    bios="seabios",
    cpu=proxmox.vm.VirtualMachineCpuArgs(
        cores=2,
        sockets=1
    ),
    memory=proxmox.vm.VirtualMachineMemoryArgs(
        dedicated=4096
    ),
    clone=proxmox.vm.VirtualMachineCloneArgs(
        node_name="esper",
        vm_id=301,
        full=False
    ),
    disks=[
        proxmox.vm.VirtualMachineDiskArgs(
            interface="scsi0",
            datastore_id="ssd_mirror",
            size=36,
            file_format="qcow2"
        )
    ],
    cdrom=proxmox.vm.VirtualMachineCdromArgs(
        file_id="none",
        interface="ide2",
    ),
    network_devices=[
        proxmox.vm.VirtualMachineNetworkDeviceArgs(
            bridge="vmbr0",
            model="virtio",
            mac_address="CA:9B:F1:85:90:C0"
        )
    ],
    on_boot=True,
    operating_system=proxmox.vm.VirtualMachineOperatingSystemArgs(),
    initialization=proxmox.vm.VirtualMachineInitializationArgs(
        type="nocloud",
        datastore_id="ssd_mirror",
        ip_configs=[
            proxmox.vm.VirtualMachineInitializationIpConfigArgs(
                ipv4=proxmox.vm.VirtualMachineInitializationIpConfigIpv4Args(
                    address="192.168.4.200/24",
                    gateway="192.168.4.1"
                ),
            )
        ]
    )
)