# Dev Role

Sets up the development sandbox (`lab`): installs the dev packages, including Claude
Code and kubectl from their respective signed apt repositories, installs uv from
Astral's install script (there is no apt repository for it), and mounts the shared
secrets volume.

## Requirements
- `common` role
- `ansible.posix` collection
- NFS export `192.168.4.11:/ssd_mirror/secrets` served by the `proxmox` role
- Debian-family host

## Variables
- `dev_packages` - Apt packages to install on the dev host
- `dev_claude_key_url` - Anthropic apt signing key to fetch
- `dev_claude_keyring` - Where that key is stored (`/etc/apt/keyrings/claude-code.asc`)
- `dev_claude_repo` - The apt source line, signed by the keyring above
- `dev_kubectl_key_url` - Kubernetes apt signing key to fetch (pinned to v1.32)
- `dev_kubectl_keyring` - Where that key is stored (`/etc/apt/keyrings/kubernetes-apt-keyring.asc`)
- `dev_kubectl_repo` - The kubectl apt source line, signed by the keyring above
- `dev_uv_installer_url` - Astral install script to fetch
- `dev_uv_installer_path` - Where that script is stored (`/usr/local/src/uv-install.sh`)
- `dev_uv_install_dir` - Where `uv` and `uvx` are installed (`/usr/local/bin`)
- `dev_secrets_mount` - Mount point for the secrets volume (`/mnt/secrets`)
- `dev_secrets_user` - Owner of the mount point
