"""Utilities for running the CrowsNet test suites.

Unit tests exercise host-side Python (the CLI, container helpers, and Pulumi
component logic), so they run directly via ``uv``. Integration tests run inside
the ops container, which already has the Pulumi virtualenv, the baked-in SSH
keys, and the Ansible collections configured.
"""

import subprocess

from utilities.container import run_container


def run_pytest() -> int:
    """Run the pytest unit suite on the host.

    Returns:
        The return code from pytest.
    """
    result = subprocess.run(["uv", "run", "pytest"], check=False)
    return result.returncode


def run_integration(role: str = "common") -> int:
    """Run the molecule integration suite for a role inside the ops container.

    Dispatches the container's `test` action through the same `run_container`
    path as production (configure/deploy), so molecule sees the production mount
    layout (ansible -> /etc/ansible, pulumi -> /pulumi) and user-namespace mapping.
    Molecule then provisions the lab VM via Pulumi, converges the role, checks
    idempotency, and destroys the VM.

    Args:
        role: The role whose molecule scenario to run.

    Returns:
        The return code from the container.
    """
    return run_container("test", [role])
