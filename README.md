# Podman Image Update Notifier

Piun is a CLI application to fetch podman image updates and notify the user
through any Apprise endpoint. Heavily inspired by it's predecessor, diun, but
for my preferred container engine and designed for rootless environments.

## Usage

Add an [apprise config](https://github.com/caronc/apprise/wiki/config) file
at `${XDG_CONFIG_HOME}/piun/piun.yml` or `~/.config/piun/piun.yml` to specify
the endpoints you want to notify.

You can then schedule this process to run at whatever interval you wish with
whatever tools you have available. Template systemd user unit and timer files
are provided under [`systemd/`](systemd/). 

## Dependencies

This requires the host to have [`skopeo`](https://github.com/containers/skopeo).

## Notes

This was very much something I hacked together for my use. It's trash from an
old ex-Python user that had an adversity to databases. Pull request are welcome.
