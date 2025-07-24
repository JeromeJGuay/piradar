import logging
import time
import argparse

import datetime
from pathlib import Path

from piradar.logger import init_logging

from piradar.navico.navico_controller import NavicoRadarController, RadarStatus

from piradar.gpio_utils import gpio_controller

from piradar.scheduled_scan_utils import main_init_sequence, run_scheduled_scans, NavicoRadarError, start_transmit, configure_exit_handling

from piradar.configs_utils import load_configs

configure_exit_handling()


def basic_scan(
        radar_controller: NavicoRadarController,
        dt: datetime.datetime,
        output_data_path: str,
        number_of_sector_to_record: int
):
    time_stamp = dt.astimezone(datetime.UTC).strftime("%Y%m%dT%H%M%S")

    if start_transmit(radar_controller) is True:
        output_file = Path(output_data_path).joinpath(f"{time_stamp}")

        radar_controller.data_recorder.start_sector_recording(
            output_file=output_file,
            number_of_sector_to_record=number_of_sector_to_record,
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
    parser = argparse.ArgumentParser(prog='Halo Radar Scheduled Scan')

    # Positional argument
    parser.add_argument("configs_dir", type=str, help="Directory path for configurations files")

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

    config = load_configs(args.configs_dir)

    logging.info("Running Basic Program Script.")
    radar_controller, output_data_path, output_report_path = main_init_sequence(config)

    ## ERROR WILL BE RAISE IN HERE.
    # - Did not start to transmit
    # - Did not stop to transmit
    # - No data were received.
    run_scheduled_scans(  # <- Watchdog for receiving data is hidden in here.
        radar_controller=radar_controller,
        scan_interval=config['scan_interval'],
        scan_func=basic_scan,
        output_data_path=output_data_path,
        number_of_sector_to_record=config['scan_count'],
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