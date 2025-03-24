import logging
import time

from piradar.logger import init_logging

from piradar.navico.navico_controller import (MulticastInterfaces, MulticastAddress, NavicoUserConfig,
                                              NavicoRadarController, wake_up_navico_radar)

### UNPACK FORM A CONFIG FILE JSON would be nice###
# interface = "192.168.1.243"

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


_range = 5 # add a check in NavicoController or RadarSetting
bearing = 0
gain = 255 / 2
antenna_height = 10
scan_speed = "low"
mode = "harbor"
sea_state = "harbour"
##... more to add ###

### APP ###

debug_level = "DEBUG"
write_log = False
##################################################


init_logging(stdout_level=debug_level, file_level=debug_level, write=write_log)
#logging.error(traceback.format_exc(), exc_info=True) ## for critical error

mcast_ifaces = MulticastInterfaces(
    report=MulticastAddress(*report_address),
    data=MulticastAddress(*data_address),
    send=MulticastAddress(*send_address),
    interface=interface
)


radar_parameters = NavicoUserConfig(
    _range=_range,
    bearing=bearing,
    gain=gain,
    antenna_height=antenna_height,
    scan_speed=scan_speed,
    mode=mode,
    sea_state=sea_state,
)

wake_up_navico_radar()

navico_radar = NavicoRadarController(
    multicast_interfaces=mcast_ifaces,
    radar_user_config=radar_parameters,
    output_dir=output_dir,
)

time.sleep(1)
navico_radar.get_reports()
while navico_radar.reports.system.radar_type is None:
    time.sleep(.5)

logging.info(f"Radar type received: {navico_radar.reports.system.radar_type}")

navico_radar.transmit()
time.sleep(5) # acquire for X seconds
navico_radar.standby()
navico_radar.close_all()



