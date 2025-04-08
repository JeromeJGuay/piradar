import logging
import time
import datetime
import threading
from pathlib import Path
from dataclasses import dataclass

from piradar.navico.navico_controller import NavicoRadarController, RadarStatus, RANGES_PRESETS

from piradar.network import check_interface_inet_is_up

from piradar.raspberry_utils import RaspIoSwitch, RaspIoLED, release_gpio


def validate_interface(interface):
    #attempt = 10
    #for _ in range(attempt):
    if check_interface_inet_is_up(interface):
        return True
    return False


def validate_output_drive(output_drive):
    #attempt = 10
    #for _ in range(attempt):
    if Path(output_drive).is_dir():
        return True
    return False


def startup_sequence(output_drive, output_report_path, output_data_path, interface_name, timeout=60):

    output_drive_found = False
    interface_is_valid = False

    for _ in range(timeout):
        # MAKE SURE THE DRIVE IS MOUNTED

        if not output_drive_found:
            if not validate_output_drive(output_drive):
                logging.warning("Output drive does not exist")
                gpio_controller.error_pulse('no_drive')
            else:
                logging.info(f"{output_drive} directory found.")
                output_drive_found = True
                # this once raised an error FIXME
                Path(output_data_path).mkdir(parents=True, exist_ok=True)
                Path(output_report_path).mkdir(parents=True, exist_ok=True)


            # FIXME Check that the directory to write to exist.
            #if not Path(output_data_path).is_dir():
            #    raise Exception(f"Output directory {output_data_path}, was not created.")
            #if not Path(output_report_path).is_dir():
            #    raise Exception(f"Output directory {output_report_path}, was not created.")

        # MAKE SURE THE INTERFACE IS UP
        if not interface_is_valid:
            if not validate_interface(interface_name):
                logging.warning(f"Interface {interface_name} not found.")
                gpio_controller.error_pulse('no_eth')
            else:
                logging.info(f"{interface_name} interface found.")
                interface_is_valid = True

        if interface_is_valid and output_drive_found:
            return True

        time.sleep(1)

    gpio_controller.error_pulse('no_eth_drive')
    return False


@dataclass  #(kw_only=True)
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
        ['sea_clutter_auto', settings.sea_clutter_auto, radar_controller.reports.setting.sea_clutter_auto],
        # I think it might be it #unsure
        ['rain_clutter', settings.rain_clutter, radar_controller.reports.setting.rain_clutter],
        ['side_lobe_suppression', settings.side_lobe_suppression,
         radar_controller.reports.filter.side_lobe_suppression],

        ['side_lobe_suppression_auto', settings.side_lobe_suppression_auto,
         radar_controller.reports.filter.side_lobe_suppression_auto],

        ['sea_state', settings.sea_state, radar_controller.reports.filter.sea_state],

        ['noise_rejection', settings.noise_rejection, radar_controller.reports.filter.noise_rejection],
        ['interference_rejction', settings.interference_rejection,
         radar_controller.reports.setting.interference_rejection],
        ['local_interference_filter', settings.local_interference_filter,
         radar_controller.reports.filter.local_interference_filter],

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
            max_try = 100  # try a bit more if it spinning u

        if _count >= max_try:
            logging.error("Radar Was not Started")
            return False

        _count += 1
    gpio_controller.transmit_start()
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
            logging.warning(
                f"Unable to change scan speed to {scan_speed} from {radar_controller.reports.filter.scan_speed}")

    else:
        logging.error(f"Unable to change scan speed from {scan_speed}. Radar did not start to transmit.")

    if standby:
        radar_controller.standby()


def round_datetime(dt: datetime.datetime, rounding_to: float, offset=0.0, up=False) -> datetime.datetime:
    """
    :param dt: datetime.datetime object (native not UTC)
    :param rounding_to: near whole seconds interval to round to.
    :param offset: Offset in seconds to round to. Rounds to each rounding_to + offset.
    :param up: Round up or down.
    :return: datetime.datetime object.
    """
    total_seconds = dt.hour * 3600 + dt.minute * 60 + dt.second - offset

#    if up:
#        total_seconds -= 1

    reminder = total_seconds % rounding_to
    rounded_seconds = total_seconds - reminder + offset

    if up:
        rounded_seconds += rounding_to

    return datetime.datetime(dt.year, dt.month, dt.day) + datetime.timedelta(seconds=rounded_seconds)


