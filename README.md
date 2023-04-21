# GW-Bot

Slack alert bot for `LIGO 04` gravitational wave alerts via Scimma's Hop Skotch. 

If you intend on using this bot within the Gravity collective workspace and are looking for feature requests, please open  a new issue. 

If you are are looking to set up the alert bot within your own workspace, follow the instructions below.

## 1. Getting started in your own workspace:

### 1.1 Configure Slack

* Start creating a new app here [https://api.slack.com/apps].
* Click on `Create New App`.
* Choose `From an App Manifest`.
* Choose your workspace. This is where the bot will be installed.
* Use the app manifest below (both JSON and YAML formats). Please note that these are the permissions that we are currently using. You may want to limit what the bot is capable of doing inside your workspace but that might come at the cost of functionality.
* Create the app.
* Navigate to `Features` > `OAuth & Permissions` and scroll down to `OAuth Tokens for Your Workspace`. From here, you can install the app to your workspace. Once you have read through the data permissions, click allow.
* You will now see a `Bot User OAuth Token`. This is what you can use within python to access the api. 

#### App manifests:
```YAML
display_information:
  name: LIGO-Alert-Bot
features:
  bot_user:
    display_name: LIGO-Alert-Bot
    always_online: false
oauth_config:
  scopes:
    bot:
      - calls:read
      - channels:join
      - channels:manage
      - chat:write
      - chat:write.customize
      - commands
      - files:write
      - groups:write
      - im:write
      - mpim:write
      - channels:read
      - groups:read
settings:
  org_deploy_enabled: false
  socket_mode_enabled: false
  token_rotation_enabled: false

```

```JSON
{
    "display_information": {
        "name": "LIGO-Alert-Bot"
    },
    "features": {
        "bot_user": {
            "display_name": "LIGO-Alert-Bot",
            "always_online": false
        }
    },
    "oauth_config": {
        "scopes": {
            "bot": [
                "calls:read",
                "channels:join",
                "channels:manage",
                "chat:write",
                "chat:write.customize",
                "commands",
                "files:write",
                "groups:write",
                "im:write",
                "mpim:write",
                "channels:read",
                "groups:read"
            ]
        }
    },
    "settings": {
        "org_deploy_enabled": false,
        "socket_mode_enabled": false,
        "token_rotation_enabled": false
    }
}
```


### 1.2 Configure Python 

* Create a file named `slack_token.py`. Within this file, store the `Bot User OAuth Token` in a variable called `SLACK_TOKEN`. This token will allow you to interface between python and slack.
* Use the `env.txt` file to recreate the python environment using conda. This can be done using `conda env create --file env.txt`.
* Activate the newly created conda environment and run `python bot.py` and you should seeing the alerts as they come in.

### 1.3 Set up via Docker:

Work in progress....

## Known Issues:

* The current alerts are not real. Thus, there is a fair bit of repetition which causes some of the channel-creation and archiving features to fail. We expect this issue to resolve itself when the engineering run begins. 

* Archiving channels after a retraction is very slow right now and will get slower as the number of channels in a workspace increases (due to linear search). Slack does not currently have api's (that I could find) that can do this efficiently (O(1)) so we might have to build something on our own. Once again, this depends on having relatively consistent data formatting (like `PRELIMINARY` alerts for any `superevent id` coming in before `RETRACTION` alerts). We hope to iron this out during the engineering run.

## Contributing:

Almost all of the code here was written in under 10 hours so there is a lot of work that can be done to improve different aspects of this project. If you want to help, please start by opening a pull request.

## Acknowledgements:

This bot was created as part of the collaborative efforts of the Gravity collective. 

While a version of this bot is going to be used for the Gravity collective Slack workspace, we acknowledge that different teams will want to customize the alert thresholds and data processing steps based on what they hope to achieve with the alerts. 
