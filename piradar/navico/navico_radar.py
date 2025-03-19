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

from piradar.network import create_udp_socket, get_local_addresses, create_udp_multicast_receiver_socket
#from piradar.network import create_udp_socket, Snooper
from piradar.navico.navico_structure import *
from piradar.navico.navico_command import *


HOST = ''
RCV_BUFF = 65535


ENTRY_GROUP_ADDRESS = '236.6.7.5'
ENTRY_GROUP_PORT = 6878

RANGE_SCALE = 10 * 2 ** (-1/2)


@dataclass
class AddressSet:
    data: IPAddress
    send: IPAddress
    report: IPAddress
    interface = interface


    def __repr__(self):
        return f'{self.interface}:\n data: {self.data.address}:{self.data.port},\n report: {self.report.address}:{self.report.port},\n send: {self.send.address}:{self.send.port}'


@dataclass
class RawReports:
    r01b2: RadarReport01B2 = None
    r01c4: RadarReport02C499 = None
    r02c4: RadarReport02C499 = None
    r03c4: RadarReport03C4129 = None
    r04c4: RadarReport04C466 = None
    r06c4: RadarReport06C468 | RadarReport06C474
    r08C4: RadarReport08C418 | RadarReport08C421 = None
    r12c4: RadarReport12C466 = None


@dataclass
class SpokeData:
    spoke_number: int = None
    angle: float = None
    range: float = None
    intensities: list[float] = None


@dataclass
class SectorData:
    time: str = None
    number_of_spokes: int = None
    spoke_data: list[SpokeData] = None


@dataclass
class SpatialReport:
    """Report 04C4"""
    bearing: float = None
    antenna_height: float = None


@dataclass
class SystemReport:
    """Report 03C4"""
    radar_type: str = None


@dataclass
class BlankingReport:
    """Report 06c4"""
    pass


