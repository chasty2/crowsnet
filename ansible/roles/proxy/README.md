# Proxy Role

Runs [Nginx Proxy Manager](https://nginxproxymanager.com/) as a rootless Podman container
on `proxy`, the reverse proxy that terminates HTTP/HTTPS for every public service. Its
configuration and Let's Encrypt certificates live on an NFS volume so they survive a
rebuild.

## Requirements
- `common` and `podman` roles
- `public` role (host is in the `dmz` group)
- `ansible.posix` and `containers.podman` collections
- NFS export `192.168.4.11:/ssd_mirror/proxy` served by the `proxmox` role

## Variables
- `proxy_internal_ports` - firewalld ports on the `internal` zone (`81/tcp`, the admin UI)
- `proxy_public_ports` - firewalld services on the `public` zone (`http`, `https`)
- `proxy_users` - Users added to the `podman` group, locally and on the NFS server

From `group_vars/all`:
- `nfs_server` - Host the group membership change is delegated to, so NFS ownership stays in sync
