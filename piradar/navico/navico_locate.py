import time

import struct
import socket
import threading

from ..network import create_udp_multicast_receiver_socket, create_udp_socket
from .navico_controller import MulticastInterfaces
from .navico_structure import RadarReport01B2, REPORTS_IDS

HOST = ""
RCV_BUFF = 65535

ENTRY_GROUP_ADDRESS = '236.6.7.5'
ENTRY_GROUP_PORT = 6878


class RadarLocator:
    group_address = ENTRY_GROUP_ADDRESS
    group_port = ENTRY_GROUP_PORT

    def __init__(self, interface, timeout=30, ping_interval=2):
        self.interface = interface
        self.timeout = timeout
        self.ping_interval = ping_interval
        self.groupA: MulticastInterfaces = None
        self.group: MulticastInterfaces = None


        self.radar_is_located = False
        self.has_timed_out = False

    def locate(self):
        report_socket = create_udp_multicast_receiver_socket(
            interface_address=self.interface,
            group_address=self.group_address,
            group_port=self.group_port
        )
        start_time = time.time()

        def _scan():
            while not self.radar_is_located and not self.has_timed_out:
                try:
                    in_data, _addrs = report_socket.recvfrom(RCV_BUFF)
                except socket.timeout:
                    continue
                if in_data:
                    if len(in_data) >= 2: #more than 2 bytes
                        print("Data received")
                        id = struct.unpack("!H", in_data[:2])[0]
                        print(f'Report {hex(id)} received.')
                        match id:
                            case REPORTS_IDS._01B2: #'#case b'\xb2\x01':
                                report = RadarReport01B2(in_data)
                                self.groupA = MulticastInterfaces(
                                    interface=self.interface,
                                    data=MulticastInterfaces(
                                        report.addrDataA[0],
                                        report.addrDataA[1]
                                    ),
                                    report=MulticastInterfaces(
                                        report.addrReportA[0],
                                        report.addrReportA[1]
                                    ),
                                    send=MulticastInterfaces(
                                        report.addrSendA[0],
                                        report.addrSendA[1]
                                    ),
                                )
                                self.groupB = MulticastInterfaces(
                                    interface=self.interface,
                                    data=MulticastInterfaces(
                                        report.addrDataB[0],
                                        report.addrDataB[1]
                                    ),
                                    report=MulticastInterfaces(
                                        report.addrReportB[0],
                                        report.addrReportB[1]
                                    ),
                                    send=MulticastInterfaces(
                                        report.addrSendB[0],
                                        report.addrSendB[1]
                                    ),
                                )
                                self.radar_is_located = True
                                break
            report_socket.close()

        receive_thread = threading.Thread(target=_scan, daemon=True)

        send_socket = create_udp_socket()
        send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        cmd = struct.pack("!H", 0x01b1)
        # not binding required

        receive_thread.start()
        while not self.radar_is_located:
            print("Ping send")
            time.sleep(self.ping_interval)
            send_socket.sendto(cmd, (self.group_address, self.group_port))

            if (time.time() - start_time) < self.timeout:
                self.has_timed_out = True
                break

        send_socket.close()
        receive_thread.join()

        if self.radar_is_located:
            print(f"Radar located on interface: {self.interface}")
        else:
            print("Radar not located on interface: {self.interface}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('interface', required=True, help='Interface address to scan')
    parser.add_argument("-t", '--timeout', help="---", type=int, default=30)
    parser.add_argument("-p", '--ping-interval', help="---", type=int, default=2)
    args = parser.parse_args()

    radar = RadarLocator(interface=args.interface, timeout=args.timeout, ping_interval=args.ping_interval)

    radar.locate()