@dataclass
class SettingReport:
    """Report 08C4"""
    sea_state: str = None
    interference_rejection: int = None
    scan_speed: int = None

    side_lobe_suppression: int = None
    noise_rejection: int = None
    target_separation: int = None
    sea_clutter: int = None

    side_lobe_suppresion_auto: bool = None
    auto_sea_clutter: bool = None


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
class RadarParameters:
    # Base
    range: float = None # maybe define literal with pre_define ranges ?
    bearing: float = None
    gain: float = None
    antenna_height: float = None
    scan_speed: Literal["low", "medium", "high"] = None  # Doubt # Default-0, increase-1 ? max-2 ???

    # filters

    sea_state: Literal['off', 'moderate', 'rough'] = None

    sea_clutter: int = None
    rain_clutter: int = None

    interference_rejection: Literal["off", "low", "medium", "high"] = None
    side_lobe_suppression: int = None

    mode: Literal["default", "harbor", "offshore", "weather", "bird"] = None

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
    def __init__(self, address_set: AddressSet, output_file, raw_output_file):
        self.address_set = address_set
        self.output_file = output_file
        self.raw_output_file = raw_output_file # fixme Make a object to store these parameter

        # make object to store initatil parameter to pass to Radar

        self.send_socket = None

        self.data_socket = None
        self.report_socket = None

        self.data_thread: threading.Thread = None
        self.report_thread: threading.Thread = None
        # self.stay_alive_thread: threading.Thread = None # TODO

        self.stop_flag = False

        ### RADAR PARAMETER ###
        ### maybe put into an object ? ####
        self.auto_gain = False
        self.auto_sea_clutter = False
        self.auto_rain_clutter = False
        self.auto_sidelobe = False

        self.init_send_socket()
        self.init_report_socket()
        self.init_data_socket()

        self.start_report_thread()
        self.start_data_thread()

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

    def send_pack_data(self, packed_data):
        #print(f"sending: {packed_data} to {self.address_set.send.address, self.address_set.send.port}")
        self.send_socket.sendto(packed_data, (self.address_set.send.address, self.address_set.send.port))

    def close_all(self):
        self.stop_flag = True
        self.report_thread.join()
        self.data_thread.join()
        self.send_socket.close()

    def report_listen(self):
        while not self.stop_flag: # have thread specific flags as well
            try:
                in_data = self.report_socket.recv(RCV_BUFF)
            except socket.timeout:
                continue
            if in_data and len(in_data) >= 2:
                self.process_report(in_data=in_data)

    def data_listen(self):
        while not self.stop_flag: # have thread specific flags as well
            try:
                in_data = self.data_socket.recv(RCV_BUFF)
                self.write_raw_data_packet(in_data)
            except socket.timeout:
                continue
            if in_data:
                print("data:", in_data)
                self.process_data(in_data=in_data)

    def process_report(self, in_data):
        id = struct.unpack("!H", in_data[:2])[0]
        match id:
            case ReportIds._01B2:  # '#case b'\xb2\x01':
                report = RadarReport01B2(in_data)

            case ReportIds._06C4:
                match len(in_data):
                    case RadarReport06C468.size:
                        report = RadarReport06C468(in_data)
                        print(f"report {in_data[:2]} not impletmented yet")
                    case RadarReport06C474.size:
                        report = RadarReport06C474(in_data)
                        print(f"report {in_data[:2]} not impletmented yet")

            case ReportIds._08C4:
                match len(in_data):
                    case RadarReport08C418.size:
                        report = RadarReport08C418(in_data)
                        print(f"report {in_data[:2]} not impletmented yet")
                    case RadarReport08C421.size:
                        report = RadarReport08C421(in_data)
                print(f"report {in_data[:2]} not impletmented yet")

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

        for spoke in raw_sector.spokes:
            print(f"Spoke number: {spoke.spoke_number} [should be between 0-4096]") #fixme maybe
            # WILL DEPEND ON RADAR TYPE THIS IS JUST FOR HALO FIXME

            print("angle", spoke.angle)
            print("heading", spoke.heading)
            print("small range", spoke.small_range)
            print("large range", spoke.large_range)
            print("angle", spoke.angle)

            spoke_data = SpokeData()
            spoke_data.spoke_number = spoke.spoke_number


            if spoke.status == 2: # Valid

                #### This here could change depending on model
                if spoke.large_range == 128:
                    if spoke.small_range == -1: # or 0xffff maybe
                        spoke_data.range = 0
                    else:
                        spoke_data.range = spoke.small_range / 4
                else:
                    spoke_data.range = spoke.large_range * spoke.small_range / 512

                spoke_data.range *= RANGE_SCALE # 10 / sqrt(2)

                spoke_data.angle = spoke.angle * 360 / 4096 # 0..4096 = 0..360

                spoke_data.intensites = []
                for bi in range(512):
                    low = spoke.data[bi] & 0x0f # 0000 1111
                    high = (spoke.data[bi] & 0xf0) >> 4 # 1111 0000
                    # This should work since data has to be a byte size value.
                    # high = spoke.data[bi] >> 4  # 1111 0000
                    spoke_data.intensites += [low, high]

            sector_data.spoke_data.append(spoke_data)

        self.write_scanline(SectorData)

    def start_report_thread(self):
        self.report_thread = threading.Thread(target=self.report_listen, daemon=True)
        self.report_thread.start()

    def start_data_thread(self):
        self.data_thread = threading.Thread(target=self.data_listen, daemon=True)
        self.data_thread.start()

    ### Belows are all the commands method ###

    def stay_alive(self, mode=0):
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
        auto = True # set as attributes
        #have object to store radar states. With all the auto_...
        cmd = None
        # valid_cmd = [
        #     "range", "range_custom", "bearing", "gain", "sea_clutter", "rain_clutter",
        #     "side_lobe", "interference_rejection", "sea_state", "scan_speed",
        #     "mode", "target_expansion", "target_sepration", "noise_rejection", "doppler"
        # ]

        olmh_map = {"off": 0, "low": 1, "medium": 2, "high": 3}

        match key:
            case "range":
                pre_define_ranges = [50, 75, 100, 250, 500, 750,
                                     1e3, 1.5e3, 2e3, 4e3, 6e3,
                                     8e3, 12e3, 15e3, 24e3]
                value = int(pre_define_ranges[value] * 10)
                cmd = RangeCmd().pack(value=value)
            case "range_custom":
                value = max(50, min(24e3, value))
                value = int(value * 10)
                cmd = RangeCmd().pack(value=value)
            case "bearing":
                value = int(value * 10)
                cmd = BearingAlignmentCmd().pack(value=value)
            case "gain":
                value = int(value * 255 / 100)
                value = min(int(value), 255)
                cmd = GainCmd().pack(auto=self.auto_gain, value=value)
            case "antenna_height":
                value = value * 1000
                value = int(value)
                cmd = AntennaHeightCmd().pack(value=value)
            case "scan_speed":
                value = {"low": 0, "medium": 1, "high": 2}[value]
                cmd = ScanSpeedCmd().pack(value=value)
            case "sea_State":
                value = {"off": 0, "moderate": 1, "rough": 2}[value]
                cmd = SeaStateCmd().pack(value=value)
            case "sea_clutter":
                value = int(value * 255 / 100)
                value = min(int(value), 255)
                cmd = SeaClutterCmd().pack(auto=self.auto_sea_clutter, value=value)
            case "rain_clutter":
                value = int(value * 255 / 100)
                value = min(int(value), 255)
                cmd = RainClutterCmd().pack(auto=self.auto_rain_clutter, value=value)
            case "interference_rejection":
                value = olmh_map[value]
                cmd = InterferenceRejection().pack(value=value)
            case "side_lobe_suppression":
                value = int(value * 255 / 100)
                value = min(int(value), 255)
                cmd = SidelobeSuppressionCmd().pack(auto=self.auto_sidelobe, value=value)
            case "mode":
                value = {"default": 0, "harbor": 1, "offshore": 2, "weather": 4, "bird": 5}[value]
                cmd = ModeCmd().pack(value=value)
            case "auto_sea_clutter_nudge":
                value = int(value)
                cmd = AutoSeaClutterNudgeCmd().pack(value)
            case "target_expansion":
                value = olmh_map[value]
                cmd = TargetExpansionCmd().pack(value=value)
            case "target_separation":
                value = olmh_map[value]
                cmd = TargetSeparationCmd().pack(value=value)
            case "noise_rejection":
                value = olmh_map[value]
                cmd = NoiseRejectionCmd().pack(value=value)
            case "doppler_mode":
                value = {"off": 0, "normal": 1, "approaching_only": 2}[value]
                cmd = DopplerModeCmd().pack(value=value)
            case "doppler_speed":
                value = value * 100
                value = int(value)
                cmd = DopplerSpeedCmd().pack(value=value)
            case "light":
                value = olmh_map[value]
                cmd = LightCmd().pack(value=value)
            case _:
                print("invalid command")
        if cmd:
            self.send_pack_data(cmd)

    def write_scanline(self, sector_data: SectorData):
        with open(self.output_file, "a") as f:
            f.write(f"FH:{sector_data.time},{sector_data.number_of_spokes}")
            for spoke_data in sector_data:
                f.write(f"SH:{spoke_data.time},{spoke_data.scan_number},{spoke_data.angle},{spoke_data.range}\n")
                f.write(f"SD:{','.join(spoke_data.intensities)}\n")

    def write_raw_data_packet(self, raw_data: bytearray):
        with open(self, self.raw_output_file, "wb") as f:
            f.write(raw_data)


