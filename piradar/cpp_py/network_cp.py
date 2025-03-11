import psutil

import struct
import socket


# def valid_interface(i):
#     return i and i.ifa_addr and i.ifa_addr.sa_family == socket.AF_INET and (i.ifa_flags & socket.IFF_UP) > 0 and (i.ifa_flags & socket.IFF_LOOPBACK) == 0 and (i.ifa_flags & socket.IFF_MULTICAST) > 0
#

def get_local_addresses():
    addresses = []
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                addresses.append(addr.address)
    return addresses

# def ip_address_to_string(a):
#     return socket.inet_ntoa(struct.pack('!I', a))

def ip_address_to_string(a):
    if isinstance(a, str):
        return a
    return socket.inet_ntoa(struct.pack('!I', a))


# def ip_address_from_string(a):
#     return struct.unpack('!I', socket.inet_aton(a))[0]


class AddressSet:
    def __init__(self, label, data, send, report, interface):
        self.label = label
        self.data = data
        self.send = send
        self.report = report
        self.interface = interface

    def __str__(self):
        return f'{self.label}: data: {ip_address_to_string(self.data.address)}:{self.data.port}, report: {ip_address_to_string(self.report.address)}:{self.report.port}, send: {ip_address_to_string(self.send.address)}:{self.send.port}'


def scan_for_radar(addresses=None):
    if addresses is None:
        addresses = get_local_addresses()
    ret = []
    for a in addresses:
        if not isinstance(a, str):
            a = socket.inet_ntoa(struct.pack('!I', a))
        listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_sock.settimeout(1)
        listen_sock.bind(('', 6878))
        mreq = struct.pack('4s4s', socket.inet_aton('236.6.7.5'), socket.inet_aton(a))
        try:
            listen_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        except OSError as e:
            listen_sock.close()
            continue

        send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        send_sock.bind((a, 0))
        data = struct.pack('!H', 0xb101)
        send_sock.sendto(data, ('236.6.7.5', 6878))
        for _ in range(3):
            try:
                in_data, from_addr = listen_sock.recvfrom(1024)
                if len(in_data) == struct.calcsize('!HHIHHHHIIBB'):
                    b201 = struct.unpack('!HHIHHHHIIBB', in_data)
                    if b201[0] == 0xb201:
                        asa = AddressSet('HaloA', b201[1], b201[2], b201[3], a)
                        ret.append(asa)
                        asb = AddressSet('HaloB', b201[4], b201[5], b201[6], a)
                        ret.append(asb)
            except socket.timeout:
                continue
        listen_sock.close()
        send_sock.close()
        if ret:
            break
    return ret


if __name__ == "__main__":

    address = '236.6.7.5'
    port = 6878
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, port))
