# Dev Role

Sets up the development sandbox (`lab`): installs Claude Code and kubectl from their
respective signed apt repositories, installs baseline dev packages (git), and mounts
the shared secrets volume.

## Requirements
- `common` role
- `ansible.posix` collection
- NFS export `192.168.4.11:/ssd_mirror/secrets` served by the `proxmox` role
- Debian-family host

## Variables
- `dev_packages` - Baseline apt packages to install (`git`)
- `dev_claude_key_url` - Anthropic apt signing key to fetch
- `dev_claude_keyring` - Where that key is stored (`/etc/apt/keyrings/claude-code.asc`)
- `dev_claude_repo` - The apt source line, signed by the keyring above
- `dev_kubectl_key_url` - Kubernetes apt signing key to fetch (pinned to v1.32)
- `dev_kubectl_keyring` - Where that key is stored (`/etc/apt/keyrings/kubernetes-apt-keyring.asc`)
- `dev_kubectl_repo` - The kubectl apt source line, signed by the keyring above
- `dev_secrets_mount` - Mount point for the secrets volume (`/mnt/secrets`)
- `dev_secrets_user` - Owner of the mount point
