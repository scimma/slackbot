import logging
from slack_sdk.errors import SlackApiError

def send_message_to_channel(client, token, channel, text):

    logging.info(f"Trying to send message to {channel} channel...")
    # This is a message without buttons and stuff. We are assuming #alert-bot-test already exists and the bot is added to it
    try:
        response = client.chat_postMessage(
                                channel=channel,
                                token = token,
                                blocks = [  {"type": "section", 
                                            "text": {
                                                        "type": "mrkdwn", 
                                                        "text": text
                                                        }
                                            } 
                                        ]
        )
        logging.info("Done")
    except SlackApiError as e:
        logging.warning("Could post message. Error: ", e.response["error"])

def create_new_channel(client, token, channel_name):
    
    logging.info(f"Trying to create a new channel: {channel_name}...")
    try:

        logging.info("Trying to create a new channel...")
        response = client.conversations_create(name=channel_name, token = token)
        logging.info("Done")

    except SlackApiError as e:

        if e.response["error"] == "name_taken":
            logging.info("Done")
        else:
            logging.warning("Could not create new channel. Error: ", e.response["error"])