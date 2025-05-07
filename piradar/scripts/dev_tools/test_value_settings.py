import logging
import time

from piradar.logger import init_logging

from piradar.navico.navico_controller import (MulticastInterfaces, MulticastAddress,
                                              NavicoRadarController, wake_up_navico_radar, NavicoRadarType)


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

wake_up_navico_radar()

navico_radar = NavicoRadarController(
    multicast_interfaces=mcast_ifaces,
    report_output_dir=output_dir,
    connect_timeout=60,
)

time.sleep(1)
navico_radar.get_reports()
time.sleep(1)


report_sleep = .05
#### value to test

# ranges = [10, 100, 1000, 10_000]
# for v in ranges:
#     navico_radar.set_range(v)
#     time.sleep(report_sleep)
#     navico_radar.get_reports()
#     time.sleep(report_sleep)
#     print("range", v, navico_radar.reports.setting._range)
#
#
# bearing = [0, 90, 180, 270, 360]
# for v in bearing:
#     navico_radar.set_bearing(v)
#     time.sleep(report_sleep)
#     navico_radar.get_reports()
#     time.sleep(report_sleep)
#     print("bearing", v, navico_radar.reports.spatial.bearing)
#
# gain = [0, 127, 255]
# for v in gain:
#     navico_radar.set_gain(v)
#     time.sleep(report_sleep)
#     navico_radar.get_reports()
#     time.sleep(report_sleep)
#     print("gain", v, navico_radar.reports.setting.gain)
#
# gain_auto = [True, False]
# for v in gain_auto:
#     navico_radar.set_gain_auto(v)
#     time.sleep(report_sleep)
#     navico_radar.get_reports()
#     time.sleep(report_sleep)
#     print("gain_auto", v, navico_radar.reports.setting.gain_auto)
#
#
# antenna_height = [0, 1, 10, 50]
# for v in antenna_height:
#     navico_radar.set_antenna_height(v)
#     time.sleep(report_sleep)
#     navico_radar.get_reports()
#     time.sleep(report_sleep)
#     print("antenna_height", v, navico_radar.reports.spatial.antenna_height)


# can only be test while the radar is transmitting.
# scan_speed = ['low', 'medium', 'high']
# for v in scan_speed:
#     navico_radar.set_scan_speed(v)
#     time.sleep(sleep)
#     navico_radar.get_reports()
#     time.sleep(sleep)
#     print("scan_speed", v, navico_radar.reports.filter.scan_speed)

sea_state = ['calm', 'moderate', 'rough']
for v in sea_state:
    navico_radar.set_sea_state(v)
    time.sleep(report_sleep)
    navico_radar.get_reports()
    time.sleep(report_sleep)
    print("sea_state", v, navico_radar.reports.filter.sea_state)


# rain_clutter = [0, 127, 255]
# for v in rain_clutter:
#     navico_radar.set_rain_clutter(v)
#     time.sleep(report_sleep)
#     navico_radar.get_reports()
#     time.sleep(report_sleep)
# # print("rain_clutter", v, navico_radar.reports.setting.rain_clutter)
#
# sea_clutter = [0, 127, 255]
# for v in sea_clutter:
#     navico_radar.set_sea_clutter(v)
#     time.sleep(report_sleep)
#     navico_radar.get_reports()
#     time.sleep(report_sleep)
#     print("sea_clutter", v, navico_radar.reports.setting.sea_clutter)
#
#
# sea_clutter_auto = [True, False]
# for v in sea_clutter_auto:
#     navico_radar.set_sea_clutter_auto(v)
#     time.sleep(report_sleep)
#     navico_radar.get_reports()
#     time.sleep(report_sleep)
#     print("sea_state_auto", v, navico_radar.reports.setting.sea_clutter_auto)
#
#
# rain_clutter_auto = [True, False]
# for v in rain_clutter_auto:
#     navico_radar.auto_settings.rain_clutter_auto = v
#     navico_radar.set_rain_clutter_auto(v)
#     time.sleep(report_sleep)
#     navico_radar.get_reports()
#     time.sleep(report_sleep)
#     print("rain_state_auto", v, navico_radar.reports.setting.sea_clutter_auto)

interference_rejection = ['off', 'low', 'medium', 'high']
for v in interference_rejection:
    navico_radar.set_interference_rejection(v)
    time.sleep(report_sleep)
    navico_radar.get_reports()
    time.sleep(report_sleep)
    print("interference_rejection", v, navico_radar.reports.setting.interference_rejection)


local_interference_filter = ["off", "low", "medium", "high"]
for v in local_interference_filter:
    navico_radar.set_local_interference_filter(v)
    time.sleep(report_sleep)
    navico_radar.get_reports()
    time.sleep(report_sleep)
    print("local_interference_filter", v, navico_radar.reports.filter.local_interference_filter)


