import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QPushButton, QMessageBox, QLabel, QSpacerItem, QSizePolicy, QProgressDialog, QDialog)
from PySide6.QtCore import QProcess, Qt, QTimer
from PySide6.QtGui import QPixmap
import time
import subprocess
import shutil
import signal
import socket

# Custom Imports
from custom_widgets import ClickableLabel, IntroWindow, LogWindow
from dialogs import PasswordDialog, DevMenuDialog, BringupCheckDialog, NavigationConfirmDialog

DELIVERY_ROBOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'amrROS2_ws/src/delivery_robot_main_controller'))
sys.path.insert(0, DELIVERY_ROBOT_PATH)

# Now you can import normally
from delivery_robot_main_controller.api_client import *

NET_INTERFACE = "wlxe84e06b0d3e0"

class LauncherApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AMR Control Panel")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnBottomHint) # Remove title bar
        self.resize(1280, 800) # Larger default size for modern screens

        # Global stylesheet for Dialogs (QMessageBox)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F9F8F8;
            }
            QMessageBox {
                font-size: 24px;
            }
            QMessageBox QLabel {
                font-size: 24px;
                min-height: 50px;
            }
            QMessageBox QPushButton {
                min-width: 150px;
                min-height: 60px;
                font-size: 20px;
            }
        """)

        # Central Widget and Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        self.layout.setSpacing(10) # Reduced spacing
        self.layout.setContentsMargins(10, 5, 10, 10) # Reduce top margin

        # Top Header (Close Button)
        top_layout = QHBoxLayout()
        
        # Spacer to push close button to right
        top_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Reduce spacer height preference to minimize vertical impact
        top_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        self.close_btn = QPushButton("X")
        self.close_btn.setFixedSize(50, 50)
        self.close_btn.setStyleSheet("background-color: red; color: white; font-size: 24px; font-weight: bold; border-radius: 25px;")
        self.close_btn.clicked.connect(self.close_app)
        top_layout.addWidget(self.close_btn)
        
        self.layout.addLayout(top_layout)

        # Developer Mode State
        self.dev_click_times = []
        self.dev_mode_enabled = False

        # Logo
        logo_label = ClickableLabel()
        logo_label.clicked.connect(self.check_secret_pattern)

        logo_label.setAlignment(Qt.AlignCenter)
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Scale if too large, e.g. height 200
            pixmap = pixmap.scaledToHeight(350, Qt.SmoothTransformation) 
            logo_label.setPixmap(pixmap)
        self.layout.addWidget(logo_label)

        # Title
        title_label = QLabel("AMR Mode")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 36px; font-weight: bold; margin-bottom: 20px;")
        self.layout.addWidget(title_label)

        # Script Buttons Configuration
        # (Label, Script Filename, IsDeveloper, RunInTerminal)
        self.buttons_config = [
            ("Navigate", "navigation.sh", False, False),
            ("Create Map", "create_map.sh", False, False),
            ("Save Map", "save_map.sh", False, False),
            ("Edit Map", "edit_map.sh", False, False),
            ("Dock", "dock.sh", True, True),
            ("Undock", "undock.sh", True, True)
        ]

        self.script_buttons = []
        self.main_process = None
        self.aux_process = None
        self.teleop_bringup_window = None # Changed from process to window logic
        self.progress_dialog = None
        self.progress_timer = None
        self.current_main_script = None

        # Create Standard Buttons
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(20)

        self.script_buttons = []

        # --- Left Column (Col 0) ---
        # Navigation Button
        nav_btn = QPushButton("Navigate")
        nav_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Pastel Green with border
        nav_btn.setStyleSheet("font-size: 96px; font-weight: bold; border-radius: 15px; border: 2px solid #555555; background-color: #C1FFC1;")
        nav_btn.clicked.connect(self.start_navigation_flow)
        self.script_buttons.append(nav_btn)
        
        # Add to grid: Row 0, Col 0, RowSpan 4, ColSpan 1
        self.grid_layout.addWidget(nav_btn, 0, 0, 4, 1)

        # --- Right Column (Col 1) ---
        # "Map Tools" Label (Row 0)
        map_tools_label = QLabel("Map Tools")
        map_tools_label.setAlignment(Qt.AlignCenter)
        map_tools_label.setStyleSheet("font-size: 30px; font-weight: bold; color: #333333;")
        self.grid_layout.addWidget(map_tools_label, 0, 1)

        # Map Buttons (Rows 1-3)
        map_buttons_config = [
            ("Create Map", "create_map.sh", 1, "protected_script"),
            ("Save Map", "save_map.sh", 2, "protected_script"),
            ("Edit Map", "edit_map.sh", 3, "protected_script")
        ]

        for label, script, row, action_type in map_buttons_config:
            btn = QPushButton(label)
            btn.setMinimumHeight(100)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.setStyleSheet("font-size: 40px; font-weight: bold; border-radius: 15px; border: 2px solid #555555;")
            btn.clicked.connect(lambda checked=False, s=script, a=action_type: self.run_script(s, action_type=a, run_in_terminal=False))
            self.script_buttons.append(btn)
            self.grid_layout.addWidget(btn, row, 1)

        # --- Dev Buttons logic moved to DevMenuDialog ---
        
        self.layout.addLayout(self.grid_layout)

        # Spacer to push Shutdown button to bottom
        self.layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # System Control Buttons (Reboot / Shutdown)
        system_controls_layout = QHBoxLayout()
        # system_controls_layout.setSpacing(40) 

        # NECTEC Logo (Right)
        nectec_logo_label = QLabel()
        nectec_logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "Logo_NECTEC.jpg")
        logo_pixmap = None
        if os.path.exists(nectec_logo_path):
            logo_pixmap = QPixmap(nectec_logo_path)
            # Scale to height 100
            logo_pixmap = logo_pixmap.scaledToHeight(150, Qt.SmoothTransformation)
            nectec_logo_label.setPixmap(logo_pixmap)
            nectec_logo_label.setContentsMargins(0, 0, 20, 20) # Left, Top, Right, Bottom

        # IP Address Label (Left)
        ip_address = self.get_ip_address()
        
        self.ip_label = QLabel(f"IP: {ip_address}")
        # Professional Style: Dark Grey, Bold, with background to ensure visibility
        self.ip_label.setStyleSheet("font-size: 30px; font-weight: bold; color: black; padding-left: 20px; background-color: #FFFFFF; border: 1px solid #CCCCCC; border-radius: 10px;")
        self.ip_label.setAlignment(Qt.AlignCenter)
        # Ensure it has sufficient height/width to not be collapsed
        self.ip_label.setMinimumHeight(60)
        self.ip_label.setMinimumWidth(250) 

        system_controls_layout.addWidget(self.ip_label)

        # Disk Drive Label
        current_disk = self.get_disk_usage()
        self.disk_label = QLabel(current_disk)
        self.disk_label.setStyleSheet("font-size: 30px; font-weight: bold; color: black; padding-left: 20px; background-color: #FFFFFF; border: 1px solid #CCCCCC; border-radius: 10px;")
        self.disk_label.setAlignment(Qt.AlignCenter)
        self.disk_label.setMinimumHeight(60)
        self.disk_label.setMinimumWidth(250)
        
        system_controls_layout.addWidget(self.disk_label)

        system_controls_layout.addStretch()

        # Container for Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(40)

        # Clear Cache Button
        self.clear_cache_btn = QPushButton("Clear Cache/Log")
        self.clear_cache_btn.setFixedSize(250, 60)
        self.clear_cache_btn.setStyleSheet("background-color: #ffb3b3; color: #b30000; font-size: 24px; font-weight: bold; border-radius: 10px;")
        self.clear_cache_btn.clicked.connect(lambda: self.run_script("clear_cache_logs.sh", action_type="protected_script"))
        buttons_layout.addWidget(self.clear_cache_btn)

        # Reboot Button
        self.reboot_btn = QPushButton("Reboot")
        self.reboot_btn.setFixedSize(200, 60)
        self.reboot_btn.setStyleSheet("background-color: #ffe0b3; color: #e65100; font-size: 30px; font-weight: bold; border-radius: 10px;")
        self.reboot_btn.clicked.connect(lambda: self.run_script("reboot.sh", action_type="reboot"))
        buttons_layout.addWidget(self.reboot_btn)

        # Shutdown Button
        self.shutdown_btn = QPushButton("Shutdown")
        self.shutdown_btn.setFixedSize(200, 60) 
        self.shutdown_btn.setStyleSheet("background-color: #ffcccc; color: red; font-size: 30px; font-weight: bold; border-radius: 10px;")
        self.shutdown_btn.clicked.connect(lambda: self.run_script("shutdown.sh", action_type="shutdown"))
        buttons_layout.addWidget(self.shutdown_btn)
        
        system_controls_layout.addLayout(buttons_layout)
        system_controls_layout.addStretch()

        # Add Logo (Right)
        system_controls_layout.addWidget(nectec_logo_label)

        self.layout.addLayout(system_controls_layout)

        # Power Button Inhibition
        # self.power_inhibit_process = None
        # self.start_power_inhibit()
        self.system_params = get_system_parameters()
        # System Parameter Update Timer (Every 10 seconds)
        self.system_params_timer = QTimer(self)
        self.system_params_timer.timeout.connect(self.update_system_parameters)
        self.system_params_timer.start(10000) # 10000 ms = 10 s

    def get_ip_address(self):
        interface = NET_INTERFACE
        try:
            # Use ip command to get address for specific interface
            # ip -4 addr show wlxe84e06b0d3de
            result = subprocess.check_output(["ip", "-4", "addr", "show", interface], stderr=subprocess.DEVNULL, text=True)
            
            for line in result.split('\n'):
                line = line.strip()
                if line.startswith("inet "):
                    # Example: inet 192.168.1.105/24 ...
                    parts = line.split()
                    if len(parts) >= 2:
                        ip_with_cidr = parts[1]
                        return ip_with_cidr.split('/')[0]
            
            return "No Network"
        except Exception:
            return "No Network"

    def get_disk_usage(self):
        try:
            total, used, free = shutil.disk_usage('/')
            # Convert to GB
            total_gb = total // (2**30)
            free_gb = free // (2**30)
            return f"Disk: {free_gb}GB / {total_gb}GB Free"
        except Exception:
            return "Disk: Unknown"

    def update_system_parameters(self):
        try:
            self.system_params = get_system_parameters()
            # Update IP periodically in case network changes
            current_ip = self.get_ip_address()
            self.ip_label.setText(f"IP: {current_ip}")
            
            # Update disk periodically
            self.disk_label.setText(self.get_disk_usage())
        except Exception as e:
            print(f"Failed to get system parameters: {e}")

    def check_secret_pattern(self):
        if self.dev_mode_enabled:
            return

        now = time.time()
        self.dev_click_times.append(now)

        # Keep only clicks within last 3 seconds
        self.dev_click_times = [t for t in self.dev_click_times if now - t <= 3.0]

        if len(self.dev_click_times) >= 4:
            if self.verify_password("12120"):
                self.enable_developer_mode()
            self.dev_click_times = [] # Reset

    def enable_developer_mode(self):
        # Open the Developer Menu Dialog
        dialog = DevMenuDialog(self)
        dialog.exec()
        # After dialog closes, we are technically "done" with this interaction
        # We don't persist "dev mode" state on the main window anymore
        self.dev_mode_enabled = False

    def verify_password(self, expected_password=None):
        # Helper to get admin password from system params
        real_password = "1234" # Default fallback
        
        if expected_password:
             real_password = expected_password
        elif hasattr(self, 'system_params') and self.system_params:
             try:
                 # system_params["data"][0]["adminPassword"]
                 real_password = str(self.system_params["data"][0]["adminPassword"])
                 # print(f"Real Password: {real_password}")
             except (KeyError, IndexError, TypeError):
                 # Fallback if structure is unexpected
                 pass

        dialog = PasswordDialog(self)
        if dialog.exec() == QDialog.Accepted:
            password = dialog.get_password()
            if password == real_password:
                return True
            else:
                QMessageBox.warning(self, "Access Denied", "Incorrect Password")
        if dialog.exec() == QDialog.Accepted:
            password = dialog.get_password()
            if password == real_password:
                return True
            else:
                QMessageBox.warning(self, "Access Denied", "Incorrect Password")
        return False

    def start_navigation_flow(self):
        # Show confirmation dialog
        dialog = NavigationConfirmDialog(self)
        if dialog.exec() == QDialog.Accepted:
            # User confirmed, start navigation
            self.run_script("navigation.sh", run_in_terminal=False)

    def close_app(self):
        if self.verify_password():
            self.close()

    def run_script(self, script_name, action_type="script", run_in_terminal=False):
        if action_type == "shutdown":
            if not self.verify_password():
                return
            reply = QMessageBox.question(self, 'Confirm Shutdown', 
                                         "Are you sure you want to shut down?", 
                                         QMessageBox.Yes | QMessageBox.No, 
                                         QMessageBox.No)
            if reply == QMessageBox.No:
                return
        elif action_type == "reboot":
            if not self.verify_password():
                return
            reply = QMessageBox.question(self, 'Confirm Reboot', 
                                         "Are you sure you want to reboot?", 
                                         QMessageBox.Yes | QMessageBox.No, 
                                         QMessageBox.No)
            if reply == QMessageBox.No:
                return
        elif action_type == "protected_script":
            if not self.verify_password():
                return

        # Determine script path
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts", script_name)
        
        if not os.path.exists(script_path):
            QMessageBox.critical(self, "Error", f"Script not found: {script_path}")
            return

        is_critical_action = action_type in ["shutdown", "reboot"]
        is_auxiliary = script_name == "save_map.sh"

        # Check if already running
        if is_auxiliary:
            if self.aux_process and self.aux_process.state() == QProcess.Running:
                return # Already saving
        elif not is_critical_action:
             # Main process check
            if self.main_process and self.main_process.state() == QProcess.Running:
                return # Already running a main process

        # Update UI Stae
        if not is_critical_action:
            if not is_auxiliary:
                self.current_main_script = script_name
            self.update_ui_state()

        # Create and start process
        proc = QProcess(self)
        
        if is_critical_action:
             # Just start, no tracking needed for reboot/shutdown as they kill app
             pass
        elif is_auxiliary:
            self.aux_process = proc
            # For aux process, we don't necessarily update UI state on finish unless we had disabled something specific
            proc.finished.connect(self.on_aux_finished)
        else:
            self.main_process = proc
            proc.finished.connect(self.on_main_finished)
            
            if script_name == "navigation.sh":
                self.show_progress_dialog("Launching Navigation...", 15)
            elif script_name == "create_map.sh":
                self.show_progress_dialog("Launching Mapping...", 5)
        
        if run_in_terminal:
             # Use gnome-terminal --wait to block until the window (child) is closed
             # removed exec bash so it closes after script finishes
             proc.start("gnome-terminal", ["--wait", "--", "/bin/bash", "-c", f"{script_path}"])
        else:
             proc.start("/bin/bash", [script_path])
    def show_progress_dialog(self, title, duration_sec):
        # We will use 100 steps for the progress bar
        steps = 100
        interval = int((duration_sec * 1000) / steps)

        self.progress_dialog = QProgressDialog(title, None, 0, steps, self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setAutoClose(False)
        self.progress_dialog.setAutoReset(False)
        self.progress_dialog.setMinimumDuration(0) # Show immediately
        self.progress_dialog.setValue(0)
        self.progress_dialog.setCancelButton(None) # Disable cancel button
        
        # Enlarge dialog
        self.progress_dialog.setMinimumSize(500, 200)
        self.progress_dialog.setStyleSheet("""
            QProgressDialog {
                font-size: 24px;
            }
            QLabel {
                font-size: 24px; 
                font-weight: bold;
                min-height: 50px;
            }
            QProgressBar {
                min-height: 40px;
            }
        """)
        
        self.progress_dialog.show()

        self.progress_value = 0
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self.update_progress)
        self.progress_timer.start(interval)

    def update_progress(self):
        if self.progress_dialog:
            self.progress_value += 1
            self.progress_dialog.setValue(self.progress_value)
            
            if self.progress_value >= 100:
                self.progress_timer.stop()
                self.progress_dialog.setLabelText("Finalizing...")
                self.progress_dialog.close()
                self.progress_dialog = None
                self.progress_timer = None

    def update_ui_state(self):
        # We rely on current_main_script being set in run_script BEFORE the process actually starts
        # checking self.main_process.state() here is too late/early in some lifecycle events
        main_running = self.current_main_script is not None
        
        for btn in self.script_buttons:
            text = btn.text()
            
            if not main_running:
                btn.setEnabled(True)
            else:
                # Main process is running
                if self.current_main_script == "create_map.sh" and text == "Save Map":
                     # Special case: Enable Save Map if Create Map is running
                    btn.setEnabled(True)
                else:
                    btn.setEnabled(False)

    def on_main_finished(self):
        # Stop timer if running (for nav)
        if self.progress_timer and self.progress_timer.isActive():
            self.progress_timer.stop()
        
        # Close progress dialog if open
        if self.progress_dialog:
            self.progress_dialog.setValue(100) # Ensure full bar
            self.progress_dialog.close()
            self.progress_dialog = None
            self.progress_timer = None

        # Check if we need to show "Clearing the process" dialog
        if self.current_main_script in ["navigation.sh", "create_map.sh"]:
             # Show indeterminate progress dialog
             self.progress_dialog = QProgressDialog("Clearing the process please wait...", None, 0, 0, self)
             self.progress_dialog.setWindowModality(Qt.WindowModal)
             self.progress_dialog.setCancelButton(None)
             self.progress_dialog.setMinimumDuration(0) # Force show immediately
             self.progress_dialog.setStyleSheet("""
                QProgressDialog { font-size: 24px; }
                QLabel { font-size: 24px; font-weight: bold; min-height: 50px; }
             """)
             self.progress_dialog.setMinimumSize(500, 150)
             self.progress_dialog.show()
             
             # Delay final cleanup
             QTimer.singleShot(2000, self.finalize_main_process)
        else:
             self.finalize_main_process()

    def finalize_main_process(self):
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None

        self.main_process = None
        self.current_main_script = None
        
        # Check if we need to kill bringup (Teleop finished)
        if self.teleop_bringup_window:
            print("Terminating Bringup Log Window...")
            self.teleop_bringup_window.kill_process()
            self.teleop_bringup_window.close()
            self.teleop_bringup_window = None

        self.update_ui_state()
        # QMessageBox.information(self, "Finished", "Script execution completed.")

    def start_teleop_session(self):
        # Check if something is already running
        if self.main_process and self.main_process.state() == QProcess.Running:
            QMessageBox.warning(self, "Busy", "Another process is running. Stop it first.")
            return

        # 1. Start Bringup (Background, managed via LogWindow)
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts", "bringup_robot.sh")
        if not os.path.exists(script_path):
             QMessageBox.critical(self, "Error", f"Script not found: {script_path}")
             return

        self.teleop_bringup_window = LogWindow("Bringup Robot Log")
        self.teleop_bringup_window.show()
        # Run bash directly since script uses exec and sets env
        self.teleop_bringup_window.start_process("/bin/bash", [script_path])
        
        # 2. Start Teleop App (As Main Process via run_script)
        # Using run_in_terminal=True for teleop is still fine as user requested it for errors
        self.run_script("teleop.sh", run_in_terminal=True)

    def on_aux_finished(self):
        self.aux_process = None
        # No UI update needed strictly, but maybe re-evaluate?
        # Ideally we don't disable things while aux runs, so nothing to re-enable
        QMessageBox.information(self, "Finished", "Save Map completed.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    print("Launcher started")
    
    # Export current python executable for scripts to use
    os.environ["LAUNCHER_PYTHON"] = sys.executable
    intro_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "Init_vid.gif")
    
    # We instantiate window ONLY after intro or if no intro, 
    # BUT constructing LauncherApp might take time (get_system_parameters).
    # To hide that loading time, we could construct it while Intro plays.
    # However, keeping it simple:
    
    # Pre-construct window to ensure it's ready? 
    # Or just construct it.
    
    window = LauncherApp()
    window.setGeometry(app.primaryScreen().availableGeometry())

    # if os.path.exists(intro_path):
    #     intro = IntroWindow(intro_path)
    #     intro.finished.connect(window.show)
    #     intro.show()
    # else:
    #     window.show()
    window.show()

    sys.exit(app.exec())
