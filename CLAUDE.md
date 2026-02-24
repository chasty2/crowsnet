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
./crowsnet.py deploy <stage|prod>          # Deploy infrastructure
./crowsnet.py destroy <stage|prod>         # Destroy infrastructure
./crowsnet.py refresh <stage|prod>         # Refresh infrastructure state

# Configuration (Ansible)
./crowsnet.py configure                    # Full site deployment
./crowsnet.py configure --tags users       # Run specific tags
./crowsnet.py configure --limit gate       # Limit to specific host
./crowsnet.py configure --check            # Dry-run mode

# Maintenance
./crowsnet.py update                       # Update and reboot all VMs
./crowsnet.py test                         # Run tests
```

## Workflow Patterns (TODO after implementing molecule testing)

## Directory Structure
```
crowsnet/
├── ansible/            # Configures servers and containers
├── pulumi/             # Infrastructure provisioning (Proxmox VMs)
├── terraform/          # Legacy infrastructure provisioning
├── docker/             # Container definitions
│   ├── Dockerfile      # Unified CrowsNet container (Ansible + Pulumi)
│   ├── entrypoint.sh   # Action dispatcher (configure, deploy, etc.)
│   └── terraform/      # Legacy terraform container
├── utilities/          # Python utilities for container operations
└── crowsnet.py         # CLI entry point for all operations
```


## Core Principles

1. **Start by forming a plan** - Do not begin work until I approve your plan
2. **Simplicity over cleverness** - Write code that's immediately understandable
3. **Leverage existing solutions** - Use standard libraries, don't reinvent
4. **Single responsibility** - Functions do one thing, under 50 lines
5. **Early returns** - Guard clauses over nested conditionals
6. **Match existing patterns** - Follow the file's conventions exactly


## Git Conventions

- Unless told otherwise, start each plan with creating a new branch
- All work should be done in a branch outside of main
- Each goal should be accomplished in its own branch
- Commit early and often, after each meaningful change
- When done, check in with the user for approval
- Submit a PR to merge into main with a semantic tag in the title (e.g., `feat:`, `fix:`, `refactor:`, `docs:`)


## Before You Start

| File | When to Read |
|------|--------------|
| ansible/CLAUDE.md | Writing new Ansible and Ansible-related code |
