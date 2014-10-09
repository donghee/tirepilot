import serial
import time
import logging
import sys

class PMC1HSUSBDriver:
    def __init__(self, port):
        self.port = port
        self.setup()
        self.lastcommand = ''
        self.speed = 4000

        self.logger = logging.getLogger('PMC1HSUSB')
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        
        self.ending_time = time.time()

        # for testing
        self.mock_current_pos = 0
    
    def spy_set_current_pos(self, x):
        self.mock_current_pos = x

    def spy_lastcommand(self):
        return self.lastcommand

    def command(self, byte_command):
        for c in byte_command:
            self.port.write(c)
        self.port.write(chr(0x0d))

    def set_speed(self, pps):
        self.speed = pps
        self.command("SPD "+ str(self.speed))

    def reset(self):
        self.command("RST")
        time.sleep(0.2)

    def setup(self):
        self.reset()
        self.set_speed(4000)

    def sleepFor(self, ticks):
        seconds = int(ticks/(self.speed*7))
        self.ending_time = time.time() + seconds
        #return time.sleep(seconds) #24v 16
        # print time.time()
        # print self.ending_time
        # print "DEBUG ISWORKING %t" % self.ending_time

    def isworking(self):
        return  (not (time.time() >= self.ending_time))

    def forward(self, ticks):
        self.lastcommand = "PIC " + str(ticks)
        self.command(self.lastcommand)
        self.logger.info('Foward: %d ', ticks )
        self.sleepFor(ticks)

    def backward(self, ticks):
        self.lastcommand = "PIC -" + str(ticks)
        self.command(self.lastcommand)
        self.logger.info('Backward: %d' , ticks )
        self.sleepFor(ticks)

    def get_current_pos(self):
        self.command("POS")
        if sys.platform == 'darwin': # mock
          _pos = "POS 0,0"
          _pos = "POS "+str(hex(self.mock_current_pos))+",0"
        else:
          _pos = self.port.read(22) 
        __pos = _pos[4:]
        pos = __pos.split(',')[0]
        pos =  int(pos, 16)
        if pos <= 0x7fffffff:
            pos = pos
        else:
            pos = -(0xffffffff-pos+1)
        return pos

    def stop(self):
        self.command("STO X")

    def close(self):
        self.port.close()
