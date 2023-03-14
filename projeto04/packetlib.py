import numpy as np
import time
from comandos import flags, message_type
from comlib import ComLib
from dataclasses import dataclass

@dataclass
class Header:
  message_type: bytearray
  total_packets: int = 0
  last_successful_packet: int = 0
  server_id: int = None
  current_packet: int = None
  file_id: int = None
  payload_size: int = None
  restart_from: int = 0

  @classmethod
  def decode(self, data: bytearray):
    curr_message_type = data[0:1]

    return Header(
      message_type=data[0:1],
      server_id=int.from_bytes(data[1:2], 'big') if data[1:2] != b'\x00' else None,
      total_packets=int.from_bytes(data[3:4], 'big'),
      current_packet=int.from_bytes(data[4:5], 'big') if curr_message_type == message_type.DATA_3 else None,
      file_id=int.from_bytes(data[5:6], 'big') if curr_message_type in [message_type.HELLO_1, message_type.READY_2] else None,
      payload_size=int.from_bytes(data[5:6], 'big') if curr_message_type == message_type.DATA_3 else None,
      restart_from=int.from_bytes(data[6:7], 'big') if curr_message_type == message_type.ERROR_6 else None,
      last_successful_packet=int.from_bytes(data[7:8], 'big'),
    )

  def encode(self):
    print(self)

    bytes = [
      self.message_type,
      self.server_id.to_bytes(1, 'big') if self.server_id is not None else b'\x00',
      b'\x00',
      self.total_packets.to_bytes(1, 'big'),
      self.current_packet.to_bytes(1, 'big') if self.message_type == message_type.DATA_3 else b'\x00',
      self.file_id.to_bytes(1, 'big') if self.message_type in [message_type.HELLO_1, message_type.READY_2] else self.payload_size.to_bytes(1, 'big') if self.message_type == message_type.DATA_3 else b'\x00',
      self.restart_from.to_bytes(1, 'big') if self.restart_from is not None else b'\x00',
      self.last_successful_packet.to_bytes(1, 'big') if self.last_successful_packet is not None else b'\x00',
      b'\x00', # CRC
      b'\x00', # CRC
    ]

    joined = b''

    for byte in bytes:
      # print(byte)
      joined = joined + byte

    return joined
      

@dataclass
class Packet:
  header: Header
  payload: bytearray = b''

  def encode(self, logger = None):
    def logif(*msg):
      if logger is not None:
        logger.log(*msg)

    logif('ENCODING', self)
    encoded = self.header.encode() + self.payload + flags.EOP
    return encoded

  @classmethod
  def decode(self, data: bytearray, logger = None):
    def logif(*msg):
      if logger is not None:
        logger.log(*msg)

    header = Header.decode(data[0:10])
    payload = data[10:-4]
    eop = data[-4:]

    if eop != flags.EOP:
      raise Exception("Invalid End Of Package")

    packet = Packet(header, payload)

    logif('DECODED', packet)

    return packet

class PacketLib:
    def __init__(self, logger) -> None:
        self.logger = logger
        pass

    def get_next_packet(self, comlib: ComLib):
      (header_bytes, _) = comlib.com.getData(10)
      # print('HEADER BYTES', header_bytes)
      if header_bytes is None:
        return None
      header = Header.decode(header_bytes)

      data = b''
      if header.message_type == message_type.DATA_3:
        (data, _) = comlib.com.getData(header.payload_size)
        # print('DATA BYTES', data)
        if data is None:
          return None

      (eop, _) = comlib.com.getData(4)
      # print('EOP BYTES', eop)
      if eop is None:
        return None

      if eop != flags.EOP:
        raise Exception("Invalid End Of Package")

      return header_bytes + data + eop
    
    def rpad(self, data, size):
        return data + b'\x00' * (size - len(data))
    
    def lpad(self, data, size):
        return b'\x00' * (size - len(data)) + data
    
    def split_data(self, data, packet_size):
        packets = []
        for i in range(0, len(data), packet_size):
            packets.append(data[i:i+packet_size])
        return packets