# Dev Role

Sets up the development sandbox (`lab`): installs the dev packages, including Claude
Code, kubectl, and gh from their respective signed apt repositories, installs uv and
Pulumi from their official install scripts (there is no apt repository for either),
and mounts the shared secrets volume.

## Requirements
- `common` role
- `ansible.posix` collection
- NFS export `192.168.4.11:/ssd_mirror/secrets` served by the `proxmox` role
- Debian-family host

## Variables
- `dev_packages` - Apt packages to install on the dev host
- `dev_apt_repos` - List of signed apt repositories to add before installing
  `dev_packages`; each entry has `name` (apt source filename), `key_url` (signing
  key to fetch), `keyring` (where that key is stored under `/etc/apt/keyrings/`),
  and `repo` (the apt source line, signed by the keyring)
- `dev_uv_installer_url` - Astral install script to fetch
- `dev_uv_installer_path` - Where that script is stored (`/usr/local/src/uv-install.sh`)
- `dev_uv_install_dir` - Where `uv` and `uvx` are installed (`/usr/local/bin`)
- `dev_pulumi_installer_url` - Pulumi install script to fetch
- `dev_pulumi_installer_path` - Where that script is stored
  (`/usr/local/src/pulumi-install.sh`)
- `dev_pulumi_install_root` - Install root passed to the script (`/usr/local`), so
  `pulumi` and its language-host helpers land in `/usr/local/bin`
- `dev_secrets_mount` - Mount point for the secrets volume (`/mnt/secrets`)
- `dev_secrets_user` - Owner of the mount point
