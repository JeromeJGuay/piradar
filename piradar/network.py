import psutil
import socket
import struct


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


def create_udp_multicast_receiver_socket(interface_address, group_address, group_port):
    sock = create_udp_socket()

    sock.bind(("", group_port))

    mreq = struct.pack("4s4s", socket.inet_aton(group_address), socket.inet_aton(interface_address))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    return sock


def ip_address_to_string(addr):
    return socket.inet_ntoa(struct.pack('!I', addr))

