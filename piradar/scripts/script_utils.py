import logging
import time
from pathlib import Path
from dataclasses import dataclass

from piradar.navico.navico_controller import NavicoRadarController, RadarStatus, RANGES_PRESETS

from piradar.network import check_interface_inet_is_up


def validate_interface(interface):
    attempt = 10
    for _ in range(attempt):
        if check_interface_inet_is_up(interface):
            return True
    return False


def validate_output_drive(output_drive):
    attempt = 10
    for _ in range(attempt):
        if Path(output_drive).is_dir():
            return True
    return False


@dataclass#(kw_only=True)
class RadarUserSettings:
    _range: int | str
    antenna_height: float

    bearing: float

    gain: int
    gain_auto: bool

    sea_clutter: int
    sea_clutter_auto: bool

    rain_clutter: int
    rain_clutter_auto: bool

    side_lobe_suppression: int
    side_lobe_suppression_auto: bool
    # add mode
    sea_state: str

    noise_rejection: str

    interference_rejection: str
    local_interference_filter: str

    #mode = None,
    target_expansion: str
    target_separation: str
    target_boost: str

    # doppler_speed = 0
    # doppler_mode = "off"

    # add light fixme
    # add nudge fixme


def set_user_radar_settings(settings: RadarUserSettings, radar_controller: NavicoRadarController):
    #    add mode
    #    radar_controller.set_doppler_speed(settings.doppler_speed)
    #    radar_controller.set_doppler_mode(settings.doppler_mode)

    #    radar_controller.set_doppler_mode(settings.doppler_mode)

    # add light fixme
    # add nudge fixme
    radar_controller.set_range(settings._range)

    radar_controller.set_antenna_height(settings.antenna_height)

    radar_controller.set_gain(settings.gain)
    radar_controller.set_gain_auto(settings.gain_auto)

    radar_controller.set_sea_clutter(settings.sea_clutter)
    radar_controller.set_sea_clutter_auto(settings.sea_clutter_auto)

    radar_controller.set_rain_clutter(settings.rain_clutter)
    radar_controller.set_rain_clutter_auto(settings.rain_clutter_auto)

    radar_controller.set_side_lobe_suppression(settings.side_lobe_suppression)
    radar_controller.set_side_lobe_suppression_auto(settings.side_lobe_suppression_auto)

    radar_controller.set_noise_rejection(settings.noise_rejection)

    radar_controller.set_noise_rejection(settings.noise_rejection)

    radar_controller.set_interference_rejection(settings.interference_rejection)
    radar_controller.set_local_interference_filter(settings.local_interference_filter)

    radar_controller.set_target_expansion(settings.target_expansion)
    radar_controller.set_target_separation(settings.target_separation)
    radar_controller.set_target_boost(settings.target_boost)


def valide_radar_settings(settings: RadarUserSettings, radar_controller: NavicoRadarController):

    check_list = [
        ['bearing', settings.bearing, radar_controller.reports.spatial.bearing],
        ['antenna_height', settings.antenna_height, radar_controller.reports.spatial.antenna_height],

        ['sea_gain', settings.gain, radar_controller.reports.setting.gain],
        ['sea_gain_auto', settings.gain_auto, radar_controller.reports.setting.gain_auto],
        ['sea_clutter', settings.sea_clutter, radar_controller.reports.setting.sea_clutter],
        ['sea_clutter_auto', settings.sea_clutter_auto, radar_controller.reports.setting.sea_clutter_auto],  # I think it might be it #unsure
        ['rain_clutter', settings.rain_clutter, radar_controller.reports.setting.rain_clutter],
        ['side_lobe_suppression', settings.side_lobe_suppression, radar_controller.reports.filter.side_lobe_suppression],

        ['side_lobe_suppression_auto', settings.side_lobe_suppression_auto, radar_controller.reports.filter.side_lobe_suppression_auto],

        ['sea_state', settings.sea_state, radar_controller.reports.filter.sea_state],

        ['noise_rejection', settings.noise_rejection, radar_controller.reports.filter.noise_rejection],
        ['interference_rejction', settings.interference_rejection, radar_controller.reports.setting.interference_rejection],
        ['local_interference_filter', settings.local_interference_filter, radar_controller.reports.filter.local_interference_filter],


        #assert settings.mode, radar_controller.reports.setting.mode
        ['target_expansion', settings.target_expansion, radar_controller.reports.setting.target_expansion],
        ['target_separation', settings.target_separation, radar_controller.reports.filter.target_separation],
        ['target_boost', settings.target_boost, radar_controller.reports.setting.target_boost],
        #assert settings.doppler_mode, radar_controller.reports.filter.doppler_mode
        #assert settings.doppler_speed, radar_controller.reports.filter.doppler_speed

        #settings.light = radar_controller.reports.spatial.light

        #settings.sea_clutter_08c4 = radar_controller.reports.filter.sea_clutter_08c4
        #settings.sea_clutter_nudge = radar_controller.reports.filter.sea_clutter_nudge

    ]
    for key, v1, v2 in check_list:
        try:
            assert v1 == v2
        except AssertionError:
            logging.error(f"{key} was not set. Expected: {v1}, Actual: {v2}")

    key = "range"
    v2 = radar_controller.reports.setting._range
    if settings._range in RANGES_PRESETS:
        v1 = RANGES_PRESETS[settings._range]
    else:
        v1 = settings._range
    try:
        assert v1 == v2
    except AssertionError:
            logging.error(f"{key} was not set. Expected: {v1}, Actual: {v2}")

def start_transmit(radar_controller: NavicoRadarController):
    max_try = 20
    _count = 0
    radar_controller.transmit()
    # FIXME THIS IS NOT WORKING
    while radar_controller.reports.status.status is not RadarStatus.transmit:
        time.sleep(.05)
        radar_controller.get_reports()

        if radar_controller.reports.status.status == RadarStatus.spinning_up:
            max_try = 100 # try a bit more if it spinning u

        if _count >= max_try:
            logging.error("Radar Was not Started")
            return False

        _count += 1
    return True


def set_scan_speed(radar_controller: NavicoRadarController, scan_speed: str, standby=False):
    # Set proper Scan speed
    max_try = 20
    _count = 0
    if start_transmit(radar_controller) is True:
        #tries for 1 seconds
        for _ in range(max_try):
            if radar_controller.reports.filter.scan_speed != scan_speed:
                radar_controller.set_scan_speed(scan_speed)
                time.sleep(1)
                radar_controller.get_reports()

            else:
                logging.info(f"Scan Speed set to {scan_speed}")
                break

        if radar_controller.reports.filter.scan_speed != scan_speed:
            logging.warning(f"Unable to change scan speed to {scan_speed} from {radar_controller.reports.filter.scan_speed}")

    else:
        logging.error(f"Unable to change scan speed from {scan_speed}. Radar did not start to transmit.")

    if standby:
        radar_controller.standby()