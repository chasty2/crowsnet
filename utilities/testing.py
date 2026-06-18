"""Utilities for running the CrowsNet test suites on the host.

Unit tests exercise host-side Python (the CLI, container helpers, and Pulumi
component logic), so they run directly via ``uv`` rather than inside the ops
container.
"""

import subprocess


def run_pytest() -> int:
    """Run the pytest unit suite on the host.

    Returns:
        The return code from pytest.
    """
    result = subprocess.run(["uv", "run", "pytest"], check=False)
    return result.returncode


def run_integration() -> int:
    """Run the molecule integration suite against the stage VM.

    Implemented in Phase 2 (molecule delegated driver + Pulumi lifecycle).
    """
    print("Integration tests are not implemented yet (Phase 2).")
    return 1
