import pulumi
import pulumi_proxmoxve as proxmox

TEMPLATES = {
    "small": {"clone_vmid": 301, "disk_size": 36},
    "large": {"clone_vmid": 302, "disk_size": 130},
}


class ProxmoxVM(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        vmid: int,
        cpu: int,
        ram: int,
        ip: str,
        mac: str,
        clone: bool,
        template: str,
        opts: pulumi.ResourceOptions = None,
    ):
        super().__init__("crowsnet:proxmox:VM", name, None, opts)

        tmpl = TEMPLATES[template]

        self.vm = proxmox.vm.VirtualMachine(
            resource_name=name,
            name=name,
            node_name="esper",
            vm_id=vmid,
            agent=proxmox.vm.VirtualMachineAgentArgs(
                enabled=True,
                trim=True,
                type="virtio",
            ),
            bios="seabios",
            cpu=proxmox.vm.VirtualMachineCpuArgs(
                cores=cpu,
                sockets=1,
            ),
            memory=proxmox.vm.VirtualMachineMemoryArgs(
                dedicated=ram,
            ),
            clone=proxmox.vm.VirtualMachineCloneArgs(
                node_name="esper",
                vm_id=tmpl["clone_vmid"],
                full=clone,
            ),
            disks=[
                proxmox.vm.VirtualMachineDiskArgs(
                    interface="scsi0",
                    datastore_id="ssd_mirror",
                    size=tmpl["disk_size"],
                    file_format="qcow2",
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
                    mac_address=mac,
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
                            address=f"{ip}/22",
                            gateway="192.168.4.1",
                        ),
                    )
                ],
            ),
            opts=pulumi.ResourceOptions(parent=self, provider=opts.provider if opts else None),
        )

        self.register_outputs({})
