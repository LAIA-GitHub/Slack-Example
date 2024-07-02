import os
from slack_sdk import WebClient
from flask import Flask, request
from dotenv import find_dotenv, load_dotenv


# Load environment variables from .env file
load_dotenv(find_dotenv())

client_id = os.environ["SLACK_CLIENT_ID"]
client_secret = os.environ["SLACK_CLIENT_SECRET"]
oauth_scope = os.environ["SLACK_SCOPES"]

app = Flask(__name__)

@app.route("/slack/install", methods=["GET"])
def pre_install():
    state = "randomly-generated-one-time-value"
    return '<a href="https://slack.com/oauth/v2/authorize?' \
        f'scope={oauth_scope}&client_id={client_id}&state={state}">' \
        'Add to Slack</a>'

@app.route("/slack/oauth_redirect", methods=["GET"])
def post_install():
    # Verify the "state" parameter

    # Retrieve the auth code from the request params
    code_param = request.args['code']

    # An empty string is a valid token for this request
    client = WebClient()

    # Request the auth tokens from Slack
    response = client.oauth_v2_access(
        client_id=client_id,
        client_secret=client_secret,
        code=code_param
    )
    print(response)

    # Save the bot token to an environmental variable or to your data store
    # for later use
    os.environ["SLACK_BOT_TOKEN"] = response['access_token']

    # Don't forget to let the user know that OAuth has succeeded!
    return "Installation is completed!"

if __name__ == "__main__":
    app.run("localhost", 3000)
