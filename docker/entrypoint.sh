#!/bin/bash
set -euo pipefail

ACTION="${1:-}"
shift || true

VAULT_PASS_FILE="/etc/ansible/vault.pass"

case "$ACTION" in
    configure)
        cd /etc/ansible
        uv run ansible-playbook --vault-password-file "$VAULT_PASS_FILE" site.yml "$@"
        ;;
    update)
        cd /etc/ansible
        uv run ansible-playbook --vault-password-file "$VAULT_PASS_FILE" update.yml "$@"
        ;;
    deploy)
        cd /pulumi
        export PULUMI_CONFIG_PASSPHRASE
        PULUMI_CONFIG_PASSPHRASE=$(cat "$VAULT_PASS_FILE")
        uv run pulumi login file:///pulumi
        uv run pulumi up --yes --stack "$@"
        ;;
    destroy)
        cd /pulumi
        export PULUMI_CONFIG_PASSPHRASE
        PULUMI_CONFIG_PASSPHRASE=$(cat "$VAULT_PASS_FILE")
        uv run pulumi login file:///pulumi
        uv run pulumi destroy --yes --stack "$@"
        ;;
    refresh)
        cd /pulumi
        export PULUMI_CONFIG_PASSPHRASE
        PULUMI_CONFIG_PASSPHRASE=$(cat "$VAULT_PASS_FILE")
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
