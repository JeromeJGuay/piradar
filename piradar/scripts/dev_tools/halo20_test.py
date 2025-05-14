import logging
import time

from pathlib import Path

from piradar.logger import init_logging

from piradar.navico.navico_controller import (MulticastInterfaces, MulticastAddress,
                                              NavicoRadarController, wake_up_navico_radar, NavicoRadarType)

from piradar.navico.navico_command import *

from piradar.scripts.script_utils import gpio_controller, configure_exit_handling

configure_exit_handling()

debug_level = "DEBUG"
write_log = False
##################################################

init_logging(stdout_level=debug_level, file_level=debug_level, write=write_log)

### NETWORK ###
interface = "192.168.1.100"

report_address = ('236.6.7.9', 6679)
data_address = ('236.6.7.8', 6678)
send_address = ('236.6.7.10', 6680)

### Write data ###
output_dir = "/home/capteur/Desktop/output_data"
# put somewhere else:
from pathlib import Path

Path(output_dir).mkdir(parents=True, exist_ok=True)

### APP ###

mcast_ifaces = MulticastInterfaces(
    report=MulticastAddress(*report_address),
    data=MulticastAddress(*data_address),
    send=MulticastAddress(*send_address),
    interface=interface
)

gpio_controller.radar_power.on()
wake_up_navico_radar()

nr = NavicoRadarController(
    multicast_interfaces=mcast_ifaces,
    report_output_dir=output_dir,
    connect_timeout=60,
)

time.sleep(1)
nr.get_reports()
time.sleep(1)


te = TargetExpansionCmd.pack
tb = TargetBoostCmd.pack
ts = TargetBoostCmd.pack

send = nr.send_pack_data

# nr.get_reports()