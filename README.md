# MagicCap API
The API used for MagicCap versioning/autoupdates, written serverlessly with Zappa, Flask and AWS Lambda.

Currently, these are the supported endpoints:
- `/travis/new/<travis_api_key>/<tag>` - Marks a new MagicCap build by tag.
- `/version` - Gets information about the current version.
- `/version/check/<current_version>` - Used by MagicCap to check the version is up to date.
