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

#from piradar.network import create_udp_socket, join_mcast_group, get_local_addresses, ip_address_to_string, create_udp_multicast_receiver_socket
from piradar.network import create_udp_socket, Snooper
from piradar.navico.navico_structure import *


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

        self.init_send_socket()
        self.init_report_snooper()
        self.init_data_snooper()

        self.start_report_thread()
        self.start_data_thread()

    def init_send_socket(self):
        self.send_socket = create_udp_socket()
        self.send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        #self.send_socket.bind((self.address_set.send.address, self.address_set.send.port))

    def init_report_snooper(self):
        self.report_snooper = Snooper(
            address=self.address_set.report.address,
            port=self.address_set.report.port,
            interface=self.address_set.interface
        )
        pass

    def init_data_snooper(self):
        self.report_snooper = Snooper(
            address=self.address_set.data.address,
            port=self.address_set.data.port,
            interface=self.address_set.interface
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
            in_data = next(self.report_snooper.read())#self.report_socket.recvfrom(65535)
            print(in_data)
            if len(in_data) >= 2: #more than 2 bytes
                match id:
                    case 0xb201:
                        report = RadarReport01B2(in_data)
                    case 0xc402:
                        pass
                        #report = RadarReport_c402()
                    case 0xc404:
                        pass
                        #report = RadarReport_c404()
                    case 0xc408:
                        pass
                        #report = RadarReport_c408()
                # do something with the report ?


    def data_listen(self):
        while not self.stop_flag: # have thread specific flags as well
            in_data = next(self.data_snooper.read())#self.report_socket.recvfrom(65535)
            if in_data:
                pass
                #do stuff


    def start_report_thread(self):
        self.report_thread = threading.Thread(target=self.report_listen, daemon=True)
        self.report_thread.start()

    def start_data_thread(self):
        self.data_thread = threading.Thread(target=self.data_listen, daemon=True)
        self.data_thread.start()

    ### Belows are all the commands method ###

    def stay_on(self):
        # should return `0xc611` I think
        cformat = "BB"
        commands = (
            (0xa0, 0xc1),
            (0x03, 0xc2),
            (0x04, 0xc2),
            (0x05, 0xc2)
            #(0x0a, 0xc2)
        )
        for command in commands:
            self.send_pack_data(struct.pack(cformat, *command))

    def transmit(self):
        cformat = "BBB"
        commands = (
            (0x00, 0xc1, 0x01),
            (0x01, 0xc1, 0x01)
        )
        for command in commands:
            self.send_pack_data(struct.pack(cformat, *command))

    def standby(self):
        cformat = "BBB"
        commands = (
            (0x00, 0xc1, 0x01),
            (0x01, 0xc1, 0x00)
        )
        for command in commands:
            self.send_pack_data(struct.pack(cformat, *command))

    def commands(self, key, value):
        #have object to store radar states. With all the auto_...
        pass



class RadarLocator:
    send_interval=2

    def __init__(self, interface, address, port, timeout=10):
        self.interface = interface
        self.address = address
        self.port = port
        self.groupA: AddressSet = None
        self.groupB: AddressSet = None
        self.radar_located = False
        self.timeout = timeout

        self.get_radar_groups()

    def get_radar_groups(self):

        snooper = Snooper(address=self.address, port=self.port, interface=self.interface)

        def _scan():
            t0 = time.time()
            while time.time() - t0 < self.timeout:
                data = next(snooper.read())
                if data:
                    if len(data) == RadarReport01B2.size:
                        if data[RadarReport01B2.field_sizes[0]] == 0x01b2:
                            report = RadarReport01B2(data)

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
                            break

        receive_thread = threading.Thread(target=_scan, daemon=True)

        send_socket = create_udp_socket()
        send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        cmd = struct.pack("!H", 0x01b1)

        receive_thread.start()
        while not self.radar_located:
            time.sleep(self.send_interval)
            send_socket.sendto(cmd, (self.address, self.port))
        send_socket.close()


if __name__ == '__main__':
    """
    navico_mac = "00:0e:91:0a:a6:a1"
    Source: 169.254.240.252 Destination: 224.0.0.22
    Membership Report
    Join group 236.6.7.13 for any sources
    Join group 236.6.7.20 for any sources
    Join group 236.6.7.14 for any sources
    Join group 236.6.7.10 for any sources
    Join group 236.6.7.5 for any sources
    """

    interface = 'Ethernet 2'
    entry_group = ('236.6.7.5', 6878)

    # addrset = AddressSet(
    #     data=IPAddress(entry_group),
    #     send=IPAddress(entry_group),
    #     report=IPAddress(entry_group),
    #     interface=interface
    #
    # )
    # nr = NavicoRadar(address_set=addrset)
    #
    #

    rlocator = RadarLocator(interface=interface, address=entry_group[0], port=entry_group[1])



