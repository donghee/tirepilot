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

# menu background
d = 0
speed = 4
prev_rudo = 0

class EegCarDashboard(QPygletWidget):

    def on_init(self):
        self.init_spin();
        self.init_labels()
        self.init_images()
        self.init_pilotdriver()
        self.setMinimumSize(QSize(250, 250))

    def init_pilotdriver(self):
        if sys.platform == 'win32':
            steering_port_name = "COM4"
            wheel_port_name = "COM3"
        elif sys.platform == 'darwin':
            steering_port_name = "/dev/tty.usbserial-A901NMD9"
            wheel_port_name = "/dev/tty.usbmodem1412"

            steering_port_name = "/dev/ttys004" # mock
            # wheel_port_name = "/dev/ttys007" # mock
        self.steering = SteeringPilot(steering_port_name, 7000) # default 5000
        self.wheel = WheelPilot(wheel_port_name)
        self.set_max_throttle(35)

    def init_spin(self):
        self.spin = Spin()
        #self.spinshape = SpinShape()

    def init_labels(self):
        _x, _y = self.get_center()
        import os

        pyglet.font.add_file(
            os.path.join(
            os.path.dirname(__file__),
            'resources/NewMedia.ttf')
        )
        newmedia_font = pyglet.font.load('NewMedia')
        pyglet.font.add_file(
            os.path.join(
            os.path.dirname(__file__),
            'resources/pf_ronda_seven.ttf')
        )
        ronda_seven_font = pyglet.font.load('PF Ronda Seven')
        self.throttle_label = pyglet.text.Label('Throttle: 0',
                                  font_name='NewMedia',
                                  #font_name='PF Ronda Seven',
                                  font_size= 36,
                                  anchor_x='left', anchor_y='center')
        self.steering_label = pyglet.text.Label('Steering: 50',
                                  font_name='NewMedia',
                                  #font_name='PF Ronda Seven',
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

        self.key_input_label = pyglet.text.Label('',
                                  font_name='PF Ronda Seven',
                                  font_size= 36,
                                  anchor_x='left', anchor_y='center')

    def init_image(self, image_file):
        image = pyglet.resource.image(image_file)
        image.anchor_x = image.width //2
        image.anchor_y = image.height //2
        return image

    def init_images(self):
#        self.up_image = self.init_image("images/up.jpg")
#        self.down_image = self.init_image("images/down.jpg")
#        self.right_image = self.init_image("images/right.jpg")
#        self.left_image = self.init_image("images/left.jpg")
#        self.stop_image = self.init_image("images/stop.jpg")
        self.up_image = self.init_image("images/stop.jpg")
        self.down_image = self.init_image("images/stop.jpg")
        self.right_image = self.init_image("images/stop.jpg")
        self.left_image = self.init_image("images/stop.jpg")
        self.stop_image = self.init_image("images/stop.jpg")

    def get_center(self):
        x = self.geometry().width() /2
        y = self.geometry().height() /2
        return (x,y)

    def on_draw_steering(self):
        image_x, image_y = self.get_center()
#
#        self.up_image.blit(image_x, image_y+140)
#        self.down_image.blit(image_x, image_y-150)
#        self.right_image.blit(image_x+150, image_y)
#        self.left_image.blit(image_x-150, image_y)
#        self.stop_image.blit(image_x, image_y)
        if self.wheel.get_recentcommand() == 'forward':
            self.up_image.blit(image_x,image_y)
            return
        if self.wheel.get_recentcommand() == 'backward':
            self.down_image.blit(image_x,image_y)
            return
        if self.wheel.get_recentcommand() == 'turn_right':
            self.right_image.blit(image_x,image_y)
            return
        if self.wheel.get_recentcommand() == 'turn_left':
            self.left_image.blit(image_x,image_y)
            return
        if self.wheel.get_recentcommand() == 'stop' or self.wheel.get_recentcommand() == 'brake':
            self.stop_image.blit(image_x,image_y)
            return

    def update(self):
        global prev_rudo
        self.wheel.update_data()
        return
        _rudo = self.wheel.get_rudo_from_rc()
        if _rudo > 0:
            rudo = (_rudo - 1515) / 10
            if prev_rudo != rudo:
                self.set_steering(rudo+50)
                self.steering.turn_by_position(rudo+50)
                prev_rudo = rudo

        # throttle
        _throttle = self.wheel.get_throttle_from_rc()
        if _throttle > 0:
            throttle =  (_throttle -1100)/10
            if throttle < 5:
                return
            # if throttle > 1200:
            self.set_throttle(throttle)
            # throttle range 1100 - 1930
            self.forward(throttle)

    def on_draw(self):
        self.update()
        pyglet.gl.glClearColor(0,0,0,0)
        # self.spinshape.draw()
        self.on_draw_steering()
        self.on_draw_label()
        self.on_draw_spin()

    def on_draw_spin(self):
        _x, _y = self.get_center()
        self.spin.draw(30, _y*2- 30)

        # for i, s in enumerate(self.spins):
        #     s.draw(30*i%_x*2, int(60*(i%10)))

    def on_draw_label(self):
        _x, _y = self.get_center()

        # label background
        width = _x*2
        height = _y*2

        verts = (
            width * 0.99, height * 0.99,
            width * 0.99, height * 0.02,
            width * 0.64, height * 0.02,
            width * 0.64, height * 0.99,
        )

        from random import randrange

        global d, speed

        d = d+speed

        if d >= 255:
            d = 255
            speed = -4
        if d <= 0:
            d = 0
            speed = 4

        colors = [
            d,0,0,0,
            0,d,0,0,
            0,0,0,200,
            0,0,0,200
            ]

#        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
#            ('v2f', verts),
#            ('c4B', colors)
#        )

        self.throttle_label.x = _x*2-250
        self.throttle_label.y = _y*2-50
        self.throttle_label.draw()

        self.steering_label.x = _x*2-250
        self.steering_label.y = _y*2-100
        self.steering_label.draw()

        self.busy_label.x = _x*2-250
        self.busy_label.y = _y*2-150
        self.busy_label.draw()

        if self.steering.isworking():
            self.busy_label.color = (255,0,0,255)
        else:
            self.busy_label.color = (255,255,255,255)

        self.busy_label.x = _x*2-250
        self.busy_label.y = _y*2-150
        self.busy_label.draw()


        self.batt48_label.x = _x*2-250
        self.batt48_label.y = 180
        self.batt48_label.text = "Batt 1: " +str(self.wheel.get_batt48()/10.0) + 'v'
        self.batt48_label.draw()

        self.batt24_label.x = _x*2-250
        self.batt24_label.y = 130
        self.batt24_label.text = "Batt 2: " +str(self.wheel.get_batt24()/10.0) + 'v'
        self.batt24_label.draw()

        #self.window.update_battery_status(48,24)

        self.key_input_label.x  = _x*2-70
        self.key_input_label.y  = 70
        self.key_input_label.draw()

    def set_throttle(self, throttle):
        self.throttle_label.text = "Throttle: " +str(throttle)

    def set_steering(self, steering):
        self.steering_label.text = "Steering: " +str(steering)

    def set_key_input(self, key):
        self.key_input_label.text = key

    def set_max_throttle(self, throttle):
        self.max_throttle = throttle

    def forward(self, throttle=None):
        self.init_images()
        self.up_image = self.init_image("images/up_clicked.jpg")
        # self.wheel.forward(self.max_throttle)
        # self.set_throttle(self.max_throttle)
        if throttle == None:
          throttle = self.max_throttle
        self.wheel.forward(throttle)
        self.set_throttle(throttle)
        self.steering.neutral()

    def backward(self):
        self.init_images()
        self.down_image = self.init_image("images/down_clicked.jpg")
        # self.wheel.backward()
        self.wheel.backward(60) # 60 is throttle power
        #self.steering.neutral()

    def turn_right(self):
        self.init_images()
        self.right_image = self.init_image("images/right_clicked.jpg")
        if self.steering.get_recentcommand() == 'turn_right': return
        self.wheel.turn_right(self.max_throttle) # 35 is throttle power
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

    def getMaxThrottle(self):
        return int(self.maxThrottle.text())

    def remote_control(self, state):

        if state == QtCore.Qt.Checked:
            print 'SET_RC_MODE'
        else:
            print 'CLEAR_RC_MODE'

    def update_battery_status(self, _batt48, _batt24):
        self.batt48(str(_batt48))
        self.batt24(str(_batt24))
        #self.batt48.
        #self.batt24.

    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Pilot Dashboard")
        self.setGeometry(300, 300, 750, 800)
        self.connectButton = QPushButton('Connect', self)
        self.dashboard = EegCarDashboard()

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.connectButton)

        # Drive Setting
        self.rc_mode = QCheckBox('R&emote control', self)
        self.rc_mode.stateChanged.connect(self.remote_control)
        self.batt48 = QLabel('Batt1 (v): ', self)
        self.batt24 = QLabel('Batt2 (v): ', self)
        drive_layout = QHBoxLayout(self)
        drive_layout.addWidget(self.batt48)
        drive_layout.addWidget(self.batt24)
        drive_layout.addWidget(self.rc_mode)
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

        self.maxThrottle = QLineEdit('35') # 35 is default
        self.maxThrottle.setMaxLength(2)
        self.maxThrottle.setMaximumWidth(40)

        throttle_layout = QHBoxLayout(self)
        throttle_layout.addWidget(self.throttle_label)
        throttle_layout.addWidget(self.throttle_slider)
        throttle_layout.addWidget(QLabel("Max:"))
        throttle_layout.addWidget(self.maxThrottle)

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
        self.layout.addWidget(self.connectButton)

        self.setIcon()
        self.setButton()
        self.show()

        self.default_backgroundcolor = self.palette().color(QtGui.QPalette.Background)
        self.previos_steering = 50

    def setIcon(self):
        self.appIcon = QIcon('logo.png')
        self.setWindowIcon(self.appIcon)

    def setButton(self):
        self.connectButton.move(50,100)
        self.connectButton.clicked.connect(self.connectMotor)

    def keyPressEvent(self, event):
        self.dashboard.set_max_throttle(self.getMaxThrottle())

        if event.key() == Qt.Key_K:
            self.throttle_slider.setValue(self.throttle_slider.value() + 5)
        if event.key() == Qt.Key_J:
            self.throttle_slider.setValue(self.throttle_slider.value() - 5)
        if event.key() == Qt.Key_H:
            self.steering_slider.setValue(self.steering_slider.value() - 5)
        if event.key() == Qt.Key_L:
            self.steering_slider.setValue(self.steering_slider.value() + 5)

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

        if event.key() == Qt.Key_S:
            self.dashboard.set_key_input('s')
            self.dashboard.stop()

        if event.key() == Qt.Key_B:
            self.dashboard.set_key_input('b')
            self.dashboard.brake()

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

        if event.key() == Qt.Key_Escape:
            self.dashboard.close()
            self.close()

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
