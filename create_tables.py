# This code is a part of MagicCap which is a MPL-2.0 licensed project.
# Copyright (C) Jake Gealer <jake@gealer.email> 2018.

from models import Version, TravisKeys
# Imports go here.


if not Version.exists():
    Version.create_table()

if not TravisKeys.exists():
    TravisKeys.create_table()
# Creates the tables if they do not exist.
