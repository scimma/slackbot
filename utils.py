import logging
from slack_sdk.errors import SlackApiError

def send_message_to_channel(client, channel_name, text):
    """
    Send a message to slack channel of your choice.

    Args:
        client (slack WebClient): This client will be used to send the message. Should be authenticated with the token.
        channel_name (string): Name of the channel to send the message to without the #. Channel should already exists.
        text (string): Text for the message to send to the channel.
    """

    logging.info(f"Trying to send message to {channel_name} channel...")
    # This is a message without buttons and stuff. We are assuming #alert-bot-test already exists and the bot is added to it
    try:
        response = client.chat_postMessage(
                                channel=f"#{channel_name}",
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

def create_new_channel(client, channel_name):
    """
    Create a new channel on your slack workspace

    Args:
        client (slack WebClient): This client will be used to create the channel. Should be authenticated with the token.
        channel_name (string): Name of the channel that needs to be created without the #. 
    """

    logging.info(f"Trying to create a new channel: {channel_name}...")
    try:

        logging.info("Trying to create a new channel...")
        response = client.conversations_create(name=channel_name)
        logging.info("Done")

    except SlackApiError as e:

        if e.response["error"] == "name_taken":
            logging.info("Done")
        else:
            logging.warning("Could not create new channel. Error: ", e.response["error"])