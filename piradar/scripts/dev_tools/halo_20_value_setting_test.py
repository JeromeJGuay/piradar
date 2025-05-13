import logging
import time

from pathlib import Path

from piradar.logger import init_logging

from piradar.navico.navico_controller import (MulticastInterfaces, MulticastAddress,
                                              NavicoRadarController, wake_up_navico_radar, NavicoRadarType)

debug_level = "ERROR"
write_log = False
##################################################

init_logging(stdout_level=debug_level, file_level=debug_level, write=write_log)

### NETWORK ###
interface = "192.168.1.100"

report_address = ('236.6.7.9', 6679)
data_address = ('236.6.7.8', 6678)
send_address = ('236.6.7.10', 6680)

### Write data ###
output_dir = "/home/capteur/Desktop/radar_test/reports"

Path(output_dir).mkdir(parents=True, exist_ok=True)

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

navico_radar.get_reports()
time.sleep(1)

report_sleep = .05
#### value to test

tests_flag= {
    "ranges": 1,
    "bearing": 1,
    "gain": 1,
    "gain_auto": 1,
    "antenna_height": 1,
    "sea_state": 1,
    "rain_clutter": 1,
    "sea_clutter": 1,
    "sea_clutter_auto": 1,
    "rain_clutter_auto": 0,
    "interference_rejection": 1,
    "local_interference_filter": 1,
    "side_lobe_suppression": 1,
    "side_lobe_suppression_auto": 1,
    "mode": 1,
    "target_expansion": 1,
    "target_separation": 1,
    "target_boost": 1,
    "noise_rejection": 1,
    "light": 1,
    "blanking": 1,

}

if tests_flag['ranges']:
    ranges = [50, 100, 1000, 10_000]
    for v in ranges:
        navico_radar.set_range(v)
        time.sleep(report_sleep)
        navico_radar.get_reports()
        time.sleep(report_sleep)
        print("range", v, navico_radar.reports.setting._range)


if tests_flag['bearing']:
    bearing = [0, 90, 180, 270, 360]
    for v in bearing:
        navico_radar.set_bearing(v)
        time.sleep(report_sleep)
        navico_radar.get_reports()
        time.sleep(report_sleep)
        print("bearing", v, navico_radar.reports.spatial.bearing)

if tests_flag['gain']:
    gain = [0, 127, 255]
    for v in gain:
        navico_radar.set_gain(v)
        time.sleep(report_sleep)
        navico_radar.get_reports()
        time.sleep(report_sleep)
        print("gain", v, navico_radar.reports.setting.gain)

if tests_flag['gain_auto']:
    gain_auto = [True, False]
    for v in gain_auto:
        navico_radar.set_gain_auto(v)
        time.sleep(report_sleep)
        navico_radar.get_reports()
        time.sleep(report_sleep)
        print("gain_auto", v, navico_radar.reports.setting.gain_auto)

if tests_flag['antenna_height']:
    antenna_height = [0, 1, 10, 50]
    for v in antenna_height:
        navico_radar.set_antenna_height(v)
        time.sleep(report_sleep)
        navico_radar.get_reports()
        time.sleep(report_sleep)
        print("antenna_height", v, navico_radar.reports.spatial.antenna_height)


if tests_flag['sea_state']:
    sea_state = ['calm', 'moderate', 'rough']
    for v in sea_state:
        navico_radar.set_sea_state(v)
        time.sleep(report_sleep)
        navico_radar.get_reports()
        time.sleep(report_sleep)
        print("sea_state", v, navico_radar.reports.filter.sea_state)


if tests_flag['rain_clutter']:
    rain_clutter = [0, 127, 255]
    for v in rain_clutter:
        navico_radar.set_rain_clutter(v, get_report=True)
        time.sleep(report_sleep)
        print("rain_clutter", v, navico_radar.reports.setting.rain_clutter)

if tests_flag['sea_clutter']:
    sea_clutter = [0, 127, 255]
    for v in sea_clutter:
        navico_radar.set_sea_clutter(v, get_report=True)
        time.sleep(report_sleep)
        print("sea_clutter", v, navico_radar.reports.setting.sea_clutter)

