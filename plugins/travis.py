# This code is a part of MagicCap which is a MPL-2.0 licensed project.
# Copyright (C) Jake Gealer <jake@gealer.email> 2018.

from flask import Blueprint
from models import Version, TravisKeys
import requests
# Imports go here.

travis = Blueprint("travis", __name__, url_prefix="/travis")
# The travis blueprint.


@travis.route("/new/<travis_api_key>/<tag>")
def new_version(travis_api_key, tag):
    """Allows Travis to mark a new version during build."""
    try:
        TravisKeys.get(travis_api_key)
    except TravisKeys.DoesNotExist:
        return "API key is invalid.", 403

    if tag.startswith("v"):
        tag = tag.lstrip("v")

    i = 0
    while True:
        try:
            Version.get(i)
            i += 1 
        except Version.DoesNotExist:
            break

    r = requests.get(
        "https://api.github.com/repos/JakeMakesStuff/MagicCap/releases/tags/v{}".format(tag)
    )

    r.raise_for_status()
    j = r.json()

    Version(
        release_id=i, version=tag, changelogs=j['body'], beta="b" in tag
    ).save()

    return "Release {} successfully saved to the database.".format(tag), 200


def setup(app):
    app.register_blueprint(travis, url_prefix="/travis")
# Sets up the API.
