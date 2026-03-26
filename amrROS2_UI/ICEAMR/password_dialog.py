import os
import sys
from PySide6 import QtCore
from PySide6.QtCore import *
from PySide6.QtCore import Signal, Slot

from passwd_ui import *


from dataclasses import dataclass

# Add project_a to sys.path
DELIVERY_ROBOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'amrROS2_ws/src/delivery_robot_main_controller'))
sys.path.insert(0, DELIVERY_ROBOT_PATH)

# Now you can import normally
from delivery_robot_main_controller.api_client import *
# from multiprocessing.connection import Client


class PasswordDialog(QDialog):
    # def __init__(self, /, parent = ..., f = ..., *, sizeGripEnabled = ..., modal = ...):
    #     super().__init__(parent, f, sizeGripEnabled=sizeGripEnabled, modal=modal)
    #     self.ui = 
    passwdSignal = Signal(str) 
    
    
    def __init__(self, parent=None):
        QDialog.__init__(self)
        self.ui = Ui_mpPasswdDialog()
        
        self.ui.setupUi(self)
        
        self.setWindowFlags(Qt.FramelessWindowHint) # Remove title bar
#	self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # self.passwdSignal = Signal(str)
        
        self.ui.mp0btn.clicked.connect(self.push_button0_clicked)
        self.ui.mp1btn.clicked.connect(self.push_button1_clicked)
        self.ui.mp2btn.clicked.connect(self.push_button2_clicked)
        self.ui.mp3btn.clicked.connect(self.push_button3_clicked)
        self.ui.mp4btn.clicked.connect(self.push_button4_clicked)
        self.ui.mp5btn.clicked.connect(self.push_button5_clicked)
        self.ui.mp6btn.clicked.connect(self.push_button6_clicked)
        self.ui.mp7btn.clicked.connect(self.push_button7_clicked)
        self.ui.mp8btn.clicked.connect(self.push_button8_clicked)
        self.ui.mp9btn.clicked.connect(self.push_button9_clicked)
        # self.ui.mpSubmitbtn.clicked.connect(self.push_buttonSubmit_clicked)
        self.ui.mpCanclebtn.clicked.connect(self.push_buttonCancel_clicked)
        self.ui.mpDelbtn.clicked.connect(self.push_buttonDelete_clicked)
        self.ui.mpPasswdLE.textChanged.connect(self.on_text_changed)
        self.ui.mpReceiveSkipBtn.clicked.connect(self.push_buttonReceiveSkip_clicked)
        self.ui.mpReceiveConfirmBtn.clicked.connect(self.handle_receive_confirm_btn)
        
        # self.current_queue_target = self.queue_list_response["data"][0]["target"]
        self.station_response = get_station_list()
        self.stationName =''
        self.stationPasswd =''
        self.isPasswdDialog2 = False
        
        
    def push_button0_clicked(self):
        self.ui.mpPasswdLE.setText(self.ui.mpPasswdLE.text()+'0')
        
    def push_button1_clicked(self):
        self.ui.mpPasswdLE.setText(self.ui.mpPasswdLE.text()+'1')
        
    def push_button2_clicked(self):
        self.ui.mpPasswdLE.setText(self.ui.mpPasswdLE.text()+'2')

    def push_button3_clicked(self):
        self.ui.mpPasswdLE.setText(self.ui.mpPasswdLE.text()+'3')
        
    def push_button4_clicked(self):
        self.ui.mpPasswdLE.setText(self.ui.mpPasswdLE.text()+'4')
        
    def push_button5_clicked(self):
        self.ui.mpPasswdLE.setText(self.ui.mpPasswdLE.text()+'5')
        
    def push_button6_clicked(self):
        self.ui.mpPasswdLE.setText(self.ui.mpPasswdLE.text()+'6')
        
    def push_button7_clicked(self):
        self.ui.mpPasswdLE.setText(self.ui.mpPasswdLE.text()+'7')
        
    def push_button8_clicked(self):
        self.ui.mpPasswdLE.setText(self.ui.mpPasswdLE.text()+'8')
        
    def push_button9_clicked(self):
        self.ui.mpPasswdLE.setText(self.ui.mpPasswdLE.text()+'9')
        
    def push_buttonCancel_clicked(self):
        self.ui.mpPasswdLE.setText('')
        
    def push_buttonDelete_clicked(self):
        text = self.ui.mpPasswdLE.text()
        self.ui.mpPasswdLE.setText(text[:-1])  # Remove last character
        
    def push_buttonReceiveSkip_clicked(self):
        print("Skip clicked.")
        
        if not (self.isPasswdDialog2):
            self.re_add_current_queue()   
            print("re add queue and close dialog")     
        self.close()
        
    def re_add_current_queue(self):
        
        self.queue_list_response = get_pending_queue()
        
        update_robot_status("LOAD_OUT")
        
        data = {
                    "action": "Delivery",
                    "target": self.queue_list_response["data"][0]["target"],
                    "boxNumber": self.queue_list_response["data"][0]["boxNumber"],
                    "priority": "Normal",
                    "sender": "Robot",
                    "status": "queue"
                }       
        add_queue(data)        
        
        rm_id = self.queue_list_response["data"][0]["_id"]
        
        print(f"re - add queue id: {rm_id}")
        print(f"re - add queue data: {data}")
        # remove_queue_by_id(rm_id)                # remove from queue list
        remove_queue_no_history(rm_id)
        
        update_robot_status("STANDBY")


    def on_text_changed(self):
        # print("Incoming text input....")    
        text = self.ui.mpPasswdLE.text()
            
        if (len(text) >= 4) and (text == self.stationPasswd):
            print("Emitting password signal. by enter passwd key.")
            self.passwdSignal.emit(text)
            self.close()
            
         
    def handle_receive_confirm_btn(self):
        text = self.ui.mpPasswdLE.text()
            
        if (text == self.stationPasswd):
            print("Emitting password signal by mpReceiveConfirmBtn clicked.")
            self.passwdSignal.emit(text)
            self.close()
        else: 
            self.ui.mpMsgLb.setText('รหัสผ่านไม่ถูกต้อง')
            
        # self.passwdSignal.emit(self.ui.mpPasswdLE.text())
        
    @Slot(bool)
    def passwd_confirm_slot(self, Confirm):
        print(f"Passwd correct : {Confirm}")
        
    @Slot(str)
    def station_name_slot(self, station):
        print(f"Current Station is {station}") 
        self.stationName = station
        
        for item in self.station_response["data"]:
            if (item['name'] == station):
                self.stationPasswd = item['password']    # get passwd from station data
                print(f"The current station passwd is : {self.stationPasswd} ")
         
    
    # @Slot(int)
    # def passwd_Box_slot(self, box):
    #     self.ui.mpBoxNumberlb.setText(str(box))      
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     ########################################################################
#     ## 
#     ########################################################################
#     dialog = PasswordDialog()
#     dialog.show()
#     sys.exit(app.exec_())        

    
        
