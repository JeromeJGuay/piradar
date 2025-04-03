import logging
import time
import datetime
from pathlib import Path

from piradar.logger import init_logging

from piradar.navico.navico_controller import (MulticastInterfaces, MulticastAddress, NavicoRadarController, RadarStatus)
from piradar.scripts.script_utils import set_user_radar_settings, valide_radar_settings, start_transmit, set_scan_speed, \
    RadarUserSettings, run_scan_schedule, startup_sequence, gpio_controller

###################################################
#        PARAMETERS TO BE LOADED FROM INI         #
###################################################
startup_timeout = 60

scan_record_interval = 60

number_of_sector_per_scan = 1

## Radar Setting ##
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


###################################################
#               Actual Script Below               #
###################################################


output_data_path = Path(output_drive).joinpath(output_data_dir)
output_report_path = Path(output_drive).joinpath(output_report_dir)


def scan(radar_controller: NavicoRadarController, dt: datetime.datetime):
    time_stamp = dt.astimezone(datetime.UTC).strftime("%Y%m%dT%H%M%S")
    if start_transmit(radar_controller) is True:
        for _gain in [0, 127, 255]:
            radar_controller.set_gain(_gain)
            time.sleep(0.1)

            scan_output_path = output_data_path.joinpath(f"{time_stamp}_s_{number_of_sector_per_scan}_gain_{_gain}.raw")

            radar_controller.start_recording_data(number_of_sector_to_record=number_of_sector_per_scan,
                                                  output_file=scan_output_path)
            gpio_controller.transmit_start()

            # add a watch dog here stop recording
            while radar_controller.is_recording_data:
                time.sleep(.1)

            gpio_controller.transmit_stop()

        # add a watchdog here (stop transmit)
        while (radar_controller.reports.status.status is RadarStatus.transmit):
            radar_controller.standby()
            radar_controller.get_reports()
            time.sleep(.1)
    else:
        logging.error("Failed to start radar scan")
        gpio_controller.error_pulse('no_radar')
        # Fixme reboot
        return

    # ping watchdog & reboot.



def main():
    ### A watchdog should be added to raise an error if the radar disconnect
    ### Turn radar off and on again.

    gpio_controller.program_started()

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

    gpio_controller.radar_power.on()

    radar_controller = NavicoRadarController(
        multicast_interfaces=mcast_ifaces,
        report_output_dir=output_report_path,
        connect_timeout=60 # the radar has 1 minutes to boot up and be available on the network
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
    # DO SOMETHING LIKE WRITE REPORT WITH TIMESTAMPS IF IT FAILS

    logging.info("Ready to record.")
    gpio_controller.ready_to_record()

    # add a watchdog here. Fixme
    run_scan_schedule(
        scan_record_interval=scan_record_interval,
        scan_func=scan,
        radar_controller=radar_controller
    )


if __name__ == '__main__':

    debug_level = "INFO"
    write_log = True
    init_logging(stdout_level=debug_level, file_level=debug_level, write=write_log)
    try:
        main()
    except Exception as e:
        logging.error(f"MAIN EXIT: {e}")
        gpio_controller.error_pulse('fatal')
        time.sleep(10)
    finally:
        gpio_controller.all_off()
