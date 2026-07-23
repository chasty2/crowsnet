# Podman Role

Installs Podman and prepares the `podman` service account to run rootless containers.
Every application role that ships a container (`proxy`, `jellyfin`, `foundry`) depends on
this role running first.

## Requirements
- `common` role (creates the `podman` user and group)
- `ansible.posix` collection

## Variables
- `podman_packages` - Packages to install (`podman`)

## Tags
- `users` - Authorizes the CrowsNet SSH key for the `podman` user and enables
  systemd lingering so its containers survive logout
- `packages` - Podman installation
