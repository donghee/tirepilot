# coding: utf-8

import sys
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtCore, QtGui, QtOpenGL
from qpygletwidget import QPygletWidget

import pyglet
from pyglet.window import key
from pyglet.window import FPSDisplay
from pilotdriver import SteeringPilot, WheelPilot

from spin import *

prev_rudo = 0
prev_throttle = 0

import os

def we_are_frozen():
    """Returns whether we are frozen via py2exe.
    This will affect how we find out where we are located."""

    return hasattr(sys, "frozen")

def module_path():
    """ This will get us the program's directory,
    even if we are frozen using py2exe"""

    if we_are_frozen():
        return os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))

    return os.path.dirname(unicode(__file__, sys.getfilesystemencoding( )))

class EegCarDashboard(QPygletWidget):

    def on_init(self):
        self.init_spin();
        self.init_labels()
        self.init_images()
        self.init_pilotdriver()
        self.init_rc_mode()

        self.setMinimumSize(QSize(640, 480))

    def init_pilotdriver(self):
        if sys.platform == 'win32':
            steering_port_name = "COM4" # motion control
            wheel_port_name = "COM3" # mbed
        elif sys.platform == 'darwin':
            # steering_port_name = "/dev/tty.usbserial-A901NMD9"
            # wheel_port_name = "/dev/tty.usbmodem1432"
            steering_port_name = "/dev/ttys004" # mock
            wheel_port_name = "/dev/ttys007" # mock
        self.steering = SteeringPilot(steering_port_name, 4000) # default 4000
        # self.steering.set_turn_ticks(150000) # kintex version, speed 5000
        # self.steering.set_turn_ticks(100000) # fulll turn
        self.steering.set_turn_ticks(50000) # half turn

        self.wheel = WheelPilot(wheel_port_name)
        self.set_max_throttle(40) # default 40
        self.set_backward_max_throttle(40) # default 40

    def init_spin(self):
        self.spin = Spin()

    def init_labels(self):
        _x, _y = self.get_center()
        import os

        pyglet.font.add_file(
            os.path.join(
                module_path(), # for py2exe
                # os.path.dirname(__file__), 
                'resources/NewMedia.ttf')
        )
        newmedia_font = pyglet.font.load('NewMedia')
        pyglet.font.add_file(
            os.path.join(
                module_path(),
                # os.path.dirname(__file__),
                'resources/pf_ronda_seven.ttf')
        )
        ronda_seven_font = pyglet.font.load('PF Ronda Seven')
        self.throttle_label = pyglet.text.Label('Throttle: 0',
                                                font_name='NewMedia',
                                                font_size= 36,
                                                anchor_x='left', anchor_y='center')
        self.steering_label = pyglet.text.Label('Steering: 50',
                                                font_name='NewMedia',
                                                font_size= 36,
                                                anchor_x='left', anchor_y='center')

        self.busy_label = pyglet.text.Label('Busy ',
                                            font_name='NewMedia',
                                            font_size= 36,
                                            anchor_x='left', anchor_y='center')

        self.batt48_label = pyglet.text.Label('Batt 1: 51v',
                                              font_name='NewMedia',
                                              font_size= 36,
                                              anchor_x='left', anchor_y='center')
        self.batt24_label = pyglet.text.Label('Batt 2: 25v',
                                              font_name='NewMedia',
                                              font_size= 36,
                                              anchor_x='left', anchor_y='center')

        self.steering_pot_label = pyglet.text.Label('Steering',
                                              font_name='NewMedia',
                                              font_size= 36,
                                              anchor_x='left', anchor_y='center')

        self.key_input_label = pyglet.text.Label('',
                                                 font_name='PF Ronda Seven',
                                                 font_size= 36,
                                                 anchor_x='left', anchor_y='center')
        self.reset_label_position()

    def reset_label_position(self):
        _x, _y = self.get_center()
        
        self.batt48_label.x = _x*2-250
        self.batt48_label.y = 220
        self.batt24_label.x = _x*2-250
        self.batt24_label.y = 170
        self.steering_pot_label.x = _x*2-250
        self.steering_pot_label.y = 120
        self.key_input_label.x  = _x*2-70
        self.key_input_label.y  = 70

        self.throttle_label.x = _x*2-250
        self.throttle_label.y = _y*2-50
        self.steering_label.x = _x*2-250
        self.steering_label.y = _y*2-100
        self.busy_label.x = _x*2-250
        self.busy_label.y = _y*2-150

    def init_image(self, image_file):
        image = pyglet.resource.image(image_file)
        image.anchor_x = image.width //2
        image.anchor_y = image.height //2
        return image

    def init_images(self):
        self.up_image = self.init_image("images/up_clicked.jpg")
        self.right_image = self.init_image("images/right_clicked.jpg")
        self.left_image = self.init_image("images/left_clicked.jpg")
        self.down_image = self.init_image("images/down_clicked.jpg")

        self.up_tire = self.init_image("images/up_tire.jpg")
        self.right_tire = self.init_image("images/right_tire.jpg")
        self.left_tire = self.init_image("images/left_tire.jpg")
        self.down_tire = self.init_image("images/down_tire.jpg")

        self.stop_image = self.init_image('images/stop_clicked.jpg')
        self.background_image = self.init_image("images/background.jpg")

    def draw_background(self, x, y):
        self.background_image.blit(x,y)

    def get_center(self):
        x = self.geometry().width() /2
        y = self.geometry().height() /2
        return (x,y)

    def draw_working_steering(self, image_x, image_y, space, tire_info_space_x, tire_info_space_y):
        self.draw_background(image_x, image_y)
        # print '----'
        # print "*STEERING: %s" % self.steering.get_recentcommand()
        # print "WHEEL: %s" % self.wheel.get_recentcommand()

        if self.wheel.get_recentcommand() == 'brake':
            self.stop_image.blit(image_x,image_y)

        if self.steering.get_recentcommand() == 'turn_right':
            self.right_image.blit(image_x+space,image_y)
            self.right_tire.blit(image_x+tire_info_space_x,image_y+tire_info_space_y)
            # TODO: (200000-self.steering.get_current_pos())/4000 +50
            # self.set_steering(int(50+1*50)) # TODO change by turn max angle'
            return

        if self.steering.get_recentcommand() == 'turn_left':
            self.left_image.blit(image_x-space,image_y)
            self.left_tire.blit(image_x+tire_info_space_x,image_y+tire_info_space_y)
            # TODO: (self.steering.get_current_pos() - 200000)/4000
            # self.set_steering(int(50-1*50)) # TODO change by turn max angle'
            return

        # # next forward
        # self.up_image.blit(image_x,image_y+space)
        # self.up_tire.blit(image_x+tire_info_space_x,image_y+tire_info_space_y)

    def on_draw_steering(self):
        image_x, image_y = self.get_center()
        space = 132
        tire_info_space_x = 469
        tire_info_space_y = 139

        if self.steering.isworking():
            self.draw_working_steering(image_x, image_y, space, tire_info_space_x, tire_info_space_y)
            return

        self.draw_background(image_x, image_y)
        
        # print '----'
        # print "STEERING: %s" % self.steering.get_recentcommand()
        # print "WHEEL: %s" % self.wheel.get_recentcommand()

        if self.wheel.get_recentcommand() == 'forward' and self.steering.get_recentcommand() == 'neutral':
            self.up_image.blit(image_x,image_y+space)
            self.up_tire.blit(image_x+tire_info_space_x,image_y+tire_info_space_y)
            return

        if self.wheel.get_recentcommand() == 'backward':
            self.down_image.blit(image_x,image_y-space)
            self.down_tire.blit(image_x+tire_info_space_x,image_y+tire_info_space_y)

        if self.wheel.get_recentcommand() == 'stop' or self.wheel.get_recentcommand() == 'brake':
            self.stop_image.blit(image_x,image_y)

        if self.steering.get_recentcommand() == 'turn_right':
            self.right_image.blit(image_x+space,image_y)
            self.right_tire.blit(image_x+tire_info_space_x,image_y+tire_info_space_y)
            # self.set_steering(int(50+1*50)) # TODO change by turn max angle'

        if self.steering.get_recentcommand() == 'turn_left':
            self.left_image.blit(image_x-space,image_y)
            self.left_tire.blit(image_x+tire_info_space_x,image_y+tire_info_space_y)
            # self.set_steering(int(50-1*50)) # TODO change by turn max angle'

    def init_rc_mode(self):
        #self.rc_mode = True
        self.rc_mode = False
        self.rc_stright_mode = False
        self.rc_mode_is_forward = True
        self.rc_mode_is_throttle_up = True

        self.ignore_eeg_input = False # priority command for rc than eeg key

        self.brake()

    def set_rc_mode(self, mode):
        self.rc_mode = mode
        if self.rc_mode == True:
            print "Dashboard RC Mode"
        else:
            print "Dashboard Pilot Mode"

    def set_ignore_eeg_input(self, state):
        self.ignore_eeg_input = state
        if self.ignore_eeg_input == True:
            print "Dashboard Ignore EEG"
        else:
            print "Dashboard Accept EEG"

    def set_rc_stright_mode(self, mode):
        self.rc_stright_mode = mode
        if self.rc_stright_mode == True:
            print "Dashboard RC STRIGHT Mode"
        else:
            print "Dashboard RC FREE L/R Mode"

    def _map(self, value, start1, stop1, start2, stop2):
        # TODO: _map(0, 3000, 2000, 0, 100) ???
        if value <= start1:
            return float(start2)
        if value >= stop1:
            return float(stop2)
        return start2 + (stop2 - start2) * (float(value - start1) / float(stop1 - start1))

    def _is_between(self, value, n1, n2):
        return n1 <= value <= n2

    def get_steering_pot(self):
        pot = self.wheel.get_steering_pot() # range 140 160 210
        # pot range: left(1.97) - middle 1.67 - right 1.15
        # pot range: left(x) - middle x - right x
        # print "Pod: %d" % pot
        return pot

    def _filter_stright_driving(self, rudo):
        if self.rc_stright_mode:
            if rudo < 30:
                rudo = 35
                #rudo = 40
            elif rudo > 70:
                rudo = 65
                #rudo = 60
            else:
                rudo = 50
        return rudo

    def check_rudo_is_updated(self, rudo, _prev_rudo):
        return rudo <= (_prev_rudo - 2) or (_prev_rudo +2) <= rudo

    def update_rudo(self):
        global prev_rudo

        # STEERING: RUDO
        # rudo range 1897(left) - 1509(middle) - 1119(right)
        # raw rudo throshold: 1000
        _rudo = self.wheel.get_rudo_from_rc()
        #print "rudo: %d " % _rudo

        if _rudo > 1000:
            # rudo = self._map(_rudo, 1200, 1897, 95, 5)
            rudo = self._map(_rudo, 1120, 1897, 100, 0)
            if rudo <= (prev_rudo - 2) or (prev_rudo +2) <= rudo:
            # if check_rudo_is_updated(rudo, prev_rudo):
                rudo = self._filter_stright_driving(rudo)
                # if self.rc_stright_mode:
                #     if rudo < 30:
                #         rudo = 35
                #         #rudo = 40
                #     elif rudo > 70:
                #         rudo = 65
                #         #rudo = 60
                #     else:
                #         rudo = 50
                
                # TODO: if not self.steering.isworking():
                if not self.steering.isworking():                
                    self.set_steering(int(rudo))
                    self.steering.turn_by_position(int(rudo), self.get_steering_pot())
                    prev_rudo = rudo
                # TODO: drawing turn left and right arrow

    def update_elev(self):
        # DIRECTION and Accept EEG Input: ELEV
        # elev range 1119(down) - 1504(normal) - 1897(up)
        _elev = self.wheel.get_elev_from_rc()
        #print "elev: %d" % _elev
        if _elev > 1000:
            if _elev < 1300:
                self.rc_mode_is_forward = False
                #print "RC Mode: BACKWARD"
            else:
                self.rc_mode_is_forward = True
                #print "RC Mode: FORWARD"

                # Accept EEG Input
                if _elev > 1800:
                    self.set_ignore_eeg_input(False)

    def update_throttle(self):
        global prev_throttle
        # THROTTLE: THROTTLE
        # TODO: check throttle response time
        # throttle range 1100 - 1930
        # throttle throshold: 1000
        _throttle = self.wheel.get_throttle_from_rc()
        print "throttle: %d " % _throttle
        if _throttle > 1000:
            throttle = self._map(_throttle, 1124, 1892, 0, 100)

            if throttle < 5: # less then 20%, stop!
                if self.rc_mode_is_throttle_up == True:
                    #self.stop()
                    self.brake()
                    prev_throttle = throttle
                    self.rc_mode_is_throttle_up = False
                return

            self.set_throttle(throttle)

            if self.rc_mode_is_forward:
                if self.rc_mode_is_throttle_up == False:
                    self.just_forward()
                    self.rc_mode_is_throttle_up = True
                    # print "RC Mode: COMMAND FORWARD"
                prev_throttle = throttle
                # TODO: ignore eeg key input if detect rc forward or backward
                self.set_ignore_eeg_input(True)
                return
            else:
                if self.rc_mode_is_throttle_up == False:
                    self.backward()
                    self.rc_mode_is_throttle_up = True
                    # print "RC Mode: COMMAND BACKWARD"
                self.set_ignore_eeg_input(True)
                return
        else: # if _throttle is 0, rc is not connected
            prev_throttle = 0
            self.rc_mode_is_throttle_up = False
            # self.stop()
            # self.brake()

    def update(self):
        # global prev_rudo, prev_throttle
        self.wheel.update_data()

        if self.rc_mode == True:
            self.update_rudo() # It's importance that update sequence (rudo, elev, throttle)
            self.update_elev()
            self.update_throttle()
            # return

        # pot = self.get_steering_pot()
        # RC Control
        # self.update_rudo()
        # self.update_elev()
        # self.update_throttle()

    def on_draw(self):
        self.update()
        pyglet.gl.glClearColor(0,0,0,0)
        self.on_draw_steering()
        self.on_draw_label()
        self.on_draw_spin()

    def on_draw_spin(self):
        _x, _y = self.get_center()
        self.spin.draw(30, _y*2- 30)

    def on_draw_label(self):
        _x, _y = self.get_center()

        self.throttle_label.draw()
        self.steering_label.draw()

        if self.steering.isworking():
            self.busy_label.color = (255,0,0,255) # RED
        else:
            self.busy_label.color = (255,255,255,255)

        self.busy_label.draw()

        self.batt48_label.text = "Batt 1: " +str(self.wheel.get_batt48()/10.0) + 'v'
        self.batt48_label.draw()

        self.batt24_label.text = "Batt 2: " +str(self.wheel.get_batt24()/10.0) + 'v'
        self.batt24_label.draw()

        self.steering_pot_label.text = "Steering: " +str(self.wheel.get_steering_pot()/100.0) + 'v'
        self.steering_pot_label.draw()

        #self.window.update_battery_status(48,24)

        self.key_input_label.draw()

    def set_throttle(self, throttle):
        self.throttle_label.text = "Throttle: " +str(throttle)

    def set_steering(self, steering):
        self.steering_label.text = "Steering: " +str(steering)

    def set_key_input(self, key):
        self.key_input_label.text = key

    def set_max_throttle(self, throttle):
        self.max_throttle = throttle

    def set_backward_max_throttle(self, throttle):
        self.backward_max_throttle = throttle

    def just_forward(self):
        self.init_images()
        self.wheel.forward(self.max_throttle)
        self.set_throttle(self.max_throttle)

    def forward(self, throttle=None):
        self.init_images()

        if throttle == None:
            throttle = self.max_throttle
            self.wheel.forward(throttle)
            self.set_throttle(throttle)
            self.steering.neutral()

    def draw_backward(self):
        self.init_images()
        self.down_image = self.init_image("images/down_clicked.jpg")

    def backward(self):
        # self.draw_backward()
        self.wheel.backward(self.backward_max_throttle) # 45 is throttle power
        #self.steering.neutral()

    def draw_turn_right(self):
        self.init_images()
        self.right_image = self.init_image("images/right_clicked.jpg")
        
    def turn_right(self):
        # self.draw_turn_right()
        if self.steering.get_recentcommand() == 'turn_right': return
        self.wheel.turn_right(self.max_throttle)
        self.set_throttle(self.max_throttle)
        self.steering.turn_right(1)
        # self.set_steering(int(50+1*50))

    def draw_turn_left(self):
        # self.init_images()
        self.left_image = self.init_image("images/left_clicked.jpg")

    def turn_left(self):
        # self.draw_turn_left()
        if self.steering.get_recentcommand() == 'turn_left': return
        self.wheel.turn_left(self.max_throttle) # self.max_throttle is throttle power
        self.set_throttle(self.max_throttle)
        self.steering.turn_left(1)
        # self.set_steering(int(50-1*50))

    def draw_stop(self):
        self.init_images()
        self.stop_image = self.init_image('images/stop_clicked.jpg')

    def stop(self):
        # self.draw_stop()
        self.wheel.stop()
        self.wheel.brake()        
        self.set_throttle(0)

    def draw_brake(self):
        self.init_images()

    def brake(self):
        self.draw_brake()
        self.wheel.brake()
        print "Brake"

    def connect(self):
        #        self.steering.connect()
        #        self.wheel.connect()
        print "dashboard connected"

    def disconnect(self):
        self.steering.disconnect()
        self.wheel.disconnect()
        print "dashboard disconnected"

    def close(self):
        self.disconnect()
