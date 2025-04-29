import configparser


def load_config(config_path):
    config = configparser.ConfigParser()
#    with open(path_to_config, 'r') as config_file:
    config.read(config_path)

    fconfig = config._sections

    fconfig['NETWORK']['report_port'] = int(config['NETWORK']['report_port'])
    fconfig['NETWORK']['data_port'] = int(config['NETWORK']['data_port'])
    fconfig['NETWORK']['send_port'] = int(config['NETWORK']['send_port'])

    fconfig['TIMEOUTS']['radar_boot_timeout'] = float(config['TIMEOUTS']['radar_boot_timeout'])
    fconfig['TIMEOUTS']['raspberry_boot_timeout'] = float(config['TIMEOUTS']['raspberry_boot_timeout'])

    fconfig['RADAR_SETTINGS']['range'] = int(config['RADAR_SETTINGS']['range'])
    fconfig['RADAR_SETTINGS']['antenna_height'] = float(config['RADAR_SETTINGS']['antenna_height'])

    fconfig['RADAR_SETTINGS']['bearing'] = float(config['RADAR_SETTINGS']['bearing'])

    fconfig['RADAR_SETTINGS']['gain'] = int(config['RADAR_SETTINGS']['gain'])
    fconfig['RADAR_SETTINGS']['gain_auto'] = int(config['RADAR_SETTINGS']['sea_clutter'])

    fconfig['RADAR_SETTINGS']['sea_clutter'] = int(config['RADAR_SETTINGS']['sea_clutter'])
    fconfig['RADAR_SETTINGS']['sea_clutter_auto'] = bool(config['RADAR_SETTINGS']['sea_clutter_auto'])

    fconfig['RADAR_SETTINGS']['rain_clutter'] = int(config['RADAR_SETTINGS']['rain_clutter'])
    fconfig['RADAR_SETTINGS']['rain_clutter_auto'] = bool(config['RADAR_SETTINGS']['rain_clutter_auto'])

    fconfig['RADAR_SETTINGS']['side_lobe_suppression'] = int(config['RADAR_SETTINGS']['side_lobe_suppression'])
    fconfig['RADAR_SETTINGS']['side_lobe_suppression_auto'] = bool(config['RADAR_SETTINGS']['side_lobe_suppression_auto'])

    return fconfig


if __name__ == '__main__':
    path_to_config = "halo_configuration.ini"

    _conf = load_config(path_to_config)
    