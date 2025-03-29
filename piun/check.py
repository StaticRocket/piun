"""Actual interface with podman"""

import logging
import subprocess

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


def get_local_digest(image_name):
    """Ask podman for the local image digest"""
    command = ["podman", "image", "inspect", "--format", "{{.Digest}}", image_name]
    try:
        digest = subprocess.run(
            command, check=True, capture_output=True, text=True
        ).stdout.strip()
        logger.info("Image %s has local digest of %s", image_name, digest)
    except subprocess.CalledProcessError:
        logger.warning("Unable to get local digest for %s", image_name)
        digest = ""
    return digest


def get_remote_digest(image_name):
    """Ask the remote repository for an image digest"""
    command = [
        "skopeo",
        "inspect",
        "-n",
        "--format",
        "{{.Digest}}",
        f"docker://{image_name}",
    ]
    try:
        digest = subprocess.run(
            command, check=True, capture_output=True, text=True
        ).stdout.strip()
        logger.info("Image %s has remote digest of %s", image_name, digest)
    except subprocess.CalledProcessError:
        logger.warning("Unable to get remote digest for %s", image_name)
        digest = ""
    return digest


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


def digests_match(digest_a, digest_b):
    """Compare two image digest strings"""
    type_a, data_a = split_digest(digest_a)
    type_b, data_b = split_digest(digest_b)
    if type_a != type_b:
        logger.info("Digest types changed, assuming update")
        return False
    if data_a != data_b:
        logger.info("Change in digest data detected")
        return False
    return True


def image_update_available(image):
    """Check if image update is available"""
    local = get_local_digest(image)
    remote = get_remote_digest(image)
    return not digests_match(local, remote)


def setup_notifier(config):
    """Setup the main notifier instance and register all URIs"""
    notifier = apprise.Apprise()
    notifier.add(config)
    return notifier


def check_images(config):
    """Process all images and send notifications if applicable"""
    notifier = setup_notifier(config)
    for image in get_images():
        if image_update_available(image):
            notifier.notify(
                title=f"Update available for {image}",
                body="An updated version of this image was found on the remote repository.",
            )
