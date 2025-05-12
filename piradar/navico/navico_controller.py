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

WAKE_UP_SLEEP = 0.5
REPORT_SLEEP = 1e-3
DATA_SLEEP = 1e-4  # 1e-5 didn't seem to be enough.
SEND_SLEEP = 1e-2


class NavicoRadarType:
    navico4G = "4G"
    navico3G = "3G"
    navicoBR24 = "BR24"
    navicoHALO = "HALO"


class RadarStatus:
    transmit = "transmit"
    spinning_up = "spinning_up"
    standby = "standby"


RADAR_ID2TYPE_MAP = {
    0x01: NavicoRadarType.navico4G,
    0x08: NavicoRadarType.navico3G,
    0x0F: NavicoRadarType.navicoBR24,
    0x00: NavicoRadarType.navicoHALO
}

RANGES_PRESETS = {
    'p1': 50, 'p2': 75, 'p3': 100, 'p4': 250, 'p5': 500, 'p6': 750, 'p7': 1000,
    'p8': 1500, 'p9': 2000, 'p10': 4000, 'p11': 6000, 'p12': 8000,
    'p13': 12000, 'p14': 15000, 'p15': 24000
}

OLMH_VAL2STR_MAP = {0: "off", 1: "low", 2: "medium", 3: "high"}
OLMH_STR2VAL_MAP = {"off": 0, "low": 1, "medium": 2, "high": 3}

OLH_VAL2STR_MAP = {0: "off", 1: "low", 2: "high"}
OLH_STR2VAL_MAP = {"off": 0, "low": 1, "high": 2}

RADAR_STATUS_VAL2STR_MAP = {1: RadarStatus.standby, 2: RadarStatus.transmit, 5: RadarStatus.spinning_up}
RADAR_STATUS_STR2VAL_MAP = {RadarStatus.standby: 1, RadarStatus.transmit: 2, RadarStatus.spinning_up: 5}

MODE_VAL2STR_MAP = {0: "custom", 1: "harbor", 2: "offshore", 4: "weather", 5: "bird", 255: "unknown"}
MODE_STR2VAL_MAP = {"custom": 0, "harbor": 1, "offshore": 2, "weather": 4, "bird": 5}

SEA_STATE_VAL2STR_MAP = {0: "calm", 1: "moderate", 2: "rough"}
SEA_STATE_STR2VAL_MAP = {"calm": 0, "moderate": 1, "rough": 2}

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
    gain_auto: bool = None
    sea_clutter_auto: str = None  # if sea_state is in auto mode ?auto_sea and auto_rain
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
class SectorBlanking:
    enable: bool = None
    start: float = None
    stop: float = None


@dataclass
class BlankingReport:
    """Report 06c4"""
    sector_0 = SectorBlanking()
    sector_1 = SectorBlanking()
    sector_2 = SectorBlanking()
    sector_3 = SectorBlanking()


@dataclass
class FilterReport:
    """Report 08C4"""
    sea_state: str = None
    local_interference_filter: str = None
    scan_speed: str = None  # why is scanspeed here not in the 04C4 reports....
    side_lobe_suppression_auto: bool = None
    side_lobe_suppression: int = None
    noise_rejection: str = None
    target_separation: str = None
    sea_clutter_08c4: int = None
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
    filter = FilterReport()
    serial = SerialNumberReport()


@dataclass
class SpokeData:
    spoke_number: int = None
    heading: float = None
    angle: float = None
    _range: float = None
    intensities: list[float] = None


@dataclass
class FrameData:
    time: str = None
    number_of_spokes: int = None
    gain: int = None
    spoke_data: list[SpokeData] = None

    def __post_init__(self):
        self.spoke_data = []


@dataclass
class NavicoRadarAutoSettings:
    gain_auto: bool = False
    sea_clutter_auto: bool = False
    rain_clutter_auto: bool = False
    side_lobe_suppression_auto: bool = False


@dataclass
class NavicoBlankingSettings:
    sector_0 = False
    sector_1 = False
    sector_2 = False
    sector_3 = False


