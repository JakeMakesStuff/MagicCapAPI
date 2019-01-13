# This code is a part of MagicCap which is a MPL-2.0 licensed project.
# Copyright (C) Jake Gealer <jake@gealer.email> 2018-2019.

from flask import Blueprint, request, jsonify, render_template
from models import IPHashTimestamps, UnvalidatedGlobalKeyRequests, GlobalKeys, OneTimeKeys
from hashlib import sha512
from uuid import uuid4
from consts import SCOPES, SENDER, ADMIN_EMAILS
import requests
import time
import re
import boto3
from botocore.exceptions import ClientError
# Imports go here.

local_api = Blueprint("local_api", __name__, url_prefix="/local_api")
# The local API blueprint.


@local_api.route("/global_token/request", methods=["POST"])
def request_global_token():
    """This is used to request global API tokens."""
    try:
        email = request.form['email']
        scopes = request.form['scopes'].split("|")
        if len(scopes) == 1 and scopes[0] == "":
            raise KeyError
        
        publisher_name = request.form['publisher_name']
        service_name = request.form['service_name']
        
        if publisher_name == "" or service_name == "" or email == "":
            raise KeyError
    except KeyError:
        err = jsonify({
            "success": False,
            "error": "Request does not contain all of the required parts."
        })
        err.status_code = 400

        return err

    try:
        ip = request.headers['CF-Connecting-IP']
    except KeyError:
        ip = request.remote_addr

    ip_hash = sha512(ip.encode()).hexdigest()
    try:
        ip_hash_timestamp_db = IPHashTimestamps.get(ip_hash)
    except IPHashTimestamps.DoesNotExist:
        ip_hash_timestamp_db = IPHashTimestamps(ip_hash=ip_hash, timestamp=0)

    current_time = int(time.time())
    if ip_hash_timestamp_db.timestamp > current_time:
        err = jsonify({
            "success": False,
            "error": "You have been ratelimited!"
        })
        err.status_code = 429

        return err

    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
        err = jsonify({
            "success": False,
            "error": "The e-mail given is invalid."
        })
        err.status_code = 400

        return err

    uuid = str(uuid4())

    for s in scopes:
        if s not in SCOPES:
            err = jsonify({
                "success": False,
                "error": f"{s} is a invalid scope."
            })
            err.status_code = 400

            return err

    data = {
        "email": email,
        "scopes": scopes,
        "publisher_name": publisher_name,
        "service_name": service_name
    }

    UnvalidatedGlobalKeyRequests(data=data, key=uuid).save()

    text = (
        "Hi,\n\nYou (or someone using your e-mail) just requested a global token for the MagicCap API."
        f" In order to request your API token for {service_name}, you must first verify your email. In order to do so, please click the link below.\n\n"
        f"https://api.magiccap.me/local_api/global_token/validate?key={uuid}"
    )

    try:
        boto3.client("ses", region_name="eu-west-1").send_email(
            Destination={
                "ToAddresses": [
                    email
                ]
            },
            Message={
                "Body": {
                    "Text": {
                        "Charset": "UTF-8",
                        "Data": text
                    }
                },
                "Subject": {
                    "Charset": "UTF-8",
                    "Data": "[MagicCap API] E-mail Verification Required"
                }
            },
            Source=SENDER
        )
    except ClientError as e:
        err = jsonify({
            "success": False,
            "error": f"E-mail sending error: {e.response['Error']['Message']}"
        })
        err.status_code = 500

        return err

    ip_hash_timestamp_db.timestamp = current_time + 86400
    ip_hash_timestamp_db.save()

    return jsonify({
        "success": True,
        "message": "Check your e-mail address for a confirmation email to continue."
    })


@local_api.route("/global_token/validate")
def validate_global_token():
    """Validates the e-mail given for the global token request."""
    try:
        key = request.args['key']
    except KeyError:
        return render_template("validate.j2", success=False)

    try:
        key_req = UnvalidatedGlobalKeyRequests.get(key)
    except UnvalidatedGlobalKeyRequests.DoesNotExist:
        return render_template("validate.j2", success=False)

    data = key_req.data
    key_req.delete()

    uuid = str(uuid4())

    model = GlobalKeys(
        key=uuid, email=data['email'], scopes=data['scopes'],
        publisher_name=data['publisher_name'], service_name=data['service_name'],
        reviewed=False
    )

    model.save()

    s = ""
    for i in data:
        s += f"\n{i}: {data[i]}"

    s += (
        f"\n\nAPPROVE: https://api.magiccap.me/local_api/global_token/judgement?key={uuid}&action=approve\n"
        f"DENY: https://api.magiccap.me/local_api/global_token/judgement?key={uuid}&action=deny"
    )

    boto3.client("ses", region_name="eu-west-1").send_email(
        Destination={
            "ToAddresses": ADMIN_EMAILS
        },
        Message={
            "Body": {
                "Text": {
                    "Charset": "UTF-8",
                    "Data": s
                }
            },
            "Subject": {
                "Charset": "UTF-8",
                "Data": "[MagicCap API] User approval required"
            }
        },
        Source=SENDER
    )

    return render_template("validate.j2", success=True)


