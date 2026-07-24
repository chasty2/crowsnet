# MicroK8s Role

Installs [MicroK8s](https://microk8s.io/) on `kube-1`, grants the configured users
cluster access, and distributes the node's kubeconfig to development servers so
`kubectl` reaches the cluster remotely.

## Requirements
- `common` role
- `community.general` collection
- Ubuntu host with `snapd` available
- `kubectl` available for `microk8s_kubeconfig_user` on each development server

## Variables
- `microk8s_packages` - Snaps to install (`microk8s`, classic confinement, channel `1.32`)
- `microk8s_users` - Users added to the `microk8s` group and given a `~/.kube` directory
- `microk8s_kubeconfig_user` - User whose `~/.kube/config` receives the kubeconfig on development servers
- `development_servers` - Inventory hosts that receive the kubeconfig (defined in `group_vars/all`)

After copying the kubeconfig, the role verifies `kubectl get nodes` works as
`microk8s_kubeconfig_user` on each development server.

Inspired by
<https://github.com/8grams/ansible-microk8s/blob/main/install_microk8s.yaml>.