side_lobe_suppression = [0, 127, 255]
for v in side_lobe_suppression:
    navico_radar.set_side_lobe_suppression(v)
    time.sleep(report_sleep)
    navico_radar.get_reports()
    time.sleep(report_sleep)
    print("side_lobe_suppression", v, navico_radar.reports.filter.side_lobe_suppression)


side_lobe_suppression_auto = [True, False]
for v in side_lobe_suppression_auto:
    navico_radar.set_side_lobe_suppression_auto(v)
    time.sleep(report_sleep)
    navico_radar.get_reports()
    time.sleep(report_sleep)
    print("side_lobe_suppression_auto", v, navico_radar.reports.filter.side_lobe_suppression_auto)

if navico_radar.reports.system.radar_type == NavicoRadarType.navicoHALO:
    print("unsure if this should work at all.")
    mode = ["custom", 'harbor', 'offshore', 'weather', 'bird']
    for v in mode:
        navico_radar.set_mode(v, get_report=True)
        time.sleep(report_sleep)
        print("mode", v, navico_radar.reports.setting.mode)


print("Unsure about this one.")
if navico_radar.reports.system.radar_type == NavicoRadarType.navico4G:
    target_expansion = [True, False]
    for v in target_expansion:
        navico_radar.set_target_expansion(v, get_report=True)
        time.sleep(report_sleep)
        print("target_expansion", v, navico_radar.reports.setting.target_expansion)

elif navico_radar.reports.system.radar_type == NavicoRadarType.navicoHALO:
    target_expansion = ["off", "low", "medium", "high"]
    for v in target_expansion:
        navico_radar.set_target_expansion(v, get_report=True)
        time.sleep(report_sleep)
        print("target_expansion", v, navico_radar.reports.setting.target_expansion)


target_separation = ["off", "low", "high"]
for v in target_separation:
    navico_radar.set_target_separation(v, get_report=True)
    time.sleep(report_sleep)
    print("target_separation", v, navico_radar.reports.filter.target_separation)


target_boost = ["off", "low", "high"]
for v in target_boost:
    navico_radar.set_target_boost(v, get_report=True)
    time.sleep(report_sleep)
    print("target_boost", v, navico_radar.reports.setting.target_boost)


noise_rejection = ["off", "low", "medium", "high"]
for v in noise_rejection:
    navico_radar.set_noise_rejection(v, get_report=True)
    time.sleep(report_sleep)
    print("noise_rejection", v, navico_radar.reports.filter.noise_rejection)


if navico_radar.reports.system.radar_type == NavicoRadarType.navicoHALO:
    light = ["off", "low", "medium", "high"]
    for v in light:
        navico_radar.set_light(v)
        time.sleep(report_sleep)
        navico_radar.get_reports()
        time.sleep(report_sleep)
        print("light", v, navico_radar.reports.spatial.light)

    #sea_clutter_nudge = [-100,0,100]
    #for v in sea_clutter_nudge:
    #    navico_radar.auto_settings.sea_clutter_auto = True
    #    navico_radar.sea_clutter_nudge(v)
    #    time.sleep(report_sleep)
    #    navico_radar.get_reports()
    #    time.sleep(report_sleep)
    #    print("Sea clutter 08c4 [auto]", v, navico_radar.reports.filter.sea_clutter_08c4)
    #    print("Sea clutter nudge [auto]", v, navico_radar.reports.filter.sea_clutter_nudge)


    # sea_clutter_nudge = [-100,0,100]
    # for v in sea_clutter_nudge:
    #     navico_radar.auto_settings.sea_clutter_auto = False
    #     navico_radar.sea_clutter_nudge(v)
    #     time.sleep(report_sleep)
    #     navico_radar.get_reports()
    #     time.sleep(report_sleep)
    #     print("Sea clutter 08c4 [manual]", v, navico_radar.reports.filter.sea_clutter_08c4)
    #     print("Sea clutter nudge [manual]", v, navico_radar.reports.filter.sea_clutter_nudge)


    blanking_start_stop = ([0, 90], [90, 180], [180, 270], [270, 360])
    for sn, [start, stop] in enumerate(blanking_start_stop):
        navico_radar.set_sector_blanking(
            sector_number=sn,
            start=start,
            stop=stop,
            get_report=True
        )
        sb = {
            0: navico_radar.reports.blanking.sector_0,
            1: navico_radar.reports.blanking.sector_1,
            2: navico_radar.reports.blanking.sector_2,
            3: navico_radar.reports.blanking.sector_3,
        }[sn]
        print(f"Sector {sn}")
        print("   enable", False, sb.enable)
        print("   start", start, sb.start)
        print("   stop", stop, sb.stop)
        navico_radar.enable_sector_blanking(sector_number=sn, value=True, get_report=True)
        print(f"Sector {sn}")
        print("   enable", True, sb.enable)
        print("   start", start, sb.start)
        print("   stop", stop, sb.stop)


navico_radar.disconnect()
