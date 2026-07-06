# Project Guidelines

## Project Overview
- **Name**: CrowsNet
- **Purpose**: Self-hosted homelab, runs entirely out of infrastructure-as-code
- **Stack**: Python (uv), Ansible, Pulumi, Podman


## Commands

```bash
# Container
./crowsnet.py build                        # Build the CrowsNet container

# Infrastructure (Pulumi)
./crowsnet.py deploy <stage|dev|prod>      # Deploy infrastructure
./crowsnet.py destroy <stage|dev|prod>     # Destroy infrastructure
./crowsnet.py refresh <stage|dev|prod>     # Refresh infrastructure state

# Configuration (Ansible)
./crowsnet.py configure                    # Full site deployment
./crowsnet.py configure --tags users       # Run specific tags
./crowsnet.py configure --limit gate       # Limit to specific host
./crowsnet.py configure --check            # Dry-run mode

# Maintenance
./crowsnet.py update                       # Update and reboot all VMs

# Testing
./crowsnet.py test                                # Unit tests (pytest, host-side, no infra)
./crowsnet.py test --integration                  # Molecule integration suite (role: common)
./crowsnet.py test --integration --role <role>    # Integration suite for a specific role
```

## Testing Workflow

The suite has two layers (a third, CI on a self-hosted runner, is still pending):

- **Unit (pytest)** — fast, host-only, no infrastructure. Covers the Click CLI
  dispatch, podman command construction, and Pulumi component logic. Lives in
  `tests/`. Run on every change via `./crowsnet.py test`.
- **Integration (Molecule)** — provisions the real `stage` VM via Pulumi,
  converges a role, checks idempotency, then tears the VM down (destroy always
  runs last, even on failure). Run when changing an Ansible role via
  `./crowsnet.py test --integration [--role <role>]`. Runs inside the ops
  container and requires Pulumi `stage` access. See `ansible/CLAUDE.md` for how
  to add a Molecule scenario to a role.

## Directory Structure
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


## Core Principles

1. **Start by forming a plan** - Do not begin work until I approve your plan
2. **Simplicity over cleverness** - Write code that's immediately understandable
3. **Leverage existing solutions** - Use standard libraries, don't reinvent
4. **Single responsibility** - Functions do one thing, under 50 lines
5. **Early returns** - Guard clauses over nested conditionals
6. **Match existing patterns** - Follow the file's conventions exactly
7. **Use uv for Python** - Invoke all Python tooling through `uv` (e.g. `uv run pytest`, `uv run python ...`, `uv pip ...`); never bare `python`/`pip`/`pytest`


## Git Conventions

- Unless told otherwise, start each plan with creating a new branch
- All work should be done in a branch outside of main
- Each goal should be accomplished in its own branch
- Commit early and often, after each meaningful change
- Always run the testing workflow and have it pass before committing
- After pushing a branch, check that its CI tests pass (e.g. `gh run list --branch <branch>`)
- When done, check in with the user for approval
- Submit a PR to merge into main with a semantic tag in the title (e.g., `feat:`, `fix:`, `refactor:`, `docs:`)


## Before You Start

| File | When to Read |
|------|--------------|
| ansible/CLAUDE.md | Writing new Ansible and Ansible-related code |
