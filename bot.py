import logging

from hop import stream, Stream
from hop.io import StartPosition
from hop.auth import Auth
from slack import WebClient
from slack_sdk.errors import SlackApiError

from slack_token import SLACK_TOKEN, hop_username, hop_pw

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

                # Events starting with S are real and MS are fake/test.
                if instance['superevent_id'][0] == 'S' or instance['superevent_id'][0] == 's':

                    logging.info(f"====================\nIncoming alert of length {len(data)}:")
                    
                    # Printing out the alert type and event id to std out
                    logging.info(f"{instance['alert_type']}: {instance['superevent_id']}")
                    new_channel_name = instance['superevent_id'].lower()


                    if instance["alert_type"] != "RETRACTION":

                        try:
                            
                            ########

                            #TODO: Whatever processing you want. Make plots, run analysis, classify event, call other api's etc

                            img_link = f"https://gracedb.ligo.org/apiweb/superevents/{instance['superevent_id']}/files/bayestar.png"
                            
                            ########



                            # Creating the message text
                            message_text = f"""
Alert Type: {instance["alert_type"]}
Superevent ID: {instance['superevent_id']}
Event Time: {instance['event']['time']} 
Alert Time: {instance['time_created']}
FAR: {instance['event']['far']} 
Detectors: {instance['event']['instruments']} 
BNS: {instance['event']['classification']['BNS']:.3f}
NSBH: {instance['event']['classification']['NSBH']:.3f} 
BBH: {instance['event']['classification']['BBH']:.3f} 
Has NS: {instance['event']['properties']['HasNS']:.3f}
Has Remnant: {instance['event']['properties']['HasRemnant']:.3f}
Has Mass Gap: {instance['event']['properties']['HasMassGap']:.3f}
Join related channel: #{instance['superevent_id'].lower()} 
Skymap image: {img_link}
                            """
                            
                            # This creates a new slack channel for the alert
                            try:
                                logging.info("Trying to create a new channel...")
                                response = client.conversations_create(name=new_channel_name, token = SLACK_TOKEN)
                                logging.info("Done")
                            except SlackApiError as e:
                                if e.response["error"] == "name_taken":
                                    logging.info("Done")
                                else:
                                    logging.warning("Could not create new channel. Error: ", e.response["error"])


                            # # This gets the bot to join the channel
                            # try:
                            #     print("Trying to join new channel...")
                            #     response = client.conversations_join(channel = new_channel_name, token = SLACK_TOKEN)
                            #     print(response)
                            # except SlackApiError as e:
                            #     print("Could not join channel. Error: ", e.response)


                            # This is a message without buttons and stuff. We are assuming #alert-bot-test already exists and the bot is added to it
                            try:
                                logging.info("Trying to send message to general channel...")
                                #response = client.chat_postMessage(channel='#alert-bot-test', text=message_text)
                                response = client.chat_postMessage(
                                                        channel=f"#bot-alerts",
                                                        token = SLACK_TOKEN,
                                                        blocks = [  {"type": "section", 
                                                                    "text": {
                                                                                "type": "mrkdwn", 
                                                                                "text": message_text
                                                                                }
                                                                    } 
                                                                ]
                                )
                                logging.info("Done")
                            except SlackApiError as e:
                                logging.warning("Could post message. Error: ", e.response["error"])


                            
                            # This is a message with buttons and stuff to the new channel
                            try:
                                logging.info("Trying to send message to event channel...")
                                response = client.chat_postMessage(
                                                        channel=f"#{new_channel_name}",
                                                        token = SLACK_TOKEN,
                                                        blocks = [  {"type": "section", 
                                                                    "text": {
                                                                                "type": "mrkdwn", 
                                                                                "text": message_text
                                                                                }
                                                                    }
                                                                    
                                                                ]
                                                        )
                                logging.info("Done")
                            except SlackApiError as e:
                                logging.warning("Could post message. Error: ", e.response["error"])
                    
                        except KeyError:
                            logging.warning('Bad data formatting...skipping message')
                            

                    # RETRACTION
                    else: 

                        """ 
                        This should archives the channel. Current method -> get list of all channels -> find id for channel name -> call archive function
                        Issue - Linear time operation in the number for channels in the workspace. We wan to avoid this. I do not have a good solution yet.
                        One possible idea is to store a hash map from super event id to channel id on our end but that does not work with dummy alerts. It
                        might work engineering run onwards. 
                        """
                        # TODO: Find O(1) method to archive channels. For now I am just sending a message that event was RETRACTED.

                        # try:
                        #     print(f"{instance['superevent_id']} was retracted. Trying to archive related channel id", end = "")
                        #     temp = "#MS230317q".lower()
                        #     channel_id = client.conversations_info(channel=temp, token=SLACK_TOKEN)['channel']['id']
                        #     print(channel_id)
                        #     try:
                        #         response  = client.conversations_archive(channel=temp)
                        #         print("Done")
                        #     except SlackApiError as e:
                        #         print("\nCould not archive channel. Error: ", e.response, response)
                        # except SlackApiError as e:
                        #         print("\nCould not find channel id. Error: ", e.response["error"])

                        try:
                            logging.info(f"Trying to send message to {new_channel_name} channel...")
                            response = client.chat_postMessage(channel=f'#{new_channel_name}', text="This alert was retracted.")
                            logging.info("Done")
                        except SlackApiError as e:
                            logging.warning("Could post message. Error: ", e.response["error"])

                    
