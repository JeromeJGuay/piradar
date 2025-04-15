import threading
import time
import datetime
import logging
from pathlib import Path

from piradar.logger import init_logging

from piradar.navico.navico_controller import (MulticastInterfaces, MulticastAddress, NavicoRadarController, RadarStatus)

from piradar.scripts.script_utils import set_user_radar_settings, valide_radar_settings, start_transmit, set_scan_speed, \
    RadarUserSettings, run_scan_schedule, startup_sequence, gpio_controller, NavicoRadarError

startup_timeout = 60

number_of_sector_to_record = 1

radar_user_settings = RadarUserSettings(
    _range=40_000,
    antenna_height=10,

    bearing=0,

    gain=127,
    gain_auto=False,

    sea_clutter=0,
    sea_clutter_auto=False,

    rain_clutter=0,
    rain_clutter_auto=False,

    side_lobe_suppression=0,
    side_lobe_suppression_auto=False,

    sea_state='calm',
    noise_rejection='off',

    interference_rejection='off',
    local_interference_filter='off',

    target_expansion='off',
    target_separation='off',
    target_boost='off',
)

scan_speed = "high"

### NETWORK ###
interface_addr = "192.168.1.100"
interface_name = "eth0"

report_address = ('236.6.7.9', 6679)
data_address = ('236.6.7.8', 6678)
send_address = ('236.6.7.10', 6680)

mcast_ifaces = MulticastInterfaces(
    report=MulticastAddress(*report_address),
    data=MulticastAddress(*data_address),
    send=MulticastAddress(*send_address),
    interface=interface_addr
)

### Write data ###
output_drive = "/media/capteur/2To"
output_data_dir = "data"
output_report_dir = "report"

output_data_path = Path(output_drive).joinpath(output_data_dir)
output_report_path = Path(output_drive).joinpath(output_report_dir)


def main():
    gpio_controller.program_started_led()

    if not startup_sequence( # return flag
            output_drive=output_drive,
            output_report_path=output_report_path,
            output_data_path=output_data_path,
            interface_name=interface_name,
            timeout=startup_timeout
    ):
        # Do something like  reboot pi ? send message to witty 4  etc...
        logging.error("Failed to run the startup sequence radar scan.")

        return

    logging.info("Powering Up Radar")
    gpio_controller.radar_power.on()
    gpio_controller.waiting_for_radar_led()

    radar_controller = NavicoRadarController(
        multicast_interfaces=mcast_ifaces,
        report_output_dir=output_report_path,
        connect_timeout=60  # the radar has 1 minutes to boot up and be available on the network
    )

    set_user_radar_settings(radar_user_settings, radar_controller)
    radar_controller.get_reports()
    time.sleep(1)  # just to be sure all reports are in and analyzed.

    valide_radar_settings(radar_user_settings, radar_controller)
    # DO SOMETHING LIKE PRINT REPORT WITH TIMESTAMP IF IT FAILS

    set_scan_speed(radar_controller=radar_controller, scan_speed=scan_speed, standby=True)

    logging.info("Ready to record.")
    gpio_controller.ready_to_record_led()

    return radar_controller


def scan_continuous(radar_controller: NavicoRadarController):

    time_stamp = datetime.datetime.now()
    scan_output_path = output_data_path.joinpath(f"{time_stamp}_s_{number_of_sector_to_record}_continuous.raw")
    radar_controller.start_recording_data(number_of_sector_to_record=number_of_sector_to_record, output_file=scan_output_path)
    gpio_controller.is_recording_led()


def start_scan(radar_controller: NavicoRadarController, scan_interval=2):

    def _inner_thread():
        if start_transmit(radar_controller) is True:

            gpio_controller.transmit_led()
            run_scan_schedule(  # <- Watchdog for receiving data is hidden in here.
                scan_record_interval=scan_interval,
                scan_func=scan_continuous,
                radar_controller=radar_controller
            )
        else:
            logging.error("Failed to start radar scan")
            raise NavicoRadarError("Radar did not start transmitting.")

    scan_thread = threading.Thread(name="Continuous-Scan", target=_inner_thread, daemon=True)

    scan_thread.start()


if __name__ == '__main__':

    debug_level = "INFO"
    write_log = True
    init_logging(stdout_level=debug_level, file_level=debug_level, write=write_log)

    rc = main()

    start_scan()




