# Dev Role

Sets up the development sandbox (`lab`): installs Claude Code from Anthropic's signed apt
repository and mounts the shared secrets volume.

## Requirements
- `common` role
- `ansible.posix` collection
- NFS export `192.168.4.11:/ssd_mirror/secrets` served by the `proxmox` role
- Debian-family host

## Variables
- `dev_claude_key_url` - Anthropic apt signing key to fetch
- `dev_claude_keyring` - Where that key is stored (`/etc/apt/keyrings/claude-code.asc`)
- `dev_claude_repo` - The apt source line, signed by the keyring above
- `dev_secrets_mount` - Mount point for the secrets volume (`/mnt/secrets`)
- `dev_secrets_user` - Owner of the mount point
