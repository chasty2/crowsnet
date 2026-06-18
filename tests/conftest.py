"""Shared pytest fixtures and path setup for the CrowsNet test suite."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
PULUMI_DIR = PROJECT_ROOT / "pulumi"

# Make the project root importable so tests can import `crowsnet` and `utilities`.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# The pulumi/ directory is a Pulumi program, not an installable package, and its
# modules import each other by bare name (e.g. `from components import ...`).
# Add it to sys.path so the unit tests can import those modules directly.
if str(PULUMI_DIR) not in sys.path:
    sys.path.insert(0, str(PULUMI_DIR))
