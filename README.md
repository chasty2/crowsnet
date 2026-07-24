# CrowsNet

A self-hosted homelab that runs entirely out of infrastructure-as-code. Pulumi
provisions virtual machines on Proxmox, Ansible configures the machines, and both
run from a single container driven by the `crowsnet.py` CLI. Applications are run
via rootless Podman containers. NFS storage of application data allows for VM's
and containers to be destroyed and rebuilt with no data loss

Feel free to use anything here that you find helpful

## Infrastructure

Three physical machines host everything. Proxmox VE runs the VMs, which are backed up to
a separate machine running Proxmox Backup Server. A GPU workstation handles development
and heavy compute

| Host | Type | Role |
|------|------|------|
| `esper` | Physical | Proxmox VE hypervisor; NFS server for container data; nightly backups to PBS |
| `simic` | Physical | Proxmox Backup Server |
| `abzan` | Physical | GPU/development server; Jupyter and Sunshine game streaming |
| `gate` | VM | Public-facing SSH bastion |
| `proxy` | VM | Nginx Proxy Manager; terminates HTTP/HTTPS for public services |
| `bailey` | VM | Web services: Jellyfin and FoundryVTT |
| `kube-1` | VM | MicroK8s node |
| `lab` | VM | Development sandbox for concurrent Claude code instances |
| `stage` | VM | Ephemeral VM used only by the integration test suite |


## Getting Started

Requirements:

- [uv](https://docs.astral.sh/uv/) for Python tooling
- [podman](https://podman.io/) to build and run the ops container
- API access to the Proxmox host
- Pulumi access token
- Ansible vault password

```bash
git config core.hooksPath .githooks   # once per clone; blocks pushes to main
uv sync                               # host-side venv for the CLI and unit tests
./crowsnet.py build                   # build the ops container
```

Secrets are not committed in plaintext. Ansible reads its vault password from
`ansible/vault.pass` and Pulumi reads its token from `pulumi/pulumi.token`; both are
mounted into the container at run time

## Provisioning (Pulumi)

VM definitions live in [`pulumi/vms.py`](pulumi/vms.py). VM's use MAC-associated fixed
IP addresses that are assigned via DHCP. VM's are are managed across three Pulumi stacks:

| Stack | Purpose |
|-------|---------|
| `stage` | Throwaway VM created and destroyed by the Molecule suite |
| `dev` | Development sandbox |
| `prod` | The live homelab |

```bash
./crowsnet.py deploy <stage|dev|prod>    # pulumi up
./crowsnet.py destroy <stage|dev|prod>   # pulumi destroy
./crowsnet.py refresh <stage|dev|prod>   # pulumi refresh
```

## Configuration (Ansible)

System-level configuration and deployment of app containers are managed via Ansible
roles. Each role splits its work across up to five task files with matching tags — 
`users`, `system`, `packages`, `services`, and `firewall` — so any slice of the 
configuration can be applied on its own. The authoring conventions are in
[`ansible/CLAUDE.md`](ansible/CLAUDE.md).

```bash
./crowsnet.py configure                    # full site deployment
./crowsnet.py configure --tags users       # run specific tags
./crowsnet.py configure --limit gate       # limit to specific host(s)
./crowsnet.py configure --check            # dry-run mode
./crowsnet.py update                       # patch and reboot all VMs
```

## Deployment via Container

Ansible and Pulumi both run inside one Docker image. This allows for reproducible runs
across different machines

## Testing

The suite has two layers (a third, CI on a self-hosted runner, is still pending):

- **Unit (pytest)** — fast, host-only, no infrastructure. Covers the Click CLI dispatch,
  podman command construction, and Pulumi component logic. Lives in [`tests/`](tests/)

- **Integration (Molecule)** — provisions the real `stage` VM via Pulumi, converges a
  role, checks idempotency, runs tests, then tears the VM down.

```bash
./crowsnet.py test                                # unit tests
./crowsnet.py test --integration                  # integration suite (role: common)
./crowsnet.py test --integration --role <role>    # integration suite for a specific role
```

CI/CD is done via GitHub Actions