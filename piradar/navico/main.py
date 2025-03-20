from .navico_controller import MulticastInterfaces, MulticastAddress, RadarSettings, NavicoRadarController

### UNPACK FORM A CONFIG FILE JSON would be nice###
# interface = "192.168.1.243"

### NETWORK ###
interface = "192.168.1.228"

report_address = ('236.6.7.9', 6679)
data_address = ('236.6.7.8', 6678)
send_address = ('236.6.7.10', 6680)

### Write data ###
output_dir = "~/Desktop/raw_data/output_data"


### Radar Settings ###


_range = 1e3,
bearing = 0,
gain = 255 / 2,
antenna_height = 10,
scan_speed = "low"
##... more to add ###

##################################################


addrset = MulticastInterfaces(
    report=MulticastAddress(report_address),
    data=MulticastAddress(data_address),
    send=MulticastAddress(send_address),
    interface=interface
)


radar_parameters = RadarSettings(
    _range=_range,
    bearing=bearing,
    gain=gain,
    antenna_height=antenna_height,
    scan_speed=scan_speed
)

navico_radar = NavicoRadarController(
    address_set=addrset,
    init_radar_parameters=radar_parameters,
    output_dir=output_dir,
)

if __name__ == '__main__':
    import time

    navico_radar.transmit()
    time.sleep(5) # acquire for X seconds
    navico_radar.standby()
    navico_radar.close_all()



