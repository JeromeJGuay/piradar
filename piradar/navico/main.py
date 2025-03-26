import logging
import time
import lgpio

from piradar.logger import init_logging

from piradar.navico.navico_controller import (MulticastInterfaces, MulticastAddress, NavicoUserConfig,
                                              NavicoRadarController, wake_up_navico_radar)

### APP ###

debug_level = "INFO"
write_log = False
init_logging(stdout_level=debug_level, file_level=debug_level, write=write_log)

#logging.error(traceback.format_exc(), exc_info=True) ## for critical error


### UNPACK FORM A CONFIG FILE JSON would be nice###
# interface = "192.168.1.243"

GPIO_RADAR_PIN = 21
GPIO_CLAIM = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(GPIO_CLAIM, GPIO_RADAR_PIN)

def power_on_radar():
    lgpio.gpio_write(GPIO_CLAIM, GPIO_RADAR_PIN, 1)

def power_off_radar():
    lgpio.gpio_write(GPIO_CLAIM, GPIO_RADAR_PIN, 0)


SCAN_INTERVAL = 60


### NETWORK ###
interface = "192.168.1.228"

report_address = ('236.6.7.9', 6679)
data_address = ('236.6.7.8', 6678)
send_address = ('236.6.7.10', 6680)

### Write data ###
output_dir = "/home/capteur/Desktop/output_data"
# put somewhere else:
from pathlib import Path

Path(output_dir).mkdir(parents=True, exist_ok=True)

### Radar Settings ###
RANGES_VALS_LIST = [50, 75, 100, 250, 500, 750, 1000,
                    1500, 2000, 4000, 6000, 8000,
                    12000, 15000, 24000]

use_config = NavicoUserConfig(
    _range=12,  # 12_000
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

    sea_state='calm',  # filter

    noise_rejection='off',

    interference_rejection='off',
    local_interference_filter='off',

    #mode = None,
    target_expansion=None,
    target_separation=None,
    target_boost=None,

    #doppler_mode = None
    #doppler_speed = None
)

##... more to add ###

# scanspeed is not in user config
scan_speed = "low"
##################################################

mcast_ifaces = MulticastInterfaces(
    report=MulticastAddress(*report_address),
    data=MulticastAddress(*data_address),
    send=MulticastAddress(*send_address),
    interface=interface
)


for _ in range(10):

    power_on_radar()

    # wake_up_navico_radar()  # this might be unnecessary

    navico_radar = NavicoRadarController(
        multicast_interfaces=mcast_ifaces,
        radar_user_config=use_config,
        output_dir=output_dir,
    )

    navico_radar.get_reports()
    while navico_radar.reports.system.radar_type is None:
        time.sleep(.1)
        navico_radar.get_reports()
        logging.info(f"Radar type received: {navico_radar.reports.system.radar_type}")

    # todo check all setting.

    navico_radar.transmit()

    #tries for 1 seconds
    for _ in range(10):
        if navico_radar.reports.filter.scan_speed != scan_speed:
            navico_radar.commands('scan_speed', scan_speed)
            time.sleep(0.1)

    if navico_radar.reports.filter.scan_speed != scan_speed:
        logging.warning(f"Unable to change scan speed to {scan_speed} from {navico_radar.reports.filter.scan_speed}")


    t0 = time.time()
    navico_radar.start_recording_data()
    while time.time() - t0 < 4: #
        time.sleep(1)
    navico_radar.stop_recording_data()

    navico_radar.close_all()

    del navico_radar

    power_off_radar()

    time.sleep(SCAN_INTERVAL)





