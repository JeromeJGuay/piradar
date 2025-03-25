import logging
import time

from piradar.logger import init_logging

from piradar.navico.navico_controller import (MulticastInterfaces, MulticastAddress, NavicoUserConfig,
                                              NavicoRadarController, wake_up_navico_radar)

RANGES_VALS_LIST = [50, 75, 100, 250, 500, 750, 1000,
                    1500, 2000, 4000, 6000, 8000,
                    12000, 15000, 24000]

OLMH_VAL2STR_MAP = {0: "off", 1: "low", 2: "medium", 3: "high"}
OLMH_STR2VAL_MAP = {"off": 0, "low": 1, "medium": 2, "high": 3}

OLH_VAL2STR_MAP = {0: "off", 1: "low", 2: "high"}
OLH_STR2VAL_MAP = {"off": 0, "low": 1, "high": 2}

RADAR_STATUS_VAL2STR_MAP = {1: "standby", 2: "transmit", 5: "spinning-up"}
RADAR_STATUS_STR2VAL_MAP = {}

MODE_VAL2STR_MAP = {0: "custom", 1: "harbor", 2: "offshore", 4: "weather", 5: "bird", 255: "unknown"}
MODE_STR2VAL_MAP = {"custom": 0, "harbor": 1, "offshore": 2, "weather": 4, "bird": 5}

SEA_STATE_VAL2STR_MAP = {0: "calm", 1: "moderate", 2: "rough"}
SEA_STATE_STR2VAL_MAP = {"calm": 0, "moderate": 1, "rough": 2}
# I dont get the difference between SEA_STATE and SEA_AUTO FIXME
SEA_AUTO_VAL2STR_MAP = {0: "off", 1: "harbor", 2: "offshore"}
SEA_AUTO_STR2VAL_MAP = {"off": 0, "harbor": 1, "offshore": 2}

DOPPLER_MODE_VAL2STR_MAP = {0: "off", 1: "normal", 2: "approaching_only"}
DOPPLER_MODE_STR2VAL_MAP = {"off": 0, "normal": 1, "approaching_only": 2}

SCAN_SPEED_VAL2STR_MAP = {0: "low", 1: "medium", 2: "high"}
SCAN_SPEED_STR2VAL_MAP = {"low": 0, "medium": 1, "high": 2}


class RadarParameterValues:
    def __init__(self):
        _range = None

        bearing = None

        gain = None
        gain_auto = None
        sea_clutter = None
        sea_clutter_auto = None
        rain_clutter = None
        rain_clutter_auto = None
        side_lobe_suppression = None
        side_lobe_suppression_auto = None

        interference_rejection = None
        target_boost = None
        sea_state = None  #filter
        auto_sea_state = None  # setting #boolean ?
        local_interference_filter = None
        scan_speed = None
        mode = None
        target_expansion = None
        noise_rejection = None
        target_separation = None
        doppler_mode = None
        light = None

        sea_clutter_filter = None
        sea_clutter_nudge = None

        doppler_speed = None
        antenna_height = None


def get_radar_values(radar: NavicoRadarController) -> RadarParameterValues:
    rpv = RadarParameterValues()

    rpv._range = radar.reports.setting._range
    rpv.bearing = radar.reports.spatial.bearing

    rpv.gain = radar.reports.setting.gain
    rpv.gain_auto = radar.reports.setting.gain_auto
    rpv.sea_clutter = radar.reports.setting.sea_clutter_08c4
    rpv.sea_clutter_auto = radar.reports.setting.sea_state_auto  # I think it might be it #unsure
    rpv.rain_clutter = radar.reports.setting.rain_clutter
    rpv.rain_clutter_auto = radar.reports.setting.sea_state_auto
    rpv.side_lobe_suppression = radar.reports.filter.side_lobe_suppression
    rpv.side_lobe_suppression_auto = radar.reports.filter.side_lobe_suppression_auto

    rpv.interference_rejection = radar.reports.setting.interference_rejection
    rpv.target_boost = radar.reports.setting.target_boost
    rpv.sea_state = radar.reports.filter.sea_state
    rpv.auto_sea_state = radar.reports.setting.sea_state_auto
    rpv.local_interference_filter = radar.reports.filter.local_interference_filter
    rpv.scan_speed = radar.reports.filter.scan_speed
    rpv.mode = radar.reports.setting.mode
    rpv.target_expansion = radar.reports.setting.target_expansion
    rpv.noise_rejection = radar.reports.filter.noise_rejection
    rpv.target_separation = radar.reports.filter.target_separation
    rpv.doppler_mode = radar.reports.filter.doppler_mode
    rpv.light = radar.reports.spatial.light

    rpv.sea_clutter_08c4 = radar.reports.filter.sea_clutter_08c4
    rpv.sea_clutter_nudge = radar.reports.filter.sea_clutter_nudge

    rpv.doppler_speed = radar.reports.filter.doppler_speed
    rpv.antenna_height = radar.reports.spatial.antenna_height


