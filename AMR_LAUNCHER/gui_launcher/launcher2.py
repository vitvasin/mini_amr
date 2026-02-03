import sys
import os
import time
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QFrame, QSpacerItem, QSizePolicy, 
                               QGraphicsDropShadowEffect, QMessageBox, QProgressDialog)
from PySide6.QtCore import Qt, QSize, QProcess, QTimer, Signal
from PySide6.QtGui import QColor, QIcon, QFont, QPixmap, QMouseEvent

# --- Custom Widgets ---

class ClickableLabel(QLabel):
    clicked = Signal()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

class ModernButton(QPushButton):
    def __init__(self, text, icon_name=None, bg_color="#333", text_color="white", is_primary=False):
        super().__init__(text)
        self.setFixedHeight(120) # STANDARD BUTTON HEIGHT (Increased from 80)
        
        font = QFont()
        font.setPixelSize(28) # STANDARD FONT SIZE (Increased from 20)
        font.setBold(True)
        self.setFont(font)
        
        self.default_style = f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border-radius: 15px;
                padding: 10px;
                border: none;
                text-align: left;
                padding-left: 30px;
            }}
            QPushButton:hover {{
                background-color: {self.adjust_color(bg_color, 20)};
            }}
            QPushButton:pressed {{
                background-color: {self.adjust_color(bg_color, -20)};
            }}
        """
        if is_primary:
            self.default_style = f"""
                QPushButton {{
                    background-color: {bg_color};
                    color: {text_color};
                    border-radius: 25px;
                    font-size: 56px; /* PRIMARY FONT SIZE (Increased from 32) */
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: {self.adjust_color(bg_color, 10)};
                }}
            """
            self.setFixedHeight(240) # PRIMARY BUTTON HEIGHT (Increased from 120)

        self.setStyleSheet(self.default_style)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

    def adjust_color(self, hex_color, factor):
        # vary color by factor
        # This is a simple helper, normally we'd use QColor methods but for string replacement...
        return hex_color # simplified for now, usually hover handles itself with QSS logic or lighter hex

class CardWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #e0e0e0;
                border-radius: 20px;
            }
        """)
        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

# --- Main App ---

