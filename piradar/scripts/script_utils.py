import sys
import signal
import logging
import time
import datetime
import threading
from pathlib import Path
from dataclasses import dataclass

from piradar.navico.navico_controller import NavicoRadarController, RadarStatus, RANGES_PRESETS, MulticastInterfaces, MulticastAddress

from piradar.network import check_interface_inet_is_up

from piradar.scripts.gpio_utils import gpio_controller




def validate_interface(interface):
    if check_interface_inet_is_up(interface):
        return True
    return False


def validate_output_drive(output_drive):
    if Path(output_drive).is_dir():
        return True
    return False


def wait_for_rpi_boot(output_drive, output_report_path, output_data_path, interface_name, timeout=60):

    output_drive_found = False
    interface_is_valid = False

    for _ in range(timeout):
        # MAKE SURE THE DRIVE IS MOUNTED

        if not output_drive_found:
            if not validate_output_drive(output_drive):
                logging.warning("Output drive does not exist")
                gpio_controller.error_pulse_led('no_drive')
            else:
                logging.info(f"{output_drive} directory found.")
                output_drive_found = True
                # this once raised an error FIXME
                Path(output_data_path).mkdir(parents=True, exist_ok=True)
                Path(output_report_path).mkdir(parents=True, exist_ok=True)

        # MAKE SURE THE INTERFACE IS UP
        if not interface_is_valid:
            if not validate_interface(interface_name):
                logging.warning(f"Interface {interface_name} not found.")
                gpio_controller.error_pulse_led('no_eth')
            else:
                logging.info(f"{interface_name} interface found.")
                interface_is_valid = True

        if interface_is_valid and output_drive_found:
            return True

        time.sleep(1)

    gpio_controller.error_pulse_led('no_eth_drive')
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


def main_init_sequence(config: dict):
    startup_timeout = config['TIMEOUTS']['radar_boot_timeout']
    connect_timeout = config['TIMEOUTS']['raspberry_boot_timeout']

    radar_user_settings = RadarUserSettings(
        _range=config['RADAR_SETTINGS']['range'],
        antenna_height=config['RADAR_SETTINGS']['antenna_height'],
        bearing=config['RADAR_SETTINGS']['bearing'],
        gain=config['RADAR_SETTINGS']['gain'],
        gain_auto=config['RADAR_SETTINGS']['gain_auto'],

        sea_clutter=config['RADAR_SETTINGS']['sea_clutter'],
        sea_clutter_auto=config['RADAR_SETTINGS']['sea_clutter_auto'],

        rain_clutter=config['RADAR_SETTINGS']['rain_clutter'],
        rain_clutter_auto=config['RADAR_SETTINGS']['rain_clutter_auto'],

        side_lobe_suppression=config['RADAR_SETTINGS']['side_lobe_suppression'],
        side_lobe_suppression_auto=config['RADAR_SETTINGS']['side_lobe_suppression_auto'],

        sea_state=config['RADAR_SETTINGS']['sea_state'],
        noise_rejection=config['RADAR_SETTINGS']['noise_rejection'],

        interference_rejection=config['RADAR_SETTINGS']['interference_rejection'],
        local_interference_filter=config['RADAR_SETTINGS']['local_interference_filter'],

        target_expansion=config['RADAR_SETTINGS']['target_expansion'],
        target_separation=config['RADAR_SETTINGS']['target_separation'],
        target_boost=config['RADAR_SETTINGS']['target_boost'],
    )

    scan_speed = config['RADAR_SETTINGS']['scan_speed']

    ### NETWORK ###
    interface_addr = config['NETWORK']['interface_addr']
    interface_name = config['NETWORK']['interface_name']

    report_address = (config['NETWORK']['report_addr'], config['NETWORK']['report_port'])
    data_address = (config['NETWORK']['data_addr'], config['NETWORK']['data_port'])
    send_address = (config['NETWORK']['send_addr'], config['NETWORK']['send_port'])

    mcast_ifaces = MulticastInterfaces(
        report=MulticastAddress(*report_address),
        data=MulticastAddress(*data_address),
        send=MulticastAddress(*send_address),
        interface=interface_addr
    )

    ### Write data ###
    output_drive = config['DATA']['drive_path']
    output_data_dir = config['DATA']['data_dir']
    output_report_dir = config['DATA']['report_dir']

    output_data_path = Path(output_drive).joinpath(output_data_dir)
    output_report_path = Path(output_drive).joinpath(output_report_dir)

    gpio_controller.program_started_led()

    if not wait_for_rpi_boot( # return flag
            output_drive=output_drive,
            output_report_path=output_report_path,
            output_data_path=output_data_path,
            interface_name=interface_name,
            timeout=startup_timeout
    ):
        # Do something like  reboot pi ? send message to witty 4  etc...
        logging.error("Failed to run the startup sequence radar scan.")

        raise NavicoRadarError("error in raspberry pi booting sequence.")

    logging.info("Powering Up Radar")
    gpio_controller.radar_power.on()
    gpio_controller.waiting_for_radar_led()

    radar_controller = NavicoRadarController(
        multicast_interfaces=mcast_ifaces,
        report_output_dir=output_report_path,
        connect_timeout=connect_timeout  # the radar has 1 minutes to boot up and be available on the network
    )

    if radar_controller.raw_reports.r01c4 is None:
       logging.info(f"Radar status reports (01c4) was not received.")

       raise Exception("Radar type not received. Communication Error")

    gpio_controller.setting_radar_led()

    set_user_radar_settings(radar_user_settings, radar_controller)
    radar_controller.get_reports()
    time.sleep(1)  # just to be sure all reports are in and analyzed.

    valide_radar_settings(radar_user_settings, radar_controller)
    # DO SOMETHING LIKE PRINT REPORT WITH TIMESTAMP IF IT FAILS

    # Not working on HALO fix me
    # set_scan_speed(radar_controller=radar_controller, scan_speed=scan_speed, standby=True)

    # disable since we are unable to set it yet...
    for si in range(4):
        radar_controller.enable_sector_blanking(si, False)

    # this shoud be put in config. FIXME
    radar_controller.set_mode("custom")

    logging.info("Ready to record.")
    gpio_controller.ready_to_record_led()

    return radar_controller, output_data_path, output_report_path