class NavicoRadarController:
    """
    Radar models default is HALO since it doesnt seem to the the system report. However 4G does ...


    FIXME add Flags (signal) to hold thread until socket are open etc
    FIXME add try -except in case error occurs when creating sockets.
    """

    def __init__(
            self, multicast_interfaces: MulticastInterfaces,
            report_output_dir: str,
            connect_timeout: float,
            keep_alive_interval: int = 10,
    ):
        self.address_set = multicast_interfaces
        self.report_output_dir = report_output_dir
        self.keep_alive_interval = keep_alive_interval
        self.connect_timeout = connect_timeout
        self.raw_reports_path = {
            report_id: Path(self.report_output_dir).joinpath(f"raw_report_{hex(report_id)}.raw")
            for report_id in REPORTS_IDS
        }

        self.send_socket = None

        self.data_socket = None
        self.report_socket = None

        self.data_thread: threading.Thread = None
        self.report_thread: threading.Thread = None
        self.keep_alive_thread: threading.Thread = None

        self.data_writer = RadarDataWriter(self)
        self.data_recorder = RadarDataRecorder(self)

        self.radar_was_detected = False
        self.is_connected = False
        self.is_receiving_data = False

        self.stop_flag = False

        ### RADAR PARAMETER ###
        # Not clear how to update this at the moment. Or use it
        self.auto_settings = NavicoRadarAutoSettings()
        self.blanking_setting = NavicoBlankingSettings()

        ### Reports Object ###
        self.raw_reports = RawReports()
        self.reports = Reports()

        # Halo don't seem to send the radar type so just go with it by default.
        self.reports.system.radar_type = NavicoRadarType.navicoHALO

        self.sector_blanking_sector_map = {
            0: self.reports.blanking.sector_0,
            1: self.reports.blanking.sector_1,
            2: self.reports.blanking.sector_2,
            3: self.reports.blanking.sector_3,
        }

        self.connect()
        if self.is_connected:
            self.start_keep_alive_thread()

            self.get_reports()

    def connect(self):
        if self.is_connected:
            return

        self.stop_flag = False
        self.init_report_socket()
        self.init_data_socket()
        self.init_send_socket()

        self.start_report_thread()
        self.start_data_thread()
        self.data_writer.start_thread()

        logging.info("Waiting for radar ...")
        for _nct in range(int(self.connect_timeout / WAKE_UP_SLEEP)):
            if not self.radar_was_detected:  # this is unlocked in the listen report thread
                logging.info(f"Waiting for radar ({_nct + 1})")
                wake_up_navico_radar()  # this might not be necessary but hey !...
                time.sleep(WAKE_UP_SLEEP)
                continue

            logging.info("Radar detected on network")
            self.is_connected = True
            return

        logging.info("Could not connect. Radar was not detected.")
        self.disconnect()

    def disconnect(self):
        if not self.is_connected:
            return

        self.data_recorder.stop_recording_data()

        logging.info("Disconnect all called.")
        self.data_writer.writing_queue.queue.clear()
        self.stop_flag = True
        self.report_thread.join()
        self.data_thread.join()
        self.data_writer.writer_thread.join()
        if self.keep_alive_thread is not None:
            self.keep_alive_thread.join()

        logging.info("All threads closed")

        self.report_socket.close()
        self.data_socket.close()
        self.send_socket.close()
        logging.info("All sockets closed")

        self.is_connected = False

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
        self.report_thread = threading.Thread(name="report", target=self.report_listen, daemon=True)
        self.report_thread.start()
        logging.debug("Report thread started")

    def start_data_thread(self):
        self.data_thread = threading.Thread(name="data", target=self.data_listen, daemon=True)
        self.data_thread.start()
        logging.debug("Data thread started")

    def start_keep_alive_thread(self):
        self.keep_alive_thread = threading.Thread(name="keep", target=self.keep_alive, daemon=True)
        self.keep_alive_thread.start()
        logging.debug("Keep alive thread started")

    def send_pack_data(self, packed_data):
        try:
            _nbytes_sent = self.send_socket.sendto(packed_data,
                                                   (self.address_set.send.address, self.address_set.send.port))
            if _nbytes_sent != len(packed_data):
                logging.error(
                    f"Failed to send command {packed_data} to {self.address_set.send.address, self.address_set.send.port}.")
            else:
                logging.debug(f"Sending: {packed_data} to {self.address_set.send.address, self.address_set.send.port}")
            time.sleep(SEND_SLEEP)  # not to overwhelm. Maybe this should be handled by a thread and a queue.
            # maybe it's fine.
        except socket.error as e:
            logging.error(f"Failed to send command {packed_data}. Error: {e}")

    def keep_alive(self):
        """FIXME MAYBE ADD MORE FLAG FOR KEEP_ALIVE ?"""
        while not self.stop_flag:
            self.stay_on_cmd()
            time.sleep(self.keep_alive_interval)

    # def start_recording_data(self, output_file: str, number_of_sector_to_record: int):
    #     if self.is_recording_data:
    #         logging.warning('Data recording already started')
    #         return
    #
    #     self.raw_data_output_file = output_file
    #     logging.info('Data recording started')
    #     self.number_of_sector_to_record = number_of_sector_to_record
    #     self.is_recording_data = True
    #
    #     self._reset_recording_vales()  # reset value (maybe not necessary but does cost much)
    #
    # def stop_recording_data(self):
    #     if not self.is_recording_data:
    #         logging.warning('Data recording already stopped')
    #         return
    #
    #     logging.info('Data recording stopped')
    #     self.is_recording_data = False
    #
    #     self._reset_recording_vales()  # reset value (maybe not necessary but does cost much)
    #
    # def _reset_recording_vales(self):
    #     self.sector_first_spoke_number = None
    #     self.current_spoke_number = None
    #     self.last_spoke_number = None
    #     self.sector_recorded_count = 0
    #
    # def check_data_recording_conditions(self):
    #     if self.sector_first_spoke_number is None:
    #         self.sector_first_spoke_number = self.current_spoke_number
    #         self.last_spoke_number = -1
    #
    #     elif self.current_spoke_number > self.last_spoke_number:
    #         self.last_spoke_number = self.current_spoke_number
    #
    #     elif self.current_spoke_number > self.sector_first_spoke_number:
    #         self.last_spoke_number = self.current_spoke_number
    #         self.sector_recorded_count += 1
    #         logging.info(f"Sector recorded {self.sector_recorded_count}")
    #
    #         if self.sector_recorded_count >= self.number_of_sector_to_record:
    #             logging.info("Sector recorded count reached.")
    #             self.stop_recording_data()

    def report_listen(self):
        while not self.stop_flag:  # have thread specific flags as well
            try:
                raw_packet = self.report_socket.recv(RCV_BUFF)  # 1 second socket timeout
            except socket.timeout:
                continue

            if raw_packet and len(raw_packet) >= 2:
                self.radar_was_detected = True
                self.process_report(raw_packet=raw_packet)

            time.sleep(REPORT_SLEEP)

    def data_listen(self):
        while not self.stop_flag:  # have thread specific flags as well
            try:
                raw_packet = self.data_socket.recv(RCV_BUFF)  # 1 second socket timeout
                self.is_receiving_data = True
            except socket.timeout:
                continue

            if raw_packet:
                logging.debug("Data received")
                try:
                    self.process_data(in_data=raw_packet)
                except Exception as e:
                    logging.error(f"Error Raise when trying to process data: {e}")
                    continue

            time.sleep(DATA_SLEEP)

    def process_report(self, raw_packet):
        # TODO DECODE ALL MISSING
        report_id = struct.unpack("!H", raw_packet[:2])[0]
        logging.debug(f"report received: {raw_packet[:2]}")
        if report_id in REPORTS_IDS:
            self.data_writer.write_report(report_id=report_id, raw_packet=raw_packet)
        else:
            logging.warning(f"report {raw_packet[:2]} unknown")
            return

        match report_id:
            case REPORTS_IDS.r_01B2:  # '#case b'\xb2\x01':
                self.raw_reports.r01b2 = RadarReport01B2(raw_packet)

            case REPORTS_IDS.r_01C4:  #STATUS
                self.raw_reports.r01c4 = RadarReport01C4(raw_packet)
                try:  # RADAR STATUS --------------
                    self.reports.status.status = RADAR_STATUS_VAL2STR_MAP[self.raw_reports.r01c4.radar_status]
                except KeyError:
                    self.reports.status.status = "unknown"
                    logging.warning(f"Unknown RadarReport01C4 status: {self.raw_reports.r01c4.radar_status}")

            case REPORTS_IDS.r_02C4:  # SETTINGS
                self.raw_reports.r02c4 = RadarReport02C4(raw_packet)

                # RANGE --------------
                self.reports.setting._range = self.raw_reports.r02c4.range / 10

                try:  # MODE --------------
                    self.reports.setting.mode = MODE_VAL2STR_MAP[
                        self.raw_reports.r02c4.mode]  #Raise or log warning for unknown type TODO
                except KeyError:
                    self.reports.setting.mode = "unknown"
                    logging.warning(f"Unknown mode: {self.raw_reports.r02c4.mode}")

                # GAIN  & GAIN AUTO --------------
                self.reports.setting.gain = self.raw_reports.r02c4.gain
                self.reports.setting.gain_auto = bool(self.raw_reports.r02c4.auto_gain)

                # SEA CUTTER & SEA CLUTTER AUTO --------------
                self.reports.setting.sea_clutter = self.raw_reports.r02c4.sea_clutter
                self.reports.setting.sea_clutter_auto = bool(self.raw_reports.r02c4.sea_clutter_auto)

                # RAIN CLUTTER --------------
                self.reports.setting.rain_clutter = self.raw_reports.r02c4.rain_clutter
                # no auto flag for rain clutter ???

                try:  # INTERFERENCE REJECTION --------------
                    self.reports.setting.interference_rejection = OLMH_VAL2STR_MAP[
                        self.raw_reports.r02c4.interference_rejection]
                except KeyError:
                    self.reports.setting.interference_rejection = "unknown"
                    logging.warning(
                        f"Unknown interference_rejection value: {self.raw_reports.r02c4.interference_rejection}")

                # TARGET EXPANSION --------------
                if self.reports.system.radar_type is not NavicoRadarType.navicoHALO:  # G4, G3 not available on BR24 ? maybe
                    # Seems to be a special case ? maybe map to high (off, high)
                    self.reports.setting.target_expansion = {0: 'off', 1: 'high'}[
                        self.raw_reports.r02c4.target_expansion]
                else:
                    try:
                        self.reports.setting.target_expansion = OLMH_VAL2STR_MAP[
                            self.raw_reports.r02c4.target_expansion]
                    except KeyError:
                        self.reports.setting.target_expansion = "unknown"
                        logging.warning(f"Unknown target_expansion value: {self.raw_reports.r02c4.target_expansion}")

                try:  # TARGET BOOST --------------
                    self.reports.setting.target_boost = OLH_VAL2STR_MAP[
                        self.raw_reports.r02c4.target_boost]  #missing in commands
                except KeyError:
                    self.reports.setting.target_boost = "unknown"
                    logging.warning(f"Unknown target_boost value: {self.raw_reports.r02c4.target_boost}")

            case REPORTS_IDS.r_03C4:  # SYSTEM # doesn't seem to be sent by Halo. odd.
                self.raw_reports.r03c4 = RadarReport03C4(raw_packet)

                try:  # RADAR TYPE --------------
                    self.reports.system.radar_type = RADAR_ID2TYPE_MAP[self.raw_reports.r03c4.radar_type]
                except KeyError:
                    self.reports.system.radar_type = "unknown"
                    logging.warning(f"Unknown radar_type: {self.raw_reports.r03c4.radar_type}")

            case REPORTS_IDS.r_04C4:  # SPATIAL
                self.raw_reports.r04c4 = RadarReport04C4(raw_packet)

                # BEARING --------------
                self.reports.spatial.bearing = self.raw_reports.r04c4.bearing_alignment / 10

                # ANTENNA HEIGHT --------------
                self.reports.spatial.antenna_height = self.raw_reports.r04c4.antenna_height / 1000
                try:
                    self.reports.spatial.light = OLMH_VAL2STR_MAP[self.raw_reports.r04c4.accent_light]
                except KeyError:
                    self.reports.spatial.light = "unknown"
                    logging.warning(f"Unknown accent_light value {self.raw_reports.r04c4.accent_light}")

            case REPORTS_IDS.r_06C4:  # BLANKING
                self.raw_reports.r06c4 = RadarReport06C4(raw_packet)
                for si in range(4):
                    _blanking_sector = {
                        0: self.reports.blanking.sector_0,
                        1: self.reports.blanking.sector_1,
                        2: self.reports.blanking.sector_2,
                        3: self.reports.blanking.sector_3,
                    }[si]
                    _blanking_sector.enable = bool(self.raw_reports.r06c4.blanking[si].enable)
                    _blanking_sector.start = self.raw_reports.r06c4.blanking[si].start / 10
                    _blanking_sector.stop = self.raw_reports.r06c4.blanking[si].stop / 10

            case REPORTS_IDS.r_08C4:  # FILTERS
                self.raw_reports.r08c4 = RadarReport08C4(raw_packet)

                try:  # SEA STATE --------------
                    self.reports.filter.sea_state = SEA_STATE_VAL2STR_MAP[self.raw_reports.r08c4.sea_state]
                except KeyError:
                    self.reports.filter.sea_state = "unknown"

                try:  # LOCAL INTERFERENCE FILTER --------------
                    self.reports.filter.local_interference_filter = OLMH_VAL2STR_MAP[
                        self.raw_reports.r08c4.local_interference_filter]
                except KeyError:
                    self.reports.filter.local_interference_filter = "unknown"
                    logging.warning(
                        f"Unknown local_interference_filter value: {self.raw_reports.r08c4.local_interference_filter}")

                try:  # SCAN SPEED --------------
                    self.reports.filter.scan_speed = SCAN_SPEED_VAL2STR_MAP[self.raw_reports.r08c4.scan_speed]
                except KeyError:
                    self.reports.filter.scan_speed = "unknown"
                    logging.warning(f"Unknown scan_speed value: {self.raw_reports.r08c4.scan_speed}")

                # SIDE LOBE SUPPRESSION AUTO --------------
                self.reports.filter.side_lobe_suppression_auto = bool(self.raw_reports.r08c4.side_lobe_suppression_auto)

                # SIDE LOBE SUPPRESSION --------------
                self.reports.filter.side_lobe_suppression = self.raw_reports.r08c4.side_lobe_suppression

                try:  # NOISE REJECTION --------------
                    self.reports.filter.noise_rejection = OLMH_VAL2STR_MAP[self.raw_reports.r08c4.noise_rejection]
                except KeyError:
                    self.reports.filter.noise_rejection = "unknown"
                    logging.warning(f'Unknown noise_rejection value: {self.raw_reports.r08c4.noise_rejection}')

                try:  # TARGET SEPARATION --------------
                    self.reports.filter.target_separation = OLMH_VAL2STR_MAP[self.raw_reports.r08c4.target_separation]
                except KeyError:
                    self.reports.filter.target_separation = "unknown"
                    logging.warning(f"Unknown target_separation value: {self.raw_reports.r08c4.target_separation}")

                # FIXME TEST THESE
                # SEA CLUTTER 08C4 --------------
                self.reports.filter.sea_clutter_08c4 = self.raw_reports.r08c4.sea_clutter
                # AUTO SEA CLUTTER NUDGE --------------
                self.reports.filter.auto_sea_clutter_nudge = self.raw_reports.r08c4.auto_sea_clutter

                try:  # DOPPLER MODE --------------
                    self.reports.filter.doppler_mode = DOPPLER_MODE_VAL2STR_MAP[self.raw_reports.r08c4.doppler_mode]
                except KeyError:
                    self.reports.filter.doppler_mode = "unknown"
                    logging.warning(f"Unknown doppler_mode value: {self.raw_reports.r08c4.doppler_mode}")

                #  Doppler Speed --------------
                self.reports.filter.doppler_speed = self.raw_reports.r08c4.doppler_speed / 100

            case REPORTS_IDS.r_12C4:  # SERIAL
                self.raw_reports.r12c4 = RadarReport12C4(raw_packet)
                # TODO
            case _:  # Should (will) never get here, but I will leave it anyway.
                logging.warning(f"report {raw_packet[:2]} unknown")

    def process_data(self, in_data):
        # This loop should be unlocked if other processes need to unpacked data (arp)
        if self.data_recorder.is_recording:
            raw_frame = RawFrameData(in_data)  # PACKET MIGHT BE BROKEN FIXME

            logging.debug(f"Number of spokes in sector: {raw_frame.number_of_spokes}")

            time_stamp = datetime.datetime.now(datetime.UTC)

            frame_data = FrameData()
            frame_data.time = int(time_stamp.timestamp())  # seconds "<L"
            frame_data.number_of_spokes = raw_frame.number_of_spokes
            frame_data.gain = self.reports.setting.gain

            for raw_spoke in raw_frame.spokes:
                spoke_data = SpokeData()

                spoke_data.spoke_number = raw_spoke.spoke_number

                # record the raw data as is.
                spoke_data.heading = raw_spoke.heading
                spoke_data.angle = raw_spoke.angle

                if raw_spoke.status in [0x02, 0x12]:  # Valid # and not 0x12 #according to NavicoReceive
                    if self.reports.system.radar_type == NavicoRadarType.navicoBR24:
                        logging.warning("Navico BR24 is not tested")
                        spoke_data._range = raw_spoke.small_range * (10 / 2 ** (1 / 2))

                    else:
                        if raw_spoke.large_range == 0x80:
                            if raw_spoke.small_range == 0xffff:
                                spoke_data._range = 0
                            else:
                                spoke_data._range = raw_spoke.small_range / 4

                        elif self.reports.system.radar_type in [NavicoRadarType.navico4G, NavicoRadarType.navico3G]:
                            spoke_data._range = raw_spoke.large_range * 64

                        else:  #elif self.reports.system.radar_type == NavicoRadarType.navicoHALO:
                            spoke_data._range = raw_spoke.large_range * raw_spoke.small_range / 512

                    spoke_data._range = int(spoke_data._range)  # save as integer. meter precision is fine.

                    spoke_data.intensities = raw_spoke.data

                    frame_data.spoke_data.append(spoke_data)
                else:
                    logging.warning("Invalid Spoke")

            last_spoke = frame_data.spoke_data[-1].spoke_number

            if self.data_recorder.is_recording_sector:
                self.data_recorder.check_sector_recording_conditions(spoke_number=last_spoke)
                output_file = self.data_recorder.output_file
            else:
                first_spoke = frame_data.spoke_data[0].spoke_number
                _ts = time_stamp.strftime("%Y%m%dT%H%M%S%f")
                filename = f"{_ts}_{first_spoke}_{last_spoke}"
                output_file = str(Path(self.data_recorder.output_dir) / filename)

            self.data_writer.write_frame(output_file=output_file, frame_data=frame_data)

    #### Belows are all the commands method ####

    def stay_on_cmd(self):
        self.send_pack_data(StayOnCmd.A)  # maybe just this will work

    def get_reports(self):
        # gets report 2,3,4,8
        # settings, system, spatial, filter
        self.send_pack_data(ReportCmds.R284)
        self.send_pack_data(ReportCmds.R3)

    def transmit(self, get_report: bool = False):
        self.send_pack_data(TxOnCmds.A)
        self.send_pack_data(TxOnCmds.B)
        logging.info("Tx On commands sent")
        if get_report:
            self.get_reports()

    def standby(self, get_report: bool = False):
        self.send_pack_data(TxOffCmds.A)
        self.send_pack_data(TxOffCmds.B)
        logging.info("Tx Off commands sent")
        if get_report:
            self.get_reports()

    def set_range(self, value: int | str, get_report: bool = False):
        """Can be a value inf meter or a prest key: ['p1', ... 'p15']"""
        if isinstance(value, str):
            value = RANGES_PRESETS[value]
        else:
            value = max(50, value) # min value is 50 meters
        cmd = RangeCmd.pack(value=int(value * 10))
        self.send_pack_data(cmd)
        if get_report:
            self.get_reports()

    def set_bearing(self, value: int, get_report: bool = False):
        cmd = BearingAlignmentCmd.pack(value=int(min(max(value, 0), 360) * 10))
        self.send_pack_data(cmd)
        if get_report:
            self.get_reports()

    def set_gain(self, value: int, get_report: bool = False):
        cmd = GainCmd.pack(auto=self.auto_settings.gain_auto, value=int(min(max(value, 0), 255)))
        self.send_pack_data(cmd)
        if get_report:
            self.get_reports()

    def set_gain_auto(self, value: bool, get_report: bool = False):
        self.auto_settings.gain_auto = value
        self.set_gain(value=self.reports.setting.gain, get_report=get_report)

    def set_antenna_height(self, value: int, get_report: bool = False):
        cmd = AntennaHeightCmd.pack(value=int(value * 1000))
        self.send_pack_data(cmd)
        if get_report:
            self.get_reports()

    def set_scan_speed(self, value: str, get_report: bool = False):
        if self.reports.status.status is not RadarStatus.transmit:
            logging.warning("Scan speed cannot be change if the radar is not transmitting")
        else:
            cmd = ScanSpeedCmd.pack(value=SCAN_SPEED_STR2VAL_MAP[value])
            self.send_pack_data(cmd)
            if get_report:
                self.get_reports()

    def set_sea_state(self, value: str, get_report: bool = False):
        cmd = SeaStateAutoCmd.pack(value=SEA_STATE_STR2VAL_MAP[value])
        self.send_pack_data(cmd)
        if get_report:
            self.get_reports()

    def set_sea_clutter(self, value: int, get_report: bool = False):
        cmd = SeaClutterCmd.pack(auto=self.auto_settings.sea_clutter_auto, value=min(max(int(value), 0), 255))
        self.send_pack_data(cmd)
        if get_report:
            self.get_reports()

    def set_sea_clutter_auto(self, value: bool, get_report: bool = False):
        self.auto_settings.sea_clutter_auto = value
        self.set_sea_clutter(value=self.reports.setting.sea_clutter, get_report=get_report)

    def set_rain_clutter(self, value: int, get_report: bool = False):
        cmd = RainClutterCmd.pack(auto=self.auto_settings.rain_clutter_auto, value=min(max(int(value), 0), 255))
        self.send_pack_data(cmd)
        if get_report:
            self.get_reports()

    def set_rain_clutter_auto(self, value: bool):
        # No need for reports since no reports has the rain_clutter_auto values
        self.auto_settings.rain_clutter_auto = value
        self.set_rain_clutter(value=self.reports.setting.rain_clutter)

    def set_side_lobe_suppression(self, value: int, get_report: bool = False):
        cmd = SidelobeSuppressionCmd.pack(auto=self.auto_settings.side_lobe_suppression_auto,
                                          value=min(max(int(value), 0), 255))
        self.send_pack_data(cmd)
        if get_report:
            self.get_reports()

    def set_side_lobe_suppression_auto(self, value: bool, get_report: bool = False):
        self.auto_settings.side_lobe_suppression_auto = value
        self.set_side_lobe_suppression(value=self.reports.filter.side_lobe_suppression, get_report=get_report)

    def set_interference_rejection(self, value: str, get_report: bool = False):
        cmd = InterferenceRejectionCmd.pack(value=OLMH_STR2VAL_MAP[value])
        self.send_pack_data(cmd)
        if get_report:
            self.get_reports()

    def set_local_interference_filter(self, value: str, get_report: bool = False):
        cmd = LocalInterferenceFilterCmd.pack(value=OLMH_STR2VAL_MAP[value])
        self.send_pack_data(cmd)
        if get_report:
            self.get_reports()

        # maybe raise warning

    def set_mode(self, value: str, get_report: bool = False):
        logging.warning("Doenst seem to work. At least on G4")
        cmd = ModeCmd.pack(value=MODE_STR2VAL_MAP[value])
        self.send_pack_data(cmd)
        if get_report:
            self.get_reports()

    def set_target_expansion(self, value: str | bool, get_report: bool = False):
        logging.warning("Unsure about the register or values.")

        match self.reports.system.radar_type:
            case NavicoRadarType.navicoHALO:
                cmd = TargetExpansionHaloCmd.pack(value=OLMH_STR2VAL_MAP[value])

            case NavicoRadarType.navico4G | NavicoRadarType.navico3G:
                if value in ['low', 'medium']:
                    logging.warning("Only `off` and `high` are available for target expansion on 4G and 3G (I think).")
                value = {'off': 0, 'low': 1, 'medium': 1, 'high': 1}[value]
                cmd = TargetExpansionCmd.pack(value=value)
            case _:
                logging.warning("target expansion is not available on BR24 (I think).")
                return

        cmd = TargetExpansionCmd.pack(value=bool(value))
        self.send_pack_data(cmd)
        if get_report:
            self.get_reports()

    def set_target_separation(self, value: str, get_report: bool = False):
        cmd = TargetSeparationCmd.pack(value=OLMH_STR2VAL_MAP[value])
        self.send_pack_data(cmd)
        if get_report:
            self.get_reports()

    def set_noise_rejection(self, value: str, get_report: bool = False):
        cmd = NoiseRejectionCmd.pack(value=OLMH_STR2VAL_MAP[value])
        self.send_pack_data(cmd)
        if get_report:
            self.get_reports()

        # check type halo

    def set_doppler_mode(self, value: str, get_report: bool = False):
        if self.reports.system.radar_type is NavicoRadarType.navicoHALO:
            cmd = DopplerModeCmd.pack(value=DOPPLER_MODE_STR2VAL_MAP[value])
            self.send_pack_data(cmd)
            if get_report:
                self.get_reports()

        else:
            logging.warning("Doppler is only available on Halo")

    def set_doppler_speed(self, value: str, get_report: bool = False):
        if self.reports.system.radar_type is NavicoRadarType.navicoHALO:
            cmd = DopplerSpeedCmd.pack(value=int(value * 100))
            self.send_pack_data(cmd)
            if get_report:
                self.get_reports()

        else:
            logging.warning("Doppler is only available on Halo")

        # just halo

    def set_light(self, value: str, get_report: bool = False):
        if self.reports.system.radar_type is NavicoRadarType.navicoHALO:
            cmd = LightCmd.pack(value=OLMH_STR2VAL_MAP[value])
            self.send_pack_data(cmd)
            if get_report:
                self.get_reports()

        else:
            logging.warning("Light is only available on Halo")

    def set_target_boost(self, value: str, get_report: bool = False):
        cmd = TargetBoostCmd.pack(value=OLH_STR2VAL_MAP[value])
        self.send_pack_data(cmd)
        if get_report:
            self.get_reports()

    def sea_clutter_nudge(self, value, get_report: bool = False):
        if self.reports.system.radar_type is NavicoRadarType.navicoHALO:
            logging.warning("Sea clutter nudge not tested yet.")  #FIXME
            value = int(max(-128, min(127, value)))
            cmd = SeaClutterNudgeCmd.pack(self.auto_settings.sea_clutter_auto, value)
            self.send_pack_data(cmd)
            if get_report:
                self.get_reports()

        else:
            logging.warning("Sea clutter nudge is only available on Halo")

    def set_sector_blanking(self, sector_number: int, start: float, stop: float, get_report: bool = False):
        # maybe only for halo but unsure.
        sector_number = int(max(0, min(3, sector_number)))
        start = int(max(0, min(360, start)))
        stop = int(max(0, min(360, stop)))
        if start > stop:
            start, stop = stop, start
        enable = self.sector_blanking_sector_map[sector_number]

        #cmd = EnableBlankingSectorCmd.pack(sector_number, 1) # may need to be enable first...
        #self.send_pack_data(cmd)

        cmd = SetBlankingSectorCmd.pack(
            sector=sector_number,
            enbale=enable,
            start=start*10,
            stop=stop*10
        )
        self.send_pack_data(cmd)

        #cmd = EnableBlankingSectorCmd.pack(sector_number, 0)
        #self.send_pack_data(cmd)
        if get_report:
            self.get_reports()

    def enable_sector_blanking(self, sector_number: int, value: bool, get_report: bool = False):
        # maybe only for halo but unsure.
        sector_number = int(max(0, min(3, sector_number)))

        value = int(value)

        self.sector_blanking_sector_map[sector_number] = bool(value)

        cmd = EnableBlankingSectorCmd.pack(sector_number, value)
        self.send_pack_data(cmd)
        if get_report:
            self.get_reports()


