"""
Decoded from B201

192.168.1.185 257
192.168.1.185 5984
236.6.7.22 6694
236.6.7.23 6684
236.6.7.24 6685
236.6.7.8 6678 # data A
236.6.7.10 6680 #send A
236.6.7.9 6679 #report A
236.6.7.13 6657 # data B
236.6.7.14 6658 # send B
236.6.7.15 6659 # report B
236.6.7.18 6688
236.6.7.20 6690
236.6.7.19 6689
236.6.7.12 6660
236.6.7.13 6661
236.6.7.14 6662

"""
import logging
import time
import datetime
import struct
import socket
import threading
import queue

from pathlib import Path
from dataclasses import dataclass

from piradar.network import create_udp_socket, create_udp_multicast_receiver_socket, ip_address_to_string
from piradar.navico.navico_structure import *
from piradar.navico.navico_command import *


HOST = ''
RCV_BUFF = 65535


ENTRY_GROUP_ADDRESS = '236.6.7.5'
ENTRY_GROUP_PORT = 6878


class NavicoRadarType:
    navico4G = "4G"
    navico3G = "3G"
    navicoBR24 = "BR24"
    navicoHALO = "HALO"


RADAR_ID2TYPE_MAP = {
    0x01: NavicoRadarType.navico4G,
    0x08: NavicoRadarType.navico3G,
    0x0F: NavicoRadarType.navicoBR24,
    0x00: NavicoRadarType.navicoHALO
}

RANGES_VALS_LIST = [50, 75, 100, 250, 500, 750, 1000,
                    1500, 2000, 4000, 6000, 8000,
                    12000, 15000, 24000]

OLMH_VAL2STR_MAP = {0: "off", 1: "low", 2: "medium", 3: "high"}
OLMH_STR2VAL_MAP = {"off": 0, "low": 1, "medium": 2, "high": 3}

OLH_VAL2STR_MAP = {0: "off", 1: "low", 2: "high"}
OLH_STR2VAL_MAP = {"off": 0, "low": 1, "high": 2}

RADAR_STATUS_VAL2STR_MAP = {1: "standby", 2: "transmit", 5: "spinning-up"}
RADAR_STATUS_STR2VAL_MAP = {}

MODE_VAL2STR_MAP = {0: "custom", 1: "harbor", 2: "offshore", 4: "weather", 5: "bird", 255: "unknown"}
MODE_STR2VAL_MAP = {"custom": 0, "harbor": 1, "offshore": 2, "weather": 4, "bird": 5}

SEA_STATE_VAL2STR_MAP = {0: "calm", 1: "moderate", 2: "rough"}
SEA_STATE_STR2VAL_MAP = {"calm": 0, "moderate": 1, "rough": 2}
# I dont get the difference between SEA_STATE and SEA_AUTO FIXME
SEA_AUTO_VAL2STR_MAP = {0: "off", 1: "harbor", 2: "offshore"}
SEA_AUTO_STR2VAL_MAP = {"off": 0, "harbor": 1, "offshore": 2}

DOPPLER_MODE_VAL2STR_MAP = {0: "off", 1: "normal", 2: "approaching_only"}
DOPPLER_MODE_STR2VAL_MAP = {"off": 0, "normal": 1, "approaching_only": 2}

SCAN_SPEED_VAL2STR_MAP = {0: "low", 1: "medium", 2: "high"}
SCAN_SPEED_STR2VAL_MAP = {"low": 0, "medium": 1, "high": 2}

@dataclass
class MulticastAddress:
    address: str | int
    port: int

    def __post_init__(self):
        if isinstance(self.address, int):
            self.address = ip_address_to_string(self.address)


@dataclass
class MulticastInterfaces:
    data: MulticastAddress
    send: MulticastAddress
    report: MulticastAddress
    interface: str


@dataclass
class RawReports:
    r01b2: RadarReport01B2 = None
    r01c4: RadarReport01C4 = None
    r02c4: RadarReport02C4 = None
    r03c4: RadarReport03C4 = None
    r04c4: RadarReport04C4 = None
    r06c4: RadarReport06C4 = None
    r08C4: RadarReport08C4 = None
    r12c4: RadarReport12C4 = None


