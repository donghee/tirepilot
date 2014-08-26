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
        self.turn_ticks = 200000
        
    def set_turn_ticks(self, ticks=150000):
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

    def turn_by_position(self, percent):
        if self.stepping_driver.isworking():
            return
        self.current_location = self.stepping_driver.get_current_pos()
        if self.current_location < -200000 or 200000 < self.current_location:
            print "Range Overflow! %d", self.current_location
            return
        target_location = (int(400000/100.0) * (100-percent)) - 200000
        delta_ticks = target_location - self.current_location
        self.logger.info('Current: %d, Target: %d, Delta ticks: %d', self.current_location, target_location, delta_ticks)
        if delta_ticks >= 0:
            self.stepping_driver.forward(abs(delta_ticks))
        else:
            self.stepping_driver.backward(abs(delta_ticks))
    
    def turn_left(self, absolute_angle):
        if self.stepping_driver.isworking():
            return
        if self.recentcommand == 'turn_right':
            absolute_angle = 2

        self.recentcommand = 'turn_left'        
        delta_ticks = int(absolute_angle * self.turn_ticks)
        self.logger.info('Current: %d Turn left: %d', self.current_location, delta_ticks)
        self.stepping_driver.forward(delta_ticks)
        self.current_location += delta_ticks

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

    def stop(self):
        if self.stepping_driver.isworking(): return
        self.logger.info('Current: %d Stop', self.current_location)
        self.stepping_driver.stop()
        
    def neutral(self):
        if self.stepping_driver.isworking(): return
        self.recentcommand = 'neutral'
        self.logger.info('Neutral: %d', self.stepping_driver.get_current_pos())
        self.current_location = self.stepping_driver.get_current_pos()
        if self.current_location >= 0:
            self.stepping_driver.backward(abs(self.current_location))
        else:
            self.stepping_driver.forward(abs(self.current_location))
        self.current_location = 0

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
        # if len(self.wheeldriver.get_data()) == 5:
        #     self.steering_pot, self.batt24, self.batt48, self.throttle_in, self.rudo_in = self.wheeldriver.get_data()

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
        self.command('s')
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
