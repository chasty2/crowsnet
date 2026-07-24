# Jellyfin Role

Runs [Jellyfin](https://jellyfin.org/) as a rootless Podman container on `bailey`. The
media library and the server's cache and config directories are NFS mounts from the
hypervisor, so container data outlives the VM.

## Requirements
- `common` and `podman` roles
- `ansible.posix` and `containers.podman` collections
- NFS exports `192.168.4.11:/ssd_mirror/jellyfin` and `192.168.4.11:/hdd_mirror/media`
  served by the `proxmox` role

## Variables
- `jellyfin_ports` - firewalld ports on the `internal` zone (`8096/tcp`)
- `jellyfin_users` - Users added to the `podman` group, locally and on the NFS server

From `group_vars/all`:
- `nfs_server` - Host the group membership change is delegated to, so NFS ownership stays in sync