debug_level = "DEBUG"
write_log = False
##################################################

init_logging(stdout_level=debug_level, file_level=debug_level, write=write_log)

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

### APP ###

#logging.error(traceback.format_exc(), exc_info=True) ## for critical error

mcast_ifaces = MulticastInterfaces(
    report=MulticastAddress(*report_address),
    data=MulticastAddress(*data_address),
    send=MulticastAddress(*send_address),
    interface=interface
)

wake_up_navico_radar()

navico_radar = NavicoRadarController(
    multicast_interfaces=mcast_ifaces,
    radar_user_config=NavicoUserConfig(),
    output_dir=output_dir,
)

time.sleep(1)
navico_radar.get_reports()
time.sleep(1)

initial_values = get_radar_values(navico_radar)


#### value to test
sleep = .5
ranges = [0, 2, 4]
for v in ranges:
    navico_radar.commands('range', v)
    time.sleep(sleep)
    navico_radar.get_reports()
    time.sleep(sleep)
    print("range", v, navico_radar.reports.setting._range)


bearing = [0, 90, 180, 270, 360]
for v in bearing:
    navico_radar.commands('bearing', v)
    time.sleep(sleep)
    navico_radar.get_reports()
    time.sleep(sleep)
    print("bearing", v, navico_radar.reports.spatial.bearing)

gain = [0, 50, 100]
for v in gain:
    navico_radar.commands('gain', v)
    time.sleep(sleep)
    navico_radar.get_reports()
    time.sleep(sleep)
    print("gain", v, navico_radar.reports.setting.gain)

gain_auto = [True, False]
for v in gain_auto:
    navico_radar.radar_user_config.gain_auto = v
    navico_radar.commands('range', 10)
    time.sleep(sleep)
    navico_radar.get_reports()
    time.sleep(sleep)
    print("gain_auto", v, navico_radar.reports.setting.gain_auto)


antenna_height = [0, 1, 10, 50]
for v in antenna_height:
    navico_radar.commands('antenna_height', v)
    time.sleep(sleep)
    navico_radar.get_reports()
    time.sleep(sleep)
    print("antenna_height", v, navico_radar.reports.spatial.antenna_height)


scan_speed = ['low', 'medium', 'high']
for v in scan_speed:
    navico_radar.commands('scan_speed', v)
    time.sleep(sleep)
    navico_radar.get_reports()
    time.sleep(sleep)
    print("scan_speed", v, navico_radar.reports.filter.scan_speed)

sea_state = ['calm', 'moderate', 'rough']
for v in sea_state:
    navico_radar.commands('sea_state', v)
    time.sleep(sleep)
    navico_radar.get_reports()
    time.sleep(sleep)
    print("sea_state", v, navico_radar.reports.filter.sea_state)


rain_clutter = [0, 50, 100]
for v in rain_clutter:
    navico_radar.commands('rain_clutter', v)
    time.sleep(sleep)
    navico_radar.get_reports()
    time.sleep(sleep)
    print("rain_clutter", v, navico_radar.reports.setting.rain_clutter)

sea_clutter = [0, 50, 100]
for v in sea_clutter:
    navico_radar.commands('sea_clutter', v)
    time.sleep(sleep)
    navico_radar.get_reports()
    time.sleep(sleep)
    print("sea_clutter", v, navico_radar.reports.setting.sea_clutter)


sea_clutter_auto = [True, False]
for v in sea_clutter_auto:
    navico_radar.radar_user_config.sea_clutter_auto = v
    navico_radar.commands('sea_clutter', 10)
    time.sleep(sleep)
    navico_radar.get_reports()
    time.sleep(sleep)
    print("sea_state_auto", v, navico_radar.reports.setting.sea_state_auto)


