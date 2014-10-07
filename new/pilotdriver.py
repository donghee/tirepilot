import serial
import logging
import sys

from wheeldriver import WheelDriver
from steeringdriver import PMC1HSUSBDriver

class SteeringPilot:
    def __init__(self, port_name, speed):
        port = serial.Serial(port_name, 9600)
        stepping_driver = PMC1HSUSBDriver(port)
        stepping_driver.stop()
        stepping_driver.set_speed(speed)
        self.init_driver(stepping_driver)
        self.recentcommand = 'neutral'
        self.turn_ticks = 100000
        
    def set_turn_ticks(self, ticks=100000):
        self.turn_ticks = ticks

    def get_recentcommand(self):
        return self.recentcommand

    def init_driver(self, _stepping_driver):
        self.stepping_driver = _stepping_driver
        self.current_location = 0
        self.logger = logging.getLogger('SteeringPilot')
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)


    def turn_by_position(self, percent, pot): # limit 100000
        if self.stepping_driver.isworking():
            return

        # TODO: need to delay? or change baud rate?
        # TODO: wait for next turn by position ??
        self.current_location = self.stepping_driver.get_current_pos()

        # print "TURN BY POSITION %d" % percent

        if self.current_location < -100100 or 100100 < self.current_location:
            # print "Range Overflow! %d" % self.current_location
            self.logger.info('Steering Range Overflow Current: %d', self.current_location) # TODO: overflow processing using pot
            self.current_location = self.stepping_driver.get_current_pos()
            # if self.current_location < -190000:
            #     overflow_delta_ticks = -190000 - self.current_location
            #     self.stepping_driver.forward(abs(overflow_delta_ticks))
            # if self.current_location > 190000:
            #     overflow_delta_ticks = self.current_location - 190000
            #     self.stepping_driver.backward(abs(overflow_delta_ticks))

        target_location = (int(200000/100.0) * (100-percent)) - 100000 # max turn tick is 100000
        # target_location = (int(self.turn_ticks/100.0) * (100-percent)) - (self.turn_ticks/2)
        delta_ticks = target_location - self.current_location
        self.logger.info('Current: %d, Target: %d, Delta ticks: %d', self.current_location, target_location, delta_ticks)
        if delta_ticks >= 0:
            self.stepping_driver.forward(abs(delta_ticks))
        else:
            self.stepping_driver.backward(abs(delta_ticks))

        # TEST MOCK
        # self.stepping_driver.spy_set_current_pos(target_location)


    def turn_by_position_limit_200000(self, percent, pot):
        if self.stepping_driver.isworking():
            return

        # TODO: need to delay? or change baud rate?
        # TODO: wait for next turn by position ??
        self.current_location = self.stepping_driver.get_current_pos()

        print "TURN BY POSITION %d" % percent

        if self.current_location < -190000 or 190000 < self.current_location:
            # print "Range Overflow! %d" % self.current_location
            self.logger.info('Steering Range Overflow Current: %d Turn right: %d', self.current_location, delta_ticks) # TODO: overflow processing using pot
            self.current_location = self.stepping_driver.get_current_pos()
            if self.current_location < -190000:
                overflow_delta_ticks = -190000 - self.current_location
                self.stepping_driver.forward(abs(overflow_delta_ticks))
            if self.current_location > 190000:
                overflow_delta_ticks = self.current_location - 190000
                self.stepping_driver.backward(abs(overflow_delta_ticks))
            return

        target_location = (int(400000/100.0) * (100-percent)) - 200000
        delta_ticks = target_location - self.current_location
        self.logger.info('Current: %d, Target: %d, Delta ticks: %d', self.current_location, target_location, delta_ticks)
        if delta_ticks >= 0:
            self.stepping_driver.forward(abs(delta_ticks))
        else:
            self.stepping_driver.backward(abs(delta_ticks))

        # TEST MOCK
        self.stepping_driver.spy_set_current_pos(target_location)

    def turn_left(self, absolute_angle):
        if self.stepping_driver.isworking():
            return
        if self.recentcommand == 'turn_right':
            absolute_angle = 2

        self.recentcommand = 'turn_left'        
        # TODO: self.stepping_driver.get_current_pos() is neutral + turn_ticks

        delta_ticks = int(absolute_angle * self.turn_ticks)
        self.logger.info('Current: %d Turn left: %d', self.current_location, delta_ticks)
        self.stepping_driver.forward(delta_ticks)
        self.current_location += delta_ticks
        # TEST MOCK
        self.stepping_driver.spy_set_current_pos(self.current_location)
    
    def turn_left_limit_200000(self, absolute_angle):
        # self.turn_ticks = 200000
        if self.stepping_driver.isworking():
            return
        if self.recentcommand == 'turn_right':
            absolute_angle = 2

        self.recentcommand = 'turn_left'        
        # TODO: self.stepping_driver.get_current_pos() is neutral + turn_ticks

        delta_ticks = int(absolute_angle * self.turn_ticks)
        self.logger.info('Current: %d Turn left: %d', self.current_location, delta_ticks)
        self.stepping_driver.forward(delta_ticks)
        self.current_location += delta_ticks
        # TEST MOCK
        self.stepping_driver.spy_set_current_pos(self.current_location)

    def turn_right(self, absolute_angle):
        if self.stepping_driver.isworking():
            return
        if self.recentcommand == 'turn_left':
            absolute_angle = 2

        self.recentcommand = 'turn_right'        
        delta_ticks = int(absolute_angle * self.turn_ticks)
        self.logger.info('Current: %d Turn right: %d', self.current_location, delta_ticks)
        self.stepping_driver.backward(delta_ticks)
        self.current_location -= delta_ticks
        # TEST MOCK
        self.stepping_driver.spy_set_current_pos(self.current_location)

    def stop(self):
        if self.stepping_driver.isworking(): return
        # self.recentcommand = 'stop'        
        self.logger.info('Current: %d Stop', self.current_location)
        self.stepping_driver.stop()
    
    def position_clear(self):
        self.stepping_driver.reset()

    def middle_position(self, pot): 
        return 
        # pot range: left(1.97) - middle 1.60 - right 1.15 #if pot > 170: #self.stepping_driver.backward(10000)
            #self.turn_right(0.05)
        #if pot < 150:
            #self.stepping_driver.forward(10000)
            #self.turn_left(0.05)
        #if 155 <= pot <= 165:
            #print 'Finish Middle Position Pot: %d' % pot
        
    def neutral(self):
        print "neutral0"
        if self.stepping_driver.isworking(): return
        print "neutral1"
        self.recentcommand = 'neutral'
        self.logger.info('Current: %d, Neutral', self.stepping_driver.get_current_pos())
        print "neutral2"
        self.current_location = self.stepping_driver.get_current_pos()
        if self.current_location >= 0:
            self.stepping_driver.backward(abs(self.current_location))
            print abs(self.current_location)
        else:
            self.stepping_driver.forward(abs(self.current_location))
            print abs(self.current_location)
        self.current_location = 0
        print "neutral3"
        # TEST MOCK
        self.stepping_driver.spy_set_current_pos(self.current_location)

    def isworking(self):
        return self.stepping_driver.isworking()

    def disconnect(self): 
        self.neutral()
        self.stepping_driver.close()

