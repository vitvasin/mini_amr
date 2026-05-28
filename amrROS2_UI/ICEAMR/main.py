########################################################################
## SPINN DESIGN CODE
# YOUTUBE: (SPINN TV) https://www.youtube.com/spinnTv
# WEBSITE: spinncode.com
########################################################################

########################################################################
## IMPORTS
########################################################################

import os
import sys
from PySide6 import QtCore
from PySide6.QtCore import *
from PySide6.QtWidgets import QDialog
import secrets
from PySide6.QtCore import Slot

# Add project_a to sys.path
DELIVERY_ROBOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'amrROS2_ws/src/delivery_robot_main_controller'))
sys.path.insert(0, DELIVERY_ROBOT_PATH)

# Now you can import normally
from delivery_robot_main_controller.api_client import *
from multiprocessing.connection import Client

########################################################################
# IMPORT GUI FILE
from ui_interface import *
from password_dialog import PasswordDialog
from stop_dialog import StopDialog
from box_status_dialog import BoxStatusDialog

########################################################################
## MAIN WINDOW CLASS
########################################################################

RPC_HOST = "localhost"
RPC_PORT =  6000
# DOOR_SERVICE = '/mservice/holding_regs'

# RPC_HOST = "10.222.41.76"
# RPC_PORT =  6000

def call_remote(fn, *args, **kwargs):
    conn = None
    try:
        conn = Client((RPC_HOST, RPC_PORT), authkey=b"secret")        
        conn.send({"fn": fn, "args": args, "kwargs": kwargs})
        resp = conn.recv()
        if not resp.get("ok"):
            raise RuntimeError(resp.get("error"))
        return resp.get("result")
    finally:
        if conn is not None:
            try:
                conn.close()
            except:
                pass

