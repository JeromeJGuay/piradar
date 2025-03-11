import socket
import struct
import threading
from ifaddr import get_adapters

class NetworkAddress:
    def __init__(self, addr=None, port=0):
        self.addr = addr
        self.port = port

    def format_network_address(self):
        return socket.inet_ntoa(self.addr)

    def get_sockaddr_in(self):
        return (self.format_network_address(), self.port)

class NavicoLocate(threading.Thread):
    def __init__(self, pi):
        threading.Thread.__init__(self)
        self.pi = pi
        self.m_interface_addr = []
        self.m_socket = []
        self.m_interface_count = 0
        self.m_errors = []
        self.m_exclusive = threading.Lock()
        self.m_is_shutdown = False
        self.m_shutdown = False
        self.m_report_count = 0

    def cleanup_cards(self):
        if self.m_interface_addr:
            self.m_interface_addr = []
        if self.m_socket:
            for s in self.m_socket:
                if s is not None:
                    s.close()
            self.m_socket = []
        self.m_interface_count = 0
        self.clear_errors()

    def update_ethernet_cards(self):
        self.cleanup_cards()
        adapters = get_adapters()
        self.m_interface_count = len(adapters)
        print(f"Found {self.m_interface_count} ethernet cards")

        if self.m_interface_count > 0:
            self.m_socket = [None] * self.m_interface_count
            self.m_interface_addr = [None] * self.m_interface_count

            for i, adapter in enumerate(adapters):
                if adapter.ips:
                    self.m_interface_addr[i] = NetworkAddress(socket.inet_aton(adapter.ips[0].ip))
                    self.m_socket[i] = self.start_udp_multicast_receive_socket(self.m_interface_addr[i], reportNavicoCommon)
                    if self.m_socket[i] is None:
                        error = f"Cannot scan interface {self.m_interface_addr[i].format_network_address()}"
                        print(error)
                        self.add_error(error)
                    else:
                        print(f"Scanning interface {self.m_interface_addr[i].format_network_address()} for radars on socket {self.m_socket[i].fileno()}")

        self.wake_radar()

    def start_udp_multicast_receive_socket(self, interface_addr, report_navico_common):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((interface_addr.format_network_address(), 0))
            mreq = struct.pack("4sl", socket.inet_aton(report_navico_common.format_network_address()), socket.INADDR_ANY)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            return sock
        except Exception as e:
            print(f"Error creating multicast socket: {e}")
            return None

    def clear_errors(self):
        with self.m_exclusive:
            self.m_errors = []

    def add_error(self, error):
        with self.m_exclusive:
            self.m_errors.append(error)

    def append_errors(self, error):
        with self.m_exclusive:
            error += '\n'.join(self.m_errors)

    def wake_radar(self):
        WAKE_COMMAND = b'\x01\xb1'
        send_addr = (socket.inet_ntoa(struct.pack('!I', 0xec060705)), 6878)

        for interface in self.m_interface_addr:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            if sock is not None:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind((interface.format_network_address(), 0))
                sent = sock.sendto(WAKE_COMMAND, send_addr)
                if sent == len(WAKE_COMMAND):
                    print(f"Sent wake command to radar on {interface.format_network_address()}")
                else:
                    print(f"Failed to send wake command to radars on {interface.format_network_address()}")
                sock.close()

    def run(self):
        print("NavicoLocate thread starting")
        self.m_is_shutdown = False
        self.update_ethernet_cards()

        while not self.m_shutdown:
            tv = 1
            fdin = []
            max_fd = None

            for s in self.m_socket:
                if s is not None:
                    fdin.append(s)
                    max_fd = max(s.fileno(), max_fd)

            if not fdin:
                continue

            r, _, _ = select.select(fdin, [], [], tv)

            if r:
                for s in self.m_socket:
                    if s is not None:
                        data, addr = s.recvfrom(1500)
                        if len(data) > 2:
                            radar_address = NetworkAddress(addr[0], addr[1])
                            self.process_report(radar_address, data)

            self.cleanup_cards()

    def process_report(self, radar_address, data):
        print(f"Processing report from {radar_address.format_network_address()}")
        # Placeholder for actual processing logic
        return True


reportNavicoCommon = NetworkAddress(socket.inet_aton('236.6.7.5'), 6878)