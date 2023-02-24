class flags:
  EOP = b'\x10\x11\x12'
  HEADER_START = b'\xF1'
  HEADER_END = b'\xF2'

class packet_type:
  DATA = b'\x00'
  COMMAND = b'\x01'

class command_type:
  PING = b'\x00'
  PONG = b'\x01'
  ACK = b'\x02'
  NACK = b'\x03'
  TRANSMISSION_OK = b'\x04'