if tests_flag['sea_clutter_auto']:
    sea_clutter_auto = [True, False]
    for v in sea_clutter_auto:
        navico_radar.set_sea_clutter_auto(v, get_report=True)
        time.sleep(report_sleep)
        print("sea_state_auto", v, navico_radar.reports.setting.sea_clutter_auto)

if tests_flag['rain_clutter_auto']:
    rain_clutter_auto = [True, False]
    for v in rain_clutter_auto:
        navico_radar.auto_settings.rain_clutter_auto = v
        navico_radar.set_rain_clutter_auto(v)
        # no report for this ...

if tests_flag['interference_rejection']:
    interference_rejection = ['off', 'low', 'medium', 'high']
    for v in interference_rejection:
        navico_radar.set_interference_rejection(v)
        time.sleep(report_sleep)
        navico_radar.get_reports()
        time.sleep(report_sleep)
        print("interference_rejection", v, navico_radar.reports.setting.interference_rejection)

if tests_flag['local_interference_filter']:
    local_interference_filter = ["off", "low", "medium", "high"]
    for v in local_interference_filter:
        navico_radar.set_local_interference_filter(v)
        time.sleep(report_sleep)
        navico_radar.get_reports()
        time.sleep(report_sleep)
        print("local_interference_filter", v, navico_radar.reports.filter.local_interference_filter)

if tests_flag['side_lobe_suppression']:
    side_lobe_suppression = [0, 127, 255]
    for v in side_lobe_suppression:
        navico_radar.set_side_lobe_suppression(v, get_report=True)
        time.sleep(report_sleep)
        print("side_lobe_suppression", v, navico_radar.reports.filter.side_lobe_suppression)

if tests_flag['side_lobe_suppression_auto']:
    side_lobe_suppression_auto = [True, False]
    for v in side_lobe_suppression_auto:
        navico_radar.set_side_lobe_suppression_auto(v, get_report=True)
        time.sleep(report_sleep)
        print("side_lobe_suppression_auto", v, navico_radar.reports.filter.side_lobe_suppression_auto)

if tests_flag['mode']:
    mode = ["custom", 'harbor', 'offshore', 'weather', 'bird']
    for v in mode:
        navico_radar.set_mode(v, get_report=True)
        time.sleep(report_sleep)
        print("mode", v, navico_radar.reports.setting.mode)

if tests_flag['target_expansion']:
    target_expansion = ["off", "low", "medium", "high"]
    for v in target_expansion:
        navico_radar.set_target_expansion(v, get_report=True)
        time.sleep(report_sleep)
        print("target_expansion", v, navico_radar.reports.setting.target_expansion)

if tests_flag['target_separation']:
    target_separation = ["off", "low", "medium", "high"]
    for v in target_separation:
        navico_radar.set_target_separation(v, get_report=True)
        time.sleep(report_sleep)
        print("target_separation", v, navico_radar.reports.filter.target_separation)

if tests_flag['target_boost']:
    target_boost = ["off", "low", "high"]
    for v in target_boost:
        navico_radar.set_target_boost(v, get_report=True)
        time.sleep(report_sleep)
        print("target_boost", v, navico_radar.reports.setting.target_boost)

if tests_flag['noise_rejection']:
    noise_rejection = ["off", "low", "medium", "high"]
    for v in noise_rejection:
        navico_radar.set_noise_rejection(v, get_report=True)
        time.sleep(report_sleep)
        print("noise_rejection", v, navico_radar.reports.filter.noise_rejection)

if tests_flag['light']:
    light = ["off", "low", "medium", "high"]
    for v in light:
        navico_radar.set_light(v)
        time.sleep(report_sleep)
        navico_radar.get_reports()
        time.sleep(report_sleep)
        print("light", v, navico_radar.reports.spatial.light)


if tests_flag['blanking']:
    blanking_start_stop = ([0, 90], [90, 180], [180, 270], [270, 360])
    for sn, [start, stop] in enumerate(blanking_start_stop):
        navico_radar.set_sector_blanking(
            sector_number=sn,
            start=start,
            stop=stop,
            get_report=True
        )
        sb = navico_radar.sector_blanking_sector_map[sn]
        navico_radar.enable_sector_blanking(sector_number=sn, value=False, get_report=True)
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
