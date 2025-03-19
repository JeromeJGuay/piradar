from .navico_radar import AddressSet, RadarParameters, NavicoRadar
from .navico_structure import IPAddress
from ..network import get_local_addresses


import time


interface = "192.168.1.243"
# interface = "192.168.1.228"

# addrset = rlocator.groupB
output_file = ""
raw_output_file = ""


# rlocator = RadarLocator(interface=interface)
# rlocator.locate()

addrset = AddressSet(
    data=IPAddress(('236.6.7.8', 6678)),
    send=IPAddress(('236.6.7.10', 6680)),
    report=IPAddress(('236.6.7.9', 6679)),
    interface=interface
)


radar_parameters = RadarParameters(
    range=1e3,
    bearing=0,
    gain=255 / 2,
    antenna_height=10,
    scan_speed="low"
)

nr = NavicoRadar(
    address_set=addrset,
    init_radar_parameters=radar_parameters,
    output_file=output_file,
    raw_output_file=raw_output_file,
)

nr.transmit()
time.sleep(2)
nr.standby()
nr.close_all()