def run_scan_schedule(scan_record_interval: int, scan_func, radar_controller: NavicoRadarController):
    """

    :param scan_record_interval: Interval of the schedule
    :param scan_func: The scan function must take radar_controller: NavicoRadarController
        and dt: datatime.datetime as arguments.
    :param radar_controller: NavicoRadarController
    :return:
    """

    scan_watchdog = ScanWatchDog(radar_controller)
    data_watchdog = DataWatchDog(radar_controller)  # will check after 10 seconds if data were received.

    dt_now = datetime.datetime.now()
    logging.info(f"App start time: {dt_now.strftime('%Y-%m-%dT%H:%M:%S')}")
    dt_next = round_datetime(dt_now, rounding_to=scan_record_interval, up=True)
    logging.info(f"First scan time: {dt_next.strftime('%Y-%m-%dT%H:%M:%S')}")
    time.sleep((dt_next - dt_now).total_seconds())

    while True:
        logging.info(f"Scan Time: {datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}")
        scan_watchdog.watch(interval=scan_record_interval) # if the scan never stopped
        data_watchdog.watch(interval=10)  # this raise an error if data are not received after the interval.
        scan_func(radar_controller, dt=dt_next)

        dt_now = datetime.datetime.now()
        logging.info(f"After scan time: {dt_now.strftime('%Y-%m-%dT%H:%M:%S')}")
        dt_next = round_datetime(dt_now, rounding_to=scan_record_interval, up=True)
        logging.info(f"Next scan time: {dt_next.strftime('%Y-%m-%dT%H:%M:%S')}")
        seconds_to_next_scan = (dt_next - dt_now).total_seconds()
        time.sleep(seconds_to_next_scan)


class DataWatchDog:
    def __init__(self, radar_controller: NavicoRadarController):
        self.radar_controller = radar_controller
        self.interval = None

        self.stand_down_flag = True
        self.thread: threading.Thread = None

    def watch(self, interval: int):
        self.interval = interval
        self.stand_down_flag = False

        self.thread = threading.Thread(name='Data Watchdog', target=self.duty, daemon=True)
        self.thread.start()

    def duty(self):
        time.sleep(self.interval)
        if self.radar_controller.is_receiving_data:
            self.radar_controller.is_receiving_data = False
        else:
            raise NavicoRadarError("No Data received.")


class ScanWatchDog:
    def __init__(self, radar_controller: NavicoRadarController):
        self.radar_controller = radar_controller
        self.interval = None

        self.stand_down_flag = False

        self.stand_down_flag = True
        self.thread: threading.Thread = None

    def watch(self, interval: int):
        self.interval = interval
        self.stand_down_flag = False

        self.thread = threading.Thread(name='Scan Watchdog', target=self.duty, daemon=True)
        self.thread.start()

    def duty(self):
        time.sleep(self.interval)
        if not self.stand_down_flag:
            raise NavicoRadarError("Scan delay timeout.")

    def stand_down(self):
        self.stand_down_flag = True


class NavicoRadarError(Exception):
    pass


class GPIOControllter:
    def __init__(self):
        self.radar_power = RaspIoSwitch(6)

        self.green_led = RaspIoLED(13) # Green
        self.blue_led = RaspIoLED(19) # Blue
        self.red_led = RaspIoLED(26) # Red

    def program_started(self):
        self.led_off()
        self.blue_led.on()
        self.green_led.on()

    def waiting_for_radar(self):
        self.led_off()
        self.green_led.on()

    def setting_radar(self):
        self.led_off()
        self.green_led.pulse(period=0.25)

    def ready_to_record(self):
        self.led_off()
        self.blue_led.pulse(period=0.5)

    def transmit_start(self):
        self.led_off()
        self.red_led.on()

    def record_start(self):
        self.led_off()
        self.red_led.pulse(period=0.5)

    def error_pulse(self, error_type: str):
        self.led_off()

        match error_type:
            case 'no_radar':
                self.green_led.pulse(period=0.5, n_pulse=10)
                self.blue_led.pulse(period=0.5, n_pulse=10)
            case 'no_eth':
                self.green_led.pulse(period=0.5, n_pulse=10)
                self.blue_led.pulse(period=0.25, n_pulse=20)
            case 'no_drive':
                self.green_led.pulse(period=0.25, n_pulse=20)
                self.blue_led.pulse(period=0.5, n_pulse=10)
            case 'no_eth_drive':
                self.green_led.pulse(period=0.5, n_pulse=10, offset=0.25)
                self.blue_led.pulse(period=0.5, n_pulse=10)
            case 'fatal':
                self.green_led.pulse(period=0.25, n_pulse=20)
                self.blue_led.pulse(period=0.25, n_pulse=20)

    def reboot_radar(self):
        self.radar_power.off()
        time.sleep(1)
        self.radar_power.on()

    def led_off(self):
        for _pin in [self.green_led, self.blue_led, self.red_led]:
            _pin.stop_pulse()
            _pin.off()

    def all_off(self):
        self.led_off()
        self.radar_power.off()

    def __aexit__(self, exc_type, exc_val, exc_tb):
        release_gpio() # myabe not be nescessary but hey.


gpio_controller = GPIOControllter()