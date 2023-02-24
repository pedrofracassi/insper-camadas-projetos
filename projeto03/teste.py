from packetlib import PacketLib
from comandos import flags, packet_type, command_type

def main():
    lib = PacketLib()

    data_size = 3
    # print(lib.lpad(b'\x11', 10) + b'\xDD' + "Hello World".encode('utf-8'))

    packets = lib.split_into_packets(b'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.', 10)
    for packet in packets:
        print(packet)
        print(lib.decode_packet(packet))

main()