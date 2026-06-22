"""Utilities for running the CrowsNet test suites.

Unit tests exercise host-side Python (the CLI, container helpers, and Pulumi
component logic), so they run directly via ``uv``. Integration tests run inside
the ops container, which already has the Pulumi virtualenv, the baked-in SSH
keys, and the Ansible collections configured.
"""

import subprocess
from pathlib import Path

from utilities.container import CONTAINER_NAME

PROJECT_ROOT = Path(__file__).parent.parent


def run_pytest() -> int:
    """Run the pytest unit suite on the host.

    Returns:
        The return code from pytest.
    """
    result = subprocess.run(["uv", "run", "pytest"], check=False)
    return result.returncode


def run_integration(role: str = "common") -> int:
    """Run the molecule integration suite for a role inside the ops container.

    Molecule provisions the lab VM via Pulumi, converges the role, checks
    idempotency, and destroys the VM. The whole repo is mounted at /workspace so
    the scenario's repo-relative paths (to pulumi/ and group_vars/) resolve, and
    molecule runs from the role directory to pick up its `default` scenario.

    Args:
        role: The role whose molecule scenario to run.

    Returns:
        The return code from the container.
    """
    token_file = PROJECT_ROOT / "pulumi" / "pulumi.token"
    token = token_file.read_text().strip() if token_file.exists() else ""

    cmd = [
        "podman",
        "run",
        "--rm",
        "--network",
        "host",
        "--volume",
        f"{PROJECT_ROOT}:/workspace",
        "--workdir",
        f"/workspace/ansible/roles/{role}",
        "--env",
        f"PULUMI_ACCESS_TOKEN={token}",
        "--entrypoint",
        "molecule",
        CONTAINER_NAME,
        "test",
    ]

    result = subprocess.run(cmd, check=False)
    return result.returncode
