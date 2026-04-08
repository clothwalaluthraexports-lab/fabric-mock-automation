"""
Utility helpers.
"""

import os
import logging

logger = logging.getLogger(__name__)


def setup_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def safe_filename(name):
    """Strip characters that are unsafe for filenames."""
    return "".join(c for c in name if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
