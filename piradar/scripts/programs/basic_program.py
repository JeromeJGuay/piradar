import logging
import time
import argparse

import datetime
from pathlib import Path

from piradar.logger import init_logging

from piradar.navico.navico_controller import NavicoRadarController, RadarStatus

from piradar.scripts.gpio_utils import gpio_controller

from piradar.scripts.script_utils import main_init_sequence, run_scheduled_scans, NavicoRadarError, start_transmit, configure_exit_handling

from piradar.scripts.configs import load_config

configure_exit_handling()

### MISSING PARAMETERS
SCAN_INTERVAL = 60
NUMBER_OF_SECTOR = 5


def scan_basic(radar_controller: NavicoRadarController, dt: datetime.datetime, output_data_path: str):
    time_stamp = dt.astimezone(datetime.UTC).strftime("%Y%m%dT%H%M%S")

    if start_transmit(radar_controller) is True:
        for si in range(NUMBER_OF_SECTOR):

            scan_output_path = Path(output_data_path).joinpath(f"{time_stamp}_s_{si}")

            radar_controller.data_recorder.start_sector_recording(
                output_file=scan_output_path,
                number_of_sector_to_record=1
            )

            gpio_controller.is_recording_led()

            while radar_controller.data_recorder.is_recording:
                time.sleep(.1)  # this will never turn off

            gpio_controller.is_transmitting_led()

        for _ in range(5):  # tries to shut down radar transmit 5 times at 1sec interval.
            if radar_controller.reports.status.status is RadarStatus.standby:
                gpio_controller.led_off()
                return  # You want to scan to exit here !

            radar_controller.standby()
            radar_controller.get_reports()
            time.sleep(1)

        raise NavicoRadarError("Radar did not stopped transmitting.")

    else:
        logging.error("Failed to start radar scan")
        raise NavicoRadarError("Radar did not start transmitting.")


def parse_arguments():
    parser = argparse.ArgumentParser(prog='Halo Radar Continuous Recording')

    # Positional argument
    parser.add_argument("config_path", type=str, help="Path to configuration file")

    # Optional argument with specific values and default
    parser.add_argument("-L", "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        default="WARNING", help="Set the logging level (default: WARNING)")

    # Flag
    parser.add_argument("-W", "--write-logging", action="store_true",
                        help="Enable log writing")

    return parser.parse_args()


def main():
    ### ENTRY POINT ###
    args = parse_arguments()

    init_logging(stdout_level=args.log_level, file_level=args.log_level, write=args.write_logging)

    config = load_config(args.config_path)

    logging.info("Running Basic Program Script.")
    radar_controller, output_data_path, output_report_path = main_init_sequence(config)

    ## ERROR WILL BE RAISE IN HERE.
    # - Did not start to transmit
    # - Did not stop to transmit
    # - No data were received.
    run_scheduled_scans(  # <- Watchdog for receiving data is hidden in here.
        radar_controller=radar_controller,
        scan_interval=SCAN_INTERVAL,
        scan_func=scan_basic,
        output_data_path=output_data_path
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"MAIN EXIT: {e}")
        gpio_controller.error_pulse_led('fatal')
        time.sleep(10)
    finally:
        gpio_controller.all_off()