import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QMessageBox, QLabel, QSpacerItem, QSizePolicy, QProgressDialog)
from PySide6.QtCore import QProcess, Qt, QTimer

from PySide6.QtGui import QPixmap

class LauncherApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AMR Control Panel")
        self.resize(1280, 800) # Larger default size for modern screens

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
        self.close_btn.clicked.connect(self.close)
        top_layout.addWidget(self.close_btn)
        
        self.layout.addLayout(top_layout)

        # Logo
        logo_label = QLabel()

        logo_label.setAlignment(Qt.AlignCenter)
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Scale if too large, e.g. height 200
            pixmap = pixmap.scaledToHeight(250, Qt.SmoothTransformation) 
            logo_label.setPixmap(pixmap)
        self.layout.addWidget(logo_label)

        # Title
        title_label = QLabel("AMR Mode")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 36px; font-weight: bold; margin-bottom: 20px;")
        self.layout.addWidget(title_label)

        # Script Buttons Configuration
        # (Label, Script Filename)
        self.buttons_config = [
            ("Navigation", "navigation.sh"),
            ("Create Map", "create_map.sh"),
            ("Save Map", "save_map.sh"),
            ("Edit Map", "edit_map.sh"),
            # ("Sensor Check", "sensor_check.sh")
        ]

        self.script_buttons = []
        self.main_process = None
        self.aux_process = None
        self.progress_dialog = None
        self.progress_timer = None
        self.current_main_script = None

        # Create Standard Buttons
        for label, script in self.buttons_config:
            btn = QPushButton(label)
            btn.setMinimumHeight(100) # Taller buttons for touch
            style = "font-size: 48px; font-weight: bold;"
            if label == "Navigation":
                style += " background-color: #C1FFC1;" # Pastel Green
            btn.setStyleSheet(style) # Larger text and color
            btn.clicked.connect(lambda checked=False, s=script: self.run_script(s))
            self.layout.addWidget(btn)
            self.script_buttons.append(btn)

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

    def run_script(self, script_name, action_type="script"):
        if action_type == "shutdown":
            reply = QMessageBox.question(self, 'Confirm Shutdown', 
                                         "Are you sure you want to shut down?", 
                                         QMessageBox.Yes | QMessageBox.No, 
                                         QMessageBox.No)
            if reply == QMessageBox.No:
                return
        elif action_type == "reboot":
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
                self.show_progress_dialog("Launching Navigation...", 10)
            elif script_name == "create_map.sh":
                self.show_progress_dialog("Launching Mapping...", 3)
        
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
        QMessageBox.information(self, "Finished", "Script execution completed.")

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
