import argparse

from piradar.logger import init_logging

from piradar.scripts.script_utils import *

from config_loader import load_config


def parse_arguments():
    parser = argparse.ArgumentParser(prog='Halo Radar Continuous Recording')

    # Positional argument
    parser.add_argument("config_path", type=str, help="Path to configuration file")

    # Optional argument with specific values and default
    parser.add_argument("-L", "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        default="WARNING", help="Set the logging level (default: WARNING)")

    # Flag
    parser.add_argument("-W", "--write-loggins", action="store_true",
                        help="Enable log writing")

    return parser.parse_args()


args = parsed_args = parse_arguments()

init_logging(stdout_level=args.log_level, file_level=args.debug_level, write=args.write_loggins)

config = load_config(args.config_path)

logging.info("Running Continuous Recording Script.")
radar_controller, output_data_path, output_report_path, gpio_controller = init_sequence(config)


def start():
    if start_transmit(radar_controller) is True:
        radar_controller.data_recorder.start_continuous_recording(output_dir=output_data_path)
        gpio_controller.is_recording_led()
    else:
        logging.error("Failed to start radar scan")
        raise NavicoRadarError("Radar did not start transmitting.")


def stop():
    radar_controller.data_recorder.stop_recording_data()

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


start()