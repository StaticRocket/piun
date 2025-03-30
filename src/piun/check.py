"""Actual interface with podman"""

import logging
import subprocess
import json

from piun.db import PiunDatabase

import apprise

logger = logging.getLogger(__name__)


def get_images():
    """Get the list of images to check"""
    command = ["podman", "container", "ls", "--format", "{{.Image}}"]
    try:
        images = subprocess.run(
            command, check=True, capture_output=True, text=True
        ).stdout.strip()
        logger.info("Checking the following images %s", images)
    except subprocess.CalledProcessError:
        logger.warning("Unable to get a list of local images")
        images = ""
    return images.split()


def get_remote_layers(image_name):
    """Ask the remote repository for layer info"""
    command = [
        "skopeo",
        "inspect",
        "-n",
        f"docker://{image_name}",
    ]
    try:
        digest = subprocess.run(
            command, check=True, capture_output=True, text=True
        ).stdout.strip()
        data = json.loads(digest)
        layers = data["Layers"]
        logger.info("Image %s has remote layers of %s", image_name, layers)
    except subprocess.CalledProcessError:
        logger.warning("Unable to get remote digest for %s", image_name)
        layers = []
    return layers


def split_digest(digest):
    """Split a digest into it's type and associated data"""
    digest_type = None
    digest_data = None
    if isinstance(digest, str):
        try:
            digest_type, digest_data = digest.split(":")
        except ValueError:
            pass
    return (digest_type, digest_data)


def image_update_available(image, db):
    """Check if image update is available"""
    update = False
    remote = get_remote_layers(image)
    for layer in remote:
        hash_type, hash_value = split_digest(layer)
        new = db.add_unique_hash(hash_type, hash_value, image)
        logger.info(
            "Image: '%s' hash: '%s' type: '%s' unique: '%s'",
            image,
            hash_value,
            hash_type,
            new,
        )
        update |= new
    return update


def setup_notifier(config):
    """Setup the main notifier instance and register all URIs"""
    notifier = apprise.Apprise()
    notifier.add(config)
    return notifier


def check_images(config):
    """Process all images and send notifications if applicable"""
    notifier = setup_notifier(config)
    db = PiunDatabase()
    for image in get_images():
        if image_update_available(image, db):
            notifier.notify(
                title=f"Update available for {image}",
                body="An updated version of this image was found on the remote repository.",
            )
