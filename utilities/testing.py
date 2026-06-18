"""Utilities for running the CrowsNet test suites on the host.

Unit tests exercise host-side Python (the CLI, container helpers, and Pulumi
component logic), so they run directly via ``uv`` rather than inside the ops
container.
"""

import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def run_pytest() -> int:
    """Run the pytest unit suite on the host.

    Returns:
        The return code from pytest.
    """
    result = subprocess.run(["uv", "run", "pytest"], check=False)
    return result.returncode


def run_integration() -> int:
    """Run the molecule integration suite against the stage VM.

    Molecule provisions the lab VM via Pulumi, converges the common role,
    checks idempotency, and destroys the VM. Runs from the role directory so
    molecule picks up that role's `default` scenario.

    Returns:
        The return code from molecule.
    """
    role_dir = PROJECT_ROOT / "ansible" / "roles" / "common"
    result = subprocess.run(
        ["uv", "run", "molecule", "test"], cwd=role_dir, check=False
    )
    return result.returncode
