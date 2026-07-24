# Foundry Role

Runs [Foundry Virtual Tabletop](https://foundryvtt.com/) as a rootless Podman container on
`bailey`, with its world data on an NFS mount from the hypervisor.

## Requirements
- `common` and `podman` roles
- `ansible.posix` and `containers.podman` collections
- NFS export `192.168.4.11:/ssd_mirror/foundry` served by the `proxmox` role
- A Foundry license tied to the configured account

## Variables
- `foundry_ports` - firewalld ports on the `internal` zone (`30000/tcp`)
- `foundry_users` - Users added to the `podman` group, locally and on the NFS server
- `foundry_login` - Foundry account used by the container to fetch the licensed build
- `foundry_login_password` - Vaulted password for that account

From `group_vars/all`:
- `nfs_server` - Host the group membership change is delegated to, so NFS ownership stays in sync
