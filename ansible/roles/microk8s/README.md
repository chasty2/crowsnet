# MicroK8s Role

Installs [MicroK8s](https://microk8s.io/) on `kube-1`, grants the configured users
cluster access, and distributes the node's kubeconfig to development servers so
`kubectl` reaches the cluster remotely.

## Requirements
- `common` role
- `community.general` collection
- Ubuntu host with `snapd` available
- `kubectl` available for `microk8s_user` on each development server

## Variables
- `microk8s_packages` - Snaps to install (`microk8s`, classic confinement, channel `1.32`)
- `microk8s_user` - User added to the `microk8s` group, given a `~/.kube` directory, and whose `~/.kube/config` receives the kubeconfig on development servers
- `development_servers` - Inventory hosts that receive the kubeconfig (defined in `group_vars/all`)
- `microk8s_permitted_ports` - Ports opened on the `internal` firewalld zone (defaults to `16443/tcp`, the kube-apiserver)

The role opens the kube-apiserver port (`16443/tcp`) on the internal zone so
`kubectl` from the development servers reaches the cluster with firewalld on.
