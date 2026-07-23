# Sunshine Role

Installs the [Sunshine](https://github.com/LizardByte/Sunshine) game-streaming host on
`abzan` and opens its streaming ports.

## Requirements
- `common` role (firewalld)
- Debian-family host; the `.deb` URL is built from the detected distribution, version, and architecture
- The Sunshine service must be started manually from a physical login session, so this role does not manage it

## Variables
- `sunshine_os`, `sunshine_os_version`, `sunshine_os_arch` - Facts-derived components of the release URL
- `sunshine_download_url` - Release `.deb` to install, assembled from the values above
- `sunshine_permitted_ports` - firewalld ports on the `internal` zone (`47989/tcp`, `47990/tcp` web UI, `47984/tcp`, `48010/tcp`, `47998-48000/udp`)

## Tags
- `packages` - Installs Sunshine from the release `.deb`
- `firewall` - Opens the streaming ports on the `internal` zone
