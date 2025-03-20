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

import time
import datetime
import struct
import socket
import threading
from typing import Literal
from pathlib import Path
from dataclasses import dataclass

from piradar.network import create_udp_socket, create_udp_multicast_receiver_socket
from piradar.navico.navico_structure import *
from piradar.navico.navico_command import *


HOST = ''
RCV_BUFF = 65535

RANGE_SCALE = 10 * 2 ** (-1/2)

@dataclass
class MulticastAddress:
    address: str | int
    port: int

    def __post_init__(self):
        if isinstance(self.address, int):
            self.address = socket.inet_ntoa(struct.pack('!I', self.address))


@dataclass
class MulticastInterfaces:
    data: MulticastAddress
    send: MulticastAddress
    report: MulticastAddress
    interface: str


@dataclass
class RawReports:
    r01b2: RadarReport01B2 = None
    r01c4: RadarReport01C418 = None
    r02c4: RadarReport02C499 = None
    r03c4: RadarReport03C4129 = None
    r04c4: RadarReport04C466 = None
    r06c4: RadarReport06C468 | RadarReport06C474 = None
    r08C4: RadarReport08C418 | RadarReport08C421 = None
    r12c4: RadarReport12C466 = None


@dataclass
class SpokeData:
    spoke_number: int = None
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
class SettingReport:
    """Report 02C4"""

    _range: float = None
    mode: str = None
    gain: float = None
    sea_state_auto: str = None
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
    interference_rejection: str = None
    scan_speed: str = None # why is scanspeed here not in the 04C4 reports....

    side_lobe_suppression: int = None
    noise_rejection: str = None
    target_separation: str = None
    sea_clutter: int = None # on Halo

    auto_side_lobe_suppresion: bool = None
    auto_sea_clutter: bool = None # on halo



@dataclass
class DopplerReport:
    """Report 08C4"""
    doppler_state: str = None
    doppler_speed: int = None


@dataclass
class SerialNumberReport:
    """Report 12C4"""
    serial_number: str = None


@dataclass
class Reports:
    spatial = SpatialReport()
    system = SystemReport()
    blanking = BlankingReport()
    setting = SettingReport()
    filters = FilterReport()
    doppler = DopplerReport()
    serial = SerialNumberReport()



@dataclass
class RadarParameters:
    # Base
    range: float = None # maybe define literal with pre_define ranges ?
    bearing: float = None
    gain: float = None
    antenna_height: float = None
    scan_speed: Literal["low", "medium", "high"] = None  # Doubt # Default-0, increase-1 ? max-2 ???

    # filters

    sea_state: Literal['off', 'harbour', 'offshore'] = None #automoatic mode ?? sea clutter maybe ?

    sea_clutter: int = None
    rain_clutter: int = None

    interference_rejection: Literal["off", "low", "medium", "high"] = None
    side_lobe_suppression: int = None

    mode: Literal["custom", "harbor", "offshore", "weather", "bird"] = None

    auto_sea_clutter_nudge: int = None

    target_expansion: Literal["off", "low", "medium", "high"] = None
    target_separation: Literal["off", "low", "medium", "high"] = None
    noise_rejection: Literal["off", "low", "medium", "high"] = None

    doppler_mode: Literal['off', 'normal', 'approaching_only'] = None
    doppler_speed: float = None

    light: Literal["off", "low", "medium", "high"] = None

    # auto
    auto_gain: bool = False
    auto_sea_clutter: bool = False
    auto_rain_clutter: bool = False
    auto_side_lobe_suppression: bool = False


