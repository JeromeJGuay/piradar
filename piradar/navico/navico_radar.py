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

#from piradar.network import create_udp_socket, join_mcast_group, get_local_addresses, ip_address_to_string, create_udp_multicast_receiver_socket
from piradar.network import create_udp_socket, Snooper
from piradar.navico.halo_radar_structure import *


HOST = ''



class AddressSet:
    def __init__(self, label, data, send, report, interface):
        self.label = label
        self.data: IPAddressStruct = data
        self.send: IPAddressStruct = send
        self.report: IPAddressStruct = report
        self.interface = interface

    def __repr__(self):
        return f'{self.label}:\n data: {self.data.address}:{self.data.port},\n report: {self.report.address}:{self.report.port},\n send: {self.send.address}:{self.send.port}'


def get_radar_group(address, port, interface=None):
    """

    """

    snoop = Snooper(address=address, port=port, interface=interface)
    t0 = time.time()
    dt=10

    while time.time() - t0 < dt:
        data = snoop.recv()

        if not data:
            continue





class NavicoRadar:
    def __init__(self, address_set: AddressSet):
        self.address_set = address_set

        self.send_socket = None
        self.data_socket = None
        self.report_socket = None

        self.data_thread: threading.Thread = None
        self.report_thread: threading.Thread = None

        self.stop_flag = False

        self.init_send_socket()
        self.init_report_socket()
        self.init_data_socket()

        self.start_report_thread()
        self.start_data_thread()

    def init_send_socket(self):
        self.send_socket = create_udp_socket()
        self.send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        #self.send_socket.bind((self.address_set.send.address, self.address_set.send.port))

    def init_report_socket(self):
        pass

    def init_data_socket(self):
        pass


    def send_pack_data(self, packed_data):
        print(f"sending: {packed_data} to {self.address_set.send.address, self.address_set.send.port}")
        self.send_socket.sendto(packed_data, (self.address_set.send.address, self.address_set.send.port))

    def close_all(self):
        self.stop_flag = True
        self.report_thread.join()
        self.data_thread.join()

    def report_listen(self):
        while not self.stop_flag: # have thread specific flags as well
            try:
                in_data, from_addr = self.report_socket.recvfrom(65535)
                print(in_data, from_addr)
                if len(in_data) >= 2: #more than 2 bytes
                    # struct.calcsize("!H") = 2
                    id = in_data[:2]
                    print(id)
                    match id:
                        case 0xb201:
                            report = RadarReport_b201(in_data[:struct.calcsize(RadarReport_b201.format)])
                        case 0xc402:
                            report = RadarReport_c402(in_data[:struct.calcsize(RadarReport_c402.format)])
                        case 0xc404:
                            report = RadarReport_c404(in_data[:struct.calcsize(RadarReport_c404.format)])
                        case 0xc408:
                            report = RadarReport_c408(in_data[:struct.calcsize(RadarReport_c408.format)])
                    #do stuff with report (update ?)
                    # make a state report. save it maybe idk
            except socket.timeout:
                continue
        self.data_socket.close()

    def data_listen(self):
        while not self.stop_flag:  # have thread specific flags as well
            try:
                in_data, from_addr = self.data_socket.recvfrom(65535)
                raw_sector = RawSectorStruct(in_data)
                print(raw_sector.lines)
                # process data
                #self.process_data(raw_sector.lines)
            except socket.timeout:
                continue
        self.data_socket.close()

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

    get_radar_group(address=entry_group[0], port=entry_group[1], interface=interface)

