# MicroK8s Role

Installs [MicroK8s](https://microk8s.io/) on `kube-1` and grants the configured user
cluster access. Everything this role does is local to the node; the `dev` role is what
pulls the node's kubeconfig onto the development servers.

## Requirements
- `common` role
- `community.general` collection
- Ubuntu host with `snapd` available

## Variables
- `microk8s_packages` - Snaps to install (`microk8s`, classic confinement, channel `1.32`)
- `microk8s_user` - User added to the `microk8s` group and given a `~/.kube` directory
- `microk8s_permitted_ports` - Ports opened on the `internal` firewalld zone (the
  kube-apiserver and the Kubernetes NodePort range)

## Testing
Covered by the `kube-1` Molecule scenario (`ansible/molecule/kube-1/`), whose
`verify.yml` includes the assertion tasks in this role's `tests/` directory.
