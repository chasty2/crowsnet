# Common Role

Baseline configuration applied to every host, physical and virtual. Creates the shared
users and groups, sets the hostname and timezone, installs the base package set, and
establishes the `internal` firewalld zone.

## Requirements
- `ansible.posix` and `community.general` collections
- Debian-family host (uses `apt` for cache updates)

## Variables
- `common_groups` - Groups created on every host, as `{ name, gid }`
- `common_service_users` - Non-login service accounts, as `{ name, uid, gid }`
- `common_ssh_keys` - Public keys authorized per user, as `{ name, public_ssh_key }`
- `common_packages` - Base packages installed everywhere
- `common_removed_packages` - Packages explicitly removed (e.g. `ufw`, which conflicts with firewalld)
- `common_services` - Services started and enabled on boot
- `common_permitted_ports` - firewalld services opened on the `internal` zone
- `common_closed_ports` - firewalld services explicitly disabled on the `internal` zone
- `common_permitted_networks` - Source networks added to the `internal` zone

From `group_vars/all`:
- `admin_users` - Human accounts granted sudo, as `{ name, uid, gid }`

## Tags
- `users` - Groups, admin and service accounts, sudoers rules, authorized SSH keys
- `system` - Hostname, set from `inventory_hostname`
- `packages` - Base package install and removal
- `services` - sshd drop-in config, timezone, enabling base services
- `firewall` - `internal` zone ports and permitted source networks

## Testing
Has a Molecule scenario: `./crowsnet.py test --integration --role common`
