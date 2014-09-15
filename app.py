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
        self.steering = SteeringPilot(steering_port_name, 5000) # default 5000
        self.wheel = WheelPilot(wheel_port_name)
        self.set_max_throttle(40)
        self.set_backward_max_throttle(40)

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

    def on_draw_steering(self):
        image_x, image_y = self.get_center()
        space = 132
        tire_info_space_x = 469
        tire_info_space_y = 139
        self.draw_background(image_x, image_y)        
        if self.wheel.get_recentcommand() == 'forward':
            self.up_image.blit(image_x,image_y+space)
            self.up_tire.blit(image_x+tire_info_space_x,image_y+tire_info_space_y)
            return
        if self.wheel.get_recentcommand() == 'backward':
            self.down_image.blit(image_x,image_y-space)
            self.down_tire.blit(image_x+tire_info_space_x,image_y+tire_info_space_y)
            return
        if self.wheel.get_recentcommand() == 'turn_right':
            self.right_image.blit(image_x+space,image_y)
            self.right_tire.blit(image_x+tire_info_space_x,image_y+tire_info_space_y)
            return
        if self.wheel.get_recentcommand() == 'turn_left':
            self.left_image.blit(image_x-space,image_y)
            self.left_tire.blit(image_x+tire_info_space_x,image_y+tire_info_space_y)
            return
        if self.wheel.get_recentcommand() == 'stop' or self.wheel.get_recentcommand() == 'brake':
            self.stop_image.blit(image_x,image_y)
            return

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

    def update(self):
        global prev_rudo, prev_throttle
        self.wheel.update_data()
        pot = self.wheel.get_steering_pot() # range 140 160 210
        # pot range: left(1.97) - middle 1.67 - right 1.15
        # pot range: left(x) - middle x - right x
        # print "Pod: %d" % pot
        if self.rc_mode == False:
            return

        # STEERING: RUDO
        # rudo range 1897(left) - 1509(middle) - 1119(right)
        # raw rudo throshold: 1000
        _rudo = self.wheel.get_rudo_from_rc()
        #print "rudo: %d " % _rudo

        if _rudo > 1000:
            rudo = self._map(_rudo, 1200, 1897, 95, 5)
            if rudo <= (prev_rudo - 2) or (prev_rudo +2) <= rudo:
                if self.rc_stright_mode:
                    if rudo < 30:
                        rudo = 35
                        #rudo = 40
                    elif rudo > 70:
                        rudo = 65
                        #rudo = 60
                    else:
                        rudo = 50
                # TODO: ignore eeg key input
                # self.set_ignore_eeg_input(True)
                self.set_steering(int(rudo))
                self.steering.turn_by_position(int(rudo), pot)
                prev_rudo = rudo

        # DIRECTION: ELEV
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

        # THROTTLE: THROTTLE
        # TODO: check throttle response time
        # throttle range 1100 - 1930
        # throttle throshold: 1000
        _throttle = self.wheel.get_throttle_from_rc()
        #print "throttle: %d " % _throttle
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
            self.busy_label.color = (255,0,0,255)
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

    def forward(self, throttle=None):
        self.init_images()

        if throttle == None:
            throttle = self.max_throttle
            self.wheel.forward(throttle)
            self.set_throttle(throttle)
            self.steering.neutral()

    def backward(self):
        self.init_images()
        self.down_image = self.init_image("images/down_clicked.jpg")
        # self.wheel.backward()
        self.wheel.backward(self.backward_max_throttle) # 45 is throttle power
        #self.steering.neutral()

    def turn_right(self):
        self.init_images()
        self.right_image = self.init_image("images/right_clicked.jpg")
        if self.steering.get_recentcommand() == 'turn_right': return
        self.wheel.turn_right(self.max_throttle)
        self.set_throttle(self.max_throttle)
        self.steering.turn_right(1)

    def turn_left(self):
        self.init_images()
        self.left_image = self.init_image("images/left_clicked.jpg")
        if self.steering.get_recentcommand() == 'turn_left': return
        self.wheel.turn_left(self.max_throttle) # self.max_throttle is throttle power
        self.set_throttle(self.max_throttle)
        self.steering.turn_left(1)

    def stop(self):
        self.init_images()
        self.stop_image = self.init_image('images/stop_clicked.jpg')
        self.wheel.stop()
        self.wheel.brake()        
        self.set_throttle(0)

    def brake(self):
        self.init_images()
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

