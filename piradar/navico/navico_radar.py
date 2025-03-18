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
import struct
import socket
import threading
import asyncio
from unittest import case

from piradar.network import create_udp_socket, get_local_addresses, create_udp_multicast_receiver_socket
#from piradar.network import create_udp_socket, Snooper
from piradar.navico.navico_structure import *
from piradar.navico.navico_command import *


HOST = ''
RCV_BUFF = 65535


ENTRY_GROUP_ADDRESS = '236.6.7.5'
ENTRY_GROUP_PORT = 6878


class AddressSet:
    def __init__(self, data, send, report, interface):
        self.data: IPAddress = data
        self.send: IPAddress = send
        self.report: IPAddress = report
        self.interface = interface

    def __repr__(self):
        return f'{self.interface}:\n data: {self.data.address}:{self.data.port},\n report: {self.report.address}:{self.report.port},\n send: {self.send.address}:{self.send.port}'


class NavicoRadar:
    def __init__(self, address_set: AddressSet, output_file):
        self.address_set = address_set
        self.output_file = output_file

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

        raw_sector = RawSector(in_data)

        print(f"Scan count: {raw_sector.scanline_count}")
        scanlines = []
        for spoke in raw_sector.lines:
            print(f"Spoke count: {spoke.scan_number}") #fixme maybe
            # WILL DEPEND ON RADAR TYPE THIS IS JUST FOR HALO FIXME
            if spoke.status == 2: # Valid
                s = Scanline
                print("large range", spoke.large_range)
                print("small range", spoke.large_range)
                print("angle", spoke.angle)
                if spoke.large_range == 128:

                    if spoke.small_range == -1: # or 0xffff maybe
                        s.range = 0
                    else:
                        s.range = spoke.small_range / 4
                else:
                    s.range = spoke.large_range * spoke.small_range / 512

                s.angle = spoke.angle * 360 / 4096

                s.intensites = []
                for bi in range(512): #divided by 15 in processData
                    s.intensites.append(spoke.data[bi] & 0xf) / 15
                    s.intensites.append((spoke.data[bi] & 0xf) >> 4) / 15

            scanlines.append(s)

        self.write_scanline(scanlines)



    def start_report_thread(self):
        self.report_thread = threading.Thread(target=self.report_listen, daemon=True)
        self.report_thread.start()

    def start_data_thread(self):
        self.data_thread = threading.Thread(target=self.data_listen, daemon=True)
        self.data_thread.start()

    ### Belows are all the commands method ###

    def stay_alive(self, mode=0):
        self.send_pack_data(StayOnCmd.A)
        if mode == 0:
            self.send_pack_data(StayOnCmd.B)
            self.send_pack_data(StayOnCmd.C)
            self.send_pack_data(StayOnCmd.D)
            self.send_pack_data(StayOnCmd.E)

    def transmit(self):
        self.send_pack_data(TxOnCmd.A)
        self.send_pack_data(TxOnCmd.B)

    def standby(self):
        self.send_pack_data(TxOffCmd.A)
        self.send_pack_data(TxOffCmd.B)

    def commands(self, key, value):
        auto = True # set as attributes
        #have object to store radar states. With all the auto_...
        cmd = None
        # valid_cmd = [
        #     "range", "bearing", "gain", "sea_clutter", "rain_clutter",
        #     "side_lobe", "interferance_rejection", "sea_state", "scan_speed",
        #     "mode", "target_expansion", "target_sepration", "noise_rejection", "doppler"
        # ]

        olmh_map = {"off": 0, "low": 1, "medium": 2, "high": 3}

        match key:
            case "range":
                value = int(value * 10)
                cmd = RangeCmd().pack(value=value)
            case "bearing":
                value = int(value * 10)
                cmd = BearingAlignmentCmd().pack(value=value)
            case "gain":
                value = int(value * 255 / 100)
                value = min(int(value), 255)
                cmd = GainCmd.pack(auto=self.auto_gain, value=value)
            case "interferance_rejection":
                value = olmh_map[value]
                cmd = InterferanceRejection().pack(value=value)
            case "sea_clutter":
                value = int(value * 255 / 100)
                value = min(int(value), 255)
                cmd = SeaClutterCmd().pack(auto=self.auto_sea_clutter, value=value)
            case "rain_clutter":
                value = int(value * 255 / 100)
                value = min(int(value), 255)
                cmd = RainClutterCmd().pack(auto=self.auto_rain_clutter, value=value)
            case "side_lobe":
                value = int(value * 255 / 100)
                value = min(int(value), 255)
                cmd = SidelobeSuppressionCmd().pack(auto=self.auto_sidelobe, value=value)
            case "sea_State":
                value = {"off": 0, "moderate": 1, "rough": 2}[value]
                cmd = SeaStateCmd().pack(value=value)
            case "scan_speed":
                value = {"low": 0, "medium": 1, "high": 2}[value]
                cmd = ScanSpeedCmd().pack(value=value)
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
            case "doppler":
                value = {"off": 0, "normal": 1, "approaching_only": 2}[value]
                cmd = DopplerCmd().pack(value=value)
            case "dopper_speed":
                value = value * 100
                cmd = DopplerSpeedCmd().pack(value=value)
            case "antenna_height":
                value = value * 1000
                cmd = AntennaHeightCmd().pack(value=value)
            case "light":
                value = olmh_map[value]
                cmd = LightCmd().pack(value=value)
            case _:
                print("invalid command")


        if cmd:
            self.send_pack_data(cmd)

    def write_scanline(self, scanlines: list[Scanline]):
        with open(self.output_file, "a") as f:
            for scanline in scanlines:
                f.write(f"angle={scanline.angle}\n")
                f.write(f"range={scanline.range}\n")
                f.write(f"intensities={','.join(scanline.intensities)}")





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

    rlocator = RadarLocator()
    rlocator.locate()

    #addrset = AddressSet(
    #    data=IPAddress(('236.6.7.8', 6678)),
    #    send=IPAddress(('236.6.7.10', 6680)),
    #    report=IPAddress(('236.6.7.9', 6679)),
    #    interface=interface
    #)

    # addrset = rlocator.groupB

    # nr = NavicoRadar(address_set=addrset)
    # nr.transmit()


