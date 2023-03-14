import numpy as np
import time
from comandos import flags

class ComLib:
    def __init__(self, com, logger):
        self.com = com
        self.logger = logger

    def waitFor(self, flag):
            time.sleep(.01)
            print(f"Esperando por {flag}")
            timeout = time.time() + 5
            while True:
              try:
                if time.time() > timeout:
                  print("TIMED OUT")
                  exit(1)
                  break
                if self.com.rx.getBufferLen() >= 1:
                  rxBuffer, _ = self.com.getData(1)
                  if rxBuffer == flag or rxBuffer in flag:
                      print(f"> {rxBuffer}")
                      time.sleep(.01)
                      return rxBuffer
              except KeyboardInterrupt:
                break

    def getAllUntil(self, flag):
        print('Getting all until', flag)
        collector = b''
        while True:
            try:
                rxBuffer, _ = self.com.getData(1)
                if rxBuffer == flag:
                    return collector
                else:
                    collector = collector + rxBuffer
            except KeyboardInterrupt:
              break

    def send(self, data):
              self.com.sendData(np.asarray(data))
              # print('SENT', data) 