class WheelPilot:

    steering_pot = 0
    batt24 = 0
    batt48 = 0
    throttle_in = 0
    rudo_in = 0
    elev_in = 0

    def get_steering_pot(self):
        return self.steering_pot

    def get_batt48(self):
        return self.batt48

    def get_batt24(self):
        return self.batt24

    def get_throttle_from_rc(self):
        return self.throttle_in

    def get_rudo_from_rc(self):
        return self.rudo_in

    def get_elev_from_rc(self):
        return self.elev_in

    def update_data(self):
        #print self.wheeldriver.get_data()
        if len(self.wheeldriver.get_data()) == 6:
            self.steering_pot, self.batt24, self.batt48, self.throttle_in, self.rudo_in, self.elev_in = self.wheeldriver.get_data()

    def get_recentcommand(self):
        return self.recentcommand

    def __init__(self, _port_name):
        self.port_name = _port_name
        self.wheeldriver = WheelDriver(self.port_name)
        self.wheeldriver.connect()
        self.recentcommand = 'stop'

    def command(self, command):
        self.wheeldriver.command(command)

    def forward(self, throttle):
        self.command('w '+str(throttle))
        self.recentcommand = 'forward'

    def backward(self, throttle):
        self.command('x '+str(throttle))
        self.recentcommand = 'backward'

    def turn_right(self, throttle):
        self.command('a '+str(throttle))
        self.recentcommand = 'turn_right'

    def turn_left(self, throttle):
        self.command('d '+str(throttle))        
        self.recentcommand = 'turn_left'

    def stop(self):
        self.command('s')
        self.recentcommand = 'stop'

    def brake(self):
        #self.command('s')
        self.command('b')        
        self.recentcommand = 'brake'

    def disconnect(self):
        self.stop()
        self.wheeldriver.disconnect()

def main_pmc1hsusb():
    port = serial.Serial("/dev/tty.usbserial-A901NMD9", 9600)
    stepping_motor = PMC1HSUSBDriver(port)
    stepping_motor.stop()
    stepping_motor.set_speed(6000)
    steering = SteeringPilot(stepping_motor)
    for i in range(3):
        steering.turn_right(1)
        steering.neutral()
        steering.turn_left(1)
        steering.neutral()
    steering.quit()

def main():
    main_pmc1hsusb()

if __name__ == "__main__":
    main()