def wake_up_navico_radar():
    # this may not be usefull
    cmd = struct.pack("2B", 0x01, 0xb1)
    send_socket = create_udp_socket()
    send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
    _nbytes_sent = send_socket.sendto(cmd, (ENTRY_GROUP_ADDRESS, ENTRY_GROUP_PORT))
    if _nbytes_sent != 2:
        logging.warning("Failed to send WakeUp command")
    else:
        logging.debug("WakeUp command sent")
    send_socket.close()


class RadarDataWriter:
    def __init__(self, radar_controller):
        self.radar_controller: NavicoRadarController = radar_controller
        self.writer_thread: threading.Thread = None
        self.writing_queue = queue.Queue()
        self.stop_flag = False

    def start_thread(self):
        self.stop_flag = False
        self.writer_thread = threading.Thread(name="writer", target=self.loop, daemon=True)
        self.writer_thread.start()
        logging.debug("Writer thread started")

    def stop(self):
        self.stop_flag = True

    def loop(self):
        while not (self.radar_controller.stop_flag or self.stop_flag):
            try:
                _write_task, *args = self.writing_queue.get(timeout=0.1) # this need to be short too.
                _write_task(*args)
            except queue.Empty:
                time.sleep(0.01) # this need to be short
            except Exception as e:
                logging.error(f"Unexpected error on writer thread: {e}.")

    def write_frame(self, output_file: str, frame_data: FrameData):
        self.writing_queue.put((self._write_raw_frame_data, output_file, frame_data))

    def write_report(self, report_id: str, raw_packet: bytearray):
        self.writing_queue.put((self._write_raw_report_packet, report_id, raw_packet))

    @staticmethod
    def _write_raw_frame_data(output_file: str, sector_data: FrameData):
        with open(Path(output_file).with_suffix(".raw"), "ba") as f:
            packed_frame_header = b"FH" + struct.pack(
                "<LBHHH",
                sector_data.time,
                sector_data.number_of_spokes,
                sector_data.spoke_data[0]._range,  #
                sector_data.spoke_data[0].heading,
                sector_data.gain,
            )
            f.write(packed_frame_header)
            f.write(b"SD")
            for spoke_data in sector_data.spoke_data:
                packed_spoke_data = struct.pack(
                    "<HH512B",
                    spoke_data.spoke_number,
                    spoke_data.angle,
                    *spoke_data.intensities
                )

                f.write(packed_spoke_data)

    def _write_raw_report_packet(self, report_id: str, raw_report: bytearray):
        with open(self.radar_controller.raw_reports_path[report_id], "wb") as f:
            f.write(raw_report)


