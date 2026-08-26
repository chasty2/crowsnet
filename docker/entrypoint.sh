#!/bin/bash
set -euo pipefail

ACTION="${1:-}"
shift || true

VAULT_PASS_FILE="/etc/ansible/vault.pass"
PULUMI_TOKEN_FILE="/pulumi/pulumi.token"

case "$ACTION" in
    configure)
        cd /etc/ansible
        ansible-playbook --vault-password-file "$VAULT_PASS_FILE" site.yml "$@"
        ;;
    update)
        cd /etc/ansible
        ansible-playbook --vault-password-file "$VAULT_PASS_FILE" update.yml "$@"
        ;;
    deploy)
        cd /pulumi
        export PULUMI_ACCESS_TOKEN
        PULUMI_ACCESS_TOKEN=$(cat "$PULUMI_TOKEN_FILE")
        pulumi up --yes --stack "$@"
        ;;
    destroy)
        cd /pulumi
        export PULUMI_ACCESS_TOKEN
        PULUMI_ACCESS_TOKEN=$(cat "$PULUMI_TOKEN_FILE")
        pulumi destroy --yes --stack "$@"
        ;;
    refresh)
        cd /pulumi
        export PULUMI_ACCESS_TOKEN
        PULUMI_ACCESS_TOKEN=$(cat "$PULUMI_TOKEN_FILE")
        pulumi refresh --yes --stack "$@"
        ;;
    test)
        SCENARIO="${1:-common}"
        # Scenarios live in ansible/molecule/<scenario>/. The common and dev roles
        # still carry their own role-scoped scenarios; drop the fallback once they
        # are folded into project-level scenarios.
        if [ -d "/etc/ansible/molecule/${SCENARIO}" ]; then
            cd /etc/ansible
            molecule test -s "${SCENARIO}"
        else
            cd "/etc/ansible/roles/${SCENARIO}"
            molecule test
        fi
        ;;
    *)
        echo "Unknown action: $ACTION"
        echo "Usage: entrypoint.sh {configure|update|deploy|destroy|refresh|test}"
        exit 1
        ;;
esac
