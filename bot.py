import logging
import sqlite3

from hop import stream, Stream
from hop.io import StartPosition
from hop.auth import Auth
from slack import WebClient

from alerts import Alert
from slack_token import SLACK_TOKEN, hop_username, hop_pw
from utils import create_new_channel, send_message_to_channel

DB_path = "04_alerts.db"

logging.getLogger().setLevel(logging.INFO)

# Auth for hop
auth = Auth(hop_username, hop_pw)
stream = Stream(auth=auth)

if __name__ == '__main__':

    with stream.open("kafka://kafka.scimma.org/igwn.gwalert", "r") as s:

        logging.info("Hop Skotch stream open. Creating Slack client...")

        # Connecting to the slack client for api calls
        client = WebClient(token=SLACK_TOKEN)

        # Connecting to local DB to prevent duplicate alerts
        con = sqlite3.connect(DB_path)
        cur = con.cursor()

        for message in s:
            
            data = message.content

            for instance in data:

                alert = Alert(instance, ignore_skymap=False)

                message_text = alert.get_GCW_detailed_message()
                retraction_message = alert.get_GCW_retraction_message()
                event_channel = alert.slack_channel
                general_channel = "bot-alerts"

                # Making sure the alert is real and passes the preliminary cuts and was not already sent to slack.
                if alert.is_real and alert.passes_GCW_general_cut() and not alert.already_sent_to_slack(cur):


                    logging.info(f"=====\nIncoming alert of length {len(data)}:")
                    logging.info(f"{alert.alert_type}: {alert.superevent_id}")

                    if not alert.is_retraction:

                        try:
                            
                            ########

                            # TODO:  Whatever processing you want. Make plots, run analysis, classify event, call other api's etc

                            ########
                            
                            # This creates a new slack channel for the alert
                            create_new_channel(client, event_channel)

                            # We are assuming #bot-alerts already exists and the bot is added to it
                            send_message_to_channel(client, general_channel, message_text)

                            # This is sending a message sent to the new channel
                            send_message_to_channel(client, event_channel, message_text)

                        except KeyError:

                            logging.warning('Bad data formatting...skipping message')
                            
                    # RETRACTION
                    else: 
                        
                        send_message_to_channel(client, event_channel, retraction_message)


                    
