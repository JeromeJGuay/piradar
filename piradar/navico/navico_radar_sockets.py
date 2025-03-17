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

from piradar.network import create_udp_socket, join_mcast_group, get_local_addresses, ip_address_to_string, create_udp_multicast_receiver_socket
#from piradar.network import create_udp_socket, Snooper
from piradar.navico.navico_structure import *
from piradar.navico.navico_command import *


HOST = ''


class AddressSet:
    def __init__(self, data, send, report, interface):
        self.data: IPAddress = data
        self.send: IPAddress = send
        self.report: IPAddress = report
        self.interface = interface

    def __repr__(self):
        return f'{self.interface}:\n data: {self.data.address}:{self.data.port},\n report: {self.report.address}:{self.report.port},\n send: {self.send.address}:{self.send.port}'


class NavicoRadar:
    def __init__(self, address_set: AddressSet):
        self.address_set = address_set

        self.send_socket = None

        self.data_snooper = None
        self.report_snooper = None

        self.data_thread: threading.Thread = None
        self.report_thread: threading.Thread = None

        self.stop_flag = False

        ### RADAR PARAMETER ###
        ### maybe put into an object ? ####
        self.auto_gain = False
        self.auto_sea_clutter = False
        self.auto_rain_clutter = False
        self.auto_sidelobe = False


        self.init_send_socket()
        self.init_report_socket()
        #self.init_data_snooper()

        self.start_report_socket()
        #self.start_data_thread()

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
        print(f"sending: {packed_data} to {self.address_set.send.address, self.address_set.send.port}")
        self.send_socket.sendto(packed_data, (self.address_set.send.address, self.address_set.send.port))

    def close_all(self):
        self.stop_flag = True
        self.report_thread.join()
        self.data_thread.join()

    def report_listen(self):
        while not self.stop_flag: # have thread specific flags as well
            in_data = self.report_socket.recvfrom(1024)
            if in_data:
                if len(in_data) >= 2: #more than 2 bytes
                    id = struct.unpack("!H", in_data[:2])
                    match id:
                        case RadarReport01B2.id: #'#case b'\xb2\x01':
                            report = RadarReport01B2(in_data)

                        case RadarReport06C4.id:
                            match len(in_data):
                                case RadarReport06C468.size:
                                    report = RadarReport06C468(in_data)
                                    print(f"report {in_data[:2]} not impletmented yet")
                                case RadarReport06C474.size:
                                    report = RadarReport06C474(in_data)
                                    print(f"report {in_data[:2]} not impletmented yet")

                        case RadarReport08C4.id:
                            match len(in_data):
                                case RadarReport08C418.size:
                                    report = RadarReport08C418(in_data)
                                    print(f"report {in_data[:2]} not impletmented yet")
                                case RadarReport08C421.size:
                                    report = RadarReport08C421(in_data)
                            print(f"report {in_data[:2]} not impletmented yet")

                        case _:
                            print(f"report {in_data[:2]} not impletmented yet")
                            #report = RadarReport_c408()
                # do something with the report ?

    def data_listen(self):
        while not self.stop_flag: # have thread specific flags as well
            in_data = self.data_socket.recvfrom(1024)
            if in_data:
                print("data:", in_data)
                pass

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
        #     "side_lobe", "interferance", "sea_state", "scan_speed",
        #     "mode", "target_expansion", "target_sepration", "noise", "doppler"
        # ]
        match key:
            case "range":
                cmd = RangeCmd.pack(value=value)
            case "bearing":
                cmd = BearingAlignmentCmd.pack(value=value)
            case "gain":
                cmd = GainCmd.pack(auto=self.auto_gain, value=value)
            # FIXME all the command will requires mapping to value
            # case "sea_clutter":
            #     cmd = SeaClutterCmd.pack(auto=self.auto_sea_clutter, value=value)
            # case "rain_clutter":
            #     cmd = RainClutterCmd.pack(auto=self.auto_rain_clutter, value=value)
            # case "auto_sea_clutter_nudge":
            #     cmd = AutoSeaClutterNudgeCmd.pack(value)
            # case "side_lobe":
            #     cmd = SidelobeSuppressionCmd.pack(auto=self.auto_sidelobe, value=value)
            # case "interferance":
            #     cmd = InterferanceRejection.pack(value=value)
            # case "sea_State":
            #     cmd = SeaStateCmd.pack(value=value)
            # case "scan_speed":
            #     cmd = ScanSpeedCmd.pack(value=value)
            # case "mode":
            #     cmd = ModeCmd.pack(value=value)
            # case "target_expansion":
            #     cmd = TargetExpansionCmd.pack(value=value)
            # case "target_separation":
            #     cmd = TargetSeparationCmd.pack(value=value)
            # case "noise":
            #     cmd = NoiseRejectionCmd.pack(value=value)
            # case "doppler":
            #     cmd = DopplerCmd.pack(value=value)
            # case "dopper_speed":
            #     cmd = DopplerSpeedCmd.pack(value=value)
            # case "antenna_height":
            #     cmd = AntennaHeightCmd.pack(value=value)
            case _:
                print("invalid command")


        if cmd:
            self.send_pack_data(cmd)



class RadarLocator:
    send_interval = 2
    group_address = '236.6.7.5'
    group_port = 6878

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
            in_data = report_socket.recvfrom(1024)
            if in_data:
                if len(in_data) >= 2: #more than 2 bytes
                    id = struct.unpack("!H", in_data[:2])
                    match id:
                        case RadarReport01B2.id: #'#case b'\xb2\x01':
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

    interface = "192.168.1.185" # change it

    addrset = AddressSet(
        data=IPAddress(('236.6.7.8', 6678)),
        send=IPAddress(('236.6.7.10', 6680)),
        report=IPAddress(('236.6.7.9', 6679)),
        interface=interface
    )

    # addrset = rlocator.groupB

    nr = NavicoRadar(address_set=addrset)
    nr.transmit()



