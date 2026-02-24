"""Utilities for building and running the CrowsNet container."""

import shutil
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent
DOCKER_DIR = PROJECT_ROOT / "docker"
ANSIBLE_DIR = PROJECT_ROOT / "ansible"
PULUMI_DIR = PROJECT_ROOT / "pulumi"
CONTAINER_NAME = "crowsnet"


def build_container() -> int:
    """Build the crowsnet container with podman.

    Copies pyproject.toml and uv.lock into the docker build context,
    builds the container, then cleans up the copied files.

    Returns:
        The return code from podman build.
    """
    pyproject_src = PROJECT_ROOT / "pyproject.toml"
    uvlock_src = PROJECT_ROOT / "uv.lock"
    pyproject_dst = DOCKER_DIR / "pyproject.toml"
    uvlock_dst = DOCKER_DIR / "uv.lock"

    try:
        shutil.copy2(pyproject_src, pyproject_dst)
        shutil.copy2(uvlock_src, uvlock_dst)

        cmd = ["podman", "build", ".", "-t", f"{CONTAINER_NAME}:latest"]
        result = subprocess.run(cmd, cwd=DOCKER_DIR, check=False)
        return result.returncode
    finally:
        pyproject_dst.unlink(missing_ok=True)
        uvlock_dst.unlink(missing_ok=True)


def run_container(action: str, args: list[str] | None = None) -> int:
    """Run an action in the crowsnet container.

    Args:
        action: The entrypoint action (configure, deploy, destroy, refresh, update, test).
        args: Additional arguments to pass after the action.

    Returns:
        The return code from podman run.
    """
    cmd = [
        "podman",
        "run",
        "-it",
        "--rm",
        "--network",
        "host",
        "--volume",
        f"{ANSIBLE_DIR}:/etc/ansible",
        "--volume",
        f"{PULUMI_DIR}:/pulumi",
        CONTAINER_NAME,
        action,
    ]

    if args:
        cmd.extend(args)

    result = subprocess.run(cmd, check=False)
    return result.returncode
