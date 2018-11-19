# MagicCap API
The API used for MagicCap versioning/autoupdates, written serverlessly with Zappa, Flask and AWS Lambda.

Currently, these are the supported endpoints:
- `/travis/new/<travis_api_key>/<tag>` - Marks a new MagicCap build by tag.
- `/version` - Gets information about the current version.
- `/version/check/<current_version>` - Used by MagicCap to check the version is up to date.

## Configuration
You will need a AWS free tier account with your credentials stored in `~/.aws/credentials`. You will then need to run `create_tables.py` locally in order to create the DynamoDB tables. The Flask instance is `main.app`. For more information about setting up Zappa, [check here](https://github.com/Miserlou/Zappa).
