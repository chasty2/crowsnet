#!/bin/bash
set -euo pipefail

ACTION="${1:-}"
shift || true

VAULT_PASS_FILE="/etc/ansible/vault.pass"
PULUMI_TOKEN_FILE="/pulumi/pulumi.token"

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
        export PULUMI_ACCESS_TOKEN
        PULUMI_ACCESS_TOKEN=$(cat "$PULUMI_TOKEN_FILE")
        uv run pulumi up --yes --stack "$@"
        ;;
    destroy)
        cd /pulumi
        export PULUMI_ACCESS_TOKEN
        PULUMI_ACCESS_TOKEN=$(cat "$PULUMI_TOKEN_FILE")
        uv run pulumi destroy --yes --stack "$@"
        ;;
    refresh)
        cd /pulumi
        export PULUMI_ACCESS_TOKEN
        PULUMI_ACCESS_TOKEN=$(cat "$PULUMI_TOKEN_FILE")
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