@dataclass
class StatusReport:
    """Report 01C4"""
    status: str = None

@dataclass
class SettingReport:
    """Report 02C4"""

    _range: float = None
    mode: str = None
    gain: float = None
    auto_gain: bool = None
    auto_sea_state: str = None # if sea_state is in auto mode ?
    sea_clutter: float = None
    rain_clutter: float = None
    interference_rejection: str = None
    target_expansion: str = None
    target_boost: str = None

@dataclass
class SpatialReport:
    """Report 04C4"""
    bearing: float = None
    antenna_height: float = None
    light: float = None


@dataclass
class SystemReport:
    """Report 03C4"""
    radar_type: str = None


@dataclass
class BlankingReport:
    """Report 06c4"""
    pass


@dataclass
class FilterReport:
    """Report 08C4"""
    sea_state: str = None
    local_interference_filter: str = None
    scan_speed: str = None # why is scanspeed here not in the 04C4 reports....
    auto_side_lobe_suppression: bool = None
    side_lobe_suppression: int = None
    noise_rejection: str = None
    target_separation: str = None
    sea_clutter: int = None
    sea_clutter_nudge: int = None
    doppler_mode: str = None
    doppler_speed: int = None


@dataclass
class SerialNumberReport:
    """Report 12C4"""
    serial_number: str = None


@dataclass
class Reports:
    status = StatusReport()
    spatial = SpatialReport()
    system = SystemReport()
    blanking = BlankingReport()
    setting = SettingReport()
    filters = FilterReport()
    serial = SerialNumberReport()



@dataclass
class SpokeData:
    spoke_number: int = None
    heading: float = None
    angle: float = None
    _range: float = None
    intensities: list[float] = None


@dataclass
class SectorData:
    time: str = None
    number_of_spokes: int = None
    spoke_data: list[SpokeData] = None

    def __post_init__(self):
        self.spoke_data = []


@dataclass
class NavicoUserConfig:
    # Base
    _range: int = None  #Literal[50, 75, 100, 250, 500, 750, 1e3, 1.5e3, 2e3, 4e3, 6e3, 8e3, 12e3, 15e3, 24e3]
    bearing: float = None
    gain: float = None
    antenna_height: float = None
    scan_speed: str = None # ["low", "medium", "high"] = None  # Doubt # Default-0, increase-1 ? max-2 ???

    # filters

    sea_state: str = None # ['calm', 'moderate', 'rough']

    sea_clutter: int = None
    rain_clutter: int = None

    interference_rejection: str = None # ["off", "low", "medium", "high"]
    local_inteference_filer: str = None # ["off", "low", "medium", "high"]
    side_lobe_suppression: int = None

    mode: str = None # ["custom", "harbor", "offshore", "weather", "bird"]

    target_expansion: str = None # ["off", "low", "medium", "high"]
    target_separation: str = None # ["off", "low", "medium", "high"]
    target_boost: str = None # ["off", "low", "high]
    noise_rejection: str = None # ["off", "low", "medium", "high"]

    doppler_mode: str = None # ['off', 'normal', 'approaching_only']
    doppler_speed: float = None

    light: str = None# ["off", "low", "medium", "high"]
    # auto
    auto_gain: bool = False
    auto_sea_clutter: bool = False
    auto_rain_clutter: bool = False
    auto_side_lobe_suppression: bool = False

    def __post_init__(self):
        if self._range:
            if self._range not in [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]:
                raise ValueError(f'Range must be a vlue between 0, and  14.')

        if self.bearing:
            if self.bearing > 360 or self.bearing < 0:
                raise ValueError(f'Bearing must be between 0 and 360.')

        if self.scan_speed:
            if self.scan_speed not in ['low', 'medium', 'high']:
                raise ValueError(f'Scan_speed must be one of low, medium, high.')

        # FIXME TODO add the rest

        if not isinstance(self.auto_gain, bool):
            raise ValueError(f'auto_gain must be a boolean.')
        if not isinstance(self.auto_sea_clutter, bool):
            raise ValueError(f'auto_sea_clutter must be a boolean.')
        if not isinstance(self.auto_rain_clutter, bool):
            raise ValueError(f'auto_rain_clutter must be a boolean.')
        if not isinstance(self.auto_side_lobe_suppression, bool):
            raise ValueError(f'auto_side_lobe_suppression must be a boolean.')




