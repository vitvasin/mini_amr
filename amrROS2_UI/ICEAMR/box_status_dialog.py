import os
import sys
from PySide6 import QtCore
from PySide6.QtCore import *
from PySide6.QtCore import Signal, Slot

from box_status_ui import *

# Add project_a to sys.path
#DELIVERY_ROBOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'amrROS2_ws/src/delivery_robot_main_controller'))
#sys.path.insert(0, DELIVERY_ROBOT_PATH)

# Now you can import normally
#from delivery_robot_main_controller.api_client import *


class BoxStatusDialog(QDialog):
    """docstring for ClassName."""
            
    def __init__(self, parent=None):
        QDialog.__init__(self)
        self.ui = Ui_mpBoxStatus()
        
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint) # Remove title bar
#	self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
