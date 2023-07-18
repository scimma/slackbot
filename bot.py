import logging

from hop import stream, Stream
from hop.io import StartPosition
from hop.auth import Auth
from slack import WebClient

from alerts import Alert
from slack_token import SLACK_TOKEN, hop_username, hop_pw
from utils import create_new_channel, send_message_to_channel

logging.getLogger().setLevel(logging.INFO)

# Auth for hop
auth = Auth(hop_username, hop_pw)
stream = Stream(auth=auth)

if __name__ == '__main__':

    with stream.open("kafka://kafka.scimma.org/igwn.gwalert", "r") as s:

        logging.info("Hop Skotch stream open. Creating Slack client...")

        # Connecting to the slack client for api calls
        client = WebClient(token=SLACK_TOKEN)

        for message in s:
            
            data = message.content

            for instance in data:
                
                # Only continue if the event is real.
                if instance['superevent_id'][0] == 'S' or instance['superevent_id'][0] == 's':

                    logging.info(f"=====\nIncoming alert of length {len(data)}:")
                    logging.info(f"{instance['alert_type']}: {instance['superevent_id']}")

                    try:
                                
                        alert = Alert(instance, ignore_skymap=False)

                        event_channel = alert.slack_channel
                        general_channel = "bot-alerts"
                        cuts_channel = "bot-alerts-good"

                        # Making sure the alert is real and passes the preliminary cuts and was not already sent to slack.
                        if alert.is_real:

                            if alert.is_retraction == False:
                                
                                message_text = alert.get_GCW_detailed_message()


                                ########

                                # TODO:  Whatever processing you want. Make plots, run analysis, classify event, call other api's etc

                                ########

                                # We are assuming #bot-alerts already exists and the bot is added to it
                                send_message_to_channel(client, general_channel, message_text)

                                # Send message to high quality event channel
                                if alert.passes_GCW_general_cut():
                                    send_message_to_channel(client, cuts_channel, message_text)

                                    
                            # RETRACTION
                            else: 

                                retraction_message = alert.get_GCW_retraction_message()
                                send_message_to_channel(client, general_channel, retraction_message)
                                send_message_to_channel(client, cuts_channel, retraction_message)

                    except KeyError:

                        logging.warning('Bad data formatting...skipping message')    

                    except Exception as e:

                        logging.warning('Something went wrong...')   
                        logging.warning(e)       


                    
