# This code is a part of MagicCap which is a MPL-2.0 licensed project.
# Copyright (C) Jake Gealer <jake@gealer.email> 2019.

from flask import Blueprint, jsonify, request
from models import InstallID, get_device_id
from hashlib import sha512
from uuid import uuid4
import requests
# Imports go here.

install_id = Blueprint("install_id", __name__, url_prefix="/install_id")
# The install ID blueprint.


@install_id.route("/new/<device_id>")
def new_install_id(device_id):
    """Creates a new install ID."""
    try:
        install_id_db = get_device_id(device_id)
    except InstallID.DoesNotExist:
        try:
            ip = request.headers['CF-Connecting-IP']
        except KeyError:
            ip = request.remote_addr
        install_id_db = InstallID(install_id=str(uuid4()), device_id=device_id, hashed_ip=sha512(ip).hexdigest())
        install_id_db.save()

    return install_id_db.install_id, 200


def setup(app):
    app.register_blueprint(install_id, url_prefix="/install_id")
# Sets up the API.
