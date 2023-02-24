import numpy as np
import time
from comandos import flags, packet_type
from comlib import ComLib

class PacketLib:
    def __init__(self) -> None:
        pass

    def get_next_packet(self, comlib: ComLib):
        (header_bytes, _) = comlib.com.getData(12)
        print('HEADER BYTES', header_bytes)
        if header_bytes is None:
            return None
        header = self.decode_header(header_bytes)

        if header['data_size'] > 0:
            (data, _) = comlib.com.getData(header['data_size'])
            print('DATA BYTES', data)
            if data is None:
                return None
        else:
            data = b''

        (eop, _) = comlib.com.getData(3)
        print('EOP BYTES', eop)
        if eop is None:
            return None
        if eop != flags.EOP:
            raise Exception("Invalid packet EOP")

        return header_bytes + data + eop

    def decode_header(self, header: bytearray):
        if header[0:1] != flags.HEADER_START or header[-1:] != flags.HEADER_END:
            raise Exception("Invalid packet header boundaries")

        ptype = header[1:2]
        metadata = header[2:8]
        data_size = header[9:11]

        if ptype == packet_type.DATA:
            return {
                'type': ptype,
                'metadata': {
                    'index': int.from_bytes(metadata[0:2], "big"),
                    'total': int.from_bytes(metadata[2:4], "big"),
                },
                'data_size': int.from_bytes(data_size),
            }

        elif ptype == packet_type.COMMAND:
            return {
                'type': ptype,
                'metadata': {
                    'command': metadata[0:1]
                },
                'data_size': int.from_bytes(data_size),
            }

    def decode_packet(self, packet):
      header = packet[0:12]
      eop = packet[-3:]

      if header[0:1] != flags.HEADER_START or header[-1:] != flags.HEADER_END:
        print(header[0:1], header[-1:])
        raise Exception("Invalid packet header boundaries")

      ptype = header[1:2]
      metadata = header[2:8]
      data_size = header[9:11]

      if eop != flags.EOP:
        raise Exception("Invalid End Of Package")

      if ptype == packet_type.DATA:
        data = packet[12:-3]
        return {
            'type': ptype,
            'metadata': {
                'index': int.from_bytes(metadata[0:2], "big"),
                'total': int.from_bytes(metadata[2:4], "big"),
            },
            'data_size': int.from_bytes(data_size),
            'data': data
        }

      elif ptype == packet_type.COMMAND:
        data = packet[12:-3]
        return {
            'type': ptype,
            'metadata': {
                'command': metadata[0:1]
            },
            'data_size': int.from_bytes(data_size),
            'data': data
        }
      
    def split_into_packets(self, data, packet_size=50):
        packets = []
        total_packets = int(np.ceil(len(data) / packet_size))
        for i in range(total_packets):
            packet_data = data[i*packet_size:(i+1)*packet_size]
            packets.append(self.build_data_packet(i+1, total_packets, packet_data))
        return packets

    
    def build_header(self, packet_type: packet_type, metadata: bytearray, data_size: int = 0):
        header = flags.HEADER_START + packet_type + self.rpad(metadata, 7) + data_size.to_bytes(2, "big") + flags.HEADER_END
        if len(header) != 12:
            raise Exception("Invalid header size")
        return header

    def build_data_packet(self, packet_index: int, total_packets: int, data):
        metadata = packet_index.to_bytes(2, "big") + total_packets.to_bytes(2, "big")
        header = self.build_header(packet_type.DATA, metadata, len(data))
        packet = header + data + flags.EOP
        if len(packet) > 65 or len(packet) < 15:
            raise Exception("Invalid packet size")
        return packet
    
    def build_command_packet(self, command):
        packet = self.build_header(packet_type.COMMAND, command) + flags.EOP
        if len(packet) > 65 or len(packet) < 15:
            raise Exception("Invalid packet size")
        return packet

    def build_command_packet(self, command):
        packet = self.build_header(packet_type.COMMAND, command) + flags.EOP
        if len(packet) != 15:
            raise Exception("Invalid packet size")
        return packet
    
    def rpad(self, data, size):
        return data + b'\x00' * (size - len(data))
    
    def lpad(self, data, size):
        return b'\x00' * (size - len(data)) + data