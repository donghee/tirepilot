# from PySide.QtCore import Signal, QThread, Qt, Slot
from PySide import QtCore, QtGui

import serial
import sys
import time

class SerialReader(QtCore.QThread):
   message = QtCore.Signal(str)
   finished = QtCore.Signal(str)

   def __init__(self, parent=None):
     super(SerialReader, self).__init__(parent)

   def start(self, ser, priority = QtCore.QThread.InheritPriority):
      self.ser = ser
      QtCore.QThread.start(self, priority)

   def run(self):
      data = ''
      while True:
         try:
            # data = self.ser.read(1)
            # n = self.ser.inWaiting()
            # if n:
                # data = data + self.ser.read(n)
            # self.message.emit("%d: %s" % (n, data))
            data = data + self.ser.read(1)
            if data[-1] == '\n':
                self.message.emit("%s" % data[:-1])
                data = ''
         except:
            errMsg = "Reader thread is terminated unexpectedly."
            self.finished.emit("%s" % errMsg)
            break

class SerialWriter(QtCore.QThread):
   message = QtCore.Signal(str)
   finished = QtCore.Signal(str)

   def start(self, ser, cmd = "", priority = QtCore.QThread.InheritPriority):
      self.ser = ser
      self.cmd = cmd
      QtCore.QThread.start(self, priority)
      
   def run(self):
      try:
         self.ser.write(str(self.cmd))
      except:
         errMsg = "Writer thread is terminated unexpectedly."
         self.finished.emit("%s" % errMsg)

   def terminate(self):
      self.wait()
      QtCore.QThread.terminate(self)

class WheelDriver():

    _data = []

    def get_data(self):
        return self._data

    @QtCore.Slot(str)
    def print_data(self, data):
        d = [int(x) for x in data.split(',')]
        # if len(d) == 5: # check size of length
        if len(d) == 6: # ELEV ADDED
          self._data = d

    def print_error(self, data):
        print "ERROR: " + data

    def __init__(self, _port_name):
        self.port_name = _port_name
        self.port = None
        self.reader = SerialReader()
        self.writer = SerialWriter()

        self.reader.message.connect(self.print_data, QtCore.Qt.QueuedConnection)
        self.reader.finished.connect(self.print_error, QtCore.Qt.QueuedConnection)

    def command(self, cmd):
        self.writer.start(self.port, cmd+chr(0x0d))

    def start_reader(self, ser):
        self.reader.start(ser)

    def stop_threads(self):
        self.stop_reader()
        self.stop_writer()
       
    def stop_reader(self):
        if self.reader.isRunning():
            self.reader.terminate()
           
    def stop_writer(self):
        if self.writer.isRunning():
            self.writer.terminate()

    def connect(self):
        self.disconnect()
        try:
            # print self.port_name
            self.port = serial.Serial(self.port_name)
            self.start_reader(self.port)
            print("Connected successfully.")
        except:
            self.port = None
            print("Failed to connect!")

    def disconnect(self):
        self.stop_threads()
        if self.port == None: return
        try:
            if self.port.isOpen:
                self.port.close()
                print("Disconnected successfully.")
        except:
            print("Failed to disconnect!")
        self.port = None

def test_wheeldriver_command():
    wheeldriver = WheelDriver("/dev/tty.usbmodem1432")
    # wheeldriver = WheelDriver("COM3")
    wheeldriver.connect()
    wheeldriver.command('w 35')
    time.sleep(2)
    # wheeldriver.command('s')
    # time.sleep(1)
    # wheeldriver.command('a 35')
    # time.sleep(2)
    # wheeldriver.command('d 35')
    # time.sleep(2)
    wheeldriver.command('s')
    time.sleep(6)
    wheeldriver.command('x 60')
    time.sleep(4)
    wheeldriver.command('s')
    time.sleep(2)
    wheeldriver.disconnect()

def main():
    test_wheeldriver_command()

if __name__ == "__main__":
    main()
