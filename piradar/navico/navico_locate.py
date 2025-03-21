import time

import struct
import socket
import threading

from piradar.network import create_udp_multicast_receiver_socket, create_udp_socket
from piradar.navico.navico_controller import MulticastInterfaces
from piradar.navico.navico_structure import RadarReport01B2, REPORTS_IDS

HOST = ""
RCV_BUFF = 65535

ENTRY_GROUP_ADDRESS = '236.6.7.5'
ENTRY_GROUP_PORT = 6878


class NavicoLocator:
    group_address = ENTRY_GROUP_ADDRESS
    group_port = ENTRY_GROUP_PORT

    def __init__(self, interface, timeout=30, ping_interval=2):
        self.interface = interface
        self.timeout = timeout
        self.ping_interval = ping_interval
        self.groupA: MulticastInterfaces = None
        self.groupB: MulticastInterfaces = None

        self.is_located = False
        self.has_timed_out = False

    def get_report_01b2(self):
        report_socket = create_udp_multicast_receiver_socket(
            interface_address=self.interface,
            group_address=self.group_address,
            group_port=self.group_port
        )
        start_time = time.time()

        def _scan():
            while not (self.is_located or self.has_timed_out):
                try:
                    in_data, _addrs = report_socket.recvfrom(RCV_BUFF)
                except socket.timeout:
                    continue
                if in_data:
                    if len(in_data) >= 2: #more than 2 bytes
                        print(f"[{self.interface}] Data received on interface.")
                        id = struct.unpack("!H", in_data[:2])[0]
                        print(f'[{self.interface}] Report {hex(id)} received.')
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
                                self.is_located = True
                                break
            report_socket.close()

        receive_thread = threading.Thread(target=_scan, daemon=True)

        send_socket = create_udp_socket()
        send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        cmd = struct.pack("!H", 0x01b1)
        # not binding required

        receive_thread.start()
        while not self.is_located:
            print(f"[{self.interface}] Ping sent")
            time.sleep(self.ping_interval)
            _nbytes_sent = send_socket.sendto(cmd, (self.group_address, self.group_port))
            if not _nbytes_sent != 2:
                print(f"[{self.interface}] Ping not sent")

            if (time.time() - start_time) < self.timeout:
                self.has_timed_out = True
                break

        send_socket.close()
        receive_thread.join()

        print(f"[{self.interface}] Report 01B2 {'not ' if not self.is_located else ''}received on interface: {self.interface}")


def main(interface: str, timeout: float, ping_interval: float):
    navico_locator = NavicoLocator(interface=interface, timeout=timeout, ping_interval=ping_interval)
    navico_locator.get_report_01b2()

    if navico_locator.is_located:
        return navico_locator.groupA, navico_locator.groupB
    else:
        return None, None


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('interface', help='Interface address to scan')
    parser.add_argument("-t", '--timeout', help="---", type=int, default=30)
    parser.add_argument("-p", '--ping-interval', help="---", type=int, default=2)
    args = parser.parse_args()

    main(interface=args.interface, timeout=args.timeout, ping_interval=args.ping_interval)


