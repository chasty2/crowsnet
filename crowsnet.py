#!.venv/bin/python3
"""CLI entry point for CrowsNet infrastructure management."""

import sys
import click
from utilities.container import build_container, run_container


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
def test():
    """Run tests."""
    sys.exit(run_container("test"))


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
