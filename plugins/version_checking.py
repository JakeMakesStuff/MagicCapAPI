# This code is a part of MagicCap which is a MPL-2.0 licensed project.
# Copyright (C) Jake Gealer <jake@gealer.email> 2018.

from flask import Blueprint, jsonify, request
from models import Version, get_version
import requests
# Imports go here.

version = Blueprint("version", __name__, url_prefix="/version")
# The version blueprint.


@version.route("/")
def get_latest_version():
    """Gets the link/latest version information."""
    r = requests.get(
        "https://api.github.com/repos/JakeMakesStuff/MagicCap/releases/latest"
    )
    r.raise_for_status()
    j = r.json()

    response = {
        "success": True,
        "version": j['tag_name'][1:],
        "changelog": j['body'],
        "github_url": j['url'],
        "releases": {
            "linux": {}
        }
    }

    for release in j['assets']:
        if "mac" in release['name']:
            response['releases']['mac'] = release['browser_download_url']
        else:
            file_format = release['name'].split(".").pop().lower()
            response['releases']['linux'][file_format] = release['browser_download_url']

    return jsonify(response)


@version.route("/check/<current_version>")
def check_version(current_version):
    """An API used by MagicCap to check if it is the latest version."""
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

    try:
        Version.get(version_db.release_id + 1)
    except Version.DoesNotExist:
        return jsonify({
            "success": True,
            "updated": True
        })

    changelogs = ""

    last_model = None
    latest = False

    i = version_db.release_id + 1
    while not latest:
        try:
            inbetween_release = Version.get(i)
        except Version.DoesNotExist:
            latest = True
            break
        changelogs += inbetween_release.changelogs + "\n"
        last_model = inbetween_release
        i += 1

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
