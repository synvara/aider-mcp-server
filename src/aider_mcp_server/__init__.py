# from aider_mcp_server.__main__ import main # Removed unused import

# This just re-exports the main function from __main__.py

from .__main__ import main as main  # Explicit re-export for entry point

# Comment about re-export is no longer necessary if it's clear