class NavicoRadarController:
    # RADAR NEED TO BE RESTARTED TO RECEIVE REPORTS FIXME
    # FIXME add Flags (signal) to hold thread until socket are open etc
    # FIXME add try -except in case error occures when creating sockets.
    # FIXME add WATCHDOG to kill everything in case of big error
    def __init__(
            self, multicast_interfaces: MulticastInterfaces,
            radar_user_config: NavicoUserConfig,
            output_dir: str,
            keep_alive_interval: int = 10,
    ):
        self.address_set = multicast_interfaces
        self.output_dir = output_dir
        self.keep_alive_interval = keep_alive_interval

        self.data_path = Path(self.output_dir).joinpath("ppi_data.txt")
        self.raw_data_path = Path(self.output_dir).joinpath("raw_ppi_data.raw")
        self.raw_reports_path = {
            report_id : Path(self.output_dir).joinpath(f"raw_report_{hex(report_id)}.raw")
            for report_id in REPORTS_IDS
        }

        # make object to store initial parameter to pass to Radar

        self.send_socket = None

        self.data_socket = None
        self.report_socket = None

        self.data_thread: threading.Thread = None
        self.report_thread: threading.Thread = None
        self.stay_alive_thread: threading.Thread = None
        self.writer_thread: threading.Thread = None
        self.writing_queue = queue.Queue()

        self.radar_was_detected = False
        self.stop_flag = False

        ### RADAR PARAMETER ###
        # Not clear how to update this at the moment. Or use it
        self.radar_user_config = NavicoUserConfig()

        ### Reports Object ###
        self.raw_reports = RawReports()
        self.reports = Reports()

        self.init_report_socket()
        self.init_data_socket()

        self.start_report_thread()
        self.start_data_thread()
        self.start_writer_thread()
        self.start_data_thread()

        logging.info("Waiting for radar ...")
        while not self.radar_was_detected: # this is unlocked in the listen report thread
            wake_up_navico_radar()
            time.sleep(1)
            # FIXME add a timeout and raise an Error
        logging.info("Radar detected on network")

        self.init_send_socket()
        self.start_keep_alive_thread()
        self.send_user_config_parameters(radar_user_config)

    def init_send_socket(self):
        self.send_socket = create_udp_socket()
        self.send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        logging.debug("Send socket initialized")
        # not binding required

    def init_report_socket(self):
        self.report_socket = create_udp_multicast_receiver_socket(
            interface_address=self.address_set.interface,
            group_address=self.address_set.report.address,
            group_port=self.address_set.report.port
        )
        logging.debug("Report socket initialized")

    def init_data_socket(self):
        self.data_socket = create_udp_multicast_receiver_socket(
            interface_address=self.address_set.interface,
            group_address=self.address_set.data.address,
            group_port=self.address_set.data.port
        )
        logging.debug("Data socket initialized")

    def start_report_thread(self):
        self.report_thread = threading.Thread(target=self.report_listen, daemon=True)
        self.report_thread.start()
        logging.debug("Report thread started")

    def start_data_thread(self):
        self.data_thread = threading.Thread(target=self.data_listen, daemon=True)
        self.data_thread.start()
        logging.debug("Data thread started")

    def start_keep_alive_thread(self):
        self.keep_alive_thread = threading.Thread(target=self.keep_alive, daemon=True)
        self.keep_alive_thread.start()
        logging.debug("Keep alive thread started")

    def start_writer_thread(self):
        self.writer_thread = threading.Thread(target=self.writer, daemon=True)
        self.writer_thread.start()
        logging.debug("Writer thread started")

    def send_pack_data(self, packed_data):
        logging.debug(f"Sending: {packed_data} to {self.address_set.send.address, self.address_set.send.port}")
        _nbytes_sent = self.send_socket.sendto(packed_data, (self.address_set.send.address, self.address_set.send.port))
        if _nbytes_sent != len(packed_data):
            logging.error(f"Failed to send command {packed_data}.")
        time.sleep(0.1)

    def close_all(self):
        logging.info("Closing all called.")
        self.stop_flag = True
        self.report_thread.join()
        self.data_thread.join()
        self.keep_alive_thread.join()
        self.writer_thread.join()
        logging.info("All threads closed")

        self.report_socket.close()
        self.data_socket.close()
        self.send_socket.close()
        logging.info("All sockets closed")

    def report_listen(self):
        while not self.stop_flag: # have thread specific flags as well
            try:
                raw_packet = self.report_socket.recv(RCV_BUFF)
            except socket.timeout:
                continue
            if raw_packet and len(raw_packet) >= 2:
                self.radar_was_detected = True
                self.process_report(raw_packet=raw_packet)

    def data_listen(self):
        while not self.stop_flag: # have thread specific flags as well
            try:
                raw_packet = self.data_socket.recv(RCV_BUFF)
            except socket.timeout:
                continue

            if raw_packet:
                logging.debug("Data received")
                self.writing_queue.put((self.write_raw_data_packet, raw_packet))
                self.process_data(in_data=raw_packet)

    def process_report(self, raw_packet):
        # TODO DECODE ALL MISSING
        report_id = struct.unpack("!H", raw_packet[:2])[0]
        logging.debug(f"report received: {raw_packet[:2]}")
        if report_id in REPORTS_IDS:
            self.writing_queue.put((self.write_raw_report_packet, report_id, raw_packet))

        match report_id:
            case REPORTS_IDS.r_01B2:  # '#case b'\xb2\x01':
                self.raw_reports.r01b2 = RadarReport01B2(raw_packet)

            case REPORTS_IDS.r_01C4: #STATUS
                self.raw_reports.r01c4 = RadarReport01C4(raw_packet)
                try:
                    self.reports.status.status = RADAR_STATUS_VAL2STR_MAP[self.raw_reports.r01c4.radar_status]
                except ValueError:
                    self.reports.status.status = "unknown"
                    logging.warning(f"Unknown RadarReport01C4 status: {self.raw_reports.r01c4.radar_status}")

            case REPORTS_IDS.r_02C4:  # SETTINGS
                self.raw_reports.r02c4 = RadarReport02C4(raw_packet)

                self.reports.setting._range = self.raw_reports.r02c4.range / 10 # Unsure about the division Fixme test

                try:
                    self.reports.setting.mode = MODE_VAL2STR_MAP[self.raw_reports.r02c4.mode] #Raise or log warning for unknown type TODO
                except KeyError:
                    self.reports.setting.mode = "unknown"
                    logging.warning(f"Unknown mode: {self.raw_reports.r02c4.mode}")

                self.reports.setting.gain = self.raw_reports.r02c4.gain * (100 / 255)
                self.reports.setting.auto_gain = bool(self.raw_reports.r02c4.auto_gain)

                try:
                    self.reports.setting.auto_sea_state = SEA_AUTO_VAL2STR_MAP[self.raw_reports.r02c4.auto_sea_state]
                except KeyError:
                    self.reports.setting.auto_sea_state = "unknown"
                    logging.warning(f"Unknown auto_sea_state value: {self.raw_reports.r02c4.auto_sea_state}")

                self.reports.setting.sea_clutter = self.raw_reports.r02c4.sea_clutter * (100 / 255)

                self.reports.setting.rain_clutter = self.raw_reports.r02c4.rain_clutter * (100 / 255)

                try:
                    self.reports.setting.interference_rejection = OLMH_VAL2STR_MAP[self.raw_reports.r02c4.interference_rejection]
                except KeyError:
                    self.reports.setting.interference_rejection = "unknown"
                    logging.warning(f"Unknown interference_rejection value: {self.raw_reports.r02c4.interference_rejection}")

                try:
                    self.reports.setting.target_expansion = OLMH_VAL2STR_MAP[self.raw_reports.r02c4.target_expansion]
                except KeyError:
                    self.reports.setting.target_expansion = "unknown"
                    logging.warning(f"Unknown target_expansion value: {self.raw_reports.r02c4.target_expansion}")

                try:
                    self.reports.setting.target_boost = OLMH_VAL2STR_MAP[self.raw_reports.r02c4.target_boost] #missing in commands
                except KeyError:
                    self.reports.setting.target_boost = "unknown"
                    logging.warning(f"Unknown target_boost value: {self.raw_reports.r02c4.target_boost}")

            case REPORTS_IDS.r_03C4:  # SYSTEM
                self.raw_reports.r03c4 = RadarReport03C4(raw_packet)
                try:
                    self.reports.system.radar_type = RADAR_ID2TYPE_MAP[self.raw_reports.r03c4.radar_type]
                except KeyError:
                    self.reports.system.radar_type = "unknown"
                    logging.warning(f"Unknown radar_type: {self.raw_reports.r03c4.radar_type}")


            case REPORTS_IDS.r_04C4:  # SPATIAL
                self.raw_reports.r04c4 = RadarReport04C4(raw_packet)

                self.reports.spatial.bearing = self.raw_reports.r04c4.bearing_alignment / 10
                self.reports.spatial.antenna_height = self.raw_reports.r04c4.antenna_height / 1000
                try:
                    self.reports.spatial.light = OLMH_VAL2STR_MAP[self.raw_reports.r04c4.accent_light]
                except KeyError:
                    self.reports.spatial.light = "unknown"
                    logging.warning(f"Unknown accent_light value {self.raw_reports.r04c4.accent_light}")

            case REPORTS_IDS.r_06C4: # BLANKING
                self.raw_reports.r06c4 = RadarReport06C4(raw_packet)
                # TODO
            case REPORTS_IDS.r_08C4: #FILTERS
                self.raw_reports.r08c4 = RadarReport08C4(raw_packet)

                try:
                    self.reports.filters.sea_state = SEA_STATE_VAL2STR_MAP[self.raw_reports.r08c4.sea_state]
                except KeyError:
                    self.reports.filters.sea_state = "unknown"

                try:
                    self.reports.filters.local_interference_filter = OLH_VAL2STR_MAP[self.raw_reports.r08c4.local_interference_filter]
                except KeyError:
                    self.reports.filters.local_interference_filter = "unknown"
                    logging.warning(f"Unknown local_interference_filter value: {self.raw_reports.r08c4.local_interference_filter}")

                try:
                    self.reports.filters.scan_speed = SCAN_SPEED_VAL2STR_MAP[self.raw_reports.r08c4.scan_speed]
                except KeyError:
                    self.reports.filters.scan_speed = "unknown"
                    logging.warning(f"Unknown scan_speed value: {self.raw_reports.r08c4.scan_speed}")

                self.reports.filters.auto_side_lobe_suppression = self.raw_reports.r08c4.auto_side_lobe_suppression

                self.reports.filters.side_lobe_suppression = self.raw_reports.r08c4.side_lobe_suppression

                try:
                    self.reports.filters.noise_rejection = OLH_VAL2STR_MAP[self.raw_reports.r08c4.noise_rejection]
                except KeyError:
                    self.reports.filters.noise_rejection = "unknown"
                    logging.warning(f'Unknown noise_rejection value: {self.raw_reports.r08c4.noise_rejection}')

                try:
                    self.reports.filters.target_separation = OLH_VAL2STR_MAP[self.raw_reports.r08c4.target_separation]
                except KeyError:
                    self.reports.filters.target_separation = "unknown"
                    logging.warning(f"Unknown target_separation value: {self.raw_reports.r08c4.target_separation}")

                # FIXME TEST THESE
                self.reports.filters.sea_clutter = self.raw_reports.r08c4.sea_clutter
                self.reports.filters.auto_sea_clutter_nudge = self.raw_reports.r08c4.auto_sea_clutter

                try:
                    self.reports.filters.doppler_mode = DOPPLER_MODE_VAL2STR_MAP[self.raw_reports.r08c4.doppler_mode]
                except KeyError:
                    self.reports.filters.doppler_mode = "unknown"
                    logging.warning(f"Unknown doppler_mode value: {self.raw_reports.r08c4.doppler_mode}")
                self.reports.filters.doppler_speed = self.raw_reports.r08c4.doppler_speed / 100

            case REPORTS_IDS.r_12C4: # SERIAL
                self.raw_reports.r12c4 = RadarReport12C4(raw_packet)
                # TODO
            case _:
                logging.warning(f"report {raw_packet[:2]} unknown")

    def process_data(self, in_data):

        # PACKET MIGHT BE BROKEN FIXME
        raw_sector = RawSectorData(in_data)

        logging.debug(f"Number of spokes in sector: {raw_sector.number_of_spokes}")
        sector_data = SectorData()
        sector_data.time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        sector_data.number_of_spokes = raw_sector.number_of_spokes

        for raw_spoke in raw_sector.spokes:
            #logging.debug(f"spoke number: {raw_spoke.spoke_number}, angle: {raw_spoke.angle * 360 / 4096}, heading: {raw_spoke.heading}")
            #logging.debug(f"small range: {hex(raw_spoke.small_range)} | {raw_spoke.small_range}, large range {hex(raw_spoke.large_range)}| {raw_spoke.large_range}")
            #logging.debug(f"rotation_angle: {raw_spoke.rotation_range}")
            spoke_data = SpokeData()

            spoke_data.spoke_number = raw_spoke.spoke_number
            spoke_data.heading = raw_spoke.heading
            spoke_data.angle = raw_spoke.angle * 360 / 4096

            if raw_spoke.status not in [0x02, 0x12]: # Valid # and not 0x12 #according to NavicoReceive
                if self.reports.system.radar_type == NavicoRadarType.navicoBR24:
                    logging.warning("Navico BR24 is not tested")
                    spoke_data._range = raw_spoke.small_range * (10 / 2 ** (1/2))

                else:
                    if raw_spoke.large_range == 0x80:
                        if raw_spoke.small_range == 0xffff:
                            spoke_data._range = 0
                        else:
                            spoke_data._range = raw_spoke.small_range / 4

                    elif self.reports.system.radar_type in [NavicoRadarType.navico4G, NavicoRadarType.navico3G]:
                        spoke_data._range = raw_spoke.large_range * 64

                    elif self.reports.system.radar_type == NavicoRadarType.navicoHALO:
                        spoke_data._range = raw_spoke.large_range * raw_spoke.small_range / 512

                    else:
                        logging.error(f"Unknown radar type {self.reports.system.radar_type}. This should not happen.")

                logging.debug(
                    f"Spoke #: {spoke_data.spoke_number}, range: {spoke_data._range}, angle: {spoke_data.angle}")

                spoke_data.intensities = self.unpack_4bit_gray_scale(raw_spoke.data)

            else:
                logging.warning("Invalid Spoke")

            sector_data.spoke_data.append(spoke_data)

        self.write_sector_data(sector_data)
        self.writing_queue.put((self.write_sector_data, sector_data))

    def unpack_4bit_gray_scale(self, data):
        """FIXME UPDATE THIS FOR DOOPLER

        """
        data_4bit = []
        for _bytes in data:
            low_nibble = _bytes & 0x0F
            high_nibble = (_bytes >> 4) & 0x0F

            data_4bit.extend([low_nibble, high_nibble])

        return data_4bit

    ### Belows are all the commands method ###
    def keep_alive(self):
        """FIXME MAYBE ADD MORE FLAG FOR KEEP_ALIVE ?"""
        while not self.stop_flag:
            self.stay_on_cmd()
            time.sleep(self.keep_alive_interval)

    def stay_on_cmd(self):
        self.send_pack_data(StayOnCmd.A)# maybe just this will work

    def get_reports(self):
        # gets report 2,3,4,8
        # settings, system, spatail, filter
        self.send_pack_data(ReportCmds.R284)
        self.send_pack_data(ReportCmds.R3)

    def transmit(self):
        self.send_pack_data(TxOnCmds.A)
        self.send_pack_data(TxOnCmds.B)
        logging.info("Transmit Started")

    def standby(self):
        self.send_pack_data(TxOffCmds.A)
        self.send_pack_data(TxOffCmds.B)
        logging.info("Transmit Stopped")

    def sea_clutter_nudge(self, value):
        value = int(max(-128, min(127, value)))
        self.send_pack_data(SeaClutterNudgeCmd(self.radar_user_config.auto_sea_clutter, value))

    def set_sector_blanking(self):
        """ # TODO
        ### DEDUCTION ###

        This command sets no transmit sectors
        You can set up to 4 sectors, which are the blanking sectors

        First the ENABLE COMMAND
        [
            register = 0x0d
            command  = 0xc1
            sector = (0x00 to 0x03) maybe or maybe 1-4 dont know yet.
            3 bytes 0x00 padding
            enable = [0x00 or 0x01] I would guess
        ]
        Then the Angle command
        [
            register = 0xc0
            command 0xc1
            sector = (0x00 to 0x03) maybe or maybe 1-4 dont know yet.
            3 bytes 0x00 padding
            start_angle = 2bytes (degree to decidegrees)
            end_angle = 2bytes (degree to decidegrees)
        """

    def commands(self, key, value):
        """TODO MAKE INDIVIDUAL COMMANDS"""
        cmd = None
        # valid_cmd = [
        #     "range", "range_custom", "bearing", "gain", "sea_clutter", "rain_clutter",
        #     "side_lobe", "interference_rejection", "sea_state", "scan_speed",
        #     "mode", "target_expansion", "target_separation", "noise_rejection", "doppler"
        # ]

        match key:
            case "range":
                cmd = RangeCmd.pack(value=int(RANGES_VALS_LIST[value] * 10))

            case "bearing":
                cmd = BearingAlignmentCmd.pack(value=int(value * 10))

            case "gain":
                cmd = GainCmd.pack(auto=self.radar_user_config.auto_gain, value=min(int(value * 255 / 100), 255))

            case "antenna_height":
                cmd = AntennaHeightCmd.pack(value=int(value * 1000))

            case "scan_speed":
                cmd = ScanSpeedCmd.pack(value=SCAN_SPEED_STR2VAL_MAP[value])

            case "sea_state":
                cmd = SeaStateAutoCmd.pack(value=SEA_STATE_STR2VAL_MAP[value])

            case "sea_clutter":
                cmd = SeaClutterCmd.pack(auto=self.radar_user_config.auto_sea_clutter, value=min(int(value * 255 / 100), 255))

            case "rain_clutter":
                cmd = RainClutterCmd.pack(auto=self.radar_user_config.auto_rain_clutter, value=min(int(value * 255 / 100), 255))

            case "interference_rejection":
                cmd = InterferenceRejectionCmd.pack(value=OLMH_STR2VAL_MAP[value])

            case "local_interference_filter":
                cmd = LocalInterferenceFilterCmd.pack(value=OLMH_STR2VAL_MAP[value])

            case "side_lobe_suppression":
                cmd = SidelobeSuppressionCmd.pack(auto=self.radar_user_config.auto_side_lobe_suppression, value=min(int(value * 255 / 100), 255))

            case "mode":
                cmd = ModeCmd.pack(value=MODE_STR2VAL_MAP[value])

            case "target_expansion": ## could be 0x09 for BR24, G4 and G3 FIXME
                cmd = TargetExpansionCmd.pack(value=OLMH_STR2VAL_MAP[value])

            case "target_separation":
                cmd = TargetSeparationCmd.pack(value=OLMH_STR2VAL_MAP[value])

            case "noise_rejection":
                cmd = NoiseRejectionCmd.pack(value=OLMH_STR2VAL_MAP[value])

            case "doppler_mode":
                cmd = DopplerModeCmd.pack(value=DOPPLER_MODE_STR2VAL_MAP[value])

            case "doppler_speed":
                cmd = DopplerSpeedCmd.pack(value=int(value * 100))

            case "light":
                cmd = LightCmd.pack(value=OLMH_STR2VAL_MAP[value])

            case "target_boost":
                cmd = TargetBoostCmd.pack(value=OLH_STR2VAL_MAP[value])

            case _:
                logging.error(f"Invalid command {key}:{value}")
        if cmd:
            self.send_pack_data(cmd)

    def send_user_config_parameters(self, radar_parameters: NavicoUserConfig):
        # FIXME do all loggings
        if radar_parameters._range is not None:
            self.commands("range", radar_parameters._range)
            logging.info(f"range set: {radar_parameters._range}")

        if radar_parameters.bearing is not None:
            self.commands("bearing", radar_parameters.bearing)
            logging.info(f"bearing set: {radar_parameters.bearing}")

        if radar_parameters.gain is not None:
            self.commands("gain", radar_parameters.gain)
            logging.info(f"gain set: {radar_parameters.gain}")

        if radar_parameters.antenna_height is not None:
            self.commands("antenna_height", radar_parameters.antenna_height)
            logging.info(f"antenna_height set: {radar_parameters.antenna_height}")

        if radar_parameters.scan_speed is not None:
            self.commands("scan_speed", radar_parameters.scan_speed)
            logging.info(f"scan_speed set: {radar_parameters.scan_speed}")

        if radar_parameters.sea_state is not None:
            self.commands("sea_state", radar_parameters.sea_state)

        if radar_parameters.sea_clutter is not None:
            self.commands("sea_clutter", radar_parameters.sea_clutter)

        if radar_parameters.rain_clutter is not None:
            self.commands("rain_clutter", radar_parameters.rain_clutter)

        if radar_parameters.interference_rejection is not None:
            self.commands("interference_rejection", radar_parameters.interference_rejection)

        if radar_parameters.local_inteference_filer is not None:
            self.commands("local_interference_filer", radar_parameters.local_inteference_filer)

        if radar_parameters.side_lobe_suppression is not None:
            self.commands('side_lobe_suppression', radar_parameters.side_lobe_suppression)

        if radar_parameters.mode is not None:
            self.commands("mode", radar_parameters.mode)

        if radar_parameters.target_expansion is not None:
            self.commands("target_expansion", radar_parameters.target_expansion)

        if radar_parameters.target_separation is not None:
            self.commands("target_separation", radar_parameters.target_separation)

        if radar_parameters.target_boost is not None:
            self.commands("target_boost", radar_parameters.target_boost)

        if radar_parameters.noise_rejection is not None:
            self.commands("noise_rejection", radar_parameters.noise_rejection)

        if radar_parameters.doppler_mode is not None:
            self.commands("doppler_mode", radar_parameters.doppler_mode)

        if radar_parameters.doppler_speed is not None:
            self.commands("doppler_speed", radar_parameters.doppler_speed)

        if radar_parameters.light is not None:
            self.commands("light", radar_parameters.light)

    def writer(self):
        while not self.stop_flag:
            _write_task, *args = self.writing_queue.get()
            _write_task(*args)

    def write_sector_data(self, sector_data: SectorData):
        with open(self.data_path, "a") as f:
            f.write(f"FH:{sector_data.time},{sector_data.number_of_spokes}\n")
            for spoke_data in sector_data.spoke_data:
                f.write(f"SH:{spoke_data.spoke_number},{spoke_data.angle},{spoke_data._range}\n")
                f.write(f"SD:" + str(spoke_data.intensities)[1:-1].replace(' ', '') + "\n") #FIXME

    def write_raw_data_packet(self, raw_data: bytearray):
        with open(self.raw_data_path, "wb") as f:
            f.write(raw_data)

    def write_raw_report_packet(self, report_id: str, raw_report: bytearray):
        with open(self.raw_reports_path[report_id], "wb") as f:
            f.write(raw_report)


def wake_up_navico_radar():
    cmd = struct.pack("2B", 0x01,0xb1)
    send_socket = create_udp_socket()
    send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
    _nbytes_sent = send_socket.sendto(cmd, (ENTRY_GROUP_ADDRESS, ENTRY_GROUP_PORT))
    if _nbytes_sent != 2:
        logging.warning("Failed to send WakeUp command")
    else:
        logging.debug("WakeUp command sent")
    send_socket.close()