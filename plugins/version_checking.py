# This code is a part of MagicCap which is a MPL-2.0 licensed project.
# Copyright (C) Jake Gealer <jake@gealer.email> 2018-2019.

from flask import Blueprint, jsonify, request
from models import Version, get_version
import requests
# Imports go here.

version = Blueprint("version", __name__, url_prefix="/version")
# The version blueprint.


@version.route("/latest")
def latest_versions():
    """Gets information about the latest MagicCap releases."""
    latest_release = None
    latest_beta = None

    release_id = 0
    while True:
        try:
            v = Version.get(release_id)
            if v.beta:
                latest_beta = v
            else:
                latest_release = v
            release_id += 1
        except Version.DoesNotExist:
            break

    beta_json = None
    beta_newer = False
    if latest_beta:
        beta_json = {
            "mac": "https://s3.magiccap.me/upgrades/v{}/magiccap-mac.dmg".format(latest_beta.version),
            "linux": "https://s3.magiccap.me/upgrades/v{}/magiccap-linux.zip".format(latest_beta.version),
            "changelogs": latest_beta.changelogs,
            "version": latest_beta.version
        }
        beta_newer = latest_beta.release_id > latest_release.release_id

    return jsonify({
        "beta": beta_json,
        "release": {
            "mac": "https://s3.magiccap.me/upgrades/v{}/magiccap-mac.dmg".format(latest_release.version),
            "linux": "https://s3.magiccap.me/upgrades/v{}/magiccap-linux.zip".format(latest_release.version),
            "changelogs": latest_release.changelogs,
            "version": latest_release.version
        },
        "is_beta_newer_than_release": beta_newer
    })


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

    last_model = updates_since.pop()

    for inbetween_release in updates_since:
        if last_model.beta == inbetween_release.beta:
            changelogs += inbetween_release.changelogs + "\n"

    changelogs += last_model.changelogs + "\n"

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