rain_clutter_auto = [True, False]
for v in rain_clutter_auto:
    navico_radar.radar_user_config.rain_clutter_auto = v
    navico_radar.commands('rain_clutter', 10)
    time.sleep(sleep)
    navico_radar.get_reports()
    time.sleep(sleep)
    print("rain_state_auto", v, navico_radar.reports.setting.sea_state_auto)

interference_rejection = ['low', 'medium', 'high']
for v in interference_rejection:
    navico_radar.commands('interference_rejection', v)
    time.sleep(sleep)
    navico_radar.get_reports()
    time.sleep(sleep)
    print("interference_rejection", v, navico_radar.reports.setting.interference_rejection)


local_interference_filter = ["off", "low", "medium", "high"]
for v in local_interference_filter:
    navico_radar.commands('local_interference_filter', v)
    time.sleep(sleep)
    navico_radar.get_reports()
    time.sleep(sleep)
    print("local_interference_filter", v, navico_radar.reports.filter.local_interference_filter)


side_lobe_suppression = [0, 50, 100]
for v in side_lobe_suppression:
    navico_radar.commands('side_lobe_suppression', v)
    time.sleep(sleep)
    navico_radar.get_reports()
    time.sleep(sleep)
    print("side_lobe_suppression", v, navico_radar.reports.filter.side_lobe_suppression)


side_lobe_suppression_auto = [True, False]
for v in rain_clutter_auto:
    navico_radar.radar_user_config.side_lobe_suppression_auto = v
    navico_radar.commands('side_lobe_suppression_auto', 10)
    time.sleep(sleep)
    navico_radar.get_reports()
    time.sleep(sleep)
    print("side_lobe_suppression_auto", v, navico_radar.reports.setting.side_lobe_suppression_auto)


mode = ["custom", 'harbor', 'offshore', 'weather', 'bird']
for v in mode:
    navico_radar.commands('mode', v)
    time.sleep(sleep)
    navico_radar.get_reports()
    time.sleep(sleep)
    print("mode", v, navico_radar.reports.setting.mode)


target_expansion = ["off", "low", "medium", "high"]
for v in target_expansion:
    navico_radar.commands('target_expansion', v)
    time.sleep(sleep)
    navico_radar.get_reports()
    time.sleep(sleep)
    print("target_expansion", v, navico_radar.reports.setting.target_expansion)


target_separation =["off", "low", "medium", "high"]
for v in target_separation:
    navico_radar.commands('target_separation', v)
    time.sleep(sleep)
    navico_radar.get_reports()
    time.sleep(sleep)
    print("target_separation", v, navico_radar.reports.filter.target_separation)


target_boost = ["off", "low", "high"]
for v in target_boost:
    navico_radar.commands('target_boost', v)
    time.sleep(sleep)
    navico_radar.get_reports()
    time.sleep(sleep)
    print("target_boost", v, navico_radar.reports.setting.target_boost)


noise_rejection = ["off", "low", "medium", "high"]
for v in noise_rejection:
    navico_radar.commands('noise_rejection', v)
    time.sleep(sleep)
    navico_radar.get_reports()
    time.sleep(sleep)
    print("noise_rejection", v, navico_radar.reports.filter.noise_rejection)


doppler_mode = ['off', 'normal', 'approaching_only']
for v in doppler_mode:
    navico_radar.commands('doppler_mode', v)
    time.sleep(sleep)
    navico_radar.get_reports()
    time.sleep(sleep)
    print("doppler_mode", v, navico_radar.reports.filter.doppler_mode)


doppler_speed = [0, 5, 10]
for v in doppler_speed:
    navico_radar.commands('doppler_speed', v)
    time.sleep(sleep)
    navico_radar.get_reports()
    time.sleep(sleep)
    print("doppler_speed", v, navico_radar.reports.filter.doppler_speed)


light = ["off", "low", "medium", "high"]
for v in light:
    navico_radar.commands('light', v)
    time.sleep(sleep)
    navico_radar.get_reports()
    time.sleep(sleep)
    print("light", v, navico_radar.reports.spatial.light)





navico_radar.close_all()