class EegCarDashboardWindow(QWidget):

    def setThrottleValue(self, x):
        self.dashboard.set_throttle(x)
        self.dashboard.wheel.forward(x)

    def setSteeringValue(self, x):
        self.dashboard.set_steering(x)
        self.dashboard.steering.turn_by_position(x)

    def setMessage(self, msg):
        print msg

    def connectMotor(self):
        self.setMessage('connected')
        self.dashboard.connect()


    def remote_control(self, state):
        if state == QtCore.Qt.Checked:
            self.dashboard.set_rc_mode(True)
            # print 'SET_RC_MODE'
        else:
            self.dashboard.set_rc_mode(False)
            # print 'CLEAR_RC_MODE'

    def keep_mode_control(self, state):
        if state == QtCore.Qt.Checked:
            self.keep_mode = True
        else:
            self.keep_mode = False

    def ignore_eeg_input_control(self, state):
        if state == QtCore.Qt.Checked:
            self.dashboard.set_ignore_eeg_input(True)
        else:
            self.dashboard.set_ignore_eeg_input(False)

    def stright_control(self, state):
        if state == QtCore.Qt.Checked:
            self.dashboard.set_rc_stright_mode(True)
            # print 'SET_RC_STRIGHT_MODE'
        else:
            self.dashboard.set_rc_stright_mode(False)
            # print 'CLEAR_RC_STRIGHT_MODE'

    def update_battery_status(self, _batt48, _batt24):
        self.batt48(str(_batt48))
        self.batt24(str(_batt24))

    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Pilot Dashboard")
        self.setGeometry(0, 0, 750, 800)
        # self.setGeometry(300, 300, 750, 800)
        # self.connectButton = QPushButton('Connect', self)
        self.dashboard = EegCarDashboard()

        self.layout = QVBoxLayout(self)
        # self.layout.addWidget(self.connectButton)

        # Drive Setting
        self.rc_mode = QCheckBox('Remote control', self)
        self.rc_mode.stateChanged.connect(self.remote_control)

        self.rc_stright_mode = QCheckBox('RC Stright', self)
        self.rc_stright_mode.stateChanged.connect(self.stright_control)

        self.keep_mode = QCheckBox('Keep Mode', self)
        self.keep_mode.stateChanged.connect(self.keep_mode_control)

        self.ignore_eeg_input = QCheckBox('Ignore Eeg input', self)
        self.ignore_eeg_input.stateChanged.connect(self.ignore_eeg_input_control)

        #self.rc_mode.toggle() # Default RC Mode
        self.batt48 = QLabel('Batt1 (v): ', self)
        self.batt24 = QLabel('Batt2 (v): ', self)
        drive_layout = QHBoxLayout(self)
        drive_layout.addWidget(self.batt48)
        drive_layout.addWidget(self.batt24)
        drive_layout.addWidget(self.rc_mode)
        drive_layout.addWidget(self.rc_stright_mode)
        drive_layout.addWidget(self.keep_mode)
        drive_layout.addWidget(self.ignore_eeg_input)

        drive_groupbox = QtGui.QGroupBox("Drive Status & Setting")
        drive_groupbox.setLayout(drive_layout)

        # Throttle Setting
        self.throttle_slider = QSlider(Qt.Horizontal)
        self.throttle_slider.setFocusPolicy(Qt.StrongFocus)
        self.throttle_slider.setTickPosition(QSlider.TicksBothSides)
        self.throttle_slider.setTickInterval(20)
        self.throttle_slider.setSingleStep(10)

        self.throttle_slider.valueChanged.connect(self.throttle_slider.setValue)
        self.connect(self.throttle_slider, SIGNAL("valueChanged(int)"), self.setThrottleValue)
        self.throttle_label = QLabel('Manual Throttle (%): ', self)
        self.steering_label = QLabel('Manual Steering (%): ', self)

        self.maxThrottle = QLineEdit('40') # 40 is default
        # self.maxThrottle.textChanged[str].connect(self.setMaxThrottle)
        self.maxThrottle.editingFinished.connect(self.setMaxThrottle)
        self.maxThrottle.setMaxLength(2)
        self.maxThrottle.setMaximumWidth(40)

        self.backwardMaxThrottle = QLineEdit('40') # 40 is default
        # self.maxThrottle.textChanged[str].connect(self.setMaxThrottle)
        self.backwardMaxThrottle.editingFinished.connect(self.setBackwardMaxThrottle)
        self.backwardMaxThrottle.setMaxLength(2)
        self.backwardMaxThrottle.setMaximumWidth(40)

        throttle_layout = QHBoxLayout(self)
        throttle_layout.addWidget(self.throttle_label)
        throttle_layout.addWidget(self.throttle_slider)
        throttle_layout.addWidget(QLabel("Forward Max:"))
        throttle_layout.addWidget(self.maxThrottle)

        throttle_layout.addWidget(QLabel("Backward Max:"))
        throttle_layout.addWidget(self.backwardMaxThrottle)

        throttle_groupbox = QtGui.QGroupBox("Throttle Range")
        throttle_groupbox.setLayout(throttle_layout)

        # Steering
        self.steering_slider = QSlider(Qt.Horizontal)
        self.steering_slider.setFocusPolicy(Qt.StrongFocus)
        self.steering_slider.setTickPosition(QSlider.TicksBothSides)
        self.steering_slider.setTickInterval(5)
        self.steering_slider.setSingleStep(5)
        self.steering_slider.setValue(50)
        self.steering_slider.valueChanged.connect(self.steering_slider.setValue)
        self.connect(self.steering_slider, SIGNAL("valueChanged(int)"), self.setSteeringValue)

        steering_layout = QHBoxLayout(self)
        steering_layout.addWidget(self.steering_label)
        steering_layout.addWidget(self.steering_slider)
        steering_groupbox = QtGui.QGroupBox("Steering Angle")
        steering_groupbox.setLayout(steering_layout)

        self.layout.addWidget(self.dashboard, 2)
        self.layout.addWidget(drive_groupbox)
        self.layout.addWidget(throttle_groupbox)
        self.layout.addWidget(steering_groupbox)
        # self.layout.addWidget(self.connectButton)

        self.setIcon()
        self.setButton()
        self.show()

        # save the state
        self.default_backgroundcolor = self.palette().color(QtGui.QPalette.Background)
        self.previos_steering = 50
        self.init_keep_mode()

    def getMaxThrottle(self):
        return int(self.maxThrottle.text())

    def getBackwardMaxThrottle(self):
        return int(self.backwardMaxThrottle.text())

    def setMaxThrottle(self):
        throttle = self.getMaxThrottle()
        if self.maxThrottle.isModified():
            if throttle >=10:
                self.dashboard.set_max_throttle(throttle)
                print throttle
                self.maxThrottle.clearFocus()
        self.maxThrottle.setModified(False)

    def setBackwardMaxThrottle(self):
        throttle = self.getBackwardMaxThrottle()
        if self.backwardMaxThrottle.isModified():
            if throttle >=10:
                self.dashboard.set_backward_max_throttle(throttle)
                self.backwardMaxThrottle.clearFocus()
        self.backwardMaxThrottle.setModified(False)

    def setIcon(self):
        self.appIcon = QIcon('logo.png')
        self.setWindowIcon(self.appIcon)

    def setButton(self):
        return 
        # self.connectButton.move(50,100)
        # self.connectButton.clicked.connect(self.connectMotor)

    def init_keep_mode(self):
        self.w_keep_countdown = 0
        self.x_keep_countdown = 0
        self.default_keep_countdown = 55
        self.keep_mode = False

    def is_keep_mode(self, ignore_key):
        # if key is 'w' -> w_keep_countdown
        # if key is 'x' -> x_keep_countdown
        # ignore several 's' key while chountdown number to zero
        if self.keep_mode:
            if ignore_key == Qt.Key_S: 
                if self.w_keep_countdown > 0:
                    self.w_keep_countdown = self.w_keep_countdown - 1
                    print "w keep countdown %d" % self.w_keep_countdown
                    return True
                if self.x_keep_countdown > 0:
                    self.x_keep_countdown = self.x_keep_countdown - 1
                    print "x keep countdown %d" % self.x_keep_countdown
                    return True
        return False

    def go_to_keep_mode(self, key):
        if key == Qt.Key_W:
            self.w_keep_countdown = self.default_keep_countdown

        if key == Qt.Key_X:
            self.x_keep_countdown = self.default_keep_countdown
                
    def keyPressEvent(self, event):

        if self.dashboard.rc_mode == True and self.dashboard.ignore_eeg_input ==True:
            self.ignore_eeg_input.setChecked(True)
            if event.key():
                self.dashboard.set_key_input('Ignore')
            return
        
        if self.is_keep_mode(event.key()):
            return

        if event.key() == Qt.Key_K:
            self.throttle_slider.setValue(self.throttle_slider.value() + 5)

        if event.key() == Qt.Key_J:
            self.throttle_slider.setValue(self.throttle_slider.value() - 5)

        if event.key() == Qt.Key_H:
            self.steering_slider.setValue(self.steering_slider.value() - 5)

        if event.key() == Qt.Key_L:
            self.steering_slider.setValue(self.steering_slider.value() + 5)

        if event.key() == Qt.Key_S:
            self.dashboard.set_key_input('s')
            self.dashboard.stop()

        if event.key() == Qt.Key_W:
            self.dashboard.set_key_input('w')
            self.dashboard.forward()

        if event.key() == Qt.Key_A:
            self.dashboard.set_key_input('a')
            self.dashboard.turn_left()

        if event.key() == Qt.Key_X:
            self.dashboard.set_key_input('x')
            self.dashboard.backward()

        if event.key() == Qt.Key_D:
            self.dashboard.set_key_input('d')
            self.dashboard.turn_right()

        if event.key() == Qt.Key_B:
            self.dashboard.set_key_input('b')
            self.dashboard.brake()

        if event.key() == Qt.Key_R:
            self.dashboard.set_key_input('r')
            # TODO: Make Inspection Mode
            # self.dashboard.steering.position_clear()
            #pot = self.dashboard.wheel.get_steering_pot()
            #self.dashboard.steering.middle_position(pot)

        if event.key() == Qt.Key_F:
            if self.dashboard.isFullScreen():
                for i in range(self.layout.count()):
                    w = self.layout.itemAt(i).widget()
                    w.show()
                self.dashboard.showNormal()
                self.change_backgroundcolor(self.default_backgroundcolor);
                self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowTitleHint)
                self.showNormal()
            else:
                for i in range(self.layout.count()):
                    w = self.layout.itemAt(i).widget()
                    if w == self.dashboard:
                        continue
                    w.hide()
                self.change_backgroundcolor(Qt.black);
                self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)
                self.showMaximized()
                self.dashboard.showFullScreen()

            self.dashboard.reset_label_position()

        if event.key() == Qt.Key_Escape:
            self.dashboard.close()
            self.close()

        self.go_to_keep_mode(event.key())

    def change_backgroundcolor(self, color):
        p = self.palette()
        p.setColor(self.backgroundRole(), color)
        self.setPalette(p)

def main():
    EegCarApp = QApplication(sys.argv)
    window = EegCarDashboardWindow()
    window.show()
    EegCarApp.exec_()

if __name__ == '__main__':
    main()

