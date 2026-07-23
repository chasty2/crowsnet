# Virtual Role

Configures Proxmox guests with the QEMU guest agent, which the hypervisor needs to
report guest IPs and perform clean shutdowns.

## Requirements
- Host is a VM running under Proxmox VE

## Variables
- `virtual_packages` - Guest tooling to install (`qemu-guest-agent`, also baked into the VM template)
- `virtual_services` - Services started and enabled on boot