class RecorderSpokeCounter:
    def __init__(self):
        self.first: int = None
        self.current: int = None
        self.last: int = -1

    def update(self, spoke_number: int):
        self.current = spoke_number

        if self.first is None:
            self.first = self.current
            return 0

        if self.current > self.last:
            self.last = self.current
            return 0

        if self.current > self.first:
            self.last = self.current
            return 1

        return 0


class RadarDataRecorder:
    # Keeps variables (flags, counters) and method relative to data recording.
    def __init__(self, radar_controller: NavicoRadarController):
        self.radar_controller = radar_controller

        self.is_recording = False
        self.is_recording_sector = False
        self.output_dir: str = None # use for continuous
        self.output_file: str = None # use for sector

        # Sector Recording #
        self.spoke_counter: RecorderSpokeCounter = None
        self.sector_count: int = None
        self.number_of_sector_to_record: int = None

    def start_sector_recording(self, output_file: str, number_of_sector_to_record: int):
        if self.is_recording:
            logging.warning('Data recording already started')
            return

        self.output_file = format_path_with_dt_subdir(output_file)
        logging.info('Data recording started')
        self.number_of_sector_to_record = number_of_sector_to_record
        self.sector_count = 0
        self.is_recording = True
        self.is_recording_sector = True

        self.spoke_counter = RecorderSpokeCounter()  # A new counter is made on each call.

    def start_continuous_recording(self, output_dir: str):
        if self.is_recording:
            logging.warning('Data recording already started')
            return
        self.output_dir = format_path_with_dt_subdir(output_dir)
        self.is_recording_sector = False
        self.is_recording = True

    def check_sector_recording_conditions(self, spoke_number):
        if self.is_recording_sector is True:
            self.sector_count += self.spoke_counter.update(spoke_number=spoke_number)

            if self.sector_count >= self.number_of_sector_to_record:
                logging.info("Sector recorded count reached.")
                self.stop_recording_data()

    def stop_recording_data(self):
        if not self.is_recording:
            logging.warning('Data recording already stopped')
            return

        logging.info('Data recording stopped')
        self.is_recording = False
        self.is_recording_sector = False


def format_path_with_dt_subdir(file_path: str) -> str:
    ts = datetime.datetime.now(datetime.UTC)
    day = ts.strftime("%Y%m%d")
    hour = ts.strftime("%H")

    root_dir = Path(file_path).parent
    filename = Path(file_path).name

    outdir = root_dir.joinpath(day, hour)
    outdir.mkdir(exist_ok=True, parents=True)

    return outdir.joinpath(filename)
