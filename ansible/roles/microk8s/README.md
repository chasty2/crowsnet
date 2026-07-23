# MicroK8s Role

Installs [MicroK8s](https://microk8s.io/) on `kube-1` and grants the configured users
cluster access.

## Requirements
- `common` role
- `community.general` collection
- Ubuntu host with `snapd` available

## Variables
- `microk8s_packages` - Snaps to install (`microk8s`, classic confinement, channel `1.32`)
- `microk8s_users` - Users added to the `microk8s` group and given a `~/.kube` directory

## Tags
- `packages` - MicroK8s snap installation
- `users` - Group membership and `~/.kube` cache directory

Inspired by
<https://github.com/8grams/ansible-microk8s/blob/main/install_microk8s.yaml>.
