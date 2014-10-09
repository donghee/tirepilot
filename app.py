# coding: utf-8

from PySide import QtCore, QtGui
from PySide.QtGui import QWidget, QLineEdit, QLabel, QIcon, QApplication, QVBoxLayout, QCheckBox, QPushButton, QHBoxLayout, QSlider, QStatusBar
from PySide.QtCore import Qt, SIGNAL

import sys
import time
from dashboard import EegCarDashboard, DEFAULT_MAX_THROTTLE, DEFAULT_MAX_BACK_THROTTLE, DEFAULT_STEERING_SPEED

class EegCarDashboardWindow(QWidget):

    def setSliderMaxThrottle(self, x):
        self.setMaxThrottle(x)
        # self.dashboard.set_throttle(x)
        # self.dashboard.wheel.forward(x)

    def setSteeringValue(self, x):
        # x range is 1-9 need to scale (10-90)
        x = x*10
        self.dashboard.set_steering(x)
        # self.dashboard.steering.turn_by_position(x)
        pot = 1.5
        self.dashboard.steering.turn_by_position(x, pot)

    def setSteeringTurnRangeValue(self, x):
        ticks = int(100000 * (x/10.0)) # max is 100000
        # print "STEERING TURN TICKS %d" % ticks
        self.dashboard.set_steering_eeg_turn_ticks(ticks)

    def steering_update_current_pos(self):
        # x = int(self.steering_current_pos.text()) + delta_x
        # while check busy
        ## read position
        ## print 'current pos %d' % x

        ticks = int(self.steering_move_ticks.text())
        seconds = int(ticks/(DEFAULT_STEERING_SPEED*7))
        seconds = seconds + 1 # at least one second
        ending_time = time.time() + seconds
        while time.time() < ending_time:
            # print "ENDNIG: %d" % ending_time
            # print "CURRENT: %d" % time.time()
            self.steering_set_current_pos(self.dashboard.steering.get_current_location())

    def steering_set_current_pos(self, x):
        self.steering_current_pos.setText(str(x))    

    def steering_move_left(self):
        ticks = int(self.steering_move_ticks.text())
        # Stepping Motor MOVE!
        self.dashboard.steering.stepping_driver.forward(ticks)
        self.setMessage('Steering left')
        self.steering_update_current_pos()

    def steering_move_right(self):
        ticks = int(self.steering_move_ticks.text())
        # Stepping Motor MOVE!
        self.dashboard.steering.stepping_driver.backward(ticks)
        self.setMessage('Steering right')
        self.steering_update_current_pos()

    def set_steering_move_ticks_value(self):
        self.steering_move_ticks.blockSignals(True) # update line edit
        ticks = int(self.steering_move_ticks.text())
        self.steering_move_ticks.setText(str(ticks)) 
        self.steering_move_ticks.blockSignals(False)
        self.steering_move_ticks.setModified(True)

        if self.steering_move_ticks.isModified():
            self.steering_move_ticks.clearFocus()
        self.maxThrottle.setModified(False)

    def steering_reset_position(self):
        # RESET
        self.setMessage('Steering Controller Reset')
        self.dashboard.steering.stepping_driver.reset() # reset
        self.dashboard.steering.stepping_driver.set_speed(DEFAULT_STEERING_SPEED) # set speed
        self.steering_update_current_pos()

    def setMessage(self, msg):
        self.statusBar.showMessage(msg, 2000)

    def remote_control(self, state):
        if state == QtCore.Qt.Checked:
            self.dashboard.set_rc_mode(True)
            self.setMessage('SET RC MODE')
        else:
            self.dashboard.set_rc_mode(False)
            self.setMessage('CLEAR RC MODE')

    def keep_mode_control(self, state):
        if state == QtCore.Qt.Checked:
            self.keep_mode = True
            self.setMessage('Keep Mode (EEG)')
        else:
            self.keep_mode = False
            self.setMessage('Keyboard Mode')

    def power_handle_mode_control(self, state):
        if state == QtCore.Qt.Checked:
            self.dashboard.set_power_handle_mode(True)
            self.setMessage('Power Handle (Auto Steering Middle)')
        else:
            self.dashboard.set_power_handle_mode(False)
            self.setMessage('Turn Off Power Handle')

    def ignore_eeg_input_control(self, state):
        if state == QtCore.Qt.Checked:
            self.dashboard.set_ignore_eeg_input(True)
            self.setMessage('Ignore EEG Input')
        else:
            self.dashboard.set_ignore_eeg_input(False)
            self.setMessage('Access EEG Input')

    def stright_control(self, state):
        if state == QtCore.Qt.Checked:
            self.dashboard.set_rc_stright_mode(True)
            self.setMessage('RC STRIGHT Mode')
        else:
            self.dashboard.set_rc_stright_mode(False)
            self.setMessage('RC FREE L/R Mode')

    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("EEG Pilot Dashboard")
        self.setGeometry(0, 0, 750, 800)
        # self.setGeometry(300, 300, 750, 800)
        self.dashboard = EegCarDashboard()
        self.dashboard.set_max_throttle(DEFAULT_MAX_THROTTLE)
        self.dashboard.set_backward_max_throttle(DEFAULT_MAX_BACK_THROTTLE)

        self.layout = QVBoxLayout(self)

        # Drive Setting
        self.rc_mode = QCheckBox('Remote Control', self)
        self.rc_mode.stateChanged.connect(self.remote_control)

        self.rc_stright_mode = QCheckBox('RC Stright', self)
        self.rc_stright_mode.stateChanged.connect(self.stright_control)

        self.keep_mode_checkbox = QCheckBox('Keep Mode', self)
        self.keep_mode_checkbox.stateChanged.connect(self.keep_mode_control)

        self.power_handle_mode_checkbox = QCheckBox('Power Handle', self)
        self.power_handle_mode_checkbox.stateChanged.connect(self.power_handle_mode_control)

        self.ignore_eeg_input = QCheckBox('Ignore Eeg Input', self)
        self.ignore_eeg_input.stateChanged.connect(self.ignore_eeg_input_control)

        drive_layout = QHBoxLayout(self)
        drive_layout.addWidget(self.rc_mode)
        drive_layout.addWidget(self.rc_stright_mode)
        drive_layout.addWidget(self.keep_mode_checkbox)
        drive_layout.addWidget(self.power_handle_mode_checkbox)
        drive_layout.addWidget(self.ignore_eeg_input)

        drive_groupbox = QtGui.QGroupBox("Drive Status & Setting")
        drive_groupbox.setLayout(drive_layout)

        # Throttle Setting
        self.throttle_slider = QSlider(Qt.Horizontal)
        self.throttle_slider.setFocusPolicy(Qt.StrongFocus)
        self.throttle_slider.setTickPosition(QSlider.TicksBothSides)
        self.throttle_slider.setTickInterval(10)
        self.throttle_slider.setSingleStep(10)
        self.throttle_slider.setValue(DEFAULT_MAX_THROTTLE)

        self.throttle_slider.valueChanged.connect(self.throttle_slider.setValue)
        self.connect(self.throttle_slider, SIGNAL("valueChanged(int)"), self.setSliderMaxThrottle)
        self.throttle_label = QLabel('Max Throttle (%): ', self)


        self.maxThrottle = QLineEdit(str(DEFAULT_MAX_THROTTLE))
        # self.maxThrottle.textChanged[str].connect(self.setMaxThrottle)
        self.maxThrottle.editingFinished.connect(self.setMaxThrottle)
        self.maxThrottle.setMaxLength(2)
        self.maxThrottle.setMaximumWidth(40)

        self.backwardMaxThrottle = QLineEdit(str(DEFAULT_MAX_BACK_THROTTLE))
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

        throttle_groupbox = QtGui.QGroupBox("Max Throttle Setting (30-99)")
        throttle_groupbox.setLayout(throttle_layout)

        # Steering
        # self.steering_label = QLabel('Steering ', self)
        # self.steering_slider = QSlider(Qt.Horizontal)
        # self.steering_slider.setFocusPolicy(Qt.StrongFocus)
        # self.steering_slider.setTickPosition(QSlider.TicksBothSides)
        # self.steering_slider.setRange(1, 9)
        # # self.steering_slider.setMinimum(2)
        # # self.steering_slider.setMaximum(8)
        # self.steering_slider.setMinimum(4)
        # self.steering_slider.setMaximum(6)
        # self.steering_slider.setTickInterval(1)
        # self.steering_slider.setSingleStep(1)
        # self.steering_slider.setValue(5)
        # self.steering_slider.valueChanged.connect(self.steering_slider.setValue)
        # self.connect(self.steering_slider, SIGNAL("valueChanged(int)"), self.setSteeringValue)

        self.steering_label = QLabel('Turn Range', self)
        self.steering_turn_range_slider = QSlider(Qt.Horizontal)
        self.steering_turn_range_slider.setFocusPolicy(Qt.StrongFocus)
        self.steering_turn_range_slider.setTickPosition(QSlider.TicksBothSides)
        self.steering_turn_range_slider.setRange(1, 9)
        # self.steering_slider.setMinimum(2)
        # self.steering_slider.setMaximum(8)
        self.steering_turn_range_slider.setMinimum(4)
        self.steering_turn_range_slider.setMaximum(8)
        self.steering_turn_range_slider.setTickInterval(1)
        self.steering_turn_range_slider.setSingleStep(1)
        self.steering_turn_range_slider.setValue(6)
        self.steering_turn_range_slider.valueChanged.connect(self.steering_turn_range_slider.setValue)
        self.connect(self.steering_turn_range_slider, SIGNAL("valueChanged(int)"), self.setSteeringTurnRangeValue)

        self.steering_adjust_label = QLabel(' Home Adjust ', self)
        self.steering_move_left_button = QPushButton('<Left+', self)
        self.steering_current_pos = QLabel('0', self)
        self.steering_move_right_button = QPushButton('-Right>', self)


        self.steering_move_ticks = QLineEdit(str(2000))
        self.steering_move_ticks.editingFinished.connect(self.set_steering_move_ticks_value)
        self.steering_move_ticks.setMaxLength(5)
        self.steering_move_ticks.setMaximumWidth(50)

        self.steering_reset = QPushButton('Reset', self)

        self.steering_move_left_button.clicked.connect(self.steering_move_left)
        self.steering_move_right_button.clicked.connect(self.steering_move_right)
        self.steering_reset.clicked.connect(self.steering_reset_position)

        steering_layout = QHBoxLayout(self)
        steering_layout.addWidget(self.steering_label)
        # steering_layout.addWidget(self.steering_slider)
        steering_layout.addWidget(self.steering_turn_range_slider)
        steering_layout.addWidget(self.steering_adjust_label)
        steering_layout.addWidget(self.steering_move_left_button)


        steering_layout.addWidget(self.steering_current_pos)
        steering_layout.addWidget(self.steering_move_right_button)
        steering_layout.addWidget(self.steering_move_ticks)
        steering_layout.addWidget(self.steering_reset)

        steering_groupbox = QtGui.QGroupBox("Steering Setting")
        steering_groupbox.setLayout(steering_layout)

        self.layout.addWidget(self.dashboard, 2)
        self.layout.addWidget(drive_groupbox)
        self.layout.addWidget(throttle_groupbox)
        self.layout.addWidget(steering_groupbox)

        self.statusBar = QStatusBar()
        self.statusBar.showMessage('Ready', 2000)
        self.layout.addWidget(self.statusBar)

        self.setIcon()
        self.show()

        # save the state
        self.default_backgroundcolor = self.palette().color(QtGui.QPalette.Background)
        self.previos_steering = 50
        self.init_keep_mode()
        self.init_power_handle_mode()

        # Timer For reading current steering position
        # self.timer = QtCore.QTimer()
        # self.timer.timeout.connect(self.readSteeringPos)
        # # check every second
        # self.timer.start(1000)  

        # Timer For Powerhandle
        # self.power_handle_timer = QtCore.QTimer()
        # self.power_handle_timer.timeout.connect(self.update_power_handle)
        # # check every half second
        # self.power_handle_timer.start(500)

    # def update_power_handle(self):
    #     if self.power_handle_mode:
    #         self.dashboard.update_power_handle()

    def readSteeringPos(self):
        # self.setMessage(str(self.dashboard.steering.get_current_steering()))
        # TODO: is it thread safe?
        # self.steering_set_current_pos(self.dashboard.steering.get_current_location())
        return

    def getMaxThrottle(self):
        return int(self.maxThrottle.text())

    def getBackwardMaxThrottle(self):
        return int(self.backwardMaxThrottle.text())

    def setMaxThrottle(self, _throttle=None):
        if _throttle is None: # from line textbox
            throttle = self.getMaxThrottle()
            self.throttle_slider.blockSignals(True); # update slider
            self.throttle_slider.setValue(throttle);
            self.throttle_slider.blockSignals(False);
        else: # from slider 
            throttle = _throttle
            self.maxThrottle.blockSignals(True); # update line edit
            self.maxThrottle.setText(str(throttle)) 
            self.maxThrottle.blockSignals(False);
            self.maxThrottle.setModified(True)

        if self.maxThrottle.isModified():
            if throttle >= 30: # throttle threshold is 30
                self.dashboard.set_max_throttle(throttle)
                self.setMessage("Forward Max Throttle: %d" % throttle)
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

    def init_keep_mode(self):
        self.w_keep_countdown = 0
        self.x_keep_countdown = 0
        self.a_keep_countdown = 0
        self.d_keep_countdown = 0
        # self.default_keep_countdown = 40
        self.default_keep_countdown = 10
        self.keep_mode = False

    def init_power_handle_mode(self):
        self.power_handle_mode = False

    def is_keep_mode(self, ignore_key):
        # if key is 'w' -> w_keep_countdown
        # if key is 'x' -> x_keep_countdown
        # ignore several 's' key while chountdown number to zero


        if self.keep_mode:
            if ignore_key == Qt.Key_S: 
                if self.dashboard.power_handle_mode == True:
                    self.dashboard.update_power_handle()
                if self.w_keep_countdown > 0:
                    self.w_keep_countdown = self.w_keep_countdown - 1
                    # print "w keep countdown %d" % self.w_keep_countdown
                    self.setMessage("w keep countdown %d" % self.w_keep_countdown)
                    self.x_keep_countdown = 0
                    return True
                if self.x_keep_countdown > 0:
                    self.x_keep_countdown = self.x_keep_countdown - 1
                    # print "x keep countdown %d" % self.x_keep_countdown
                    self.setMessage("x keep countdown %d" % self.x_keep_countdown)
                    self.w_keep_countdown = 0
                    return True
                # if self.a_keep_countdown > 0:
                #     self.a_keep_countdown = self.a_keep_countdown - 1
                #     print "a keep countdown %d" % self.a_keep_countdown
                #     return True
                # if self.d_keep_countdown > 0:
                #     self.d_keep_countdown = self.d_keep_countdown - 1
                #     print "d keep countdown %d" % self.d_keep_countdown
                #     return True
 
        return False

    def go_to_keep_mode(self, key):
        if key == Qt.Key_W:
            self.w_keep_countdown = self.default_keep_countdown

        if key == Qt.Key_X:
            self.x_keep_countdown = self.default_keep_countdown

        # if key == Qt.Key_A:
        #     self.a_keep_countdown = self.default_keep_countdown

        # if key == Qt.Key_D:
        #     self.d_keep_countdown = self.default_keep_countdown
                
    def keyPressEvent(self, event):
        if self.dashboard.rc_mode == True :
            if self.dashboard.ignore_eeg_input ==True:
                self.ignore_eeg_input.setChecked(True)
                if event.key():
                    self.dashboard.set_key_input('Ignore')
                return
            else: 
                self.ignore_eeg_input.setChecked(False)

        # self.update_power_handle(event.key())

        if self.is_keep_mode(event.key()):
            return

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
