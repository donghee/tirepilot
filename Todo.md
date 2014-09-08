
 - Forcus 버리기
 - Steering Voltage
 - RC 모드
 - (v) Speed Up

 - rc 모드에서 brake 여러번 나오는거 해결하기
  1. 178번 줄에서 self.brake() 추가. 처음 시작을 brake()로 시작한다.

    def init_rc_mode(self):
        #self.rc_mode = True
        self.rc_mode = False
        self.rc_stright_mode = False
        self.rc_mode_is_forward = True
        self.rc_mode_is_throttle_up = True
        self.brake() # 추가

  2. 286번 줄에서 self.brake() 삭제

        else: # if _throttle is 0, rc is not connected
            prev_throttle = 0
            self.rc_mode_is_throttle_up = False
            #self.stop()
            # self.brake() # 삭제
