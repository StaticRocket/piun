"""Config file parsing stuff"""

import os
import logging
from pathlib import Path

import apprise

logger = logging.getLogger(__name__)

DEFAULT_PATHS = [Path(os.environ.get("XDG_CONFIG_HOME")).joinpath("piun/piun.yml")]


def load_config(override_path):
    """Load the config from the given path and return a valid config structure"""
    config = apprise.AppriseConfig()
    search_paths = DEFAULT_PATHS
    if isinstance(override_path, Path):
        search_paths.append(override_path)
    for path in search_paths:
        if path.is_file():
            config.add(path.as_posix())
    return config