def set_scan_speed(radar_controller: NavicoRadarController, scan_speed: str, standby=False, max_try=20):
    # Set proper Scan speed
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


def start_transmit(radar_controller: NavicoRadarController, max_try=20):
    _count = 0
    radar_controller.transmit()
    while radar_controller.reports.status.status is not RadarStatus.transmit:
        time.sleep(.05)
        radar_controller.get_reports()

        if radar_controller.reports.status.status == RadarStatus.spinning_up:
            max_try = 100  # try a bit more if it spinning u

        if _count >= max_try:
            logging.error("Radar Was not Started")
            return False

        _count += 1
    gpio_controller.is_transmitting_led()
    return True


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


def wait_for_next_scan(scan_interval: int):
    dt_now = datetime.datetime.now()
    logging.info(f"Current time: {dt_now.strftime('%Y-%m-%dT%H:%M:%S')}")
    dt_next = round_datetime(dt_now, rounding_to=scan_interval, up=True)
    logging.info(f"Next scan time: {dt_next.strftime('%Y-%m-%dT%H:%M:%S')}")
    gpio_controller.scan_standby_led()
    time.sleep((dt_next - dt_now).total_seconds())

    return dt_next


def run_scheduled_scans(radar_controller: NavicoRadarController, scan_interval: int, scan_func, **func_kwargs):
    """

    :param radar_controller: NavicoRadarController
    :param scan_interval: Interval of the schedule, must minimally take radar_controller and dt:datetime.datetime as kwargs.
    :param scan_func: The scan function must take radar_controller: NavicoRadarController
        and dt: datatime.datetime as arguments.

    :return:
    """

    scan_watchdog = BaseWatchDog(radar_controller, name="ScanWatchDog")
    data_watchdog = DataWatchDog(radar_controller)

    dt_next = wait_for_next_scan(scan_interval)

    while True:
        logging.info(f"Scan Time: {datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}")
        scan_watchdog.watch(interval=scan_interval)  # if the scan never stopped
        data_watchdog.watch(interval=10)  # this raise an error if data are not received after the interval.

        scan_func(radar_controller, dt=dt_next, **func_kwargs)

        scan_watchdog.stand_down() # test if is ok FIXME
        data_watchdog.stand_down()

        dt_next = wait_for_next_scan(scan_interval)


class NavicoRadarError(Exception):
    pass


class BaseWatchDog:
    """Raises Error if no data self.stand_down() is not called before the timeout."""
    def __init__(self, radar_controller: NavicoRadarController, name="BaseWatchDog"):
        self.radar_controller = radar_controller
        self.interval = None

        self.stand_down_flag = True
        self.thread: threading.Thread = None

        self.name = name

    def watch(self, interval: int):
        self.interval = interval
        self.stand_down_flag = False

        self.thread = threading.Thread(name=self.name, target=self.duty, daemon=True)
        self.thread.start()

    def duty(self):
        time.sleep(self.interval)

        if self.stand_down_flag:
            return

        raise NavicoRadarError("Scan delay timeout.")

    def stand_down(self):
        self.stand_down_flag = True


class DataWatchDog(BaseWatchDog):
    """Raises error if data was not received before timeout and self.stand_down() was not called."""
    def __init__(self, radar_controller: NavicoRadarController, name="DataWatchDog"):
        BaseWatchDog.__init__(self, radar_controller=radar_controller, name=name)

    def duty(self):
        time.sleep(self.interval)
        if self.radar_controller.is_receiving_data:
            self.radar_controller.is_receiving_data = False
            return

        if self.stand_down_flag:
            return

        raise NavicoRadarError("No Data received.")


def catch_termination_signal():
    """Raise Exceptions if a signal.SIGTERM signal is receive.d"""
    def handle_sigterm(signum, frame):
        logging.error("Received SIGTERM, cleaning up...")
        gpio_controller.all_off() # this sould work instead of try:except:finally:
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_sigterm)
