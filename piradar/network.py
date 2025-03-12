"""
Other relevent sockopt (maybe):
    # ttl = 2 # 2-hop restriction in network TIME TO LIVE
    # sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
"""

import psutil
import socket
import struct

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


def join_mcast_group(sock, address, interface):
    mreq = socket.inet_aton(address) + socket.inet_aton(interface)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)


def ip_address_to_string(addr):
    return socket.inet_ntoa(struct.pack('!I', addr))
