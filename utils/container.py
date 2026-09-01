"""Utilities for building and running the CrowsNet container."""

import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent
DOCKER_DIR = PROJECT_ROOT / "docker"
ANSIBLE_DIR = PROJECT_ROOT / "ansible"
PULUMI_DIR = PROJECT_ROOT / "pulumi"
CONTAINER_NAME = "crowsnet"


def build_container() -> int:
    """Build the crowsnet container with podman.

    Copies pyproject.toml, uv.lock, and the Ansible collection requirements
    into the docker build context, builds the container, then cleans up the
    copied files.

    Returns:
        The return code from podman build.
    """
    pyproject_src = PROJECT_ROOT / "pyproject.toml"
    uvlock_src = PROJECT_ROOT / "uv.lock"
    requirements_src = ANSIBLE_DIR / "roles" / "requirements.yml"
    pyproject_dst = DOCKER_DIR / "pyproject.toml"
    uvlock_dst = DOCKER_DIR / "uv.lock"
    requirements_dst = DOCKER_DIR / "requirements.yml"

    try:
        shutil.copy2(pyproject_src, pyproject_dst)
        shutil.copy2(uvlock_src, uvlock_dst)
        shutil.copy2(requirements_src, requirements_dst)

        cmd = ["podman", "build", ".", "-t", f"{CONTAINER_NAME}:latest"]
        result = subprocess.run(cmd, cwd=DOCKER_DIR, check=False)
        return result.returncode
    finally:
        pyproject_dst.unlink(missing_ok=True)
        uvlock_dst.unlink(missing_ok=True)
        requirements_dst.unlink(missing_ok=True)


def run_container(action: str, args: list[str] | None = None) -> int:
    """Run an action in the crowsnet container.

    Args:
        action: The entrypoint action (configure, deploy, destroy, refresh, update, test).
        args: Additional arguments to pass after the action.

    Returns:
        The return code from podman run.
    """
    # Allocate a TTY only when attached to one; CI runners have no TTY.
    tty_flag = "-it" if sys.stdout.isatty() else "-i"

    cmd = [
        "podman",
        "run",
        tty_flag,
        "--rm",
        "--userns=keep-id",
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
