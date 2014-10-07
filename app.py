# coding: utf-8

from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtCore, QtGui, QtOpenGL
from dashboard import *

DEFAULT_MAX_THROTTLE = 40

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

    def steering_update_current_pos(self, delta_x):
        x = int(self.steering_current_pos.text()) + delta_x
        # while check busy
        ## read position
        ## print 'current pos %d' % x
        self.steering_current_pos.setText(str(x))

    def steering_move_left(self):
        ticks = int(self.steering_move_ticks.text())
        x = -1 * ticks
        # MOVE!
        print 'Steering left'
        self.steering_update_current_pos(x)

    def steering_move_right(self):
        ticks = int(self.steering_move_ticks.text())
        x = 1 * ticks
        # MOVE!
        print 'Steering right'
        self.steering_update_current_pos(x)

    def steering_reset_position(self):
        x = 0
        # RESET
        print 'Steering reset'
        self.steering_update_current_pos(x)

    # def setMessage(self, msg):
    #     print msg

    # def connectMotor(self):
    #     self.setMessage('connected')
    #     self.dashboard.connect()

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
            print 'Keep Mode (EEG)'
        else:
            self.keep_mode = False
            print 'Keyboard Mode'

    def ignore_eeg_input_control(self, state):
        if state == QtCore.Qt.Checked:
            self.dashboard.set_ignore_eeg_input(True)
        else:
            self.dashboard.set_ignore_eeg_input(False)

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

    # def update_battery_status(self, _batt48, _batt24):
    #     self.batt48(str(_batt48))
    #     self.batt24(str(_batt24))

    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Pilot Dashboard")
        self.setGeometry(0, 0, 750, 800)
        # self.setGeometry(300, 300, 750, 800)
        # self.connectButton = QPushButton('Connect', self)
        self.dashboard = EegCarDashboard()
        self.dashboard.set_max_throttle(DEFAULT_MAX_THROTTLE)
        self.dashboard.set_backward_max_throttle(DEFAULT_MAX_THROTTLE)

        self.layout = QVBoxLayout(self)

        # Drive Setting
        self.rc_mode = QCheckBox('Remote Control', self)
        self.rc_mode.stateChanged.connect(self.remote_control)

        self.rc_stright_mode = QCheckBox('RC Stright', self)
        self.rc_stright_mode.stateChanged.connect(self.stright_control)

        self.keep_mode = QCheckBox('Keep Mode', self)
        self.keep_mode.stateChanged.connect(self.keep_mode_control)

        self.ignore_eeg_input = QCheckBox('Ignore Eeg Input', self)
        self.ignore_eeg_input.stateChanged.connect(self.ignore_eeg_input_control)

        #self.rc_mode.toggle() # Default RC Mode
        # self.batt48 = QLabel('Batt1 (v): ', self)
        # self.batt24 = QLabel('Batt2 (v): ', self)
        drive_layout = QHBoxLayout(self)
        # drive_layout.addWidget(self.batt48)
        # drive_layout.addWidget(self.batt24)
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

        self.backwardMaxThrottle = QLineEdit(str(DEFAULT_MAX_THROTTLE))
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
        self.steering_label = QLabel('Steering ', self)
        self.steering_slider = QSlider(Qt.Horizontal)
        self.steering_slider.setFocusPolicy(Qt.StrongFocus)
        self.steering_slider.setTickPosition(QSlider.TicksBothSides)
        self.steering_slider.setRange(1, 9)
        # self.steering_slider.setMinimum(2)
        # self.steering_slider.setMaximum(8)
        self.steering_slider.setMinimum(4)
        self.steering_slider.setMaximum(6)
        self.steering_slider.setTickInterval(1)
        self.steering_slider.setSingleStep(1)
        self.steering_slider.setValue(5)
        self.steering_slider.valueChanged.connect(self.steering_slider.setValue)
        self.connect(self.steering_slider, SIGNAL("valueChanged(int)"), self.setSteeringValue)

        self.steering_adjust_label = QLabel(' Home Adjust ', self)
        self.steering_move_left_button = QPushButton('<Left', self)
        self.steering_current_pos = QLabel('0', self)
        self.steering_move_right_button = QPushButton('Right>', self)

        self.steering_move_ticks = QLineEdit(str(2000))
        self.steering_move_ticks.editingFinished.connect(self.setBackwardMaxThrottle)
        self.steering_move_ticks.setMaxLength(5)
        self.steering_move_ticks.setMaximumWidth(50)

        self.steering_reset = QPushButton('Reset', self)

        self.steering_move_left_button.clicked.connect(self.steering_move_left)
        self.steering_move_right_button.clicked.connect(self.steering_move_right)
        self.steering_reset.clicked.connect(self.steering_reset_position)

        steering_layout = QHBoxLayout(self)
        steering_layout.addWidget(self.steering_label)
        steering_layout.addWidget(self.steering_slider)
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
        # self.layout.addWidget(self.connectButton)

        self.setIcon()
        self.show()

        # save the state
        self.default_backgroundcolor = self.palette().color(QtGui.QPalette.Background)
        self.previos_steering = 50
        self.init_keep_mode()

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
                print "Forward Max Throttle: %d" % throttle
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
        self.default_keep_countdown = 40
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
                    self.x_keep_countdown = 0
                    return True
                if self.x_keep_countdown > 0:
                    self.x_keep_countdown = self.x_keep_countdown - 1
                    print "x keep countdown %d" % self.x_keep_countdown
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

        if key == Qt.Key_A:
            self.a_keep_countdown = self.default_keep_countdown

        if key == Qt.Key_D:
            self.d_keep_countdown = self.default_keep_countdown
                
    def keyPressEvent(self, event):
        if self.dashboard.rc_mode == True :
            if self.dashboard.ignore_eeg_input ==True:
                self.ignore_eeg_input.setChecked(True)
                if event.key():
                    self.dashboard.set_key_input('Ignore')
                return
            else: 
                self.ignore_eeg_input.setChecked(False)
       
        if self.is_keep_mode(event.key()):
            return

        # if event.key() == Qt.Key_K:
        #     self.throttle_slider.setValue(self.throttle_slider.value() + 5)

        # if event.key() == Qt.Key_J:
        #     self.throttle_slider.setValue(self.throttle_slider.value() - 5)

        # if event.key() == Qt.Key_H:
        #     self.steering_slider.setValue(self.steering_slider.value() - 5)

        # if event.key() == Qt.Key_L:
        #     self.steering_slider.setValue(self.steering_slider.value() + 5)

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
