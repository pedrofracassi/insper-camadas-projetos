from packetlib import Header, Packet
from comandos import message_type

def main():
    packet = Packet(
        header=Header(
            message_type=message_type.DATA_3,
            last_successful_packet=0,
            total_packets=10,
            current_packet=1,
            restart_from=0,
            server_id=77,
            file_id=10,
        ),
        payload=b'',
    )

    print(packet)

    # print(packet.encode())

    decoded = Packet.decode(packet.encode())
    print(decoded)

main()