import logging
import time
from pathlib import Path

from piradar.logger import init_logging
from piradar.raspberry_utils import RaspIoSwitch

from piradar.navico.navico_controller import (MulticastInterfaces, MulticastAddress,
                                              NavicoRadarController, wake_up_navico_radar)

### APP ###
debug_level = "INFO"
write_log = False
init_logging(stdout_level=debug_level, file_level=debug_level, write=write_log)

### Raspb ###
RADAR_POWER_PIN = 21

#logging.error(traceback.format_exc(), exc_info=True) ## for critical error


### UNPACK FORM A CONFIG FILE JSON would be nice###
# interface = "192.168.1.243"

SCAN_INTERVAL = 60

SCAN_DURATION = 10

## Radar Setting ##
_range = 12
antenna_height = 10

bearing = 0

gain = 50
gain_auto = False

sea_clutter = 0
sea_clutter_auto = False

rain_clutter = 0
rain_clutter_auto = False

side_lobe_suppression = 0
side_lobe_suppression_auto = False

sea_state = 'calm'  # filter

noise_rejection = 'off'

interference_rejection = 'off'
local_interference_filter = 'off'

#mode = None,
target_expansion = None,
target_separation = None,
target_boost = None,



### NETWORK ###
INTERFACE = "192.168.1.228"

REPORT_ADDRESS = ('236.6.7.9', 6679)
DATA_ADDRESS = ('236.6.7.8', 6678)
SEND_ADDRESS = ('236.6.7.10', 6680)

### Write data ###
OUTPUT_DIR = "/home/capteur/Desktop/output_data"
# put somewhere else:


Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

### Radar Settings ###

radar_power_switch = RaspIoSwitch(pin=RADAR_POWER_PIN)


#doppler_mode = None
#doppler_speed = None


##... more to add ###

# scanspeed is not in user config
scan_speed = "low"
##################################################

mcast_ifaces = MulticastInterfaces(
    report=MulticastAddress(*REPORT_ADDRESS),
    data=MulticastAddress(*DATA_ADDRESS),
    send=MulticastAddress(*SEND_ADDRESS),
    interface=INTERFACE
)

for _ in range(10):

    radar_power_switch.on()

    # wake_up_navico_radar()  # this might be unnecessary
    rc = NavicoRadarController(
        multicast_interfaces=mcast_ifaces,
        output_dir=OUTPUT_DIR,
    )

    rc.get_reports()
    while rc.reports.system.radar_type is None:
        time.sleep(.1)
        rc.get_reports()
        logging.info(f"Radar type received: {rc.reports.system.radar_type}")

    # todo check all setting.

    rc.transmit()

    #tries for 1 seconds
    for _ in range(10):
        if rc.reports.filter.scan_speed != scan_speed:
            rc.set_scan_speed = rc.set_scan_speed(scan_speed)
            time.sleep(0.1)

    if rc.reports.filter.scan_speed != scan_speed:
        logging.warning(f"Unable to change scan speed to {scan_speed} from {rc.reports.filter.scan_speed}")

    t0 = time.time()
    rc.start_recording_data()
    while time.time() - t0 < SCAN_DURATION:  #
        time.sleep(1)
    rc.stop_recording_data()

    rc.disconnect()

    del rc

    radar_power_switch.off()

    time.sleep(SCAN_INTERVAL)
