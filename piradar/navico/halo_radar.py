import struct
import socket
import threading

from piradar.network import create_udp_socket, join_mcast_group, get_local_addresses
from piradar.navico.halo_radar_structure import *


HOST = ''
# Other possible 236.6.7.10:6680
# mcast_group = '236.6.7.9'
# mcast_port = 6679

maddresses = [
    ('236.6.7.15', 6659),
    ("236.6.7.10", 6878),
    ('236.6.7.10', 6680),
    ('236.6.7.9', 6679),
    ]

MCAST_GROUP, MCAST_PORT = maddresses[0]

def ip_address_to_string(a):
    return socket.inet_ntoa(struct.pack('!I', a))


class AddressSet:
    def __init__(self, label, data, send, report, interface):
        self.label = label
        self.data: IPAddress = data
        self.send: IPAddress = send
        self.report: IPAddress = report
        self.interface = interface

    def __str__(self):
        return f'{self.label}: data: {ip_address_to_string(self.data.address)}:{self.data.port}, report: {ip_address_to_string(self.report.address)}:{self.report.port}, send: {ip_address_to_string(self.send.address)}:{self.send.port}'


def scan_for_halo_radar(group=MCAST_GROUP, port=MCAST_PORT):
    """

    """
    laddrs = get_local_addresses()

    ret = []

    for interface in laddrs:
        listen_socket = create_udp_socket()
        listen_socket.bind((HOST, port))
        try:
            join_mcast_group(sock=listen_socket, address=group, interface=interface)
        except OSError as e:
            listen_socket.close()
            continue

        send_socket = create_udp_socket()
        send_socket.bind((interface, port))
        send_socket.sendto(struct.pack('!H', 0xb101), (group, port))
        print(interface, group, port)
        for _ in range(3):
            try:
                in_data, from_addr = listen_socket.recvfrom(1024)
                print(in_data, from_addr)
                if len(in_data) == struct.calcsize(RadarReport_b201.format):
                    b201 = RadarReport_b201(in_data)
                    if b201.id == 0xb201:
                        asa = AddressSet('HaloA', b201.addrDataA, b201.addrSendA,  b201.addrReportA, interface)
                        ret.append(asa)
                        asb = AddressSet('HaloB', b201.addrDataB, b201.addrSendB,  b201.addrReportB, interface)
                        ret.append(asb)
            except socket.timeout:
                continue
        listen_socket.close()
        send_socket.close()
    return ret


class HaloRadar:
    def __init__(self, address_set: AddressSet):
        self.address_set = address_set
        self.send_socket = None
        self.data_socket = None
        self.report_socket = None
        self.data_socket = None

        self.sender_thread: threading.Thread = None
        self.data_thread: threading.Thread = None
        self.report_thread: threading.Thread = None

        self.stop_flag = False

        self.init_send_socket()
        self.init_report_socket()
        self.init_data_socket()

    def init_send_socket(self):
        send_socket = create_udp_socket()
        send_socket.bind((self.address_set.send.address, self.address_set.send.port))

    def init_report_socket(self):
        self.report_socket = create_udp_socket()
        self.report_socket.bind((HOST, self.address_set.report.port))
        join_mcast_group(
            sock=self.report_socket,
            address=self.address_set.report.address,
            interface=self.address_set.interface
        )

    def init_data_socket(self):
        self.data_socket = create_udp_socket()
        self.data_socket.bind((HOST, self.address_set.data.port))
        join_mcast_group(
            sock=self.data_socket,
            address=self.address_set.data.address,
            interface=self.address_set.interface
        )

    def send_pack_data(self, packed_data):
        self.send_socket.sendto(packed_data, (self.address_set.send.address, self.address_set.send.port))

    def close_all(self):
        self.stop_flag = True
        self.report_thread.join()
        self.data_thread.join()

    def report_listen(self):
        while not self.stop_flag: # have thread specific flags as well
            try:
                in_data, from_addr = self.data_socket.recvfrom(65535)
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
                raw_sector = RawSector(in_data)
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
        commands = (
            (0xa0, 0xc1),
            (0x03, 0xc2),
            (0x04, 0xc2),
            (0x05, 0xc2)
            #(0x0a, 0xc2)
        )

        fmt = "2B"
        for command in commands:
            self.send_pack_data(struct.pack(fmt, *command))

    def transmit(self):
        commands = (
            (0x00, 0xc1, 0x01),
            (0x01, 0xc1, 0x01)
        )
        fmt = "3B"
        for command in commands:
            self.send_pack_data(struct.pack(fmt, *command))

    def standby(self):
        commands = (
            (0x00, 0xc1, 0x01),
            (0x01, 0xc1, 0x00)
        )
        fmt = "3B"
        for command in commands:
            self.send_pack_data(struct.pack(fmt, *command))

    def set_range(self, meters):
        decimeters = meters * 10
        command = (0xc103, decimeters)
        fmt = "!HI"
        self.send_pack_data(struct.pack(fmt, *command))


    def set_bearing_aligment(self, bearing):
        cmd = 0xc106
        sub_cmd = 0xc106
        decimeters = bearing * 10
        command = (0xc106, bearing)
        fmt="!HIIB"


if __name__ == '__main__':
    radar_addresses = scan_for_halo_radar()
