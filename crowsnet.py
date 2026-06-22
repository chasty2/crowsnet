#!.venv/bin/python3
"""CLI entry point for CrowsNet infrastructure management."""

import sys
import click
from utilities.container import build_container, run_container
from utilities.testing import run_integration, run_pytest


@click.group()
def cli():
    """CrowsNet infrastructure management CLI."""


@cli.command()
def build():
    """Build the CrowsNet container."""
    sys.exit(build_container())


@cli.command()
@click.argument("stack", type=click.Choice(["stage", "prod"]))
def deploy(stack):
    """Deploy infrastructure with Pulumi."""
    sys.exit(run_container("deploy", [stack]))


@cli.command()
@click.argument("stack", type=click.Choice(["stage", "prod"]))
def destroy(stack):
    """Destroy infrastructure with Pulumi."""
    sys.exit(run_container("destroy", [stack]))


@cli.command()
@click.argument("stack", type=click.Choice(["stage", "prod"]))
def refresh(stack):
    """Refresh infrastructure state with Pulumi."""
    sys.exit(run_container("refresh", [stack]))


@cli.command()
@click.option("--limit", default=None, help="Limit to specific hosts")
def update(limit):
    """Update and reboot all VMs."""
    args = []
    if limit:
        args.extend(["--limit", limit])
    sys.exit(run_container("update", args if args else None))


@cli.command()
@click.option("--integration", is_flag=True, help="Run the molecule integration suite against the stage VM")
@click.option("--role", default="common", help="Role to run the integration suite against")
def test(integration, role):
    """Run the test suite (pytest unit tests by default)."""
    if integration:
        sys.exit(run_integration(role))
    sys.exit(run_pytest())


@cli.command()
@click.option("--tags", default=None, help="Ansible tags to run (comma-separated)")
@click.option("--limit", default=None, help="Limit to specific hosts")
@click.option("--check", is_flag=True, help="Run in check/dry-run mode")
def configure(tags, limit, check):
    """Run Ansible site.yml with optional filters."""
    args = []
    if tags:
        args.extend(["--tags", tags])
    if limit:
        args.extend(["--limit", limit])
    if check:
        args.append("--check")
    sys.exit(run_container("configure", args if args else None))


if __name__ == "__main__":
    cli()
