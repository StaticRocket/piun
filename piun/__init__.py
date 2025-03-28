"""Primary entrypoint"""

import logging
import argparse
from pathlib import Path
from piun.config import load_config

logger = logging.getLogger(__name__)


def main():
    """Main application entrypoint"""
    parser = argparse.ArgumentParser(prog="piun")
    parser.add_argument(
        "-c", "--config", help="override config file with given path", type=Path
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="override log verbosity",
        action=argparse.BooleanOptionalAction,
    )
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.ERROR)

    config = load_config(args.config)
    print(load_config(args.config))