@local_api.route("/global_token/judgement")
def global_token_judgement():
    """Allows staff to make a judgement on a global token."""
    ACTION_MAP = {
        "approve": True,
        "deny": False
    }

    try:
        judgement = ACTION_MAP[request.args['action']]
    except KeyError:
        return "Either invalid judgment or judgment not given.", 404

    try:
        key = request.args['key']
    except KeyError:
        return "Key not found in request.", 400

    try:
        global_key_db = GlobalKeys.get(key)
    except GlobalKeys.DoesNotExist:
        return "Key doesn't exist in DB. Either it is wrong or a deny judgement has been cast.", 404

    if global_key_db.reviewed:
        return "Judgement already been cast.", 400

    judgement_type = "APPROVED" if judgement else "DENIED"

    body = f"Hi,\n\nYour global API key application for {service_name} has been {judgement_type}."
    if judgement:
        body += f" Your key is below:\n\n{global_key_db.key}\n\nThanks,\nThe MagicCap Development Team"
        global_key_db.reviewed = True
        global_key_db.save()
    else:
        body += "\n\nThanks,\nThe MagicCap Development Team"
        global_key_db.delete()

    boto3.client("ses", region_name="eu-west-1").send_email(
        Destination={
            "ToAddresses": [
                global_key_db.email
            ]
        },
        Message={
            "Body": {
                "Text": {
                    "Charset": "UTF-8",
                    "Data": body
                }
            },
            "Subject": {
                "Charset": "UTF-8",
                "Data": "[MagicCap API] A key judgement has been cast"
            }
        },
        Source=SENDER
    )

    return f"{judgement_type} judgment cast.", 200


@local_api.route("/global_token")
def global_token_info():
    """Gets all of the information held about the global token."""
    try:
        key = request.args['key']
    except KeyError:
        err = jsonify({
            "success": False,
            "error": "Key not found."
        })
        err.status_code = 400

        return err

    try:
        key_db = GlobalKeys.get(key)
    except GlobalKeys.DoesNotExist:
        err = jsonify({
            "success": False,
            "error": "The key given is invalid."
        })
        err.status_code = 400

        return err

    return jsonify({
        "email": key_db.email,
        "scopes": key_db.scopes,
        "publisher_name": key_db.publisher_name,
        "service_name": key_db.service_name
    })


@local_api.route("/one_time/generate")
def generate_one_time_token():
    """Generates a one time token with the global token."""
    try:
        key = request.args['key']
    except KeyError:
        err = jsonify({
            "success": False,
            "error": "Key not found."
        })
        err.status_code = 400

        return err

    try:
        global_token_db = GlobalKeys.get(key)
    except GlobalKeys.DoesNotExist:
        err = jsonify({
            "success": False,
            "error": "Key doesn't exist."
        })
        err.status_code = 403

        return err

    uuid = str(uuid4())

    OneTimeKeys(key=uuid, global_key=key).save()

    return jsonify({
        "success": True,
        "information": {
            "email": global_token_db.email,
            "scopes": global_token_db.scopes,
            "publisher_name": global_token_db.publisher_name,
            "service_name": global_token_db.service_name
        },
        "token": uuid
    })


@local_api.route("/one_time/<key>")
def one_time_usage(key):
    """Uses the one time token."""
    try:
        one_time = OneTimeKeys.get(key)
    except OneTimeKeys.DoesNotExist:
        err = jsonify({
            "success": False,
            "error": "Key not found. Has it been used?"
        })
        err.status_code = 404

        return err

    global_token_db = GlobalKeys.get(one_time.global_key)
    one_time.delete()

    return jsonify({
        "email": global_token_db.email,
        "scopes": global_token_db.scopes,
        "publisher_name": global_token_db.publisher_name,
        "service_name": global_token_db.service_name
    })


def setup(app):
    app.register_blueprint(local_api, url_prefix="/local_api")
# Sets up the API.
