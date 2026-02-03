"""Shared environment loading for Logfire skill scripts."""
import os
from pathlib import Path

from dotenv import load_dotenv


def load_env():
    """Load LOGFIRE_READ_TOKEN from .env files in common locations."""
    # Check if already set
    if os.getenv('LOGFIRE_READ_TOKEN'):
        return

    # Search locations in order of priority
    search_paths = [
        Path.cwd() / '.env',  # Current directory
        Path.home() / '.env',  # Home directory
        Path.home() / 'raysurfer' / '.env',  # Raysurfer project
        Path.home() / 'raysurfer-backend' / '.env',  # Backend project
    ]

    for env_path in search_paths:
        if env_path.exists():
            load_dotenv(env_path)
            if os.getenv('LOGFIRE_READ_TOKEN'):
                return


# Auto-load on import
load_env()
