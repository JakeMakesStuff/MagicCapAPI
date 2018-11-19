# This code is a part of MagicCap which is a MPL-2.0 licensed project.
# Copyright (C) Jake Gealer <jake@gealer.email> 2018.

from pynamodb.models import Model
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from pynamodb.attributes import UnicodeAttribute, NumberAttribute
# Imports go here.


class VersionIndex(GlobalSecondaryIndex):
    """The index used for querying the version."""
    class Meta:
        read_capacity_units = 2
        write_capacity_units = 1
        projection = AllProjection()

    version = UnicodeAttribute(hash_key=True)


class Version(Model):
    """The model used for each version."""
    class Meta:
        table_name = "magiccap_versions"
        region = "eu-west-2"
        read_capacity_units = 2
        write_capacity_units = 1

    release_id = NumberAttribute(hash_key=True)
    version = UnicodeAttribute()
    version_index = VersionIndex()
    changelogs = UnicodeAttribute()


def get_version(version):
    """Uses the index to get a version."""
    for i in Version.version_index.query(version):
        return i
    raise Version.DoesNotExist


class TravisKeys(Model):
    """The model used for Travis API keys."""
    class Meta:
        table_name = "magiccap_travis_keys"
        region = "eu-west-2"
        read_capacity_units = 1
        write_capacity_units = 1

    key = UnicodeAttribute(hash_key=True)
