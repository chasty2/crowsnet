#!/bin/bash
set -euo pipefail

ACTION="${1:-}"
shift || true

case "$ACTION" in
    configure)
        cd /etc/ansible
        uv run ansible-playbook --vault-password-file vault.pass site.yml "$@"
        ;;
    update)
        cd /etc/ansible
        uv run ansible-playbook --vault-password-file vault.pass update.yml "$@"
        ;;
    deploy)
        cd /pulumi
        uv run pulumi login file:///pulumi
        uv run pulumi up --yes --stack "$@"
        ;;
    destroy)
        cd /pulumi
        uv run pulumi login file:///pulumi
        uv run pulumi destroy --yes --stack "$@"
        ;;
    refresh)
        cd /pulumi
        uv run pulumi login file:///pulumi
        uv run pulumi refresh --yes --stack "$@"
        ;;
    test)
        echo "Test action placeholder"
        ;;
    *)
        echo "Unknown action: $ACTION"
        echo "Usage: entrypoint.sh {configure|update|deploy|destroy|refresh|test}"
        exit 1
        ;;
esac
