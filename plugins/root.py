# This code is a part of MagicCap which is a MPL-2.0 licensed project.
# Copyright (C) Jake Gealer <jake@gealer.email> 2018.

def root_route():
    return "This is the root of the API."
# The route for /.


def setup(app):
    app.add_url_rule("/", "root", root_route)
# Sets up the API.
