import logging

from hop import stream, Stream
from hop.io import StartPosition
from hop.auth import Auth

from alerts import Alert
from slack_token import SLACK_TOKEN, hop_username, hop_pw
from utils import create_new_channel, send_message_to_channel

logging.getLogger().setLevel(logging.INFO)

auth = Auth(hop_username, hop_pw)
stream = Stream(auth=auth)

if __name__ == '__main__':

    with stream.open("kafka://kafka.scimma.org/igwn.gwalert", "r") as s:

        logging.info("Hop Skotch stream open. Creating Slack client...")
        client = WebClient(token=SLACK_TOKEN)

        for message in s:
            
            # Schema for data available at https://emfollow.docs.ligo.org/userguide/content.html#kafka-notice-gcn-scimma
            data = message.content

            # Data is a list that can (potentially) have more than 1 element? This is inconsistent with the alert schema
            for instance in data:

                alert = Alert(instance)

                if alert.is_real:

                    logging.info(f"=====\nIncoming alert of length {len(data)}:")
                    logging.info(f"{alert.alert_type}: {alert.superevent_id}")

                    if not alert.is_retraction:

                        try:
                            
                            ########

                            # TODO:  Whatever processing you want. Make plots, run analysis, classify event, call other api's etc

                            message_text = alert.get_GCW_detailed_message
                            retraction_message = alert.get_GCW_retraction_message
                            event_channel = alert.slack_channel
                            general_channel = "#bot-alerts"

                            ########
                            
                            # This creates a new slack channel for the alert
                            logging.info("Trying to create a new channel...")
                            create_new_channel(client, SLACK_TOKEN, event_channel)

                            # This is a message without buttons and stuff. We are assuming #alert-bot-test already exists and the bot is added to it
                            logging.info("Trying to send message to general channel...")
                            send_message_to_channel(client, SLACK_TOKEN, message_text)

                            # This is a message with buttons and stuff to the new channel
                            logging.info(f"Trying to send message to {event_channel} channel...")
                            send_message_to_channel(client, SLACK_TOKEN, event_channel, message_text)

                        except KeyError:

                            logging.warning('Bad data formatting...skipping message')
                            

                    # RETRACTION
                    else: 

                        logging.info(f"Trying to send message to {event_channel} channel...")
                        send_message_to_channel(client, SLACK_TOKEN, event_channel, retraction_message)


                    
