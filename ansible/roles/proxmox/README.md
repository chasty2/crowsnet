# Proxmox Role

Configures the Proxmox VE hypervisor (`esper`): exports the ZFS datasets that hold
container data over NFS, schedules backups of those datasets to the Proxmox Backup
Server, and bounds the ZFS ARC so the cache leaves RAM for the VMs.

The ARC bounds are written to `/etc/modprobe.d/zfs.conf` and the initramfs is rebuilt,
so they take effect on the host's **next boot** — run `./crowsnet.py update` to pick
them up.

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
- `proxmox_zfs_arc_min` - Lower bound on the ZFS ARC, in bytes (4 GiB)
- `proxmox_zfs_arc_max` - Upper bound on the ZFS ARC, in bytes (16 GiB)
- `proxmox_nfs_mounts` - Exported directories, as
  `{ path: "/mount/path", owner: remote_user, group: nfs_group, mode: "0770" }`
- `proxmox_cron_jobs` - Backup and pool-maintenance jobs, as
  `{ name, minute, hour, weekday, job }`
- `proxmox_pbs_repository` - Vaulted PBS repository the backup script targets
- `proxmox_pbs_password` - Vaulted password used to authenticate to PBS

From `group_vars/all`:
- `admin_users` - Admin accounts added to the `podman` group so they can read container
  data, as `{ name, uid, gid }`
