# CrowsNet

A self-hosted homelab that runs entirely out of infrastructure-as-code. Pulumi
provisions virtual machines on Proxmox, Ansible configures every machine, and both
run from a single container driven by the `crowsnet.py` CLI. Nothing is configured by
hand — a rebuilt host reaches its intended state by re-running the code in this repo.

Feel free to use anything here that you find helpful.

## Homelab Overview

Three physical machines host everything. Proxmox runs the VMs, a separate box holds
backups, and a GPU workstation handles compute.

| Host | Type | Role |
|------|------|------|
| `esper` | Physical | Proxmox VE hypervisor; NFS server for container data; nightly backups to PBS |
| `simic` | Physical | Proxmox Backup Server |
| `abzan` | Physical | GPU/development server; Jupyter and Sunshine game streaming |
| `gate` | VM | Public-facing SSH bastion |
| `proxy` | VM | Nginx Proxy Manager; terminates HTTP/HTTPS for public services |
| `bailey` | VM | Web services: Jellyfin and FoundryVTT |
| `kube-1` | VM | MicroK8s node |
| `lab` | VM | Development sandbox |
| `stage` | VM | Ephemeral VM used only by the integration test suite |

Everything sits on `192.168.4.0/22`. `gate` and `proxy` are the only hosts exposed to
the internet, and both live in the `dmz` inventory group where the `public` role
applies fail2ban and a locked-down firewalld zone.

> A network diagram is still to come — see [issue #97](https://github.com/chasty2/crowsnet/issues/97).

## Repository Layout

```
crowsnet/
├── ansible/            # Configures servers and containers
├── pulumi/             # Infrastructure provisioning (Proxmox VMs)
├── docker/             # Container definitions
│   ├── Dockerfile      # Unified CrowsNet container (Ansible + Pulumi)
│   └── entrypoint.sh   # Action dispatcher (configure, deploy, etc.)
├── utilities/          # Python utilities for container operations
├── tests/              # Host-side pytest unit tests (CLI, container, Pulumi)
└── crowsnet.py         # CLI entry point for all operations
```

## Getting Started

Requirements:

- [uv](https://docs.astral.sh/uv/) for Python tooling
- [podman](https://podman.io/) to build and run the ops container
- API access to the Proxmox host and a Pulumi access token

```bash
git config core.hooksPath .githooks   # once per clone; blocks pushes to main
uv sync                               # host-side venv for the CLI and unit tests
./crowsnet.py build                   # build the ops container
```

Secrets are not committed in plaintext. Ansible reads its vault password from
`ansible/vault.pass` and Pulumi reads its token from `pulumi/pulumi.token`; both are
mounted into the container at run time.

## Infrastructure (Pulumi)

VM definitions live in [`pulumi/vms.py`](pulumi/vms.py), one list per stack. `select_vms()`
resolves the stack name to its list, and [`pulumi/__main__.py`](pulumi/__main__.py) builds a
`ProxmoxVM` component for each entry.

| Stack | VMs | Purpose |
|-------|-----|---------|
| `stage` | `stage` (250) | Throwaway VM created and destroyed by the Molecule suite |
| `dev` | `lab` (200) | Development sandbox |
| `prod` | `gate` (100), `proxy` (101), `bailey` (125), `kube-1` (126) | The live homelab |

Every VM is cloned from one of two Proxmox templates defined in
[`pulumi/components.py`](pulumi/components.py) — `small` (vmid 301, 36 GB disk) or `large`
(vmid 302, 130 GB disk). The `ProxmoxVM` component handles the rest: CPU/memory, a virtio
NIC on `vmbr0` with a fixed MAC, and a cloud-init (`nocloud`) static IP on
`192.168.4.0/22` behind gateway `192.168.4.1`. Disks and cloud-init images land on the
`ssd_mirror` datastore.

```bash
./crowsnet.py deploy <stage|dev|prod>    # pulumi up
./crowsnet.py destroy <stage|dev|prod>   # pulumi destroy
./crowsnet.py refresh <stage|dev|prod>   # pulumi refresh
```

## Configuration (Ansible)

[`ansible/hosts`](ansible/hosts) defines three groups: `physical` (esper, simic, abzan),
`virtual` (gate, proxy, bailey, kube-1, lab), and `dmz` (gate, proxy).
[`ansible/site.yml`](ansible/site.yml) imports [`physical.yml`](ansible/physical.yml) and
[`virtual.yml`](ansible/virtual.yml), which map roles onto those hosts:

| Host(s) | Roles |
|---------|-------|
| all physical | `common`, `physical` |
| `esper` | `proxmox` |
| `simic` | `pbs` |
| `abzan` | `podman`, `jupyter`, `sunshine` |
| all virtual | `common`, `virtual` |
| `dmz` | `public` |
| `gate` | `public_ssh` |
| `proxy` | `podman`, `proxy` |
| `bailey` | `podman`, `jellyfin`, `foundry` |
| `lab` | `dev` |
| `kube-1` | `microk8s` |

Each role splits its work across up to five task files with matching tags — `users`,
`system`, `packages`, `services`, and `firewall` — so any slice of the configuration can
be applied on its own. Every role carries a README describing its purpose, requirements,
and variables; the authoring conventions are in
[`ansible/CLAUDE.md`](ansible/CLAUDE.md). Shared variables
live in `ansible/group_vars/all` and collection versions are pinned in
[`ansible/roles/requirements.yml`](ansible/roles/requirements.yml).

```bash
./crowsnet.py configure                    # full site deployment
./crowsnet.py configure --tags users       # run specific tags
./crowsnet.py configure --limit gate       # limit to specific host
./crowsnet.py configure --check            # dry-run mode
./crowsnet.py update                       # patch and reboot all VMs
```

## Deployment via Container

Ansible and Pulumi both run inside one image, so no local install of either is needed and
every run uses identical tooling. [`docker/Dockerfile`](docker/Dockerfile) layers the
Pulumi CLI, the `uv`-managed Python dependencies, the pinned Ansible collections, and the
SSH keys used to reach the fleet onto `python:3.12-slim`.

[`utilities/container.py`](utilities/container.py) runs the image with `--network host`
and two bind mounts:

- `ansible/` → `/etc/ansible`
- `pulumi/` → `/pulumi`

[`docker/entrypoint.sh`](docker/entrypoint.sh) dispatches on the first argument —
`configure`, `update`, `deploy`, `destroy`, `refresh`, or `test` — and forwards the rest
to `ansible-playbook`, `pulumi`, or `molecule`. Every `crowsnet.py` subcommand except the
unit-test path goes through it, so local runs and CI runs take the same code path.

## Testing

The suite has two layers (a third, CI on a self-hosted runner, is still pending):

- **Unit (pytest)** — fast, host-only, no infrastructure. Covers the Click CLI dispatch,
  podman command construction, and Pulumi component logic. Lives in [`tests/`](tests/).
  Run on every change.
- **Integration (Molecule)** — provisions the real `stage` VM via Pulumi, converges a
  role, checks idempotency, then tears the VM down (destroy always runs last, even on
  failure). Run when changing an Ansible role. Runs inside the ops container and requires
  Pulumi `stage` access.

```bash
./crowsnet.py test                                # unit tests
./crowsnet.py test --integration                  # integration suite (role: common)
./crowsnet.py test --integration --role <role>    # integration suite for a specific role
```

GitHub Actions runs `pytest` on every push, alongside `ansible-lint` over `ansible/` and
`ruff` over the Python code.

## License

GPL 3.0
