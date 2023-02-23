dados = {
  1: b'\x00\x00\x00\x00',
  2: b'\x00\x00\xAA\x00',
  3: b'\xAA\x00\x00',
  4: b'\x00\xAA\x00',
  5: b'\x00\x00\xAA',
  6: b'\x00\xAA',
  7: b'\xAA\x00',
  8: b'\x00',
  9: b'\xFF',
}

class flags:
  IM_HERE = b'\x70'
  GO_AHEAD = b'\x71'
  REPEAT = b'\x72'
  START_TRANSMISSION = b'\x73'
  END_TRANSMISSION = b'\x74'
  START_COMMAND = b'\x75'
  END_COMMAND = b'\x76'

  COMMANDS_DONE = b'\x77'
  FEEDBACK_READY = b'\x78'
  FEEDBACK_DONE = b'\x79'
  FEEDBACK_ERROR = b'\x7A'
  FEEDBACK_OK = b'\x7B'