class RadarLocator:
    send_interval = 2
    group_address = ENTRY_GROUP_ADDRESS
    group_port = ENTRY_GROUP_PORT

    def __init__(self, interface, timeout=30):
        self.interface = interface
        self.radar_located = False
        self.groupA: AddressSet = None
        self.group: AddressSet = None
        self.timeout = timeout

    def locate(self):
        report_socket = create_udp_multicast_receiver_socket(
            interface_address=self.interface,
            group_address=self.group_address,
            group_port=self.group_port
        )

        def _scan():
            while not self.radar_located:
                try:
                    in_data, _addrs = report_socket.recvfrom(RCV_BUFF)
                except socket.timeout:
                    continue
                if in_data:
                    if len(in_data) >= 2: #more than 2 bytes
                        id = struct.unpack("!H", in_data[:2])[0]
                        match id:
                            case ReportIds._01B2: #'#case b'\xb2\x01':
                                report = RadarReport01B2(in_data)
                                self.groupA = AddressSet(
                                    interface=self.interface,
                                    data=report.addrDataA,
                                    report=report.addrReportA,
                                    send=report.addrSendA,
                                )
                                self.groupB = AddressSet(
                                    interface=self.interface,
                                    data=report.addrDataB,
                                    report=report.addrReportB,
                                    send=report.addrSendB,
                                )
                                self.radar_located = True
                                report_socket.close()

        receive_thread = threading.Thread(target=_scan, daemon=True)

        send_socket = create_udp_socket()
        send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        cmd = struct.pack("!H", 0x01b1)
        # not binding required

        receive_thread.start()
        while not self.radar_located:
            print(cmd)
            time.sleep(self.send_interval)
            send_socket.sendto(cmd, (self.group_address, self.group_port))
        send_socket.close()






if __name__ == "__main__":

    interface = "192.168.1.243"
    # interface = "192.168.1.228"

    #rlocator = RadarLocator(interface=interface)
    #rlocator.locate()

    addrset = AddressSet(
        data=IPAddress(('236.6.7.8', 6678)),
        send=IPAddress(('236.6.7.10', 6680)),
        report=IPAddress(('236.6.7.9', 6679)),
        interface=interface
    )

    #addrset = rlocator.groupB
    output_file=""
    raw_output_file=""
    nr = NavicoRadar(address_set=addrset, output_file=output_file, raw_output_file=raw_output_file)

    nr.commands("range", 1000) #1000 km

    nr.transmit()