class MainWindow(QMainWindow):  
    boxNumber=0  
    target = ''
    passwdConfirmSignal = Signal(bool)
    stationNameSignal = Signal(str)
    
    def __init__(self, parent=None):
               
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        # self.passwd_ui = Ui_mpPasswdDialog()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint) # Remove title bar
        # self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)        
        self.w = None
        
        self.doorA_state = 0
        self.doorB_state = 0
        self.doorC_state = 0
        self.doorD_state = 0
        self.doorE_state = 0
        self.doorF_state = 0
        self.doorG_state = 0
        self.doorH_state = 0
        
        self.box1_state = False    # False = door close, True = door open
        self.box2_state = False
        self.box3_state = False
        self.box4_state = False
        self.box5_state = False
        self.box6_state = False
        self.box7_state = False
        self.box8_state = False
        
        self.box1_use_state = False # False = not use, True = use
        self.box2_use_state = False
        self.box3_use_state = False
        self.box4_use_state = False
        self.box5_use_state = False
        self.box6_use_state = False
        self.box7_use_state = False
        self.box8_use_state = False
        
        self.box1_selected_state = False # False = not selected, True = selected
        self.box2_selected_state = False
        self.box3_selected_state = False
        self.box4_selected_state = False
        self.box5_selected_state = False
        self.box6_selected_state = False
        self.box7_selected_state = False
        self.box8_selected_state = False
        
        self.passwd_dlg = None
        self.box_status_dlg = None
        self.map_image_file = None
        
        self.is_rm_current_queue = True
        
        update_robot_status("STANDBY")
        #update_robot_status("PAUSED")
        ## ---------------------------------------------------------        
        # self.ui.widget.setVisible(True)
        # self.ui.widget_2.setHidden(True)
        self.ui.myStackedWidget.setCurrentIndex(0)
        self.ui.mpTargetLb.setText("Home")
        self.ui.mpTargetCmb.setCurrentIndex(0)
        
        ## ---------------------------------------------------------
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(200) # 1000 ms 
        
        ##----------------------------------------------------------
        
        self.prev_status = ""
        self.current_status = ""
        
        self.prev_queue_action = ""
        self.current_queue_action = ""
        
        self.prev_queue_target = ""
        self.current_queue_target = ""
        
        self.prev_queue_box = ""
        self.current_queue_box = ""
        self.BoxInt = 0

        self.receive_passwd = ""
        
        self.wait_load_out_flag = True
        
        self.ui.mpSendConfirmBtn.setDisabled(True)

        ########################################################################
        ## QSTACKWIDGETS NAVIGATION
        ########################################################################
        # self.ui.prev.clicked.connect(lambda: self.ui.myStackedWidget.slideToPreviousWidget())
        # self.ui.nxt.clicked.connect(lambda: self.ui.myStackedWidget.slideToNextWidget())
        
        # self.ui.mpTargetBtn.clicked.connect(lambda: self.ui.myStackedWidget.setCurrentWidget(self.ui.location_page))
        # self.ui.mpSendBtn.clicked.connect(lambda: self.ui.myStackedWidget.setCurrentWidget(self.ui.send_page))
        # self.ui.mpReceiveBtn.clicked.connect(lambda: self.ui.myStackedWidget.setCurrentWidget(self.ui.receive_page))
        
        # self.ui.mpBacktoHomePageBtn.clicked.connect(lambda: self.ui.myStackedWidget.setCurrentWidget(self.ui.home_page))
        # self.ui.mpBacktoHomePageBtn_2.clicked.connect(lambda: self.ui.myStackedWidget.setCurrentWidget(self.ui.home_page))
        # self.ui.mpBacktoHomePageBtn_3.clicked.connect(lambda: self.ui.myStackedWidget.setCurrentWidget(self.ui.home_page))
        
        self.ui.mpTargetBtn.pressed.connect(lambda: self.ui.myStackedWidget.setCurrentWidget(self.ui.location_page))
        # self.ui.mpTargetBtn.pressed.connect(lambda: update_robot_status("PAUSED"))
        self.ui.mpTargetBtn.pressed.connect(lambda: update_robot_status("STANDBY"))
        
        self.ui.pushButton_3.pressed.connect(self.open_pause_dialog)
        
        # self.ui.mpSendBtn.pressed.connect(lambda:self.ui.myStackedWidget.setCurrentWidget(self.ui.send_page))     
        self.ui.mpSendBtn.pressed.connect(self.goto_send_page) 
        self.ui.mpSendBtn.pressed.connect(lambda: self.ui.mpSendConfirmBtn.setDisabled(False))
        
        self.ui.mpReceiveBtn.pressed.connect(lambda: self.ui.myStackedWidget.setCurrentWidget(self.ui.receive_page))
        self.ui.mpReceiveBtn.pressed.connect(lambda: update_robot_status("PAUSED"))
        self.ui.mpReceiveBtn.pressed.connect(self.receive_page_init)
        
        self.ui.mpBacktoHomePageBtn.pressed.connect(lambda: self.ui.myStackedWidget.setCurrentWidget(self.ui.home_page))
        self.ui.mpBacktoHomePageBtn_2.pressed.connect(lambda: self.ui.myStackedWidget.setCurrentWidget(self.ui.home_page))
        self.ui.mpBacktoHomePageBtn_3.pressed.connect(lambda: self.ui.myStackedWidget.setCurrentWidget(self.ui.home_page))
        # self.ui.mpBacktoHomePageBtn_3.pressed.connect(lambda: self.ui.myStackedWidget.setCurrentWidget(self.ui.home_page))
        
        
        self.system_params = get_system_parameters()    # Get all system parameters    
        self.wait_loadout_timeout = self.system_params["data"][0]["waitLoadoutTimeout"]  # Get wait loadout timeout parameter      
        # print("Wait Loadout Timeout:", self.wait_load_out_param)
        self.door_open_timeout = self.system_params["data"][0]["doorOpenTimeout"] # Get door open timeout parameter
        
        # self.ui.mpBoxNumberCb.currentIndexChanged.connect(self.handle_box_index_changed)
        self.ui.mpBoxNumberCb.currentTextChanged.connect(self.handle_box_text_changed)
        #------- Location Page --------------
                    

        self.station_response = get_station_list()
        idx=0
        for item in self.station_response["data"]:
            # print(item["name"])
            self.ui.mpTargetCmb.addItem(item["name"])
            self.ui.mpTargetCmb.setItemIcon( idx, QIcon(u":/white/icons_white/font_awesome/solid/location-crosshairs.png"))
            self.ui.mpTargetCmb.setIconSize(QSize(40, 40))
            idx = idx+1
        
        # self.ui.mpTargetCmb.currentIndexChanged.connect(self.location_confirm)
        self.ui.mpOkBtn.clicked.connect(self.location_confirm)
        
        # #--------------  Set Map Image   --------------------------------
        # URL_MAP_IMAGE = "https://placehold.co/600x400@2x.png"
        # file_name = 'downloaded_image.jpg'
        
        # try:
        #     response = requests.get(url=URL_MAP_IMAGE)
        #     response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        #     with open(file_name, 'wb') as file:
        #         file.write(response.content)

        #     print(f"Image downloaded successfully as {file_name}")
            
        #     # Load pixmap and set to label
        #     if os.path.exists(file_name):
        #         pixmap = QPixmap(file_name)
                
        #         # Set the pixmap to the label
        #         self.ui.mpMaplb.setPixmap(pixmap)

        #         # Optional: Scale the image to fit the label
        #         self.ui.mpMaplb.setScaledContents(True)
                
        #         # Store reference to allow cleanup later
        #         self.map_image_file = file_name
        #     else:
        #         print(f"Downloaded file {file_name} not found")

        # except requests.exceptions.RequestException as e:
        #     print(f"Error downloading image: {e}")
            
                
        #------- Send Page --------------------
        
        self.ui.mpDoorA.setIcon(QIcon(u":/black/Icons/feather/lock.png"))
        self.ui.mpDoorA.setIconSize(QSize(50, 50))  
        self.ui.mpDoorB.setIcon(QIcon(u":/black/Icons/feather/lock.png"))
        self.ui.mpDoorB.setIconSize(QSize(50, 50))  
        self.ui.mpDoorC.setIcon(QIcon(u":/black/Icons/feather/lock.png"))
        self.ui.mpDoorC.setIconSize(QSize(50, 50))
        self.ui.mpDoorD.setIcon(QIcon(u":/black/Icons/feather/lock.png"))
        self.ui.mpDoorD.setIconSize(QSize(50, 50))
        self.ui.mpDoorE.setIcon(QIcon(u":/black/Icons/feather/lock.png"))
        self.ui.mpDoorE.setIconSize(QSize(50, 50))
        self.ui.mpDoorF.setIcon(QIcon(u":/black/Icons/feather/lock.png"))
        self.ui.mpDoorF.setIconSize(QSize(50, 50)) 
        self.ui.mpDoorG.setIcon(QIcon(u":/black/Icons/feather/lock.png"))
        self.ui.mpDoorG.setIconSize(QSize(50, 50))
        self.ui.mpDoorH.setIcon(QIcon(u":/black/Icons/feather/lock.png"))
        self.ui.mpDoorH.setIconSize(QSize(50, 50))
        
        self.ui.mpDoorA.clicked.connect(self.doorA_clicked)
        self.ui.mpDoorB.clicked.connect(self.doorB_clicked)
        self.ui.mpDoorC.clicked.connect(self.doorC_clicked)
        self.ui.mpDoorD.clicked.connect(self.doorD_clicked)
        self.ui.mpDoorE.clicked.connect(self.doorE_clicked)
        self.ui.mpDoorF.clicked.connect(self.doorF_clicked)
        self.ui.mpDoorG.clicked.connect(self.doorG_clicked)
        self.ui.mpDoorH.clicked.connect(self.doorH_clicked)
               
        # self.ui.mpSendOkBtn.clicked.connect(lambda: self.ui.myStackedWidget.setCurrentWidget(self.ui.Moving_page))
        
        
        model = QStringListModel()
        self.boxList = model.stringList() 
        self.stationList = model.stringList()
        
        # self.stationList.append('No Station Selected')
        # idx=0
        for item in self.station_response["data"]:
            self.stationList.append('  '+item["name"])
            # self.station_name[idx] = item['name']
            # idx = idx+1

        
        # print(self.station_name)
            
                
        self.mapping_door_response = list_mapping()
        for mapping in self.mapping_door_response["data"]:            
            if mapping['door'] == 'A':                
                self.ui.mpDoorA.setStyleSheet(self.get_door_color(mapping['box']))
            elif mapping['door'] == 'B': 
                self.ui.mpDoorB.setStyleSheet(self.get_door_color(mapping['box']))
            elif mapping['door'] == 'C': 
                self.ui.mpDoorC.setStyleSheet(self.get_door_color(mapping['box']))
            elif mapping['door'] == 'D': 
                self.ui.mpDoorD.setStyleSheet(self.get_door_color(mapping['box']))
            elif mapping['door'] == 'E': 
                self.ui.mpDoorE.setStyleSheet(self.get_door_color(mapping['box']))
            elif mapping['door'] == 'F': 
                self.ui.mpDoorF.setStyleSheet(self.get_door_color(mapping['box']))
            elif mapping['door'] == 'G': 
                self.ui.mpDoorG.setStyleSheet(self.get_door_color(mapping['box']))
            elif mapping['door'] == 'H': 
                self.ui.mpDoorH.setStyleSheet(self.get_door_color(mapping['box']))
            
            if mapping['box'] == '1':                
                self.boxList.append('  Box 1')
            elif mapping['box'] == '2':  
                self.boxList.append('  Box 2')
            elif mapping['box'] == '3':  
                self.boxList.append('  Box 3')
            elif mapping['box'] == '4': 
                self.boxList.append('  Box 4')
            elif mapping['box'] == '5': 
                self.boxList.append('  Box 5')
            elif mapping['box'] == '6': 
                self.boxList.append('  Box 6')
            elif mapping['box'] == '7': 
                self.boxList.append('  Box 7')
            elif mapping['box'] == '8': 
                self.boxList.append('  Box 8')
                
        # print(self.boxList)
        self.uniqueStrList = list(set(self.boxList))    
        self.uniqueStrList.sort()
        # self.uniqueStrList.insert(0,' No Box Selected')
        # print(self.uniqueStrList) 
        self.boxListCount = len(self.uniqueStrList)
        print(self.boxListCount)
        
        # Set vertical header alignment to center
        self.ui.mpQueueTable.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.ui.mpQueueTable.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        
        # Stop horizontal column resizing
        self.ui.mpQueueTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        # Stop vertical row resizing
        self.ui.mpQueueTable.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

        # 🔧 Change header size
        self.ui.mpQueueTable.horizontalHeader().setFixedHeight(80)    # Header height
        self.ui.mpQueueTable.verticalHeader().setFixedWidth(62)       # Row header width
        
        # Set specific column widths
        self.ui.mpQueueTable.setColumnWidth(0, 250)#254)#294)
        self.ui.mpQueueTable.setColumnWidth(1, 458)#335)#295) 
        # self.ui.mpQueueTable.setRowHeight()

        # Apply stylesheet to table (cleaned of invalid QSS comments)
        self.ui.mpQueueTable.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #ccc;
                font: 40 italic 25pt "Ubuntu Sans Mono";
            }

            QHeaderView::section {
                background-color: #007acc;
                color: white;
                padding: 4px;
                border: 1px solid #6c6c6c;
                font: 80 italic 25pt "Ubuntu Sans Mono";
                selection-color: rgb(51, 209, 122);
            }

            QHeaderView#verticalHeader::section {
                background-color: #0066cc;
                color: white;
                font-weight: bold;
                border: 1px solid #ccc;
                padding: 4px;
            }

            QTableWidget::item {
                selection-background-color: #C6E3E7;
                selection-color: black;
            }

            QTableCornerButton::section {
                background-color: #007acc;
                border: 1px solid #6c6c6c;
            }
        """)
        
        self.ui.mpSendCancelBtn.clicked.connect(self.remove_selected_row)    
        self.ui.mpSendConfirmBtn.clicked.connect(self.send_delivery_task)
        
        #-------- Receive Page -----------------
        self.ui.mpReceiveOkBtn.clicked.connect(self.open_password_dialog2)      
        # self.ui.mpReceiveCancelBtn.clicked.connect(self.re_add_current_queue)  
        
        #-------- Moving Page ------------------        
        # self.ui.mpSendCancelBtn2.clicked.connect(lambda: self.ui.myStackedWidget.setCurrentWidget(self.ui.send_page)) 
        self.ui.mpSendCancelBtn2.clicked.connect(self.send_cancel_in_move_clicked)
        
        ########################################################################
        ## QSTACKWIDGETS ANIMATION
        # ######################################################################## 
               
        self.ui.myStackedWidget.setTransitionDirection(QtCore.Qt.Horizontal)
        self.ui.myStackedWidget.setTransitionSpeed(800)
        # self.ui.myStackedWidget.setTransitionEasingCurve(QtCore.QEasingCurve.Linear)
        self.ui.myStackedWidget.setTransitionEasingCurve(QtCore.QEasingCurve.OutBack)
        # ACTIVATE Animation
        self.ui.myStackedWidget.setSlideTransition(True)

        # # Fade animation
        self.ui.myStackedWidget.setFadeSpeed(500)
        self.ui.myStackedWidget.setFadeCurve(QtCore.QEasingCurve.Linear)
        self.ui.myStackedWidget.setFadeTransition(True)
        ########################################################################
        ## 
        ########################################################################

        #######################################################################
        # SHOW WINDOW
        #######################################################################
        self.show()
        ########################################################################
    
    def closeEvent(self, event):
        """Clean up resources when window is closed."""
        # Stop the update timer
        if self.timer is not None:
            self.timer.stop()
        
        # Clean up dialog references
        if self.passwd_dlg is not None:
            try:
                self.passwd_dlg.close()
                self.passwd_dlg.deleteLater()
            except:
                pass
        
        if self.box_status_dlg is not None:
            try:
                self.box_status_dlg.close()
                self.box_status_dlg.deleteLater()
            except:
                pass
        
        # Clean up pixmap
        try:
            self.ui.mpMaplb.setPixmap(None)
        except:
            pass
        
        # Clean up downloaded image file
        if self.map_image_file is not None:
            try:
                if os.path.exists(self.map_image_file):
                    os.remove(self.map_image_file)
                    print(f"Cleaned up image file: {self.map_image_file}")
            except Exception as e:
                print(f"Error cleaning up image file: {e}")
        
        # Accept the close event
        event.accept()
    
    def doorA_clicked(self):
        self.door_clicked('A')
    
    def doorB_clicked(self):
        self.door_clicked('B')
    
    def doorC_clicked(self):
        self.door_clicked('C')
    
    def doorD_clicked(self):
        self.door_clicked('D')
    
    def doorE_clicked(self):
        self.door_clicked('E')
    
    def doorF_clicked(self):
        self.door_clicked('F')
    
    def doorG_clicked(self):
        self.door_clicked('G')
    
    def doorH_clicked(self):
        self.door_clicked('H')
            
    #------ Header  ------------------
    def update_status(self):
        # For Battery percentage
        self.batt_percent = get_robot_status_by_name("percentage")
        # int_batt_percent = int(float(self.batt_percent)) 
        float_batt_percent = round(float(self.batt_percent),2) 
        self.ui.pushButton.setText(f"{str(float_batt_percent)} %")
        
        if (self.current_status == "SAFE_STOP") and (self.prev_status != "MOVE"):
            self.open_safe_stop_dialog()
        
        # For Update Status bar
        self.current_status = get_robot_status_by_name("status")    
        # For Update target station
        self.target_station = get_robot_status_by_name("target_station")     
        # statusStr = "Status: " + self.current_status
        self.ui.mpStatuslb.setText("Status: " + self.current_status)#statusStr)
        
        
        self.dock_state = get_robot_status_by_name("dock_state") 
        self.charge_state = get_robot_status_by_name("charge_state")
        
        # if self.current_status == "DOCK":           
            
        self.ui.mpDockStatuslb.setText(self.dock_state)
        self.ui.mpChargeStatuslb.setText(self.charge_state)
        self.ui.mpCurrentBattBtn.setText(" "+f"{str(float_batt_percent)} %")
        self.ui.mpCurrentBattBtn.setIconSize(QSize(400, 400))

        
        
        # For Page control
        
        if (self.current_status != "DOCK") :
            
            if (self.current_status == "STANDBY" and self.prev_status == "DOCK" and self.dock_state != "UNDOCKING"):
                self.ui.myStackedWidget.setCurrentWidget(self.ui.home_page) 
        
            self.queue_list_response = get_pending_queue()
            if self.queue_list_response["data"] != []:
                self.current_queue_action = self.queue_list_response["data"][0]["action"]
                self.current_queue_target = self.queue_list_response["data"][0]["target"]               
                    
                #---  For action delivery -------------------
                if self.current_queue_action == "Delivery":
                    # if (self.current_status != "DOCK") :
                        if (self.current_status == "MOVE"): #and self.ui.myStackedWidget.currentIndex() != 4:
                            # self.ui.mpStationTargetLb.setText(self.current_queue_target)
                            self.ui.mpStationTargetLb.setText(self.target_station)
                            self.ui.myStackedWidget.setCurrentWidget(self.ui.Moving_page) 
                            
                        if (self.current_status == "WAIT_LOAD_OUT") and (self.prev_status == "MOVE" or self.prev_status == "AFTER_MOVE"):
                        #if (self.current_status == "WAIT_LOAD_OUT"): #and (self.ui.myStackedWidget.currentIndex() != 3):
                            self.current_queue_box = self.queue_list_response["data"][0]["boxNumber"]
                            
                            QTimer.singleShot(self.wait_loadout_timeout*1000, self.wait_load_out)
                            # QTimer.singleShot(10000, self.wait_load_out)
                            print("Set wait load out timer:", self.wait_loadout_timeout)
                            self.open_password_dialog()
                            
                        if (self.prev_status == "AFTER_MOVE" or self.prev_status == "MOVE") and (self.current_status == "STANDBY"):
                            self.ui.myStackedWidget.setCurrentWidget(self.ui.home_page)  
                            
                
                if self.current_queue_action == "Request":
                    # if (self.prev_status == "STANDBY") and (self.current_status == "MOVE"):
                    if (self.current_status == "MOVE"):
                        # self.ui.mpStationTargetLb_2.setText(self.current_queue_target)
                        self.ui.mpStationTargetLb_2.setText(self.target_station)
                        self.ui.myStackedWidget.setCurrentWidget(self.ui.Move2Target_page) 
                   
                    if (self.prev_status == "AFTER_MOVE" or self.prev_status == "MOVE") and (self.current_status == "STANDBY"):
                        self.ui.myStackedWidget.setCurrentWidget(self.ui.home_page) 
                
                
                                         
                
                self.prev_queue_action = self.current_queue_action
                self.prev_queue_target = self.current_queue_target
                self.prev_queue_box = self.current_queue_box    
                
            else:
                if self.current_queue_action != "Idle":
                    print(f"Queue empty: current state-> {self.current_status} : queue_action-> {self.current_queue_action}")
                    
                    if self.current_queue_action == "Delivery":
                        if (self.prev_status == "LOAD_OUT") and (self.current_status == "STANDBY"):
                            self.ui.myStackedWidget.setCurrentWidget(self.ui.home_page)                    
                            self.current_queue_action = "Idle"
                        
                    elif self.current_queue_action == "Request":
                        if (self.current_status == "STANDBY"):
                            self.ui.myStackedWidget.setCurrentWidget(self.ui.home_page)
                            self.current_queue_action = "Idle"
                    else:
                        self.ui.myStackedWidget.setCurrentWidget(self.ui.home_page)
                        self.current_queue_action = "Idle"  
                
                else:
                    if (self.prev_status == "STANDBY") and (self.current_status == "MOVE"):
                        self.ui.mpStationTargetLb_2.setText(self.target_station)
                        self.ui.myStackedWidget.setCurrentWidget(self.ui.Move2Target_page) 
                
        else:
            if self.prev_status != "DOCK":
                self.ui.myStackedWidget.setCurrentWidget(self.ui.dock_page)
            # self.dock_state = get_robot_status_by_name("dock_state") 
            # self.charge_state = get_robot_status_by_name("charge_state")
                
            if self.dock_state == "DOCKED":
                self.ui.mpDockStatuslb.setText("Docked")
                self.ui.mpDockImageBtn.setIcon(QIcon(u":/dock/Icons_dock/Dock.png"))
                self.ui.mpDockImageBtn.setIconSize(QSize(500, 650))
                # self.ui.mpDoorE.setIconSize(QSize(50, 50))
                
            elif self.dock_state == "DOCKING":   
                self.ui.mpDockStatuslb.setText("Docking")
                self.ui.mpDockImageBtn.setIcon(QIcon(u":/dock/Icons_dock/Dock.png"))
                self.ui.mpDockImageBtn.setIconSize(QSize(500, 650))
                
            elif self.dock_state == "UNDOCKING":   
                self.ui.mpDockStatuslb.setText("Undocking")
                self.ui.mpDockImageBtn.setIcon(QIcon(u":/dock/Icons_dock/Udock.png"))
                self.ui.mpDockImageBtn.setIconSize(QSize(500, 650))
                        
         
                
        # if self.current_queue_action == "Idle":        
        #     print(f"current state-> {self.current_status} : previous state-> {self.prev_status}")
                
        if self.prev_status != self.current_status:
            print(f"queue action->{self.current_queue_action} :  current state-> {self.current_status} : previous state-> {self.prev_status}")
            self.prev_status = self.current_status
            
        
    def open_pause_dialog(self):
        update_robot_status("PAUSED")
        stop_dlg = StopDialog()
        stop_dlg.ui.mpStopText.setText("PAUSED")
        stop_dlg.ui.label.setText("ผู้ใช้งานหยุดการเคลื่อนที่ของหุ่นยนต์.\nกรุณากดปุ่ม RUN\n เพื่อเริ่มการทำงานใหม่.")
    
        if stop_dlg.exec_() == QDialog.Accepted:
            print("Dialog accepted!")        
        else:
            print("Dialog rejected!")
            
    def open_safe_stop_dialog(self):
        # update_robot_status("STANDBY")
        stop_dlg = StopDialog()
        stop_dlg.ui.mpStopText.setText("SAFE STOP")
        stop_dlg.ui.label.setText("หุ่นยนต์หยุด เนื่องจากมีสิ่งกีดขวาง. \nกรุณากดปุ่ม RUN\n เพื่อเริ่มการทำงานใหม่.")
    
        if stop_dlg.exec_() == QDialog.Accepted:
            print("Dialog accepted!")        
        else:
            print("Dialog rejected!")
            
    def open_skip_dialog(self):
        update_robot_status("PAUSED")
        stop_dlg = StopDialog()
        stop_dlg.ui.mpStopText.setText("Current Task Skipped")
        stop_dlg.ui.label.setText("Current task cancel by user.\nPress run button to\n run next queue.")
    
        if stop_dlg.exec_() == QDialog.Accepted:
            print("Dialog accepted!")        
        else:
            print("Dialog rejected!")
        

        
    
    # ----- Location Page -------------
    def location_confirm(self):
        print(self.station_response["data"][self.ui.mpTargetCmb.currentIndex()]["name"])

        data = {
            "action": "Request",
            "target": self.station_response["data"][self.ui.mpTargetCmb.currentIndex()]["name"],
            "boxNumber": 1,
            "priority": "Normal",
            "sender": "Robot",
            "status": "queued",
            
        }
        add_queue(data)
        
        update_robot_status("STANDBY")
    
    # ------------ Send page --------------------------------------------- 
    def remove_selected_row(self):
        self.selected_indexes = self.ui.mpQueueTable.selectionModel().selectedRows()
        # print(self.selected_indexes.)           
        
        for index in sorted(self.selected_indexes, reverse=True):
            item= self.ui.mpQueueTable.item(index.row(),0)
            if item.text() == 'Box1':
                self.box1_selected_state = False
            elif item.text() == 'Box2':
                self.box2_selected_state = False
            elif item.text() == 'Box3':
                self.box3_selected_state = False
            elif item.text() == 'Box4':
                self.box4_selected_state = False
            elif item.text() == 'Box5':
                self.box5_selected_state = False
            elif item.text() == 'Box6':
                self.box6_selected_state = False
            elif item.text() == 'Box7':
                self.box7_selected_state = False
            elif item.text() == 'Box8':
                self.box8_selected_state = False
                
            self.ui.mpQueueTable.removeRow(index.row())
        
    def add_row(self, box):
        current_rows = self.ui.mpQueueTable.rowCount()
        if current_rows < self.boxListCount:
            self.ui.mpQueueTable.insertRow(current_rows)
            self.ui.mpQueueTable.setRowHeight(current_rows, 70)
            
            item = QTableWidgetItem(box)
            item.setTextAlignment(Qt.AlignCenter)
                
            self.ui.mpQueueTable.setItem(current_rows, 0, item)
                
            station_combo = QComboBox()
            station_combo.addItems(self.stationList)
            station_combo.setStyleSheet("""
                QComboBox{
                    color: rgb(0, 0, 0);
                    font: 20 italic 30px "Ubuntu Sans Mono"; 
                }
                                
            """)
            self.ui.mpQueueTable.setCellWidget(current_rows, 1, station_combo)
                
            if box == 'Box1':
                self.box1_selected_state = True
            elif box == 'Box2':
                self.box2_selected_state = True
            elif box == 'Box3':
                self.box3_selected_state = True
            elif box == 'Box4':
                self.box4_selected_state = True
            elif box == 'Box5':
                self.box5_selected_state = True
            elif box == 'Box6':
                self.box6_selected_state = True
            elif box == 'Box7':
                self.box7_selected_state = True
            elif box == 'Box8':
                self.box8_selected_state = True
                
    # def add_row2(self, box, station):
    #     current_rows = self.ui.mpQueueTable.rowCount()
    #     if current_rows < self.boxListCount:
    #         self.ui.mpQueueTable.insertRow(current_rows)
    #         self.ui.mpQueueTable.setRowHeight(current_rows, 70)
            
    #         item = QTableWidgetItem(box)
    #         item.setTextAlignment(Qt.AlignCenter)
                
    #         self.ui.mpQueueTable.setItem(current_rows, 0, item)
                
    #         station_combo = QComboBox()
    #         station_combo.addItems(self.stationList)
    #         station_combo.setCurrentText('  '+station)
    #         station_combo.setStyleSheet("""
    #             QComboBox{
    #                 color: rgb(0, 0, 0);
    #                 font: 20 italic 30px "Ubuntu Sans Mono"; 
    #             }
                                
    #         """)
    #         self.ui.mpQueueTable.setCellWidget(current_rows, 1, station_combo)
                
            # if box == 'Box1':
            #     self.box1_use_state = True
            # elif box == 'Box2':
            #     self.box2_use_state = True
            # elif box == 'Box3':
            #     self.box3_use_state = True
            # elif box == 'Box4':
            #     self.box4_use_state = True
            # elif box == 'Box5':
            #     self.box5_use_state = True
            # elif box == 'Box6':
            #     self.box6_use_state = True
            # elif box == 'Box7':
            #     self.box7_use_state = True
            # elif box == 'Box8':
            #     self.box8_use_state = True
            
    def get_door_color(self, boxNumber):
        color='background-color: rgb(242, 252, 252);'
        if boxNumber == '1':
            color = 'background-color: rgb(143, 240, 164);'
        elif boxNumber == '2':
            color = 'background-color: rgb(153, 193, 241);'
        elif boxNumber == '3':
            color = 'background-color: rgb(249, 240, 107);'
        elif boxNumber == '4':
            color = 'background-color: rgb(246, 97, 81);'
        elif boxNumber == '5':
            color = 'background-color: rgb(220, 138, 221);'
        elif boxNumber == '6':
            color = 'background-color: rgb(255, 190, 111);'
        elif boxNumber == '7':
            color = 'background-color: rgb(242, 37, 141);'        
        elif boxNumber == '8':
            color = 'background-color: rgb(222, 221, 218);'
        return color
    
    def show_box_frame(self, color):
        if self.ui.mpFrameBox1.isHidden():
            self.ui.mpFrameBox1.setHidden(False)
            self.ui.mpFrameBox1.setStyleSheet(color)
        elif self.ui.mpFrameBox2.isHidden():
            self.ui.mpFrameBox2.setHidden(False)
            self.ui.mpFrameBox2.setStyleSheet(color)
        elif self.ui.mpFrameBox3.isHidden():
            self.ui.mpFrameBox3.setHidden(False)
            self.ui.mpFrameBox3.setStyleSheet(color)
        elif self.ui.mpFrameBox4.isHidden():
            self.ui.mpFrameBox4.setHidden(False)
            self.ui.mpFrameBox4.setStyleSheet(color)
        elif self.ui.mpFrameBox5.isHidden():
            self.ui.mpFrameBox5.setHidden(False)
            self.ui.mpFrameBox5.setStyleSheet(color)
        elif self.ui.mpFrameBox6.isHidden():
            self.ui.mpFrameBox6.setHidden(False)
            self.ui.mpFrameBox6.setStyleSheet(color)
        elif self.ui.mpFrameBox7.isHidden():
            self.ui.mpFrameBox7.setHidden(False)
            self.ui.mpFrameBox7.setStyleSheet(color)
        elif self.ui.mpFrameBox8.isHidden():
            self.ui.mpFrameBox8.setHidden(False)
            self.ui.mpFrameBox8.setStyleSheet(color)
            
    
    
    def door_clicked(self, name):
        currentBox = 0
        for data in self.mapping_door_response['data']:
            if data['door'] == name:
                # print(data['BoxNumber'])
                currentBox = data['box']
                boxColor = self.get_door_color(currentBox)
        
        if currentBox == '1':            
            if(self.box1_use_state==False):
                self.box1_state = not self.box1_state 
            self.state = self.box1_state
            
            if(self.box1_selected_state==False):
                if(self.box1_use_state==False):
                    # self.box1_state = not self.box1_state 
                    # self.state = self.box1_state                    
                    self.add_row('Box1')
                else:
                    print("Box 1 already in use")
                    # Clean up previous dialog if it exists
                    if self.box_status_dlg is not None:
                        try:
                            self.box_status_dlg.deleteLater()
                        except:
                            pass
                    # Create new dialog
                    self.box_status_dlg = BoxStatusDialog()
                    self.box_status_dlg.ui.mpBoxInuselb.setText("Box 1 is already in use.\nPlease select another box.")
                    self.box_status_dlg.exec_()
                    self.box_status_dlg.deleteLater()
                    self.box_status_dlg = None
            
            use_state = self.box1_use_state
            
        elif currentBox == '2':            
            if(self.box2_use_state==False):
                self.box2_state = not self.box2_state
            self.state = self.box2_state
            
            if(self.box2_selected_state==False):
                if(self.box2_use_state==False):
                    # self.box2_state = not self.box2_state
                    # self.state = self.box2_state
                    self.add_row('Box2')
                else:
                    print("Box 2 already in use")
                    # Clean up previous dialog if it exists
                    if self.box_status_dlg is not None:
                        try:
                            self.box_status_dlg.deleteLater()
                        except:
                            pass
                    # Create new dialog
                    self.box_status_dlg = BoxStatusDialog()
                    self.box_status_dlg.ui.mpBoxInuselb.setText("Box 2 is already in use.\nPlease select another box.")
                    self.box_status_dlg.exec_()
                    self.box_status_dlg.deleteLater()
                    self.box_status_dlg = None
            use_state = self.box2_use_state
            
        elif currentBox == '3':            
            if(self.box3_use_state==False):
                self.box3_state = not self.box3_state
            self.state = self.box3_state
            
            if(self.box3_selected_state==False):
                if(self.box3_use_state==False):
                    # self.box3_state = not self.box3_state
                    # self.state = self.box3_state
                    self.add_row('Box3')
                else:
                    print("Box 3 already in use")
                    # Clean up previous dialog if it exists
                    if self.box_status_dlg is not None:
                        try:
                            self.box_status_dlg.deleteLater()
                        except:
                            pass
                    # Create new dialog
                    self.box_status_dlg = BoxStatusDialog()
                    self.box_status_dlg.ui.mpBoxInuselb.setText("Box 3 is already in use.\nPlease select another box.")
                    self.box_status_dlg.exec_()
                    self.box_status_dlg.deleteLater()
                    self.box_status_dlg = None
            use_state = self.box3_use_state
            
        elif currentBox == '4':            
            if(self.box4_use_state==False):
                self.box4_state = not self.box4_state
            self.state = self.box4_state
            
            if(self.box4_selected_state==False):
                if(self.box4_use_state==False):
                    # self.box4_state = not self.box4_state
                    # self.state = self.box4_state
                    self.add_row('Box4')
                else:
                    print("Box 4 already in use")
                    # Clean up previous dialog if it exists
                    if self.box_status_dlg is not None:
                        try:
                            self.box_status_dlg.deleteLater()
                        except:
                            pass
                    # Create new dialog
                    self.box_status_dlg = BoxStatusDialog()
                    self.box_status_dlg.ui.mpBoxInuselb.setText("Box 4 is already in use.\nPlease select another box.")
                    self.box_status_dlg.exec_()
                    self.box_status_dlg.deleteLater()
                    self.box_status_dlg = None
            use_state = self.box4_use_state
            
        elif currentBox == '5':            
            if(self.box5_use_state==False):
                self.box5_state = not self.box5_state
            self.state = self.box5_state
            
            if(self.box5_selected_state==False):
                if(self.box5_use_state==False):
                    # self.box5_state = not self.box5_state
                    # self.state = self.box5_state
                    self.add_row('Box5')
                else:
                    print("Box 5 already in use")
                    # Clean up previous dialog if it exists
                    if self.box_status_dlg is not None:
                        try:
                            self.box_status_dlg.deleteLater()
                        except:
                            pass
                    # Create new dialog
                    self.box_status_dlg = BoxStatusDialog()
                    self.box_status_dlg.ui.mpBoxInuselb.setText("Box 5 is already in use.\nPlease select another box.")
                    self.box_status_dlg.exec_()
                    self.box_status_dlg.deleteLater()
                    self.box_status_dlg = None
            use_state = self.box5_use_state
            
        elif currentBox == '6':            
            if(self.box6_use_state==False):
                self.box6_state = not self.box6_state
            self.state = self.box6_state
            
            if(self.box6_selected_state==False):
                if(self.box6_use_state==False):
                    # self.box6_state = not self.box6_state
                    # self.state = self.box6_state
                    self.add_row('Box6')
                else:
                    print("Box 6 already in use")
                    # Clean up previous dialog if it exists
                    if self.box_status_dlg is not None:
                        try:
                            self.box_status_dlg.deleteLater()
                        except:
                            pass
                    # Create new dialog
                    self.box_status_dlg = BoxStatusDialog()
                    self.box_status_dlg.ui.mpBoxInuselb.setText("Box 6 is already in use.\nPlease select another box.")
                    self.box_status_dlg.exec_()
                    self.box_status_dlg.deleteLater()
                    self.box_status_dlg = None
            use_state = self.box6_use_state
            
        elif currentBox == '7':            
            if(self.box7_use_state==False):
                self.box7_state = not self.box7_state   
            self.state = self.box7_state  
            
            if(self.box7_selected_state==False):
                if(self.box7_use_state==False):
                    # self.box7_state = not self.box7_state
                    # self.state = self.box7_state
                    self.add_row('Box7')
                else:
                    print("Box 7 already in use")
                    # Clean up previous dialog if it exists
                    if self.box_status_dlg is not None:
                        try:
                            self.box_status_dlg.deleteLater()
                        except:
                            pass
                    # Create new dialog
                    self.box_status_dlg = BoxStatusDialog()
                    self.box_status_dlg.ui.mpBoxInuselb.setText("Box 7 is already in use.\nPlease select another box.")
                    self.box_status_dlg.exec_()
                    self.box_status_dlg.deleteLater()
                    self.box_status_dlg = None
            use_state = self.box7_use_state
            
        elif currentBox == '8':            
            if(self.box8_use_state==False):
                self.box8_state = not self.box8_state
            self.state = self.box8_state
            
            if(self.box8_selected_state==False):
                if(self.box8_use_state==False):
                    # self.box8_state = not self.box8_state
                    # self.state = self.box8_state
                    self.add_row('Box8')
                else:
                    print("Box 8 already in use")
                    # Clean up previous dialog if it exists
                    if self.box_status_dlg is not None:
                        try:
                            self.box_status_dlg.deleteLater()
                        except:
                            pass
                    # Create new dialog
                    self.box_status_dlg = BoxStatusDialog()
                    self.box_status_dlg.ui.mpBoxInuselb.setText("Box 8 is already in use.\nPlease select another box.")
                    self.box_status_dlg.exec_()
                    self.box_status_dlg.deleteLater()
                    self.box_status_dlg = None
            use_state = self.box8_use_state
            
        # print(f"Box state : {state} , use state : {use_state}")
              
        for data in self.mapping_door_response['data']:
            if data['box'] == currentBox:
                if (self.state == True) and (use_state==False):
                    print('Open door ', data['door'])  
                    if data['door'] == 'A':
                        self.ui.mpDoorA.setIcon(QIcon(u":/black/Icons/feather/unlock.png"))
                        self.ui.mpDoorA.setIconSize(QSize(50, 50))  
                        print("Open door #A:", call_remote("door_command", 1, 1))
                        # print("Open door #A:")
                                                
                    elif data['door'] == 'B':
                        self.ui.mpDoorB.setIcon(QIcon(u":/black/Icons/feather/unlock.png"))
                        self.ui.mpDoorB.setIconSize(QSize(50, 50))  
                        print("Open door #B:", call_remote("door_command", 2, 1))
                        # print("Open door #B:")
                    
                    elif data['door'] == 'C':
                        self.ui.mpDoorC.setIcon(QIcon(u":/black/Icons/feather/unlock.png"))
                        self.ui.mpDoorC.setIconSize(QSize(50, 50))
                        print("Open door #C:", call_remote("door_command", 3, 1))
                        # print("Open door #C:")
                    
                    elif data['door'] == 'D':
                        self.ui.mpDoorD.setIcon(QIcon(u":/black/Icons/feather/unlock.png"))
                        self.ui.mpDoorD.setIconSize(QSize(50, 50))
                        print("Open door #D:", call_remote("door_command", 4, 1))
                        # print("Open door #D:")
                    
                    elif data['door'] == 'E':
                        self.ui.mpDoorE.setIcon(QIcon(u":/black/Icons/feather/unlock.png"))
                        self.ui.mpDoorE.setIconSize(QSize(50, 50))
                        print("Open door #E:", call_remote("door_command", 5, 1))
                        # print("Open door #E:")
                    
                    elif data['door'] == 'F':
                        self.ui.mpDoorF.setIcon(QIcon(u":/black/Icons/feather/unlock.png"))
                        self.ui.mpDoorF.setIconSize(QSize(50, 50)) 
                        print("Open door #F:", call_remote("door_command", 6, 1))
                        # print("Open door #F:")
                    
                    elif data['door'] == 'G':
                        self.ui.mpDoorG.setIcon(QIcon(u":/black/Icons/feather/unlock.png"))
                        self.ui.mpDoorG.setIconSize(QSize(50, 50))
                        print("Open door #G:", call_remote("door_command", 7, 1))
                        # print("Open door #G:")
                    
                    elif data['door'] == 'H':
                        self.ui.mpDoorH.setIcon(QIcon(u":/black/Icons/feather/unlock.png"))
                        self.ui.mpDoorH.setIconSize(QSize(50, 50))
                        print("Open door #H:", call_remote("door_command", 8, 1))
                        # print("Open door #H:")
                else:
                    print('Close door ', data['door']) 
                    if data['door'] == 'A':
                        self.ui.mpDoorA.setIcon(QIcon(u":/black/Icons/feather/lock.png"))
                        self.ui.mpDoorA.setIconSize(QSize(50, 50))  
                        print("Close door #A:", call_remote("door_command", 1, 0))
                        # print("Close door #A:")
                        
                    elif data['door'] == 'B':
                        self.ui.mpDoorB.setIcon(QIcon(u":/black/Icons/feather/lock.png"))
                        self.ui.mpDoorB.setIconSize(QSize(50, 50)) 
                        print("Close door #B:", call_remote("door_command", 2, 0))
                        # print("Close door #B:")
                        
                    elif data['door'] == 'C':
                        self.ui.mpDoorC.setIcon(QIcon(u":/black/Icons/feather/lock.png"))
                        self.ui.mpDoorC.setIconSize(QSize(50, 50))
                        print("Close door #C:", call_remote("door_command", 3, 0))
                        # print("Close door #C:")
                         
                    elif data['door'] == 'D':
                        self.ui.mpDoorD.setIcon(QIcon(u":/black/Icons/feather/lock.png"))
                        self.ui.mpDoorD.setIconSize(QSize(50, 50))
                        print("Close door #D:", call_remote("door_command", 4, 0))
                        # print("Close door #D:")
                        
                    elif data['door'] == 'E':
                        self.ui.mpDoorE.setIcon(QIcon(u":/black/Icons/feather/lock.png"))
                        self.ui.mpDoorE.setIconSize(QSize(50, 50))
                        print("Close door #E:", call_remote("door_command", 5, 0))
                        # print("Close door #E:")
                        
                    elif data['door'] == 'F':
                        self.ui.mpDoorF.setIcon(QIcon(u":/black/Icons/feather/lock.png"))
                        self.ui.mpDoorF.setIconSize(QSize(50, 50)) 
                        print("Close door #F:", call_remote("door_command", 6, 0))
                        # print("Close door #F:")
                    
                    elif data['door'] == 'G':
                        self.ui.mpDoorG.setIcon(QIcon(u":/black/Icons/feather/lock.png"))
                        self.ui.mpDoorG.setIconSize(QSize(50, 50))
                        print("Close door #G:", call_remote("door_command", 7, 0))
                        # print("Close door #G:")
                        
                    elif data['door'] == 'H':
                        self.ui.mpDoorH.setIcon(QIcon(u":/black/Icons/feather/lock.png"))
                        self.ui.mpDoorH.setIconSize(QSize(50, 50))
                        print("Close door #H:", call_remote("door_command", 8, 0))
                        # print("Close door #H:")
    
     
        
    def goto_send_page(self):
        self.ui.myStackedWidget.setCurrentWidget(self.ui.send_page)
        update_robot_status("LOAD_IN")
        
    def send_delivery_task(self):
        if (self.box1_state==False and self.box2_state==False and self.box3_state==False and self.box4_state==False and self.box5_state==False and self.box6_state==False and self.box7_state==False and self.box8_state==False):
            print('delivery')
            num_row = self.ui.mpQueueTable.rowCount()            
            
            for row in range(num_row):
                box = self.ui.mpQueueTable.item(row, 0)
                if box.text() == 'Box1':
                    self.boxNumber = 1
                    self.box1_use_state = True
                elif box.text() == 'Box2':
                    self.boxNumber = 2
                    self.box2_use_state = True
                elif box.text() == 'Box3':
                    self.boxNumber = 3
                    self.box3_use_state = True
                elif box.text() == 'Box4':
                    self.boxNumber = 4
                    self.box4_use_state = True
                elif box.text() == 'Box5':
                    self.boxNumber = 5
                    self.box5_use_state = True
                elif box.text() == 'Box6':
                    self.boxNumber = 6
                    self.box6_use_state = True
                elif box.text() == 'Box7':
                    self.boxNumber = 7
                    self.box7_use_state = True
                elif box.text() == 'Box8':
                    self.boxNumber = 8
                    self.box8_use_state = True
                                        
                station = self.ui.mpQueueTable.cellWidget(row, 1)
                self.target = station.currentText().strip() 
         
                print(f"{box.text()} : {station.currentText()}")
                
                data = {
                    "action": "Delivery",
                    "target": self.target,
                    "boxNumber": self.boxNumber,
                    "priority": "Normal",
                    "sender": "Robot",
                    "status": "queued"
                }       
                add_queue(data)
                print(f"add queue: {data}")
                
            # for row in range(num_row):                                              # Add 9/1/26
            #     self.ui.mpQueueTable.removeRow(row)
            
            self.ui.mpQueueTable.clearContents()                                       # Add 9/1/26
            self.ui.mpQueueTable.setRowCount(0)                                     # Add 9/1/26
            
            self.box1_selected_state = False
            self.box2_selected_state = False
            self.box3_selected_state = False
            self.box4_selected_state = False
            self.box5_selected_state = False
            self.box6_selected_state = False
            self.box7_selected_state = False
            self.box8_selected_state = False
            
            update_robot_status("STANDBY")
            
            self.ui.mpSendConfirmBtn.setDisabled(True)
            
    
    #-----  Receive Page ------------
    @Slot()
    def open_password_dialog(self):       # self.ui.mpReceiveOkBtn.clicked.connect(self.open_password_dialog) 
        
        update_robot_status("LOAD_OUT")      # Change Status from WAIT_LOAD_OUT to LOAD_OUT
        
        self.passwd_dlg = PasswordDialog()
        self.passwd_dlg.passwdSignal.connect(self.check_passwd)   
        # self.passwdConfirmSignal.connect(self.passwd_dlg.passwd_confirm_slot)  
        # self.passwdStationSignal.connect(self.passwd_dlg.passwd_station_slot)     
        self.stationNameSignal.connect(self.passwd_dlg.station_name_slot)
         
        self.passwd_dlg.ui.mpBoxNumberlb.setText(str(self.current_queue_box)) 
        
        # for item in self.station_response["data"]:
        #     if (item['name'] == self.current_queue_target):
        #         passwd = item['password']    # get passwd from station data
        #         print(f"station passwd : {item['password']}")
                
        #         self.passwdStationSignal.emit(passwd)
        
                
        self.stationNameSignal.emit(self.current_queue_target)      
        self.passwd_dlg.isPasswdDialog2 = False
        self.is_rm_current_queue = True
        
        if self.passwd_dlg.exec_() == QDialog.Accepted:
            print("Dialog accepted!")
        else:
            print("Dialog rejected!")        
            
    def open_password_dialog2(self):       # self.ui.mpReceiveOkBtn.clicked.connect(self.open_password_dialog) 
        
        update_robot_status("LOAD_OUT")      # Change Status from WAIT_LOAD_OUT to LOAD_OUT
        
        self.passwd_dlg = PasswordDialog()
        self.passwd_dlg.passwdSignal.connect(self.check_passwd)   
        self.passwdConfirmSignal.connect(self.passwd_dlg.passwd_confirm_slot)        
        self.stationNameSignal.connect(self.passwd_dlg.station_name_slot)
        
        self.passwd_dlg.ui.mpBoxNumberlb.setText(str(self.BoxInt))  # use to show box number on password dialog 
        
    #   self.ui.mpTargetTextLb.setText(data['target'])
    #   self.ui.mpBoxTextLb.setText(str(data['boxNumber']))
    
        # print(self.TargetStr)
        self.stationNameSignal.emit(self.TargetStr)
        self.passwd_dlg.isPasswdDialog2 = True
        self.is_rm_current_queue = False
        
        if self.passwd_dlg.exec_() == QDialog.Accepted:
            print("Password Dialog 2 accepted!")
        else:
            print("Password Dialog 2 rejected!")
            
    # def open_box_status_dialog(self):       # self.ui.mpReceiveOkBtn.clicked.connect(self.open_password_dialog) 
        
    #     self.box_status_dlg = BoxStatusDialog()
        
    #     if self.box_status_dlg.exec_() == QDialog.Accepted:
    #         print("Dialog accepted!")
    #     else:
    #         print("Dialog rejected!")
        
    def remove_current_queue_handle(self):
        self.boxed_handle(False)      # Close Box
        if self.is_rm_current_queue:
            self.remove_current_queue()
        else:
            self.remove_selected_queue()
            index = self.ui.mpBoxNumberCb.currentIndex()
            if index >= 0:
                self.ui.mpBoxNumberCb.removeItem(index)
            # self.receive_page_init()
        
        
    def wait_load_out(self):
        print("In wait load out timeout function")
        if (self.current_status == "WAIT_LOAD_OUT"):
            print("Wait load out timeout. Remove current queue.")
            self.re_add_current_queue()
            self.passwd_dlg.close()
  
            
        # self.wait_load_out_flag = True
    
    def boxed_handle(self, state):
        if self.is_rm_current_queue:
            boxStr = str(self.current_queue_box)
        else:
            boxStr = str(self.BoxInt)
            
        for data in self.mapping_door_response['data']:
            if data['box'] == boxStr:
                if state:
                    print('Open door ', data['door'])  
                    if data['door'] == 'A':
                        self.ui.mpDoorA.setIcon(QIcon(u":/black/Icons/feather/unlock.png"))
                        self.ui.mpDoorA.setIconSize(QSize(50, 50))  
                        print("Open door #A:", call_remote("door_command", 1, 1))
                        # print("Open door #A:")
                        
                    elif data['door'] == 'B':
                        self.ui.mpDoorB.setIcon(QIcon(u":/black/Icons/feather/unlock.png"))
                        self.ui.mpDoorB.setIconSize(QSize(50, 50))  
                        print("Open door #B:", call_remote("door_command", 2, 1))
                        # print("Open door #B:")
                    
                    elif data['door'] == 'C':
                        self.ui.mpDoorC.setIcon(QIcon(u":/black/Icons/feather/unlock.png"))
                        self.ui.mpDoorC.setIconSize(QSize(50, 50))
                        print("Open door #C:", call_remote("door_command", 3, 1))
                        # print("Open door #C:")
                    
                    elif data['door'] == 'D':
                        self.ui.mpDoorD.setIcon(QIcon(u":/black/Icons/feather/unlock.png"))
                        self.ui.mpDoorD.setIconSize(QSize(50, 50))
                        print("Open door #D:", call_remote("door_command", 4, 1))
                        # print("Open door #D:")
                    
                    elif data['door'] == 'E':
                        self.ui.mpDoorE.setIcon(QIcon(u":/black/Icons/feather/unlock.png"))
                        self.ui.mpDoorE.setIconSize(QSize(50, 50))
                        print("Open door #E:", call_remote("door_command", 5, 1))
                        # print("Open door #E:")
                    
                    elif data['door'] == 'F':
                        self.ui.mpDoorF.setIcon(QIcon(u":/black/Icons/feather/unlock.png"))
                        self.ui.mpDoorF.setIconSize(QSize(50, 50)) 
                        print("Open door #F:", call_remote("door_command", 6, 1))
                        # print("Open door #F:")
                    
                    elif data['door'] == 'G':
                        self.ui.mpDoorG.setIcon(QIcon(u":/black/Icons/feather/unlock.png"))
                        self.ui.mpDoorG.setIconSize(QSize(50, 50))
                        print("Open door #G:", call_remote("door_command", 7, 1))
                        # print("Open door #G:")
                    
                    elif data['door'] == 'H':
                        self.ui.mpDoorH.setIcon(QIcon(u":/black/Icons/feather/unlock.png"))
                        self.ui.mpDoorH.setIconSize(QSize(50, 50))
                        print("Open door #H:", call_remote("door_command", 8, 1))
                        # print("Open door #H:")
                else:
                    print('Close door ', data['door']) 
                    if data['door'] == 'A':
                        self.ui.mpDoorA.setIcon(QIcon(u":/black/Icons/feather/lock.png"))
                        self.ui.mpDoorA.setIconSize(QSize(50, 50))  
                        print("Close door #A:", call_remote("door_command", 1, 0))
                        # print("Close door #A:")
                        
                    elif data['door'] == 'B':
                        self.ui.mpDoorB.setIcon(QIcon(u":/black/Icons/feather/lock.png"))
                        self.ui.mpDoorB.setIconSize(QSize(50, 50)) 
                        print("Close door #B:", call_remote("door_command", 2, 0))
                        # print("Close door #B:")
                        
                    elif data['door'] == 'C':
                        self.ui.mpDoorC.setIcon(QIcon(u":/black/Icons/feather/lock.png"))
                        self.ui.mpDoorC.setIconSize(QSize(50, 50))
                        print("Close door #C:", call_remote("door_command", 3, 0))
                        # print("Close door #C:")
                         
                    elif data['door'] == 'D':
                        self.ui.mpDoorD.setIcon(QIcon(u":/black/Icons/feather/lock.png"))
                        self.ui.mpDoorD.setIconSize(QSize(50, 50))
                        print("Close door #D:", call_remote("door_command", 4, 0))
                        # print("Close door #D:")
                        
                    elif data['door'] == 'E':
                        self.ui.mpDoorE.setIcon(QIcon(u":/black/Icons/feather/lock.png"))
                        self.ui.mpDoorE.setIconSize(QSize(50, 50))
                        print("Close door #E:", call_remote("door_command", 5, 0))
                        # print("Close door #E:")
                        
                    elif data['door'] == 'F':
                        self.ui.mpDoorF.setIcon(QIcon(u":/black/Icons/feather/lock.png"))
                        self.ui.mpDoorF.setIconSize(QSize(50, 50)) 
                        print("Close door #F:", call_remote("door_command", 6, 0))
                        # print("Close door #F:")
                    
                    elif data['door'] == 'G':
                        self.ui.mpDoorG.setIcon(QIcon(u":/black/Icons/feather/lock.png"))
                        self.ui.mpDoorG.setIconSize(QSize(50, 50))
                        print("Close door #G:", call_remote("door_command", 7, 0))
                        # print("Close door #G:")
                        
                    elif data['door'] == 'H':
                        self.ui.mpDoorH.setIcon(QIcon(u":/black/Icons/feather/lock.png"))
                        self.ui.mpDoorH.setIconSize(QSize(50, 50))
                        print("Close door #H:", call_remote("door_command", 8, 0))
                        # print("Close door #H:")
    
          
    @Slot(str)
    def check_passwd(self, receive_str):
        self.receive_passwd = receive_str
        # print(receive_str)
        self.boxed_handle(True)  #  Open Box                        
        QTimer.singleShot(self.door_open_timeout*1000, self.remove_current_queue_handle)   # wait 5 sec to remove queue
            
        # if self.receive_passwd == '':
        #     self.passwdConfirmSignal.emit(True)
        #     self.boxed_handle(True)  #  Open Box                        
        #     QTimer.singleShot(self.door_open_timeout*1000, self.remove_current_queue_handle)   # wait 5 sec to remove queue
            
        # else:
        #     self.passwdConfirmSignal.emit(False)
            
        #     self.boxed_handle(True)  #  Open Box                        
        #     QTimer.singleShot(self.door_open_timeout*1000, self.remove_current_queue_handle)   # wait 5 sec to remove queue
            
            # if passwd == self.receive_passwd:
            #     self.boxed_handle(True)  #  Open Box                        
            #     QTimer.singleShot(self.door_open_timeout*1000, self.remove_current_queue_handle)   # wait 5 sec to remove queue
            # else:
            #     # print('Add new queue with current queue')
            #     print('Show MessageBox: wrong passwd')
        
            # for item in self.station_response["data"]:
            #     if (item['name'] == self.current_queue_target):
            #         passwd = item['password']    # get passwd from station data
            #         print(f"Item passwd : {item['password']}   ---  Your enter passwd : { self.receive_passwd}")
                        
            #         # print(f"Current_queue_box : {self.current_queue_box}")
                        
            #         if passwd == self.receive_passwd:
            #             self.boxed_handle(True)  #  Open Box                        
            #             QTimer.singleShot(self.door_open_timeout*1000, self.remove_current_queue_handle)   # wait 5 sec to remove queue
            #         else:
            #             # print('Add new queue with current queue')
            #             print('Show MessageBox: wrong passwd')
        
        
    def remove_current_queue(self):
        if self.queue_list_response["data"] != []:
            rm_id = self.queue_list_response["data"][0]["_id"]  # get id to remove queue
            
            box_item = self.queue_list_response["data"][0]["boxNumber"]
            print(f"rm_id = {rm_id} , box_item = {box_item}")
                
            if box_item == 1:
                self.box1_use_state = False
            elif box_item == 2:
                self.box2_use_state = False
            elif box_item == 3:
                self.box3_use_state = False
            elif box_item == 4:
                self.box4_use_state = False
            elif box_item == 5:
                self.box5_use_state = False
            elif box_item == 6:
                self.box6_use_state = False
            elif box_item == 7:
                self.box7_use_state = False
            elif box_item == 8:
                self.box8_use_state = False 
                
            update_queue_status(rm_id, "completed")
                    
            remove_queue_by_id(rm_id)                # remove from queue list  
            print(f"remove queue id: {rm_id}")   
                 
        # update_robot_status("STANDBY")  
        QTimer.singleShot(1000, self.after_remove_current_queue)   # wait 1 sec to update status to STANDBY
        
    def remove_selected_queue(self):
        if self.queue_list_response["data"] != []:
            
            # rm_id = self.queue_list_response["data"][0]["_id"]  # get id to remove queue
            for queue in self.queue_list_response["data"]:
                if queue['target'] == self.TargetStr:
                    rm_id = queue["_id"]  # get id to remove queue          
            
            
            
            # box_item = self.queue_list_response["data"][0]["boxNumber"]
            box_item = self.BoxInt
            print(f"rm_id = {rm_id} , box_item = {box_item}")
                
            if box_item == 1:
                self.box1_use_state = False
            elif box_item == 2:
                self.box2_use_state = False
            elif box_item == 3:
                self.box3_use_state = False
            elif box_item == 4:
                self.box4_use_state = False
            elif box_item == 5:
                self.box5_use_state = False
            elif box_item == 6:
                self.box6_use_state = False
            elif box_item == 7:
                self.box7_use_state = False
            elif box_item == 8:
                self.box8_use_state = False 
                
            update_queue_status(rm_id, "completed")
                    
            remove_queue_by_id(rm_id)                # remove from queue list  
            print(f"remove queue id: {rm_id}")   
                 
        # update_robot_status("STANDBY")  
        QTimer.singleShot(1000, self.after_remove_current_queue)   # wait 1 sec to update status to STANDBY
    
    def after_remove_current_queue(self):
        update_robot_status("STANDBY")
        
    def send_cancel_in_move_clicked(self):   
        
        # update_robot_status("PAUSED")
        # QTimer.singleShot(3000, self.re_add_current_queue)   # wait 3 sec to re-add current queue
        self.open_skip_dialog()
        self.re_add_current_queue()
        
        
             
    def re_add_current_queue(self):
        
        # num_row = self.ui.mpQueueTable.rowCount()
        if self.current_status != "PAUSED":
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
        
        
    def receive_page_init(self):
                
        #     first_queue = self.queue_list_response["data"][0]
        #     self.ui.mpTargetTextLb.setText(first_queue['target'])
        #     self.ui.mpBoxTextLb.setText(str(first_queue['boxNumber']))
        self.ui.mpTargetTextLb.setText('')
        self.ui.mpBoxTextLb.setText('')
        
        self.ui.mpBoxNumberCb.clear()
        if self.queue_list_response["data"] != []:           
            for data in self.queue_list_response['data']:
                box = data['boxNumber'] 
                if(data['action'] == 'Delivery'):
                    self.ui.mpBoxNumberCb.addItem("   Box number"+str(box))
                
    
     
    # @Slot(int)
    # def handle_box_index_changed(self, index):
    #     print(f"Selected index changed to {index}, text = {self.ui.mpBoxNumberCb.itemText(index)}")
        
    #     if self.queue_list_response["data"] != []:           
    #         for data in self.queue_list_response['data']:
    #             if (data['boxNumber'] == index+1) and (data['action'] == 'Delivery'):
    #                 self.ui.mpTargetTextLb.setText(data['target'])
    #                 self.ui.mpBoxTextLb.setText(str(data['boxNumber']))
        
    @Slot(str)
    def handle_box_text_changed(self, text):
        # self.target = station.currentText().strip()
        print(f"Selected text changed to: {text}  : {text.strip().replace('Box number', '')}")  
        
        box = text.strip().replace('Box number', '')
        
        if not box.isdigit():
            # Skip empty/placeholder entries triggered while clearing the combo box
            self.ui.mpTargetTextLb.setText('')
            self.ui.mpBoxTextLb.setText('')
            return
        
        if self.queue_list_response["data"] != []:           
            for data in self.queue_list_response['data']:
                if (data['boxNumber'] == int(box)) and (data['action'] == 'Delivery'):
                    self.ui.mpTargetTextLb.setText(data['target'])
                    self.ui.mpBoxTextLb.setText(str(data['boxNumber']))
                    self.BoxInt = data['boxNumber'] 
                    self.TargetStr = data['target']
        

 
########################################################################
## EXECUTE APP
########################################################################
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ########################################################################
    ## 
    ########################################################################
    window = MainWindow()
    window.showMaximized()
    window.show()
    sys.exit(app.exec_())
########################################################################
## END===>
########################################################################
