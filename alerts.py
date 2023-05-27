import healpy as hp
import matplotlib.pyplot as plt

class Alert():

    def __init__(self, instance, ignore_skymap = True):

        # Parsing the incoming Kafka notice
        self.parse_instance(instance, ignore_skymap)

        # Events starting with S are real and MS are fake/test.
        if self.superevent_id[0] == 'S':
            self.is_real = True
        else:
            self.is_real = False

    def parse_instance(self, instance, ignore_skymap):

        # Parsed according to the schema here: 
        # https://emfollow.docs.ligo.org/userguide/content.html#kafka-notice-gcn-scimma
        self.instance = instance

        self.alert_type = instance['alert_type']
        self.superevent_id = instance['superevent_id']
        self.time_created = instance['time_created']
        self.gracedb_url = instance['urls']['gracedb']

        self.slack_channel = self.superevent_id.lower()
        self.skymap_img_url = f"https://gracedb.ligo.org/apiweb/superevents/{self.superevent_id}/files/bayestar.png"

        if self.alert_type != "RETRACTION":

            self.is_retraction = False

            self.event_time = instance['event']['time']
            self.FAR = instance['event']['far']
            self.significant = instance['event']['significant']
            self.instruments = instance['event']['instruments']
            self.num_instruments = len(self.instruments)
            self.search = instance['event']['search']
            self.group = instance['event']['group']

            if self.group  == "CBC":

                self.pipeline = instance['event']['pipeline']

                # Only available for Burst
                self.duration = None
                self.central_frequency = None

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

                # Only available for Burst
                self.duration = instance['event']['duration']
                self.central_frequency = instance['event']['central_frequency']

                # Only available for CBC
                self.has_ns = None
                self.has_remnant = None
                self.has_mass_gap = None

                # Only available for CBC
                self.bns = None
                self.nsbh = None
                self.bbh = None
                self.noise = None

            # Enable if the fits file is not going to be used
            if ignore_skymap == False:

                binary_data = instance['event']['skymap']
                skymap, skymap_header = hp.read_map(binary_data, h=True, verbose=False)
                
                self.skymap_header = dict(skymap_header)
                self.skymap = skymap
        else: 
            self.is_retraction = True

        # TODO: Parse the external_coinc data...

    def passes_GCW_general_cut(self):
        """
        Cuts made before sending incoming alerts to the Gravity collective's alert bot slack channel.

        Returns:
            bool: True if the alert passes the cut, false otherwise,
        """

        if self.num_instruments >= 2 and self.group == "CBC" and (self.nsbh > 0 or self.bns > 0):
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

        message_text = f"""
Alert Type: {self.alert_type}
Superevent ID: {self.superevent_id}
Event Time: {self.event_time} 
Alert Time: {self.time_created}
FAR: {self.FAR} 
Detectors: {self.instruments} 
BNS: {self.bns:.3f}
NSBH: {self.nsbh:.3f} 
BBH: {self.bbh:.3f} 
Has NS: {self.has_ns:.3f}
Has Remnant: {self.has_remnant:.3f}
Has Mass Gap: {self.has_mass_gap:.3f}
Join related channel: #{self.slack_channel} 
Skymap image: {self.skymap_img_url}
        """
        return message_text
    
    
if __name__=="__main__":

    from slack_token import SLACK_TOKEN, hop_username, hop_pw
    from hop import stream, Stream
    from hop.io import StartPosition
    from hop.auth import Auth

    # You might have to authorize here
    ## auth = Auth(hop_username, hop_pw)
    stream = Stream()

    with stream.open("kafka://kafka.scimma.org/igwn.gwalert", "r") as s:

        for message in s:
            
            # Schema for data available at https://emfollow.docs.ligo.org/userguide/content.html#kafka-notice-gcn-scimma
            data = message.content

            # Data is a list that can (potentially) have more than 1 element? This is inconsistent with the alert schema
            for instance in data:
                
                temp = Alert(instance, ignore_skymap=True)
                print(temp.instance)
                # print(temp.skymap_header)
                # hp.mollview(temp.skymap)
                # plt.show()