class NavicoRadar:

    def __init__(
            self, multicast_interfaces: MulticastInterfaces,
            init_radar_parameters: RadarParameters,
            output_dir: str,
            stay_alive_interval: int = 10,
    ):
        self.address_set = multicast_interfaces
        self.output_dir = output_dir

        self.data_path = Path(self.output_dir).joinpath("ppi_data.txt")
        self.raw_data_path = Path(self.output_dir).joinpath("raw_ppi_data.raw")
        self.raw_reports_path = {
            key: Path(self.output_dir).joinpath("raw_ppi_data.raw") for key in ReportIds.__dict__.keys()
        }

        # make object to store initatil parameter to pass to Radar

        self.send_socket = None

        self.data_socket = None
        self.report_socket = None

        self.data_thread: threading.Thread = None
        self.report_thread: threading.Thread = None
        self.stay_alive_thread: threading.Thread = None
        self.writer_thread: threading.Thread = None

        self.radar_was_detected = False
        self.stop_flag = False

        ### RADAR PARAMETER ###
        # Not clear how to update this at the moment. Or use it
        self.radar_parameters = RadarParameters()

        ### Reports Object ###
        self.raw_reports = RawReports()
        self.reports = Reports()

        self.init_send_socket()
        self.init_report_socket()
        self.init_data_socket()

        self.start_report_thread()
        self.start_data_thread()
        self.start_keep_alive_thread()
        self.start_writer_thread()

        while not self.radar_was_detected:
            time.sleep(1)
            # FIXME add a timeout and raise an Error

        self.send_radar_parameters(init_radar_parameters)


    def init_ouput_path(self):
        self.data_path =

        self.raw_report_paths = {
            ""
        }

    def init_send_socket(self):
        self.send_socket = create_udp_socket()
        self.send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        # not binding required

    def init_report_socket(self):
        self.report_socket = create_udp_multicast_receiver_socket(
            interface_address=self.address_set.interface,
            group_address=self.address_set.report.address,
            group_port=self.address_set.report.port
        )

    def init_data_socket(self):
        self.data_socket = create_udp_multicast_receiver_socket(
            interface_address=self.address_set.interface,
            group_address=self.address_set.data.address,
            group_port=self.address_set.data.port
        )

    def start_report_thread(self):
        self.report_thread = threading.Thread(target=self.report_listen, daemon=True)
        self.report_thread.start()

    def start_data_thread(self):
        self.data_thread = threading.Thread(target=self.data_listen, daemon=True)
        self.data_thread.start()

    def start_keep_alive_thread(self):
        self.keep_alive_thread = threading.Thread(target=self.keep_alive, daemon=True)
        self.keep_alive_thread.start()

    def start_writer_thread(self):
        self.writer_thread = threading.Thread(target=self.writer, daemon=True)
        self.writer_thread.start()

    def send_pack_data(self, packed_data):
        #print(f"sending: {packed_data} to {self.address_set.send.address, self.address_set.send.port}")
        self.send_socket.sendto(packed_data, (self.address_set.send.address, self.address_set.send.port))
        time.sleep(0.1)

    def close_all(self):
        self.stop_flag = True
        self.report_thread.join()
        self.data_thread.join()
        self.keep_alive_thread.join()
        self.writer_thread.join()

        self.report_socket.close()
        self.data_socket.close()
        self.send_socket.close()

    def report_listen(self):
        while not self.stop_flag: # have thread specific flags as well
            try:
                in_data = self.report_socket.recv(RCV_BUFF)
            except socket.timeout:
                continue
            if in_data and len(in_data) >= 2:
                self.radar_was_detected = True
                self.process_report(in_data=in_data)

    def data_listen(self):
        while not self.stop_flag: # have thread specific flags as well
            try:
                in_data = self.data_socket.recv(RCV_BUFF)
                self.write_raw_data_packet(in_data)
            except socket.timeout:
                continue
            if in_data:
                print("Data received")
                self.process_data(in_data=in_data)

    def process_report(self, in_data):
        id = struct.unpack("!H", in_data[:2])[0]
        olmh_map = {0: "off", 1: "low", 2: "medium", 3: "high"} # maybe set as class attributes
        match id:
            case ReportIds._01B2:  # '#case b'\xb2\x01':
                self.raw_reports.r01b2 = RadarReport01B2(in_data)

            case ReportIds._01C4: #STATUS
                self.raw_reports.r01c4 = RadarReport01C418(in_data)
                print(f"report {in_data[:2]} not decoded yet")

            case ReportIds._02C4: #SETTINGS
                self.raw_reports.r02c4 = RadarReport02C499(in_data)

                self.reports.setting._range = self.raw_reports.r02c4.range / 10 #unsure about the division
                mode_map = {0: "custom", 1: "harbor", 2: "offshore", 4: "weather", 5: "bird"}
                if self.raw_reports.r02c4.mode == 255:  # returned 255,
                    self.raw_reports.r02c4.mode = mode_map[0]
                else:
                    self.reports.setting.mode = mode_map[self.raw_reports.r02c4.mode]
                self.reports.setting.gain = self.raw_reports.r02c4.gain * (100 / 255)
                sea_stato_auto_map = {0: "off", 1: "harbour", 2: "offshore"}
                self.reports.setting.sea_state_auto = sea_stato_auto_map[self.raw_reports.r02c4.sea_state_auto]
                self.reports.setting.sea_clutter = self.raw_reports.r02c4.sea_clutter * (100 / 255)
                self.reports.setting.rain_clutter = self.raw_reports.r02c4.rain_clutter * (100 / 255)

                if self.raw_reports.r02c4.interference_rejection: #maybe add `if`s elsewhere ???
                    self.reports.setting.interference_rejection = olmh_map[self.raw_reports.r02c4.interference_rejection]
                if self.raw_reports.r02c4.target_expansion:
                    self.reports.setting.target_expansion = olmh_map[self.raw_reports.r02c4.target_expansion]
                if self.raw_reports.r02c4.target_boost:
                    self.reports.setting.target_boost = olmh_map[self.raw_reports.r02c4.target_boost] #missing in commands

                print(f"report {in_data[:2]} not decoded yet")

            case ReportIds._03C4: # SYSTEM
                self.raw_reports.r03c4 = RadarReport03C4129(in_data)
                # use to get model ?
                print(f"report {in_data[:2]} not decoded yet")

            case ReportIds._04C4: #SPATIAL
                self.raw_reports.r04c4 = RadarReport04C466(in_data)

                self.reports.spatial.bearing = self.raw_reports.r04c4.bearing_alignment / 10
                self.reports.spatial.antenna_height = self.raw_reports.r04c4.antenna_height / 1000
                if self.raw_reports.r04c4.accent_light:
                    self.reports.spatial.light = olmh_map[self.raw_reports.r04c4.accent_light]
                # accent light ??? s

            case ReportIds._06C4: # BLANKING
                match len(in_data):
                    case RadarReport06C468.size:
                        self.raw_reports.r06c4 = RadarReport06C468(in_data)
                    case RadarReport06C474.size:
                        self.raw_reports.r06c4 = RadarReport06C474(in_data)
                    # self.reports.blanking # Fixme

            case ReportIds._08C4: #FILTERS
                match len(in_data):
                    case RadarReport08C418.size: # Without Dooplers
                        self.raw_reports.r08c4 = RadarReport08C418(in_data)

                    case RadarReport08C421.size: #With Dooplers
                        self.raw_reports.r08c4 = RadarReport08C421(in_data)
                # do som,ething like if dopper in raw_reports -> set values
                print(f"report {in_data[:2]} not impletmented yet")

            case ReportIds._12C4: # SERIAL
                report = RadarReport12C466(in_data)
                self.raw_reports.r12c4 = report
                print(f"report {in_data[:2]} not decoded yet")

            case _:
                print(f"report {in_data[:2]} not impletmented yet")
                # report = RadarReport_c408()

    # do something with the report ?

    def process_data(self, in_data):

        # PACKET MIGHT BE BROKEN FIXME
        # Any processing could be done in a new thread using Queue (maybe).
        raw_sector = RawSectorData(in_data)

        print(f"Number of spokes in sector: {raw_sector.number_of_spokes}")
        sector_data = SectorData()
        sector_data.time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        sector_data.number_of_spokes = raw_sector.number_of_spokes

        for raw_spoke in raw_sector.spokes:
            print(f"Spoke number: {raw_spoke.spoke_number} [should be between 0-4096]") #fixme maybe
            # WILL DEPEND ON RADAR TYPE THIS IS JUST FOR HALO FIXME

            print(f"spoke number: {raw_spoke.spoke_number}, "
                  f"angle: {raw_spoke.angle * 360 / 4096}, "
                  f"heading: {raw_spoke.heading}")
            print(f"small range: {hex(raw_spoke.small_range)} | {raw_spoke.small_range}, "
                  f"large range {hex(raw_spoke.large_range)}| {raw_spoke.large_range}")

            spoke_data = SpokeData()
            spoke_data.spoke_number = raw_spoke.spoke_number

            if raw_spoke.status == 2: # Valid
                #### This here could change depending on model
                if raw_spoke.large_range == 128: #why not smaller ? is this the min value for large_range ?
                    if raw_spoke.small_range == -1: # or 0xffff maybe
                        spoke_data._range = 0
                    else:
                        spoke_data._range = raw_spoke.small_range / 4
                else:
                    # I guess this is at normal resolutin using 4 bytes ? with not use a L
                    spoke_data._range = raw_spoke.large_range * raw_spoke.small_range / 512

                spoke_data._range *= RANGE_SCALE # 10 / sqrt(2)

                print(f"Acutal range {spoke_data}")

                spoke_data.angle = raw_spoke.angle * 360 / 4096 # 0..4096 = 0..360

                spoke_data.intensities = []
                for bi in range(512):
                    low = raw_spoke.data[bi] & 0x0f # 0000 1111
                    high = (raw_spoke.data[bi] & 0xf0) >> 4 # 1111 0000
                    # This should work since data has to be a byte size value.
                    # high = spoke.data[bi] >> 4  # 1111 0000
                    spoke_data.intensities += [low, high]
            else:
                print("Invalid Spoke")

            sector_data.spoke_data.append(spoke_data)

        self.write_sector_data(sector_data)


    ### Belows are all the commands method ###
    def keep_alive(self):
        while self.stop_flag:
            self.send_pack_data(StayOnCmds.A0)
            time.sleep(self.stay_alive_interval)

    def stay_alive_cmds(self, mode=0):
        self.send_pack_data(StayOnCmds.A0)# maybe just this will work
        if mode == 1:
            self.send_pack_data(StayOnCmds.A)
            self.send_pack_data(StayOnCmds.B)
            self.send_pack_data(StayOnCmds.C)
            self.send_pack_data(StayOnCmds.D)
            self.send_pack_data(StayOnCmds.E)

    def transmit(self):
        self.send_pack_data(TxOnCmds.A)
        self.send_pack_data(TxOnCmds.B)

    def standby(self):
        self.send_pack_data(TxOffCmds.A)
        self.send_pack_data(TxOffCmds.B)

    def commands(self, key, value):

        cmd = None
        # valid_cmd = [
        #     "range", "range_custom", "bearing", "gain", "sea_clutter", "rain_clutter",
        #     "side_lobe", "interference_rejection", "sea_state", "scan_speed",
        #     "mode", "target_expansion", "target_separation", "noise_rejection", "doppler"
        # ]

        olmh_map = {"off": 0, "low": 1, "medium": 2, "high": 3}

        match key:
            case "range":
                pre_define_ranges = [50, 75, 100, 250, 500, 750,
                                     1e3, 1.5e3, 2e3, 4e3, 6e3,
                                     8e3, 12e3, 15e3, 24e3]
                value = int(pre_define_ranges[value] * 10)
                cmd = RangeCmd.pack(value=value)
            case "range_custom":
                value = max(50, min(24e3, value))
                value = int(value * 10)
                cmd = RangeCmd.pack(value=value)
            case "bearing":
                value = int(value * 10)
                cmd = BearingAlignmentCmd.pack(value=value)
            case "gain":
                value = int(value * 255 / 100)
                value = min(int(value), 255)
                cmd = GainCmd.pack(auto=self.radar_parameters.auto_gain, value=value)
            case "antenna_height":
                value = value * 1000
                value = int(value)
                cmd = AntennaHeightCmd.pack(value=value)
            case "scan_speed":
                value = {"low": 0, "medium": 1, "high": 2}[value]
                cmd = ScanSpeedCmd.pack(value=value)
            case "sea_state_auto":
                value = {"off": 0, "harbour": 1, "offshore": 2}[value]
                cmd = SeaStateAutoCmd.pack(value=value)
            case "sea_clutter":
                value = int(value * 255 / 100)
                value = min(int(value), 255)
                cmd = SeaClutterCmd.pack(auto=self.radar_parameters.auto_sea_clutter, value=value)
            case "rain_clutter":
                value = int(value * 255 / 100)
                value = min(int(value), 255)
                cmd = RainClutterCmd.pack(auto=self.radar_parameters.auto_rain_clutter, value=value)
            case "interference_rejection":
                value = olmh_map[value]
                cmd = InterferenceRejectionCmd.pack(value=value)
            case "side_lobe_suppression":
                value = int(value * 255 / 100)
                value = min(int(value), 255)
                cmd = SidelobeSuppressionCmd.pack(auto=self.radar_parameters.auto_side_lobe_suppression, value=value)
            case "mode":
                value = {"custom": 0, "harbor": 1, "offshore": 2, "weather": 4, "bird": 5}[value]
                cmd = ModeCmd.pack(value=value)
            case "auto_sea_clutter_nudge":
                value = int(value)
                cmd = AutoSeaClutterNudgeCmd.pack(value)
            case "target_expansion":
                value = olmh_map[value]
                cmd = TargetExpansionCmd.pack(value=value)
            case "target_separation":
                value = olmh_map[value]
                cmd = TargetSeparationCmd.pack(value=value)
            # target boost seems to be missing FIXME
            case "noise_rejection":
                value = olmh_map[value]
                cmd = NoiseRejectionCmd.pack(value=value)
            case "doppler_mode":
                value = {"off": 0, "normal": 1, "approaching_only": 2}[value]
                cmd = DopplerModeCmd.pack(value=value)
            case "doppler_speed":
                value = value * 100
                value = int(value)
                cmd = DopplerSpeedCmd.pack(value=value)
            case "light":
                value = olmh_map[value]
                cmd = LightCmd.pack(value=value)
            case _:
                print("invalid command")
        if cmd:
            self.send_pack_data(cmd)

    def send_radar_parameters(self, radar_parameters: RadarParameters):
        # Base
        if radar_parameters.range:
            self.commands("range", radar_parameters.range)
        if radar_parameters.bearing:
            self.commands("bearing", radar_parameters.bearing)
        if radar_parameters.gain:
            self.commands("gain", radar_parameters.gain)
        if radar_parameters.antenna_height:
            self.commands("antenna_height", radar_parameters.antenna_height)
        if radar_parameters.scan_speed:
            self.commands("scan_speed", radar_parameters.scan_speed)
        if radar_parameters.sea_state:
            self.commands("sea_state", radar_parameters.sea_state)
        if radar_parameters.sea_clutter:
            self.commands("sea_clutter", radar_parameters.sea_clutter)
        if radar_parameters.rain_clutter:
            self.commands("rain_clutter", radar_parameters.rain_clutter)
        if radar_parameters.interference_rejection:
            self.commands("interference_rejection", radar_parameters.interference_rejection)
        if radar_parameters.side_lobe_suppression:
            self.commands('side_lobe_suppression', radar_parameters.side_lobe_suppression)
        if radar_parameters.mode:
            self.commands("mode", radar_parameters.mode)
        if radar_parameters.auto_sea_clutter_nudge:
            self.commands('auto_sea_clutter_nudge', radar_parameters.auto_sea_clutter_nudge)
        if radar_parameters.target_expansion:
            self.commands("target_expansion", radar_parameters.target_expansion)
        if radar_parameters.target_separation:
            self.commands("target_separation", radar_parameters.target_separation)
        if radar_parameters.noise_rejection:
            self.commands("noise_rejection", radar_parameters.noise_rejection)
        if radar_parameters.doppler_mode:
            self.commands("doppler_mode", radar_parameters.doppler_mode)
        if radar_parameters.doppler_speed:
            self.commands("doppler_speed", radar_parameters.doppler_speed)
        if radar_parameters.light:
            self.commands("light", radar_parameters.light)

    def write_sector_data(self, sector_data: SectorData):

        with open(self.output_dir + "data.txt", "a") as f:
            f.write(f"FH:{sector_data.time},{sector_data.number_of_spokes}")
            for spoke_data in sector_data.spoke_data:
                f.write(f"SH:{spoke_data.spoke_number},{spoke_data.angle},{spoke_data._range}\n")
                f.write(f"SD:" + str(spoke_data.intensities)[1:-1].replace(' ', '') + "\n") #FIXME
                #f.write(f"SD:{','.join(spoke_data.intensities)}\n")

    def write_raw_data_packet(self, raw_data: bytearray):
        with open(self.output_dir + "/", "wb") as f:
            f.write(raw_data)




if __name__ == "__main__":

    # interface = "192.168.1.243"
    interface = "192.168.1.228"


    report_address = MulticastAddress(('236.6.7.9', 6679))
    data_address = MulticastAddress(('236.6.7.8', 6678))
    send_address = MulticastAddress(('236.6.7.10', 6680))

    addrset = MulticastInterfaces(
        report=report_address,
        data=data_address,
        send=send_address,
        interface=interface
    )

    #addrset = rlocator.groupB
    output_dir="~/Desktop/raw_data/output_data"

    radar_parameters = RadarParameters(
        range=1e3,
        bearing=0,
        gain=255/2,
        antenna_height=10,
        scan_speed="low"
    )

    nr = NavicoRadar(
        address_set=addrset,
        init_radar_parameters=radar_parameters,
        output_dir=output_dir,
    )


