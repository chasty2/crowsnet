# Ansible Codebase

## Overview
This is an Ansible codebase for managing a homelab environment. The ansible directory is attached to a container that runs ansible to configure the homelab infrastructure.

## Ansible Role Structure Standards

All Ansible roles in this project follow a standardized 5-task organization pattern:

### Task Organization
Each role splits tasks into up to 5 standardized task files, each with a specific tag:

1. **`users.yml`** - `tags: users` - User/group management, SSH keys, sudo configuration
2. **`system.yml`** - `tags: system` - System-level configuration (hostname, etc.)  
3. **`packages.yml`** - `tags: packages` - Package installation/removal
4. **`services.yml`** - `tags: services` - Service management (start/stop/enable)
5. **`firewalld.yml`** - `tags: firewall` - Firewall configuration

### Key Patterns
- `tasks/main.yml` includes each task file with `ansible.builtin.include_tasks` and assigns the corresponding tag
- Roles don't need to implement all 5 files - only what's needed
- Tags enable selective execution (e.g., `ansible-playbook --tags users,firewall`)
- Individual task files use `block:` structure to ensure tags are properly applied to all tasks
- Ensures consistent organization across all roles in the homelab

### Standard Role Structure
```
role_name/
├── tasks/
│   ├── main.yml          # Entry point with includes and tags
│   ├── role_name_users.yml         # User management tasks
│   ├── role_name_system.yml        # System configuration tasks
│   ├── role_name_packages.yml      # Package management tasks
│   ├── role_name_services.yml      # Service management tasks
│   └── role_name_firewalld.yml     # Firewall configuration tasks
├── molecule/
│   └── default/          # Molecule integration scenario (see Molecule Testing)
├── vars/main.yml         # Role variables
├── handlers/main.yml     # Event handlers
├── templates/            # Jinja2 templates
└── files/               # Static files
```

This standardization allows predictable role structure and granular control over which aspects of configuration to apply during playbook runs.

> **Note:** Roles are tested with Molecule (see below), not the legacy
> `tests/test.yml` playbook. New roles get a `molecule/` scenario instead of a
> `tests/` directory.

## Molecule Testing

Roles are integration-tested with Molecule. A `molecule test` run provisions the
real `stage` lab VM via Pulumi, converges the role, checks **idempotency**, runs
the verifier, then destroys the VM (destroy always runs last, even on failure).

Run a role's scenario from the repo root:
```bash
./crowsnet.py test --integration --role <role>   # defaults to `common`
```

### Adding a scenario to a role
Place the scenario under the role:
```
roles/<role>/molecule/default/
├── molecule.yml      # scenario config
├── converge.yml      # applies the role
└── verify.yml        # optional smoke checks
```

The lifecycle playbooks (`create`, `prepare`, `destroy`) are written **once** in
`ansible/molecule/shared/` and reused by every role — do **not** reimplement them
per role. The fastest path to a new scenario is to copy
`roles/common/molecule/default/` and adjust the role name.

**`molecule.yml`** — `driver: default`; one platform named `lab`; a galaxy
dependency pointing at `../requirements.yml`; `provisioner.playbooks` wiring the
three shared playbooks; `ANSIBLE_ROLES_PATH` set to the roles directory; and
`verifier: ansible`:
```yaml
---
driver:
  name: default

platforms:
  - name: lab

dependency:
  name: galaxy
  options:
    requirements-file: ${MOLECULE_PROJECT_DIRECTORY}/../requirements.yml

provisioner:
  name: ansible
  playbooks:
    create: ${MOLECULE_PROJECT_DIRECTORY}/../../molecule/shared/create.yml
    prepare: ${MOLECULE_PROJECT_DIRECTORY}/../../molecule/shared/prepare.yml
    destroy: ${MOLECULE_PROJECT_DIRECTORY}/../../molecule/shared/destroy.yml
  env:
    ANSIBLE_HOST_KEY_CHECKING: "false"
    ANSIBLE_ROLES_PATH: ${MOLECULE_PROJECT_DIRECTORY}/..

verifier:
  name: ansible
```

**`converge.yml`** — `hosts: all`, `become: true`, loads shared vars from
`group_vars/all`, and lists the role:
```yaml
---
- name: Converge
  hosts: all
  become: true
  vars_files:
    - "{{ lookup('env', 'MOLECULE_PROJECT_DIRECTORY') }}/../../group_vars/all"
  roles:
    - <role> # noqa syntax-check[specific]
```

**`verify.yml`** (optional) — minimal smoke checks asserting the role's key
effects (a service is running, a user exists, etc.). Do **not** test idempotency
here; molecule's built-in `idempotence` step handles that.

## Formatting
- End each `.yml` file with a newline