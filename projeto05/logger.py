import time
import datetime
import threading

class Logger():
    def __init__(self, folder):
      timestamp = time.time()
      value = datetime.datetime.fromtimestamp(timestamp)
      text = f"{value.strftime('%Y-%m-%dT%H-%M-%S')}"
      self.filename = folder + '/' + text + '.log'
      self.buffer = []
      self.threadStop = False

    def log(self, *message):
      timestamp = time.time()
      value = datetime.datetime.fromtimestamp(timestamp)

      text = f"[{value.strftime('%Y-%m-%dT%H:%M:%S')}] {' '.join(map(str, message))}"

      print(text)
      self.buffer.append(text)

    def thread(self):
      while not self.threadStop:
        if len(self.buffer) > 0:
          f = open(self.filename, "a", encoding='utf-8')
          f.write(self.buffer.pop(0) + '\n')
          f.close()

    def startThread(self):
      self.threadStop = False
      self.threadInstance = threading.Thread(target=self.thread, args=())
      self.threadInstance.start()

    def stopThread(self):
      self.threadStop = True