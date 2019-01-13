# This code is a part of MagicCap which is a MPL-2.0 licensed project.
# Copyright (C) Jake Gealer <jake@gealer.email> 2018-2019.

from models import Version, TravisKeys, IPHashTimestamps, UnvalidatedGlobalKeyRequests, GlobalKeys, OneTimeKeys
# Imports go here.


if not Version.exists():
    Version.create_table()

if not TravisKeys.exists():
    TravisKeys.create_table()

if not IPHashTimestamps.exists():
    IPHashTimestamps.create_table()

if not UnvalidatedGlobalKeyRequests.exists():
    UnvalidatedGlobalKeyRequests.create_table()

if not GlobalKeys.exists():
    GlobalKeys.create_table()

if not OneTimeKeys.exists():
    OneTimeKeys.create_table()
# Creates the tables if they do not exist.