class LauncherApp2(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AMR Control Panel 2.0")
        self.resize(1024, 600)
        
        # Dark Theme Background
        self.setStyleSheet("background-color: #1e1e1e; font-family: 'Segoe UI', sans-serif;")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(20)

        # -- Top Bar --
        self.setup_top_bar()

        # -- Content Area --
        content_layout = QHBoxLayout()
        content_layout.setSpacing(40)
        self.main_layout.addLayout(content_layout)

        # Left Side (Navigation)
        self.setup_left_panel(content_layout)

        # Right Side (Mapping Tools)
        self.setup_right_panel(content_layout)

        # -- Bottom Bar (Footer) --
        self.setup_footer()

        # -- Logic Setup --
        self.setup_logic()

    def setup_top_bar(self):
        top_bar = QHBoxLayout()
        
        # Avatar/Icon
        # For now a circle placeholder or unicode
        self.avatar_label = ClickableLabel("👤") 
        self.avatar_label.setStyleSheet("font-size: 36px; color: #aaa; background-color: #333; border-radius: 25px; padding: 5px;")
        self.avatar_label.setFixedSize(60, 60)
        self.avatar_label.setAlignment(Qt.AlignCenter)
        self.avatar_label.clicked.connect(self.check_secret_pattern)
        top_bar.addWidget(self.avatar_label)

        # Title
        title = QLabel("AMR Control Panel")
        title.setStyleSheet("color: white; font-size: 32px; font-weight: bold; margin-left: 15px;") # Increased font
        top_bar.addWidget(title)
        
        top_bar.addStretch()

        # Battery (Mock)
        battery_frame = QFrame()
        battery_frame.setStyleSheet("background-color: transparent;")
        batt_layout = QHBoxLayout(battery_frame)
        batt_layout.setContentsMargins(0,0,0,0)
        
        batt_icon = QLabel("🔋") # Unicode placeholder
        batt_icon.setStyleSheet("font-size: 32px; color: #4CAF50;") # Increased size
        
        batt_text = QLabel("78%\nOnline")
        batt_text.setStyleSheet("color: white; font-size: 16px;") # Increased size
        
        batt_layout.addWidget(batt_icon)
        batt_layout.addWidget(batt_text)
        top_bar.addWidget(battery_frame)

        # Settings
        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(60, 60) # Increased size
        settings_btn.setStyleSheet("""
            QPushButton { background-color: transparent; color: #aaa; font-size: 36px; border: none; }
            QPushButton:hover { color: white; }
        """)
        top_bar.addWidget(settings_btn)

        # Close
        close_btn = QPushButton("✖")
        close_btn.setFixedSize(60, 60) # Increased size
        close_btn.setStyleSheet("""
            QPushButton { background-color: transparent; color: #aaa; font-size: 30px; border: none; }
            QPushButton:hover { color: #ff5555; }
        """)
        close_btn.clicked.connect(self.close)
        top_bar.addWidget(close_btn)

        self.main_layout.addLayout(top_bar)

    def setup_left_panel(self, parent_layout):
        left_layout = QVBoxLayout()
        left_layout.setSpacing(20)
        
        # Spacer
        left_layout.addStretch()

        # Big Navigation Button
        self.nav_btn = ModernButton("  Navigate", bg_color="#2196F3", is_primary=True)
        # Assuming we might add an icon locally, but for now text
        self.nav_btn.clicked.connect(lambda: self.run_script("navigation.sh"))
        left_layout.addWidget(self.nav_btn)

        # Status Label
        status_layout = QHBoxLayout()
        status_icon = QLabel("🧭") # Compass icon placeholder
        status_icon.setStyleSheet("color: #2196F3; font-size: 32px;") # Increased size
        
        self.status_text = QLabel("Status: Ready for Task")
        self.status_text.setStyleSheet("color: #888; font-size: 24px;") # Increased size
        
        status_layout.addWidget(status_icon)
        status_layout.addWidget(self.status_text)
        status_layout.addStretch()
        
        left_layout.addLayout(status_layout)
        
        # Spacer
        left_layout.addStretch()

        parent_layout.addLayout(left_layout, 1) # Stretch factor 1

    def setup_right_panel(self, parent_layout):
        card = CardWidget()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)

        # Header
        header = QLabel("Mapping Tools")
        header.setStyleSheet("color: #333; font-size: 28px; font-weight: bold; margin-bottom: 20px;") # Increased size
        header.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(header)

        # Buttons
        # Use white/light buttons on the grey card
        
        btn_style_card = """
            QPushButton {
                background-color: white;
                color: #333;
                border: 1px solid #ddd;
                border-radius: 12px;
                font-size: 24px; /* Increased font */
                font-weight: bold;
                text-align: left;
                padding-left: 30px;
            }
            QPushButton:hover { background-color: #f9f9f9; }
            QPushButton:pressed { background-color: #eee; }
        """

        self.create_map_btn = QPushButton("🗺  Create Map")
        self.create_map_btn.setFixedHeight(80) # Increased height
        self.create_map_btn.setStyleSheet(btn_style_card)
        self.create_map_btn.clicked.connect(lambda: self.run_script("create_map.sh"))
        card_layout.addWidget(self.create_map_btn)

        self.edit_map_btn = QPushButton("✏  Edit Map")
        self.edit_map_btn.setFixedHeight(80) # Increased height
        self.edit_map_btn.setStyleSheet(btn_style_card)
        self.edit_map_btn.clicked.connect(lambda: self.run_script("edit_map.sh"))
        card_layout.addWidget(self.edit_map_btn)

        self.save_map_btn = QPushButton("☁  Save Map")
        self.save_map_btn.setFixedHeight(80) # Increased height
        self.save_map_btn.setStyleSheet(btn_style_card)
        self.save_map_btn.clicked.connect(lambda: self.run_script("save_map.sh"))
        card_layout.addWidget(self.save_map_btn)
        
        # Developer Buttons (Hidden initially)
        self.sensor_check_btn = QPushButton("🔍  Sensor Check")
        self.sensor_check_btn.setFixedHeight(80) # Increased height
        self.sensor_check_btn.setStyleSheet(btn_style_card)
        self.sensor_check_btn.hide()
        self.sensor_check_btn.clicked.connect(lambda: self.run_script("sensor_check.sh"))
        card_layout.addWidget(self.sensor_check_btn)

        self.bringup_btn = QPushButton("🤖  Bringup Robot")
        self.bringup_btn.setFixedHeight(80) # Increased height
        self.bringup_btn.setStyleSheet(btn_style_card)
        self.bringup_btn.hide()
        self.bringup_btn.clicked.connect(lambda: self.run_script("bringup_robot.sh"))
        card_layout.addWidget(self.bringup_btn)


        card_layout.addStretch()
        parent_layout.addWidget(card, 1)

    def setup_footer(self):
        footer_layout = QHBoxLayout()
        footer_layout.setAlignment(Qt.AlignCenter)
        footer_layout.setSpacing(20)

        reboot_btn = QPushButton("Reboot")
        reboot_btn.setFixedSize(200, 80) # Increased size
        reboot_btn.setStyleSheet("""
            QPushButton { background-color: #FF9800; color: white; font-weight: bold; border-radius: 12px; font-size: 24px; }
            QPushButton:hover { background-color: #F57C00; }
        """)
        reboot_btn.clicked.connect(lambda: self.run_script("reboot.sh", "reboot"))

        shutdown_btn = QPushButton("Shutdown")
        shutdown_btn.setFixedSize(200, 80) # Increased size
        shutdown_btn.setStyleSheet("""
            QPushButton { background-color: #F44336; color: white; font-weight: bold; border-radius: 12px; font-size: 24px; }
            QPushButton:hover { background-color: #D32F2F; }
        """)
        shutdown_btn.clicked.connect(lambda: self.run_script("shutdown.sh", "shutdown"))

        footer_layout.addWidget(reboot_btn)
        footer_layout.addWidget(shutdown_btn)

        self.main_layout.addLayout(footer_layout)

    def setup_logic(self):
        self.main_process = None
        self.aux_process = None
        self.progress_dialog = None
        self.progress_timer = None
        
        self.dev_click_times = []
        self.dev_mode_enabled = False

    def check_secret_pattern(self):
        if self.dev_mode_enabled: return
        now = time.time()
        self.dev_click_times.append(now)
        self.dev_click_times = [t for t in self.dev_click_times if now - t <= 3.0]
        if len(self.dev_click_times) >= 4:
            self.enable_developer_mode()
            self.dev_click_times = []

    def enable_developer_mode(self):
        self.dev_mode_enabled = True
        QMessageBox.information(self, "Developer Mode", "Developer Mode Enabled!")
        self.sensor_check_btn.show()
        self.bringup_btn.show()

    def run_script(self, script_name, action_type="script"):
        # Determine script path
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts", script_name)
        
        if action_type in ["shutdown", "reboot"]:
             reply = QMessageBox.question(self, f'Confirm {action_type.title()}', 
                                         f"Are you sure you want to {action_type}?", 
                                         QMessageBox.Yes | QMessageBox.No)
             if reply == QMessageBox.No: return
        
        if not os.path.exists(script_path):
            QMessageBox.critical(self, "Error", f"Script not found: {script_path}")
            return

        is_auxiliary = script_name in ["save_map.sh", "sensor_check.sh"] # Simplified logic
        
        # Simple concurrent check
        if not is_auxiliary and action_type == "script":
            if self.main_process and self.main_process.state() == QProcess.Running:
                QMessageBox.warning(self, "Busy", "A main process is already running.")
                return

        proc = QProcess(self)
        if action_type == "script" and not is_auxiliary:
            self.main_process = proc
            proc.finished.connect(self.on_main_finished)
            self.status_text.setText(f"Status: Running {script_name}...")
            
            if script_name == "navigation.sh":
                self.show_progress_dialog("Launching Navigation...", 10)
            elif script_name == "create_map.sh":
                self.show_progress_dialog("Launching Mapping...", 5)
        
        elif is_auxiliary:
            self.aux_process = proc
            proc.finished.connect(self.on_aux_finished)
            
        proc.start("/bin/bash", [script_path])

    def show_progress_dialog(self, title, duration_sec):
        steps = 100
        interval = int((duration_sec * 1000) / steps)

        self.progress_dialog = QProgressDialog(title, None, 0, steps, self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setAutoClose(False)
        self.progress_dialog.setAutoReset(False)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.setValue(0)
        self.progress_dialog.setCancelButton(None)
        
        # Style the progress dialog to match dark theme roughly
        self.progress_dialog.setStyleSheet("""
            QProgressDialog { background-color: #333; color: white; }
            QLabel { color: white; }
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
                QTimer.singleShot(1000, self.close_progress)

    def close_progress(self):
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
            self.progress_timer = None

    def on_main_finished(self):
        self.main_process = None
        self.status_text.setText("Status: Task Completed")
        # Reset specific styling or state if needed

    def on_aux_finished(self):
        self.aux_process = None
        QMessageBox.information(self, "Finished", "Operation completed.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LauncherApp2()
    window.setGeometry(app.primaryScreen().availableGeometry())
    window.show()
    sys.exit(app.exec())
