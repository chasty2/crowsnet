# Proxmox Role

Configures the Proxmox VE hypervisor (`esper`): exports the ZFS datasets that hold
container data over NFS, and schedules backups of those datasets to the Proxmox Backup
Server.

## Requirements
- `common` role (firewalld)
- `ansible.posix` collection
- Host is running Proxmox Virtual Environment with the ZFS datasets already created
- Host is configured to reach a Proxmox Backup Server
- The system users that own the exported data exist on this host and on the NFS clients

## Variables
- `proxmox_packages` - Packages to install (`nfs-kernel-server`)
- `proxmox_services` - Services started and enabled on boot
- `proxmox_ports` - firewalld ports on the `internal` zone (`8006/tcp` web UI, `2049/tcp` NFS)
- `proxmox_nfs_mounts` - Exported directories, as
  `{ path: "/mount/path", owner: remote_user, group: nfs_group, mode: "0770" }`
- `proxmox_cron_jobs` - Backup and pool-maintenance jobs, as
  `{ name, minute, hour, weekday, job }`
- `proxmox_pbs_repository` - Vaulted PBS repository the backup script targets
- `proxmox_pbs_password` - Vaulted password used to authenticate to PBS

From `group_vars/all`:
- `admin_users` - Admin accounts added to the `podman` group so they can read container
  data, as `{ name, uid, gid }`

## Tags
- `users` - Adds admin users to the `podman` group and installs `/root/backup.sh` from
  `templates/backup_script.j2`
- `packages` - NFS server installation
- `services` - Creates the exported directories, renders `/etc/exports`, schedules the
  backup cron jobs, enables the NFS server
- `firewall` - Opens the web UI and NFS ports on the `internal` zone
