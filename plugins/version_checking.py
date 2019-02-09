# This code is a part of MagicCap which is a MPL-2.0 licensed project.
# Copyright (C) Jake Gealer <jake@gealer.email> 2018.

from flask import Blueprint, jsonify, request
from models import Version, get_version
import requests
# Imports go here.

version = Blueprint("version", __name__, url_prefix="/version")
# The version blueprint.


def get_updates(release_id, beta):
    """Gets all updates that is avaliable for the user."""
    updates = []
    current_id = release_id + 1
    while True:
        try:
            u = Version.get(current_id)
            
            if u.beta:
                if beta:
                    updates.append(u)
            else:
                updates.append(u)

            current_id += 1
        except Version.DoesNotExist:
            break

    return updates


@version.route("/check/<current_version>")
def check_version(current_version):
    """An API used by MagicCap to check if it is the latest version."""
    beta_channel = request.args.get("beta", "false").lower() == "true"

    if current_version.startswith("v"):
        current_version = current_version.lstrip("v")
        if current_version == "":
            err = jsonify({
                "success": False,
                "error": "Version was solely v."
            })
            err.status_code = 400
            return err

    try:
        version_db = get_version(current_version)
    except Version.DoesNotExist:
        err = jsonify({
            "success": False,
            "error": "Version does not exist in the database."
        })
        err.status_code = 400
        return err

    updates_since = get_updates(version_db.release_id, beta_channel)
    if len(updates_since) == 0:
        return jsonify({
            "success": True,
            "updated": True
        })

    changelogs = ""

    for inbetween_release in updates_since:
        changelogs += inbetween_release.changelogs + "\n"

    last_model = updates_since.pop()

    return jsonify({
        "success": True,
        "updated": False,
        "latest": {
            "version": last_model.version,
            "zip_paths": {
                "mac": "https://s3.magiccap.me/upgrades/v{}/magiccap-mac.zip".format(last_model.version),
                "linux": "https://s3.magiccap.me/upgrades/v{}/magiccap-linux.zip".format(last_model.version)
            }
        },
        "changelogs": changelogs
    })


def setup(app):
    app.register_blueprint(version, url_prefix="/version")
# Sets up the API.
