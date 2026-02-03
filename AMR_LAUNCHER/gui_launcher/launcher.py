import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QPushButton, QMessageBox, QLabel, QSpacerItem, QSizePolicy, QProgressDialog, QInputDialog, QLineEdit, QDialog)
from PySide6.QtCore import QProcess, Qt, QTimer, Signal, QObject
from PySide6.QtGui import QMouseEvent
import time
import subprocess
import shutil

from PySide6.QtGui import QPixmap

class ClickableLabel(QLabel):
    clicked = Signal()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Password Required")
        self.setModal(True)
        self.setMinimumSize(400, 500)

        layout = QVBoxLayout(self)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("font-size: 32px; height: 50px;")
        layout.addWidget(self.password_input)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        
        buttons = [
            ('7', 0, 0), ('8', 0, 1), ('9', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('1', 2, 0), ('2', 2, 1), ('3', 2, 2),
            ('0', 3, 1)
        ]

        for text, r, c in buttons:
            btn = QPushButton(text)
            btn.setFixedSize(80, 80)
            btn.setFocusPolicy(Qt.NoFocus) # Don't steal focus
            btn.setStyleSheet("font-size: 24px; font-weight: bold;")
            # Fix: Accept the 'checked' boolean from clicked signal so it doesn't overwrite 't'
            btn.clicked.connect(lambda checked, t=text: self.password_input.insert(t))
            grid_layout.addWidget(btn, r, c)

        # Clear and Backspace
        clear_btn = QPushButton("C")
        clear_btn.setFixedSize(80, 80)
        clear_btn.setFocusPolicy(Qt.NoFocus)
        clear_btn.setStyleSheet("font-size: 24px; font-weight: bold; background-color: #ffcccc;")
        clear_btn.clicked.connect(self.password_input.clear)
        grid_layout.addWidget(clear_btn, 3, 0)
        
        back_btn = QPushButton("<-")
        back_btn.setFixedSize(80, 80)
        back_btn.setFocusPolicy(Qt.NoFocus)
        back_btn.setStyleSheet("font-size: 24px; font-weight: bold; background-color: #ffe0b3;")
        back_btn.clicked.connect(self.backspace)
        grid_layout.addWidget(back_btn, 3, 2)
        
        layout.addLayout(grid_layout)

        # Action Buttons
        action_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet("font-size: 24px; padding: 10px; background-color: #C1FFC1;")
        ok_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("font-size: 24px; padding: 10px; background-color: #ffcccc;")
        cancel_btn.clicked.connect(self.reject)

        action_layout.addWidget(cancel_btn)
        action_layout.addWidget(ok_btn)
        layout.addLayout(action_layout)

    def backspace(self):
        text = self.password_input.text()
        self.password_input.setText(text[:-1])

    def get_password(self):
        return self.password_input.text()

class LauncherApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AMR Control Panel")
        self.setWindowFlags(Qt.FramelessWindowHint) # Remove title bar
        self.resize(1280, 800) # Larger default size for modern screens

        # Global stylesheet for Dialogs (QMessageBox)
        self.setStyleSheet("""
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
        self.layout.setSpacing(20) # Increase spacing

        # Top Header (Close Button)
        top_layout = QHBoxLayout()
        top_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
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
            pixmap = pixmap.scaledToHeight(400, Qt.SmoothTransformation) 
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
            ("Navigation", "navigation.sh", False, False),
            ("Create Map", "create_map.sh", False, False),
            ("Save Map", "save_map.sh", False, False),
            ("Edit Map", "edit_map.sh", False, False),
            ("Dock", "dock.sh", True, True),
            ("Undock", "undock.sh", True, True)
        ]

        self.script_buttons = []
        self.main_process = None
        self.aux_process = None
        self.progress_dialog = None
        self.progress_timer = None
        self.current_main_script = None

        # Create Standard Buttons
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(20)

        # Keep track of buttons to show/hide
        self.dev_buttons = []

        visible_count = 0
        for label, script, is_dev, run_terminal in self.buttons_config:
            btn = QPushButton(label)
            btn.setMinimumHeight(100) # Taller buttons for touch
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) # Expand to fill grid cells
            
            style = "font-size: 48px; font-weight: bold;border-radius: 15px; border: 2px solid #555555;  "
            if label == "Navigation":
                style += " background-color: #C1FFC1; " # Pastel Green with border
            elif is_dev:
                style += " background-color: #E0E0E0; color: #555; border-radius: 15px; border: 2px solid #555555;" # Grey for dev buttons
            
            btn.setStyleSheet(style) # Larger text and color
            btn.clicked.connect(lambda checked=False, s=script, t=run_terminal: self.run_script(s, run_in_terminal=t))
            
            self.script_buttons.append(btn)

            if is_dev:
                self.dev_buttons.append(btn)
                btn.hide()
            else:
                 # Layout for visible buttons
                row = visible_count // 2
                col = visible_count % 2
                self.grid_layout.addWidget(btn, row, col)
                visible_count += 1
        
        self.layout.addLayout(self.grid_layout)

        # Spacer to push Shutdown button to bottom
        self.layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # System Control Buttons (Reboot / Shutdown)
        system_controls_layout = QHBoxLayout()
        system_controls_layout.setSpacing(40)
        system_controls_layout.setAlignment(Qt.AlignCenter)

        # Reboot Button
        self.reboot_btn = QPushButton("Reboot")
        self.reboot_btn.setFixedSize(200, 60)
        self.reboot_btn.setStyleSheet("background-color: #ffe0b3; color: #e65100; font-size: 30px; font-weight: bold; border-radius: 10px;")
        self.reboot_btn.clicked.connect(lambda: self.run_script("reboot.sh", action_type="reboot"))
        system_controls_layout.addWidget(self.reboot_btn)

        # Shutdown Button
        self.shutdown_btn = QPushButton("Shutdown")
        self.shutdown_btn.setFixedSize(200, 60) 
        self.shutdown_btn.setStyleSheet("background-color: #ffcccc; color: red; font-size: 30px; font-weight: bold; border-radius: 10px;")
        self.shutdown_btn.clicked.connect(lambda: self.run_script("shutdown.sh", action_type="shutdown"))
        system_controls_layout.addWidget(self.shutdown_btn)
        
        self.layout.addLayout(system_controls_layout)

        # Power Button Inhibition
        self.power_inhibit_process = None
        # self.start_power_inhibit()

    def start_power_inhibit(self):
        """Starts a background process to inhibit the power button."""
        
        # 1. Systemd Inhibit (Background Process)
        if not (self.power_inhibit_process and self.power_inhibit_process.state() == QProcess.Running):
            self.power_inhibit_process = QProcess(self)
            # Inhibit everything possible
            program = "systemd-inhibit"
            arguments = [
                "--what=shutdown:sleep:idle:handle-power-key:handle-suspend-key:handle-hibernate-key:handle-lid-switch",
                "--who=AMR Launcher",
                "--why=Kiosk Mode",
                "--mode=block",
                "sleep",
                "infinity"
            ]
            self.power_inhibit_process.start(program, arguments)
            
        # 2. Xmodmap Inhibit (X11 Key Unmapping)
        self.original_power_keymap = None
        if shutil.which("xmodmap"):
            try:
                # Find keycode for XF86PowerOff
                # Try getting the current mapping
                result = subprocess.run(["xmodmap", "-pke"], capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.splitlines():
                        if "XF86PowerOff" in line:
                            # format: keycode 124 = XF86PowerOff ...
                            parts = line.split('=')
                            if len(parts) >= 2 and "keycode" in parts[0]:
                                keycode = parts[0].strip().split()[1]
                                self.original_power_keymap = line.strip()
                                # Disable it by mapping to NoSymbol (or VoidSymbol)
                                subprocess.run(["xmodmap", "-e", f"keycode {keycode} = NoSymbol"])
                                break
            except Exception as e:
                print(f"Xmodmap inhibit failed: {e}")
    
    def stop_power_inhibit(self):
        """Stops the inhibition process."""
        # 1. Stop Systemd Inhibit
        if self.power_inhibit_process:
            self.power_inhibit_process.terminate()
            self.power_inhibit_process.waitForFinished(1000)
            self.power_inhibit_process = None
            
        # 2. Restore Xmodmap
        if self.original_power_keymap:
            try:
                 subprocess.run(["xmodmap", "-e", self.original_power_keymap])
            except Exception as e:
                 print(f"Xmodmap restore failed: {e}")

    def closeEvent(self, event):
        """Override close event to ensure inhibition is stopped."""
        self.stop_power_inhibit()
        super().closeEvent(event)

    def check_secret_pattern(self):
        if self.dev_mode_enabled:
            return

        now = time.time()
        self.dev_click_times.append(now)

        # Keep only clicks within last 3 seconds
        self.dev_click_times = [t for t in self.dev_click_times if now - t <= 3.0]

        if len(self.dev_click_times) >= 4:
            if self.verify_password("4321"):
                self.enable_developer_mode()
            self.dev_click_times = [] # Reset

    def enable_developer_mode(self):
        self.dev_mode_enabled = True
        QMessageBox.information(self, "Developer Mode", "Developer Mode Enabled!")
        
        # Add dev buttons to the grid
        # Currently we have 4 normal buttons (0,0), (0,1), (1,0), (1,1)
        # So next starts at row 2
        
        # Calculate current visible count to know where to start adding
        # We know we have 4 standard buttons
        current_count = 4 
        
        for btn in self.dev_buttons:
            btn.show()
            row = current_count // 2
            col = current_count % 2
            self.grid_layout.addWidget(btn, row, col)
            current_count += 1

    def verify_password(self, expected_password="1234"):
        dialog = PasswordDialog(self)
        if dialog.exec() == QDialog.Accepted:
            password = dialog.get_password()
            if password == expected_password:
                return True
            else:
                QMessageBox.warning(self, "Access Denied", "Incorrect Password")
        return False

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

        self.main_process = None
        self.current_main_script = None
        self.update_ui_state()
        # QMessageBox.information(self, "Finished", "Script execution completed.")

    def on_aux_finished(self):
        self.aux_process = None
        # No UI update needed strictly, but maybe re-evaluate?
        # Ideally we don't disable things while aux runs, so nothing to re-enable
        QMessageBox.information(self, "Finished", "Save Map completed.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LauncherApp()
    window.setGeometry(app.primaryScreen().availableGeometry())
    window.show()
    sys.exit(app.exec())
