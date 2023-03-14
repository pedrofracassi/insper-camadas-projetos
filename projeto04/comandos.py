class flags:
  EOP = b'\xAA\xBB\xCC\xDD'

class message_type:
  HELLO_1 = b'\x01'
  READY_2 = b'\x02'
  DATA_3 = b'\x03'
  ACK_4 = b'\x04'
  TIMEOUT_5 = b'\x05'
  ERROR_6 = b'\x06'