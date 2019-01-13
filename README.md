# MagicCap API
The API used for MagicCap versioning/autoupdates/local API security handling, written serverlessly with Zappa, Flask and AWS Lambda.

Currently, these are the supported endpoints:
- `/travis/new/<travis_api_key>/<tag>` - Marks a new MagicCap build by tag.
- `/version` - Gets information about the current version.
- `/version/check/<current_version>` - Used by MagicCap to check the version is up to date.
- `/local_api/global_token/request` - This is used to request a global API token. This is used to generate one time tokens to request local API access. To prevent abuse, this endpoint can only be used once every 24 hours.
- `/local_api/global_token/validate` - This is used with `key` as a argument to validate the email.
- `/local_api/global_token/judgement` - Used so staff can cast a judgement.
- `/local_api/global_token` - This can be used with `key` as a argument with the global API token to get information on it.
- `/local_api/one_time/generate` - This can be used with `key` as a argument with the global API token to get a one time token.
- `/local_api/one_time/<key>` - This is used by MagicCap to validate one time tokens and get information on them to show the request prompt.

## Configuration
You will need a AWS free tier account with your credentials stored in `~/.aws/credentials`. You will then need to run `create_tables.py` locally in order to create the DynamoDB tables. The Flask instance is `main.app`. For more information about setting up Zappa, [check here](https://github.com/Miserlou/Zappa).
