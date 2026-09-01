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
├── tests/                # Assertion tasks, one file per task file (see Molecule Testing)
├── vars/main.yml         # Role variables
├── handlers/main.yml     # Event handlers
├── templates/            # Jinja2 templates
└── files/               # Static files
```

This standardization allows predictable role structure and granular control over which aspects of configuration to apply during playbook runs.

## Molecule Testing

Integration testing is done with Molecule. A `molecule test` run provisions the
real `stage` VM via Pulumi, converges the scenario, checks **idempotency**, runs
the verifier, then destroys the VM (destroy always runs last, even on failure).

Run a scenario from the repo root:
```bash
./crowsnet.py test --integration --scenario <scenario>   # defaults to `common`
```

### Scenarios are per host, tests are per role
A scenario models a **host**, not a role. It converges the same role stack that
host receives in `site.yml`, and its `verify.yml` does nothing but include the
assertion tasks that each of those roles keeps in its own `tests/` directory.
Roles are therefore reusable across scenarios, and a host is tested the way it is
actually built:

```
molecule/
├── shared/           # create.yml, destroy.yml — written once
└── <host>/
    ├── molecule.yml  # scenario config
    ├── converge.yml  # applies the host's roles
    └── verify.yml    # includes each role's tests/

roles/<role>/tests/
├── packages.yml      # assertions for <role>_packages.yml
├── users.yml         # assertions for <role>_users.yml
└── ...               # one file per task file, named to match
```

`ansible/molecule/kube-1/` is the reference scenario. The `common` and `dev`
roles predate this layout and still carry role-scoped
`roles/<role>/molecule/default/` scenarios; fold them in rather than adding more.

The lifecycle playbooks (`create`, `destroy`) live **once** in
`molecule/shared/` — do **not** reimplement them per scenario. Molecule runs from
`ansible/`, so `MOLECULE_PROJECT_DIRECTORY` is that directory and every path is
written relative to it.

There is no `prepare` step: `create.yml` waits for SSH, and the apt cache is
refreshed by the `common` role, which every scenario converges first.

**`molecule.yml`** — `driver: default`; one platform named `stage`; a galaxy
dependency pointing at the roles requirements; `provisioner.playbooks` wiring the
two shared playbooks; `ANSIBLE_ROLES_PATH` set to the roles directory; and
`verifier: ansible`:
```yaml
---
driver:
  name: default

platforms:
  - name: stage

dependency:
  name: galaxy
  options:
    requirements-file: ${MOLECULE_PROJECT_DIRECTORY}/roles/requirements.yml

provisioner:
  name: ansible
  playbooks:
    create: ${MOLECULE_PROJECT_DIRECTORY}/molecule/shared/create.yml
    destroy: ${MOLECULE_PROJECT_DIRECTORY}/molecule/shared/destroy.yml
  env:
    ANSIBLE_HOST_KEY_CHECKING: "false"
    ANSIBLE_ROLES_PATH: ${MOLECULE_PROJECT_DIRECTORY}/roles

verifier:
  name: ansible
```

**`converge.yml`** — `hosts: all`, `become: true`, loads shared vars from
`group_vars/all`, and lists the host's roles in `site.yml` order:
```yaml
---
- name: Converge
  hosts: all
  become: true
  vars_files:
    - "{{ lookup('env', 'MOLECULE_PROJECT_DIRECTORY') }}/group_vars/all"
  roles:
    - common # noqa syntax-check[specific]
    - <role> # noqa syntax-check[specific]
```

**`verify.yml`** — includes only. Load each covered role's `vars/main.yml` through
`vars_files` so the assertions read the same values the role applied; role vars are
otherwise out of scope once the role finishes:
```yaml
---
- name: Verify
  hosts: all
  become: true
  gather_facts: false
  vars:
    ansible_dir: "{{ lookup('env', 'MOLECULE_PROJECT_DIRECTORY') }}"
  vars_files:
    - "{{ lookup('env', 'MOLECULE_PROJECT_DIRECTORY') }}/roles/<role>/vars/main.yml"
  tasks:
    - name: Verify <role> packages
      ansible.builtin.include_tasks: "{{ ansible_dir }}/roles/<role>/tests/packages.yml"
```

Assertion tasks are read-only: give every `command` a `changed_when: false`. Do
**not** test idempotency there; molecule's built-in `idempotence` step handles it.

Roles must not reach outside the host they run on. A `delegate_to` at another
inventory host makes a role unconvergeable against a single VM — put the work in
the role that owns the target host instead.

## Formatting
- End each `.yml` file with a newline