"""Config file parsing stuff"""

import os
import logging
from dataclasses import dataclass, field
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

DEFAULT_PATHS = [Path(os.environ.get("XDG_CONFIG_HOME")).joinpath("piun/piun.yml")]


@dataclass
class PiunConfig:
    """Piun config structure"""

    notification_uri_list: list[int] = field(default_factory=list)
    watch_stopped: bool = False


def load_config(override_path):
    """Load the config from the given path and return a valid config structure"""
    config = {}
    search_paths = DEFAULT_PATHS
    if override_path:
        search_paths.insert(override_path, 0)
    for path in search_paths:
        if path.is_file():
            with path.open(mode="r", encoding="UTF-8") as file:
                config = yaml.safe_load(file)
                logger.info("Loading config from: %s", path)
    return unpack(config)


def unpack(yaml_structure):
    """Unpack the yaml_structure and return a standard config"""
    notif = yaml_structure.get("notif")
    if not isinstance(notif, list):
        notif = []
        logger.info("Using default value for notif: %s", notif)
    watch_stopped = yaml_structure.get("watch_stopped")
    if not isinstance(watch_stopped, bool):
        watch_stopped = False
    return PiunConfig(notif, watch_stopped)
