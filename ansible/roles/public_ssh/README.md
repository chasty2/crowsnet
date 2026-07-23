# Public SSH Role

Turns a DMZ host into the SSH bastion (`gate`): adds the fail2ban sshd jail and opens SSH
on the firewalld `public` zone. Split from the `public` role so that only the bastion
accepts inbound SSH from the internet.

## Requirements
- `public` role (installs fail2ban and assigns the `public` zone)

## Variables
- `public_ssh_permitted_ports` - firewalld services opened on the `public` zone (`ssh`)

The jail itself is the static `files/jail_sshd`, installed to
`/etc/fail2ban/jail.d/sshd.local`.

## Tags
- `services` - Installs the sshd jail and reloads fail2ban
- `firewall` - Opens SSH on the `public` zone
