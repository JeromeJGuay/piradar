"""
Other relevent sockopt (maybe):
    # ttl = 2 # 2-hop restriction in network TIME TO LIVE
    # sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
"""

import psutil
import socket
import struct
import pyshark


HOST = ""
RCV_SOCKET_BUFSIZE = 65535



def get_local_addresses():
    addresses = []
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                addresses.append(addr.address)
    return addresses


def create_udp_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(1)
    return sock


def join_mcast_group(sock, interface_address, group_address):
    mreq = struct.pack("4s4s", socket.inet_aton(group_address) + socket.inet_aton(interface_address))
    #mreq = struct.pack("4sL", socket.inet_aton(group_address), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    #sock.setsockopt(socket.SOL_SOCKET, socket.IP_ADD_MEMBERSHIP, mreq)



def create_udp_multicast_receiver_socket(interface_address, group_address, group_port):
    sock = create_udp_socket()

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, RCV_SOCKET_BUFSIZE)

    sock.bind((HOST, group_port))


    join_mcast_group(sock, interface_address, group_address)
    return sock


def ip_address_to_string(addr):
    return socket.inet_ntoa(struct.pack('!I', addr))


class Snooper:

    def __init__(self, address, port, interface=None):
        self.capture = pyshark.LiveCapture(
            interface=interface,
            bpf_filter=f"dst host {address} and dst port {port}",  # either address or address and port should work
            use_ek=True,
            include_raw=True
        )

    def recv(self):
        packet = self.capture.sniff(packet_count=1, timeout=1)
        if packet:
            return packet.data.data.value
        else:
            return None

#            return
        #return next(self.capture.sniff_continuously(1)).data.data.value


if __name__ == "__main__":
    pass