import healpy as hp

class Alerts():

    def __init__(self, instance, ignore_fits = True):

        self.instance = instance

        self.alert_type = instance['alert_type']

        self.superevent_id = instance['superevent_id']
        if self.superevent_id[0] == 'S':
            self.is_real = True
        else:
            self.is_real = False

        self.event_time = instance['event']['time']
        self.alert_time = instance['time_created']

        self.FAR = instance['event']['far']
        self.significant = instance['event']['significant']

        self.detectors = instance['event']['instruments']
        self.num_detectors = len(self.detectors)

        self.bns = instance['event']['classification']['BNS']
        self.nsbh = instance['event']['classification']['NSBH']
        self.bbh = instance['event']['classification']['BBH']

        self.has_ns = instance['event']['properties']['HasNS']
        self.has_remnant = instance['event']['properties']['HasRemnant']
        self.has_mass_gap = instance['event']['properties']['HasMassGap']

        # Disable if the fits file is not going to be used
        if ignore_fits == False:

            binary_data = instance['event']['skymap']
            skymap, skymap_header = hp.read_map(binary_data, h=True, verbose=False)
            
            self.skymap_header = dict(skymap_header)
            self.skymap = skymap

    def passes_GWC_general_cut(self):

        return True