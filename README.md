# GW-Bot

Slack alert bot for `LIGO 04` gravitational wave alerts via Scimma's Hopskotch. 

If you intend on using this bot within the Gravity collective workspace and are looking for feature requests, please open a new issue. 

If you are are looking to set up the alert bot within your own workspace, follow the instructions below. 

Specifically, `alerts.py` should give you all of the information from JSON, decomposed as a python object - this is supposed to serve as the starting point for further configuration. I have added the functions used for the Gravity collectives update criteria to this file.

Further, `utils.py` has some useful helper function to help with slack functionality.

# Citation

If you use the this utility for any of your work, please cite the corresponding paper. Citation details can be found below or in citation.bib

```
@ARTICLE{2023arXiv231015240S,
       author = {{Shah}, Ved G. and {Narayan}, Gautham and {Perkins}, Haille M.~L. and {Foley}, Ryan J. and {Chatterjee}, Deep and {Cousins}, Bryce and {Macias}, Phillip},
        title = "{Predictions for Electromagnetic Counterparts to Neutron Star Mergers Discovered during LIGO-Virgo-KAGRA Observing Runs 4 and 5}",
      journal = {arXiv e-prints},
     keywords = {Astrophysics - High Energy Astrophysical Phenomena, Astrophysics - Instrumentation and Methods for Astrophysics},
         year = 2023,
        month = oct,
          eid = {arXiv:2310.15240},
        pages = {arXiv:2310.15240},
          doi = {10.48550/arXiv.2310.15240},
archivePrefix = {arXiv},
       eprint = {2310.15240},
 primaryClass = {astro-ph.HE},
       adsurl = {https://ui.adsabs.harvard.edu/abs/2023arXiv231015240S},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}
```

## 1. Getting started in your own workspace:

### 1.1 Set up Hopskotch listener

You can find detailed information about setting up the hop client here:

https://hop-client.readthedocs.io/en/stable/

Specifically, https://hop-client.readthedocs.io/en/stable/user/quickstart.html#using-the-cli might be useful if you are interested in subscribing to certain topics. 


### 1.2 Configure Slack

* Start creating a new app here [https://api.slack.com/apps].
* Click on `Create New App`.
* Choose `From an App Manifest`.
* Choose your workspace. This is where the bot will be installed.
* Use the app manifest below (both JSON and YAML formats). Please note that these are the permissions that we are currently using. You may want to limit what the bot is capable of doing inside your workspace but that might come at the cost of functionality.
* Create the app.
* Navigate to `Features` > `OAuth & Permissions` and scroll down to `OAuth Tokens for Your Workspace`. From here, you can install the app to your workspace. Once you have read through the data permissions, click allow.
* You will now see a `Bot User OAuth Token`. This is what you can use within python to access the api. 

#### App manifests:

Use either `manifest.yml` or `manifest.json` to create the app in slack. Be sure to change the name of the app as you see fit. 


### 1.3 Configure Python 

* Create a file named `slack_token.py`. Within this file, store the `Bot User OAuth Token` in a variable called `SLACK_TOKEN`. This token will allow you to interface between python and slack. The hop client authentication (`hop_username` and `hop_pw`) should also be added to this file. 

* Use `requirements.txt` to install the relevant dependancies to your environment.
* Run `python bot.py` and you should seeing the alerts as they come in.

### 1.4 Set up via Docker (Optional):

Both the `Dockerfile` and `docker-compose.yml` files have been provided if you want to build the slack bot as a Docker app.

Rebuild and restart:

`docker compose build`

`docker compose up -d`

If you need to stop the service, use:

`docker compose down`

For monitoring, use:

`docker compose ps`

`docker compose logs -f`

## Known Issues:

* DUPLICATES !!!

HOPSKOTCH allows for “at least once” delivery semantics [https://scimma.org/hopskotch.html]. While this is great for not missing alerts, our bot send a message for every alert it receives leading to duplicates. Solving that would be too easy so Slack has its own bug to complicate matters [https://github.com/slackapi/bolt-python/issues/764]. I am going to try to address this issues ASAP since it is cluttering the channel with unnecessary messages.

* [CURRENTLY DISABLED] ARCHIVING CHANNELS

Archiving channels after a retraction is very slow right now and will get slower as the number of channels in a workspace increases (due to linear search). Slack does not currently have api's (that I could find) that can do this efficiently (O(1)) so we might have to build something on our own. Once again, this depends on having relatively consistent data formatting (like `PRELIMINARY` alerts for any `superevent id` coming in before `RETRACTION` alerts). 
For now, I am just sending the RETRACTION alerts to the respective channels.

Current method -> get list of all channels -> find id for channel name -> call archive function
Issue - Linear time operation in the number for channels in the workspace. We wan to avoid this. I do not have a good solution yet. One possible idea is to store a hash map from super event id to channel id on our end but that does not work with dummy alerts. It might work engineering run onwards. 


## Contributing:

If you want to help, please start by opening a pull request. The alerts class should be flexible enough to allow for extensive configuration. 

## Acknowledgements:

This bot was created as part of the collaborative efforts of the Gravity collective. 

While a version of this bot is going to be used for the Gravity collective Slack workspace, we acknowledge that different teams will want to customize the thresholds and data processing steps based on what they hope to achieve with the alerts. If you do use this project in your work, please acknowledge the developers Ved Shah (vedgs2@illinois.edu), Gautham Narayan (gsn@illinois.edu) and the UIUCSN team.
