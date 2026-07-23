# PBS Role

Configures the Proxmox Backup Server host (`simic`) by opening the port its web UI and
backup clients use. The backup jobs themselves are scheduled by the `proxmox` role on the
hypervisor.

## Requirements
- `common` role (firewalld)
- `ansible.posix` collection
- Host is running Proxmox Backup Server

## Variables
- `pbs_permitted_ports` - firewalld ports on the `internal` zone (`8007/tcp`, backups and web portal)

## Tags
- `firewall` - Opens the PBS port on the `internal` zone
