import logging
import time

from pathlib import Path
import psutil

import schedule

from piradar.logger import init_logging
#from piradar.raspberry_utils import RaspIoSwitch

from piradar.navico.navico_controller import (MulticastInterfaces, MulticastAddress, NavicoRadarController)
from piradar.scripts.script_utils import set_user_radar_settings, valide_radar_settings, start_transmit, set_scan_speed, \
    RadarUserSettings

### APP ###
debug_level = "INFO"
write_log = False
init_logging(stdout_level=debug_level, file_level=debug_level, write=write_log)

### Raspb ###
RADAR_POWER_PIN = 21

#logging.error(traceback.format_exc(), exc_info=True) ## for critical error

RECORD_INTERVAL = 60
WAKE_UP_ADVANCE = 20
TRANSMIT_ADVANCE = 5

SECTOR_RECORD_COUNT = 4

## Radar Setting ##
radar_user_settings = RadarUserSettings(
    _range=12,
    antenna_height=10,

    bearing=0,

    gain=50,
    gain_auto=False,

    sea_clutter=0,
    sea_clutter_auto=False,

    rain_clutter=0,
    rain_clutter_auto=False,

    side_lobe_suppression=0,
    side_lobe_suppression_auto=False,

    sea_state='calm',
    noise_rejection='off',

    interference_rejection='off',
    local_interference_filter='off',

    target_expansion='off',
    target_separation='off',
    target_boost='off',
)

### NETWORK ###
INTERFACE_NAME = "eth0"
INTERFACE = "192.168.1.228"

REPORT_ADDRESS = ('236.6.7.9', 6679)
DATA_ADDRESS = ('236.6.7.8', 6678)
SEND_ADDRESS = ('236.6.7.10', 6680)

### Write data ###
DRIVE_PATH = "/media/capteur/2To"
OUTPUT_DIR = "/data"
# put somewhere else:


# scanspeed is not in user config
scan_speed = "low"

###################################################
#         SCRIPT BELOW | SETTINGS ABOVE           #
###################################################



#radar_power_switch = RaspIoSwitch(pin=RADAR_POWER_PIN)




if __name__ == "__main__":

    # MAKE SURE THE DRIVE IS MOUNTED
    while not Path(DRIVE_PATH).is_dir():
        time.sleep(0.1)
    logging.info(f"{DRIVE_PATH} directory found.")

    output_dir = Path(DRIVE_PATH).joinpath(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    # MAKE SURE THE INTERFACE IS UP
    while not INTERFACE_NAME not in psutil.net_if_addrs():
        time.sleep(0.1)
    logging.info(f"{INTERFACE_NAME} interface found.")

    mcast_ifaces = MulticastInterfaces(
        report=MulticastAddress(*REPORT_ADDRESS),
        data=MulticastAddress(*DATA_ADDRESS),
        send=MulticastAddress(*SEND_ADDRESS),
        interface=psutil.net_if_addrs()[INTERFACE_NAME]
    )

    # radar_power_switch.on()

    # wake_up_navico_radar()  # this might be unnecessary
    rc = NavicoRadarController(
        multicast_interfaces=mcast_ifaces,
        output_dir=output_dir,
    )

    logging.info(f"Radar type received: {rc.reports.system.radar_type}")

    set_user_radar_settings(radar_user_settings, rc)
    valide_radar_settings(radar_user_settings, rc)

    set_scan_speed(rc, scan_speed=scan_speed)

    if start_transmit(rc) is True:

        rc.start_recording_data(number_of_sector_to_record=SECTOR_RECORD_COUNT)
        # add a watch dog here
        while rc._data_recording_is_started:
            time.sleep(1)

        # rc.stop_recording_data()

        rc.disconnect()