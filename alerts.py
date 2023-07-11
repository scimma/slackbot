import logging

from io import BytesIO
from astropy.io import fits
from astropy.coordinates import Distance
from astropy import units as u

class Alert():

    def __init__(self, instance, ignore_skymap = False):

        # Parsing the incoming Kafka notice
        self.instance = instance
        self.parse_instance(instance, ignore_skymap)

        # Events starting with S are real and MS/TS are mock/test.
        if self.superevent_id[0] == 'S':
            self.is_real = True
        else:
            self.is_real = False

    def parse_instance(self, instance, ignore_skymap):

        # Parsed according to the schema here: 
        # https://emfollow.docs.ligo.org/userguide/content.html#kafka-notice-gcn-scimma
        self.instance = instance
        self.slack_bot_link = "https://github.com/scimma/slackbot"

        self.alert_type = instance['alert_type']
        self.superevent_id = instance['superevent_id']
        self.time_created = instance['time_created']
        self.gracedb_url = instance['urls']['gracedb']

        self.slack_channel = self.superevent_id.lower()

        # Initialize all variables 
        self.event_time = None
        self.FAR = None
        self.significant = None
        self.instruments = None
        self.num_instruments = None
        self.search = None
        self.group = None

        self.pipeline = None
        self.FAR_per_year = None

        # Only available for Burst
        self.duration = None
        self.central_frequency = None

        # Only available for CBC
        self.has_ns = None
        self.has_remnant = None
        self.has_mass_gap = None

        # Only available for CBC
        self.bns = None
        self.nsbh = None
        self.bbh = None
        self.noise = None

        self.dist_mean = None
        self.dist_std = None
        self.dist_modulus = None

        if self.alert_type != "RETRACTION":

            self.is_retraction = False

            self.event_time = instance['event']['time']
            self.FAR = instance['event']['far']
            self.significant = instance['event']['significant']
            self.instruments = instance['event']['instruments']
            self.num_instruments = len(self.instruments)
            self.search = instance['event']['search']
            self.group = instance['event']['group']

            # Converting FAR to years
            self.FAR_per_year = (self.FAR * u.Hz).to(1/u.year).value

            if self.group  == "CBC":

                self.pipeline = instance['event']['pipeline']
                self.skymap_img_url = f"https://gracedb.ligo.org/apiweb/superevents/{self.superevent_id}/files/bayestar.png"

                # Only available for CBC
                self.has_ns = instance['event']['properties']['HasNS']
                self.has_remnant = instance['event']['properties']['HasRemnant']
                self.has_mass_gap = instance['event']['properties']['HasMassGap']

                # Only available for CBC
                self.bns = instance['event']['classification']['BNS']
                self.nsbh = instance['event']['classification']['NSBH']
                self.bbh = instance['event']['classification']['BBH']
                self.noise = instance['event']['classification']['Terrestrial']
                
            else:

                self.pipeline = instance['event']['pipeline']
                self.skymap_img_url = f"https://gracedb.ligo.org/apiweb/superevents/{self.superevent_id}/files/cwb.png" 

                # Only available for Burst
                self.duration = instance['event']['duration']
                self.central_frequency = instance['event']['central_frequency']


            # Enable if the fits file is not going to be used
            if ignore_skymap == False:

                binary_data = instance['event']['skymap']

                skymap = fits.open(BytesIO(binary_data))

                try:
                    # Get distance values from skymap
                    self.dist_mean = skymap[1].header['DISTMEAN']
                    self.dist_std = skymap[1].header['DISTSTD']

                    # Compute distance modulus 
                    self.dist_modulus = Distance(self.dist_mean * u.Mpc).distmod.value

                except KeyError:

                    # Flag for something going wrong
                    self.dist_mean = -1
                    self.dist_std = -1
                    self.dist_modulus = -1          
                

        else: 
            self.is_retraction = True


    def passes_GCW_general_cut(self):
        """
        Cuts made before sending incoming alerts to the Gravity collective's alert bot slack channel.

        Returns:
            bool: True if the alert passes the cut, false otherwise,
        """

        if self.group == "CBC" and self.num_instruments >= 2 and (self.nsbh > 0.3 or self.bns > 0.3) and self.significant:
            return True
        
        elif self.group == "Burst" and self.num_instruments >= 2 and self.significant:
            return True
        
        else:
            return False
    
    def get_GCW_retraction_message(self):
        
        message = "This alert was retracted."
        return message

    def get_GCW_detailed_message(self):
        """
        Message sent to the Gravity collective's alert bot slack channel.

        Return:
            string: String containing relevant information about the event.
        """

        if self.group == "CBC":
            message = f"""
Alert Type: {self.alert_type}
Superevent ID: {self.superevent_id}
Group: {self.group}

Event Time: {self.event_time} 
Alert Time: {self.time_created}
FAR [1/yr]: {self.FAR_per_year} 
Detectors: {self.instruments}

Terrestrial : {self.noise:.3f}
BNS: {self.bns:.3f}
NSBH: {self.nsbh:.3f} 
BBH: {self.bbh:.3f} 

Has NS: {self.has_ns:.3f}
Has Remnant: {self.has_remnant:.3f}
Has Mass Gap: {self.has_mass_gap:.3f}

Distance (Mean): {self.dist_mean:.3f} +/- {self.dist_std:.3f} Mpc
Distance modulus: {self.dist_modulus:.3f}

--------------------
Join related channel: #{self.slack_channel} 
<{self.skymap_img_url}|Skymap Link> | <{self.gracedb_url}|Grace DB> | <{self.slack_bot_link}|Github>
            """

        else:

            message = f"""
Alert Type: {self.alert_type}
Superevent ID: {self.superevent_id}
Group: {self.group}

Event Time: {self.event_time} 
Alert Time: {self.time_created}
FAR [1/yr]: {self.FAR_per_year} 
Detectors: {self.instruments}

--------------------
Join related channel: #{self.slack_channel} 
<{self.skymap_img_url}|Skymap Link> | <{self.gracedb_url}|Grace DB> | <{self.slack_bot_link}|Github>
            """

        return message
    
    
if __name__=="__main__":


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

    #stream = Stream(auth=auth)
    stream = Stream(auth=auth, start_at=StartPosition.EARLIEST)

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
                                
                                # This creates a new slack channel for the alert
                                create_new_channel(client, event_channel)

                                # We are assuming #bot-alerts already exists and the bot is added to it
                                send_message_to_channel(client, general_channel, message_text)

                                # This is sending a message sent to the new channel
                                send_message_to_channel(client, event_channel, message_text)

                                # Send message to high quality event channel
                                if alert.passes_GCW_general_cut():
                                    send_message_to_channel(client, cuts_channel, message_text)


                                    
                            # RETRACTION
                            else: 

                                retraction_message = alert.get_GCW_retraction_message()
                                send_message_to_channel(client, event_channel, retraction_message)

                    except KeyError:

                        logging.warning('Bad data formatting...skipping message')

                    except Exception as e:

                        logging.warning('Something went wrong...')   
                        logging.warning(e)                 



