"""Single source of truth for the package version.

Bumped here only; ``pyproject.toml`` reads it via hatchling's dynamic version and
the MCP server reports it at runtime, so the three can no longer drift apart.
"""

__version__ = "0.1.5"
