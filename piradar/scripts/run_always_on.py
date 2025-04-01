import logging
import time
import datetime
from pathlib import Path


from piradar.logger import init_logging
#from piradar.raspberry_utils import RaspIoSwitch

from piradar.navico.navico_controller import (MulticastInterfaces, MulticastAddress, NavicoRadarController, RadarStatus)
from piradar.scripts.script_utils import set_user_radar_settings, valide_radar_settings, start_transmit, set_scan_speed, \
    RadarUserSettings, validate_interface, validate_output_drive, round_datetime

###################################################
#       PARAMETERS TO BE LOADED FROM INI          #
###################################################
record_interval = 60

number_of_sector_per_scan = 1

## Radar Setting ##
radar_user_settings = RadarUserSettings(
    _range=12,
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

scan_speed = "high"

### Write data ###
output_drive = "/media/capteur/2To"
output_data_dir = "data"
output_report_dir = "report"
output_data_path = Path(output_drive).joinpath(output_data_dir)
output_report_path = Path(output_drive).joinpath(output_report_dir)


def scan(radar_controller: NavicoRadarController, dt: datetime.datetime):
    time_stamp = dt.astimezone(datetime.UTC).strftime("%Y%m%dT%H%M%S")

    if start_transmit(radar_controller) is True:
        for _gain in [0, 127, 255]:
            radar_controller.set_gain(_gain)
            time.sleep(0.1)

            radar_controller.start_recording_data(
                number_of_sector_to_record=number_of_sector_per_scan,
                output_file=output_data_path.joinpath(f"{time_stamp}_s_{number_of_sector_per_scan}_gain_{_gain}.raw")
            )

            # add a watch dog here
            while radar_controller._data_recording_is_started:
                time.sleep(.1)

        while (radar_controller.reports.status.status is RadarStatus.transmit):
            radar_controller.standby()
            radar_controller.get_reports()
            time.sleep(.1)
    else:
        logging.error("Failed to start radar scan")
    # ping watchdog & reboot.


def run_schedule(radar_controller: NavicoRadarController):

    dt_now = datetime.datetime.now()
    logging.info(f"app start time: {dt_now.strftime('%Y-%m-%dT%H:%M:%S')}")
    dt_next = round_datetime(dt_now, rounding_to=record_interval, up=True)
    logging.info(f"First scan time: {dt_next.strftime('%Y-%m-%dT%H:%M:%S')}")
    time.sleep((dt_next - dt_now).total_seconds())

    while True:
        logging.info(f"Scan Time: {datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}")

        scan(radar_controller, dt=dt_next)

        dt_now = datetime.datetime.now()
        logging.info(f"After scan time: {dt_now.strftime('%Y-%m-%dT%H:%M:%S')}")
        dt_next = round_datetime(dt_now, rounding_to=record_interval, up=True)
        logging.info(f"Next scan time: {dt_next.strftime('%Y-%m-%dT%H:%M:%S')}")
        seconds_to_next_scan = (dt_next - dt_now).total_seconds()
        time.sleep(seconds_to_next_scan)



def main():
    ### A watchdog should be added to raise an error if the radar disconnect
    ### Turn radar off and on again.

    for _ in range(60):
        try:
            # MAKE SURE THE DRIVE IS MOUNTED
            if not validate_output_drive(output_drive):
                raise Exception("Output drive does not exist")
            logging.info(f"{output_drive} directory found.")
            Path(output_data_path).mkdir(parents=True, exist_ok=True)
            Path(output_report_path).mkdir(parents=True, exist_ok=True)

            if not Path(output_data_path).is_dir():
                raise Exception(f"Output directory {output_data_path}, war not created")

            if not Path(output_report_path).is_dir():
                raise Exception(f"Output directory {output_report_path}, war not created")

            # MAKE SURE THE INTERFACE IS UP
            if not validate_interface(interface_name):
                raise Exception(f"Interface {interface_name} not found.")
            logging.info(f"{interface_name} interface found.")

            break
        except Exception as e:
            time.sleep(1)

    radar_controller = NavicoRadarController(
        multicast_interfaces=mcast_ifaces,
        report_output_dir=output_report_path,
    )

    # power on radar here if necessary

    if radar_controller.reports.system.radar_type is None:
        logging.info(f"Radar type received: {radar_controller.reports.system.radar_type}")
        raise Exception("Radar type not received. Communication Error")

    set_user_radar_settings(radar_user_settings, radar_controller)
    radar_controller.get_reports()
    time.sleep(1)  #just to be sure all reports are in and analyzed.

    valide_radar_settings(radar_user_settings, radar_controller)
    # DO SOMETHING LIKE PRINT REPORT WITH TIMESTAMP IF IT FAILS

    set_scan_speed(radar_controller=radar_controller, scan_speed=scan_speed, standby=True)
    # DO SOMETHIGN LIKE WRITE REPORT WITH TIMESTAMPS IF IT FAILS

    logging.info("Ready to record.")

    #### Scheduler ####

    # add a watchdog here. FIXMe
    run_schedule(radar_controller=radar_controller)


if __name__ == '__main__':
    debug_level = "INFO"
    write_log = True
    init_logging(stdout_level=debug_level, file_level=debug_level, write=write_log)

    main()
