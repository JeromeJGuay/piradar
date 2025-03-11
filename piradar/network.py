"""
Other relevent sockopt (maybe):
    # ttl = 2 # 2-hop restriction in network TIME TO LIVE
    # sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
"""

import psutil
import socket

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





if __name__ == '__main__':
    import threading
    import struct

#     "#################################################"
#     #addrs = get_local_addresses()
#     #
#     # message = b'very important data'
#     #
#     # ### RADAR PORT and GROUP [TO DETERMINE] maybe with Wireshark
#     # ## look into pyshark
    laddrs = get_local_addresses()

    HOST = ""
    interface = laddrs[1]

    maddresses = [
        ('236.6.7.15', 6659),
        ("236.6.7.10", 6878),
        ('236.6.7.10', 6680),
        ('236.6.7.9', 6679),
    ]
    mcast_group, mcast_port = maddresses[0]
    # sender_sock = create_udp_socket()
    # sender_sock.bind((HOST, mcast_port))
    #
    # def send():
    #     data = struct.pack('!H', 0xb101)
    #     sender_sock.sendto(data, (mcast_group, mcast_port))

    listener_sock = create_udp_socket()
    join_mcast_group(listener_sock, mcast_group, interface)
    listener_sock.bind((HOST, mcast_port))

    def listen():
        while True:
            try:
                in_data, from_addr = listener_sock.recvfrom(1024)
                print(in_data, from_addr)
            except socket.timeout:
                continue

    listen_thread = threading.Thread(target=listen, daemon=True)

    listen_thread.start()

    "#################################################"

    # Example usage:
    # Replace 'eth0' with the name of your network interface
    #monitor_full_multicast_range(addrs[6], duration=1)
    "#################################################"

    #radar_eth = '169.254.228.66'


    # r=scan(addrs[0])
#
    "a0:29:19:48:f6:c6"