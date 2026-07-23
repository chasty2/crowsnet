# Public Role

Hardens the internet-facing hosts in the `dmz` group (`gate` and `proxy`). Installs
fail2ban with the project's jail defaults and binds the external interface to the
restrictive firewalld `public` zone.

## Requirements
- `common` role (firewalld)
- Host has an internet-facing interface matching `public_permitted_interfaces`

## Variables
- `public_packages` - Packages to install (`ipset`, `fail2ban`)
- `public_services` - Services started and enabled on boot (`fail2ban`)
- `public_closed_ports` - firewalld services explicitly disabled on the `public` zone
- `public_permitted_interfaces` - Interfaces assigned to the `public` zone (`ens18`)

Per-jail configuration lives in the `files/jail_local` template installed to
`/etc/fail2ban/jail.local`; individual jails are added by roles like `public_ssh`.

## Tags
- `packages` - fail2ban and ipset installation
- `services` - Removes the Debian default jail config, installs `jail.local`, enables fail2ban
- `firewall` - Closes unused services and attaches the external interface to the `public` zone
