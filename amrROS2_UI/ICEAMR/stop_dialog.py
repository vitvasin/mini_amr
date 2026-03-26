import os
import sys
from PySide6 import QtCore
from PySide6.QtCore import *
from PySide6.QtCore import Signal, Slot

from stop_ui import *

# Add project_a to sys.path
DELIVERY_ROBOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'amrROS2_ws/src/delivery_robot_main_controller'))
sys.path.insert(0, DELIVERY_ROBOT_PATH)

# Now you can import normally
from delivery_robot_main_controller.api_client import *


class StopDialog(QDialog):
    """docstring for ClassName."""
            
    def __init__(self, parent=None):
        QDialog.__init__(self)
        self.ui = Ui_mpStopDialog()
        
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint) # Remove title bar
#	self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # self.ui.mpStopText.setText(stop_mode)
        
        self.ui.mpRunAgainBtn.pressed.connect(self.run_again)
        
        # ## ---------------------------------------------------------
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.update_status)
        # self.timer.start(500) # 1000 ms        
        # ##----------------------------------------------------------
        # self.current_status = ""
        # self.prev_status = ""
        
    def run_again(self):
        update_robot_status("STANDBY")
        self.close()
        
    # def update_status(self):
    #     self.current_status = get_robot_status_by_name("status")       
        
    
    #     if self.current_status != self.prev_status:
    #         self.prev_status = self.current_status
            

    
