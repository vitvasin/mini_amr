from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QGridLayout, QPushButton, QHBoxLayout, QLabel, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QPixmap
import subprocess
import os
import signal

# ... existsing imports ...

class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Admin Password")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint) # Remove title bar but keep dialog properties
        self.setModal(True)
        self.setStyleSheet("background-color: #FFFFFF; border: 2px solid #555555; border-radius: 10px;")
        self.setMinimumSize(400, 500)

        layout = QVBoxLayout(self)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter Admin Password")
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

_ROS_SOURCE = (
    "source /opt/ros/jazzy/setup.bash && "
    "source /home/smr/workspaces/mini_amr/install/setup.bash"
)

def _ros_cmd(ros2_args: list) -> list:
    """Wrap a ros2 command so it runs inside a bash shell with ROS sourced."""
    inner = " ".join(ros2_args)
    return ["bash", "-c", f"{_ROS_SOURCE} && {inner}"]


# Module-level set keeps worker QThread Python wrappers alive while threads run.
# Without this, when the dialog is GC'd, its worker references die, the QThread
# Python wrapper is GC'd, and the still-running C++ thread crashes the process.
_active_workers = set()


class ChargeStateWorker(QThread):
    result_ready = Signal(int)  # emits raw data value, -1 on error

    def __init__(self):
        super().__init__()
        self._proc = None
        self._cancelled = False
        _active_workers.add(self)
        self.finished.connect(lambda: _active_workers.discard(self))

    def cancel(self):
        self._cancelled = True
        if self._proc is not None:
            try:
                self._proc.kill()
            except Exception:
                pass

    def run(self):
        env = os.environ.copy()
        env["ROS_DOMAIN_ID"] = "41"
        try:
            cmd = _ros_cmd(["ros2", "topic", "echo", "--once", "--no-arr", "--flow-style", "/ir_charge_state"])
            self._proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
            if self._cancelled:
                self._proc.kill()
                self._proc.communicate()
                return
            try:
                stdout, _ = self._proc.communicate(timeout=3)
            except subprocess.TimeoutExpired:
                self._proc.kill()
                self._proc.communicate()
                return
            if not self._cancelled and self._proc.returncode == 0:
                for line in stdout.splitlines():
                    if "data:" in line:
                        value = int(line.split("data:")[1].strip().split()[0])
                        if not self._cancelled:
                            self.result_ready.emit(value)
                        return
        except Exception:
            pass
        if not self._cancelled:
            self.result_ready.emit(-1)


class HWNodeWorker(QThread):
    result_ready = Signal(bool)  # True = /robot_hardware in node list

    def __init__(self):
        super().__init__()
        self._proc = None
        self._cancelled = False
        _active_workers.add(self)
        self.finished.connect(lambda: _active_workers.discard(self))

    def cancel(self):
        self._cancelled = True
        if self._proc is not None:
            try:
                self._proc.kill()
            except Exception:
                pass

    def run(self):
        env = os.environ.copy()
        env["ROS_DOMAIN_ID"] = "41"
        try:
            self._proc = subprocess.Popen(
                _ros_cmd(["ros2", "node", "list"]),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env
            )
            if self._cancelled:
                self._proc.kill()
                self._proc.communicate()
                return
            try:
                stdout, _ = self._proc.communicate(timeout=3)
            except subprocess.TimeoutExpired:
                self._proc.kill()
                self._proc.communicate()
                return
            if not self._cancelled:
                self.result_ready.emit("/robot_hardware" in stdout)
        except Exception:
            if not self._cancelled:
                self.result_ready.emit(False)


class TopicCheckerWorker(QThread):
    result_ready = Signal(str, str, str) # topic, hz, data

    def __init__(self, topic, check_data=True):
        super().__init__()
        self.topic = topic
        self.check_data = check_data

    def run(self):
        # Prepare environment with correct ROS_DOMAIN_ID
        env = os.environ.copy()
        env["ROS_DOMAIN_ID"] = "41"
        env["CYLCONDEDS_URI"] = os.path.expanduser("~/cyclonedds.xml") # Just in case

        # 1. Check HZ
        hz_status = "0.00"
        try:
            # -w 2 window, count 1 is usually not enough for reliable calculation but we want speed
            # Let's try ros2 topic hz -w 1 --window 2 /topic to be faster
            cmd = _ros_cmd(["ros2", "topic", "hz", "--window", "2", self.topic])

            # We run for a short duration
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
            try:
                # Wait up to 3 seconds for output. ros2 topic hz needs time to collect samples.
                outs, errs = proc.communicate(timeout=3)
                if "average:" in outs:
                     # Parse approximate average
                     for line in outs.splitlines():
                         if "average:" in line:
                             hz_status = line.split("average:")[1].split()[0]
                             break
            except subprocess.TimeoutExpired:
                # If it times out but we got no output, it might be silent (no data)
                proc.kill()
                outs, errs = proc.communicate()
                 # Check if we captured anything before timeout
                if "average:" in outs:
                     for line in outs.splitlines():
                         if "average:" in line:
                             hz_status = line.split("average:")[1].split()[0]
                             break
        except Exception as e:
            print(f"HZ Check Error: {e}")

        # 2. Check Data (Echo one message)
        data_preview = "No Data"
        if hz_status != "0.00" and self.check_data:
            try:
                # ros2 topic echo --once --no-arr --flow-style /topic
                cmd = _ros_cmd(["ros2", "topic", "echo", "--once", "--no-arr", "--flow-style", self.topic])
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=2, env=env)
                if result.returncode == 0:
                    data = result.stdout.strip()
                    # Truncate for display
                    if len(data) > 50:
                        data_preview = data[:50] + "..."
                    else:
                        data_preview = data
            except subprocess.TimeoutExpired:
                 pass
            except Exception as e:
                print(f"Data Check Error: {e}")

        self.result_ready.emit(self.topic, hz_status, data_preview)

class BringupCheckDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bringup System Check")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint) # Remove title bar but keep dialog properties
        self.setModal(True)
        self.setStyleSheet("background-color: #FFFFFF; border: 2px solid #555555; border-radius: 10px;")
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Header
        title = QLabel("ROS 2 Topic Monitor")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Control Buttons
        btn_layout = QHBoxLayout()
        self.start_bringup_btn = QPushButton("Start Bringup")
        self.start_bringup_btn.setStyleSheet("background-color: #C1FFC1; font-size: 18px; padding: 10px;")
        self.start_bringup_btn.clicked.connect(self.request_bringup)
        
        self.check_btn = QPushButton("Run Check")
        self.check_btn.setStyleSheet("background-color: #b3e0ff; font-size: 18px; padding: 10px;")
        self.check_btn.clicked.connect(self.start_check)
        
        btn_layout.addWidget(self.start_bringup_btn)
        btn_layout.addWidget(self.check_btn)
        layout.addLayout(btn_layout)

        # Topic Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Topic", "Hz", "Data Preview"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setStyleSheet("font-size: 16px;")
        layout.addWidget(self.table)

        self.check_topics = [
            "/odom",
            "/scan",
            "/ir_charge_state"
        ]
        
        # Initialize Table
        self.table.setRowCount(len(self.check_topics))
        for i, topic in enumerate(self.check_topics):
            self.table.setItem(i, 0, QTableWidgetItem(topic))
            self.table.setItem(i, 1, QTableWidgetItem("-"))
            self.table.setItem(i, 2, QTableWidgetItem("-"))

        # Close Button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("background-color: #ffcccc; padding: 10px;")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.workers = []

    def request_bringup(self):
        # We need to ask the main window to run bringup (which is `teleop.sh` logic essentially, or standard launch)
        # Parent is usually DevMenuDialog, grandparent is LauncherApp
        # But `parent()` inside QDialog points to the widget passed in __init__, which is DevMenuDialog
        # DevMenuDialog parent is LauncherApp
        
        # Try to find LauncherApp reference
        main_app = self.parent()
        while main_app and not hasattr(main_app, 'start_teleop_session'):
             main_app = main_app.parent()
        
        if main_app:
             QMessageBox.information(self, "Bringup", "Starting Bringup Sequence...")
             # main_app.start_teleop_session()
             if hasattr(main_app, 'run_script'):
                 main_app.run_script("bringup_robot.sh", run_in_terminal=True)
             else:
                 QMessageBox.warning(self, "Error", "run_script not supported by parent.")
        else:
             QMessageBox.warning(self, "Error", "Could not find main application to start bringup.")

    def start_check(self):
        self.workers = [] # Clear refs
        for i, topic in enumerate(self.check_topics):
            # Update Status to Checking...
            self.table.setItem(i, 1, QTableWidgetItem("Checking..."))
            self.table.setItem(i, 2, QTableWidgetItem("..."))

            worker = TopicCheckerWorker(topic)
            worker.result_ready.connect(self.update_row)
            worker.start()
            self.workers.append(worker)

    def update_row(self, topic, hz, data):
        # Find row
        row = -1
        for i in range(self.table.rowCount()):
             if self.table.item(i, 0).text() == topic:
                 row = i
                 break
        
        if row != -1:
            # HZ Item
            hz_item = QTableWidgetItem(f"{hz} Hz")
            if float(hz) > 0:
                hz_item.setForeground(Qt.darkGreen)
                hz_item.setText(f"✔ {hz} Hz")
            else:
                hz_item.setForeground(Qt.red)
                hz_item.setText(f"✖ {hz} Hz")
            
            self.table.setItem(row, 1, hz_item)
            
            # Data Item
            self.table.setItem(row, 2, QTableWidgetItem(data))

class DevMenuDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Developer Menu")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint) # Remove title bar but keep dialog properties
        self.setModal(True)
        self.setStyleSheet("background-color: #FFFFFF; border: 2px solid #555555; border-radius: 10px;")
        self.setMinimumSize(400, 350)

        # Styles
        self.setStyleSheet("""
            QDialog {
                background-color: #F9F8F8;
            }
            QPushButton {
                min-height: 70px;
                font-size: 22px;
                font-weight: bold;
                border-radius: 10px;
                border: 2px solid #555;
                margin: 3px;
            }
            QPushButton:hover {
                filter: brightness(110%);
                border-width: 3px;
            }
            QPushButton:pressed {
                padding-top: 4px;
                padding-left: 4px;
                border-width: 1px;
            }
            QPushButton:disabled {
                color: #999;
                border-color: #ccc;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title_label = QLabel("Developer Tools")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #333; margin-bottom: 10px; border: none;")
        layout.addWidget(title_label)

        buttons_config = [
            ("Dock", "dock.sh", True),
            ("Undock", "undock.sh", True)
        ]
        
        for label, script, run_terminal in buttons_config:
            btn = QPushButton(label)
            btn.setStyleSheet("background-color: #E0E0E0; color: #333;")
            # Connect to parent's run_script
            btn.clicked.connect(lambda checked=False, s=script, rt=run_terminal: parent.run_script(s, run_in_terminal=rt))
            layout.addWidget(btn)

        # Teleop Button
        teleop_btn = QPushButton("Teleop Controller")
        teleop_btn.setStyleSheet("background-color: #b3e0ff; color: #004080; border: 2px solid #0059b3;")
        teleop_btn.clicked.connect(self.open_teleop)
        layout.addWidget(teleop_btn)

        # Bringup Check Button
        check_btn = QPushButton("Bringup Check")
        check_btn.setStyleSheet("background-color: #C1FFC1; color: #006600; border: 2px solid #004d00;")
        check_btn.clicked.connect(self.open_bringup_check)
        layout.addWidget(check_btn)

        # HW Interface Toggle Button
        self._hw_proc = None
        self._hw_external = False  # cached from last HWNodeWorker poll
        self._hw_node_worker = None
        self.hw_btn = QPushButton("Start HW Interface")
        self.hw_btn.setStyleSheet("background-color: #E0E0E0; color: #333; border: 2px solid #555;")
        self.hw_btn.clicked.connect(self.toggle_hw_interface)
        layout.addWidget(self.hw_btn)

        self.hw_state_label = QLabel("HW Interface: Unknown")
        self.hw_state_label.setAlignment(Qt.AlignCenter)
        self.hw_state_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 6px; border-radius: 6px; background-color: #e0e0e0; color: #333; border: 1px solid #aaa;")
        layout.addWidget(self.hw_state_label)

        # Charge Buttons — row: [Charge Once] [Auto Charge]
        self._auto_charging = False
        self._auto_charge_retry_timer = QTimer(self)
        self._auto_charge_retry_timer.setInterval(2000)
        self._auto_charge_retry_timer.timeout.connect(self._auto_charge_retry)

        charge_row = QHBoxLayout()
        charge_row.setSpacing(8)

        self.charge_once_btn = QPushButton("Charge Once")
        self.charge_once_btn.setStyleSheet("background-color: #fff3cd; color: #856404; border: 2px solid #856404;")
        self.charge_once_btn.clicked.connect(self.charge_once)
        charge_row.addWidget(self.charge_once_btn)

        self.charge_auto_btn = QPushButton("Auto Charge")
        self.charge_auto_btn.setStyleSheet("background-color: #ffe0b2; color: #7d3a00; border: 2px solid #7d3a00;")
        self.charge_auto_btn.clicked.connect(self.toggle_auto_charge)
        charge_row.addWidget(self.charge_auto_btn)

        layout.addLayout(charge_row)

        self.stop_charge_btn = QPushButton("Stop Charging")
        self.stop_charge_btn.setStyleSheet("background-color: #f8d7da; color: #721c24; border: 2px solid #721c24;")
        self.stop_charge_btn.clicked.connect(self.stop_charging)
        layout.addWidget(self.stop_charge_btn)

        # IR Charge State Indicator
        self.charge_state_label = QLabel("IR Charge State: --")
        self.charge_state_label.setAlignment(Qt.AlignCenter)
        self.charge_state_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 6px; border-radius: 6px; background-color: #e0e0e0; color: #333; border: 1px solid #aaa;")
        layout.addWidget(self.charge_state_label)

        self._charge_state_worker = None
        self._charge_poll_timer = QTimer(self)
        self._charge_poll_timer.setInterval(1500)
        self._charge_poll_timer.timeout.connect(self._poll_charge_state)
        self._charge_poll_timer.timeout.connect(self._poll_hw_node)
        self._charge_poll_timer.timeout.connect(self._sync_hw_btn_proc_only)
        self._charge_poll_timer.start()
        self._poll_charge_state()
        self._poll_hw_node()

        layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("background-color: #ffcccc; color: #333;")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def open_teleop(self):
        # Delegate to parent's dedicated method
        if hasattr(self.parent(), 'start_teleop_session'):
            self.parent().start_teleop_session()
        else:
             QMessageBox.warning(self, "Error", "Teleop session not supported by parent.")
        pass

    def open_bringup_check(self):
        dialog.exec()

    def toggle_hw_interface(self):
        env = os.environ.copy()
        env["ROS_DOMAIN_ID"] = "41"
        proc_running = self._hw_proc is not None and self._hw_proc.poll() is None
        if proc_running:
            self.hw_btn.setEnabled(False)
            self.hw_btn.setText("Stopping...")
            self._hw_proc.terminate()
            try:
                self._hw_proc.wait(timeout=3)
            except Exception:
                self._hw_proc.kill()
            self._hw_proc = None
            self._hw_external = False
            self._update_hw_ui()
            self.hw_btn.setEnabled(True)
        elif self._hw_external:
            QMessageBox.information(self, "HW Interface", "Hardware interface running externally (part of bringup). Stop bringup to kill it.")
        else:
            self.hw_btn.setEnabled(False)
            self.hw_btn.setText("Starting...")
            try:
                self._hw_proc = subprocess.Popen(
                    _ros_cmd(["ros2", "run", "robot_hardware_interface", "robot_hardware"]),
                    env=env
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to start hardware interface:\n{e}")
                self.hw_btn.setEnabled(True)
                self._update_hw_ui()
                return
            self._update_hw_ui()
            self.hw_btn.setEnabled(True)

    def _poll_hw_node(self):
        if self._hw_node_worker and self._hw_node_worker.isRunning():
            return
        if self._hw_proc is not None and self._hw_proc.poll() is None:
            return  # we own it, no need to poll
        self._hw_node_worker = HWNodeWorker()
        self._hw_node_worker.result_ready.connect(self._on_hw_node_result)
        self._hw_node_worker.start()

    def _on_hw_node_result(self, running: bool):
        self._hw_external = running
        self._update_hw_ui()

    def _sync_hw_btn_proc_only(self):
        if self._hw_proc is not None:
            self._update_hw_ui()

    def _update_hw_ui(self):
        proc_running = self._hw_proc is not None and self._hw_proc.poll() is None
        if proc_running:
            self.hw_btn.setText("Stop HW Interface")
            self.hw_btn.setStyleSheet("background-color: #d4edda; color: #155724; border: 2px solid #155724;")
            self.hw_state_label.setText("HW Interface: Running")
            self.hw_state_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 6px; border-radius: 6px; background-color: #d4edda; color: #155724; border: 1px solid #155724;")
        elif self._hw_external:
            self.hw_btn.setText("HW Interface (External)")
            self.hw_btn.setStyleSheet("background-color: #cce5ff; color: #004085; border: 2px solid #004085;")
            self.hw_state_label.setText("HW Interface: Running (External)")
            self.hw_state_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 6px; border-radius: 6px; background-color: #cce5ff; color: #004085; border: 1px solid #004085;")
        else:
            self.hw_btn.setText("Start HW Interface")
            self.hw_btn.setStyleSheet("background-color: #E0E0E0; color: #333; border: 2px solid #555;")
            self.hw_state_label.setText("HW Interface: Stopped")
            self.hw_state_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 6px; border-radius: 6px; background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb;")

    def _poll_charge_state(self):
        if self._charge_state_worker and self._charge_state_worker.isRunning():
            return
        self._charge_state_worker = ChargeStateWorker()
        self._charge_state_worker.result_ready.connect(self._on_charge_state)
        self._charge_state_worker.start()

    def _on_charge_state(self, value):
        STATE_MAP = {
            0:  ("Not at Dock",      "#f8d7da", "#721c24", "#f5c6cb"),
            10: ("Ready to Charge",  "#fff3cd", "#856404", "#ffeeba"),
            11: ("Charging",         "#d4edda", "#155724", "#c3e6cb"),
        }
        if value in STATE_MAP:
            text, bg, fg, border = STATE_MAP[value]
            label = f"IR Charge State: {text} ({value})"
        else:
            label = f"IR Charge State: Unknown ({value})" if value >= 0 else "IR Charge State: No Signal"
            bg, fg, border = "#e0e0e0", "#333", "#aaa"
        self.charge_state_label.setText(label)
        self.charge_state_label.setStyleSheet(
            f"font-size: 16px; font-weight: bold; padding: 6px; border-radius: 6px;"
            f"background-color: {bg}; color: {fg}; border: 1px solid {border};"
        )
        if value == 11 and self._auto_charging:
            self._stop_auto_charge()

    def closeEvent(self, event):
        try:
            self._charge_poll_timer.stop()
            self._auto_charge_retry_timer.stop()
        except Exception:
            pass
        for worker in (self._charge_state_worker, self._hw_node_worker):
            if worker is not None:
                try:
                    worker.result_ready.disconnect()
                except (RuntimeError, TypeError):
                    pass
                try:
                    worker.cancel()
                except Exception:
                    pass
                # No wait() — workers are kept alive by _active_workers set
                # and will self-clean via finished signal. _cancelled flag
                # prevents emit on dead slots.
        if self._hw_proc is not None and self._hw_proc.poll() is None:
            try:
                self._hw_proc.terminate()
            except Exception:
                pass
        super().closeEvent(event)

    def _send_charge_command(self, data_value: int):
        env = os.environ.copy()
        env["ROS_DOMAIN_ID"] = "41"
        cmd = _ros_cmd([
            "ros2", "topic", "pub", "-1",
            "/set_charge_state",
            "std_msgs/msg/Int16",
            f"'{{data: {data_value}}}'"
        ])
        try:
            subprocess.Popen(cmd, env=env)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send charge command:\n{e}")

    def _ensure_hw_then(self, callback):
        """Start HW interface if not running, then call callback (with 2s delay if started)."""
        hw_alive = (self._hw_proc is not None and self._hw_proc.poll() is None) or self._hw_external
        if not hw_alive:
            self.charge_state_label.setText("IR Charge State: Starting HW node...")
            env = os.environ.copy()
            env["ROS_DOMAIN_ID"] = "41"
            try:
                self._hw_proc = subprocess.Popen(
                    _ros_cmd(["ros2", "run", "robot_hardware_interface", "robot_hardware"]),
                    env=env
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to start hardware node:\n{e}")
                return
            self._update_hw_ui()
            QTimer.singleShot(2000, callback)
        else:
            callback()

    def charge_once(self):
        self.charge_once_btn.setEnabled(False)
        def do_send():
            self._send_charge_command(20)
            self.charge_once_btn.setEnabled(True)
        self._ensure_hw_then(do_send)

    def toggle_auto_charge(self):
        if self._auto_charging:
            self._stop_auto_charge()
        else:
            self._auto_charging = True
            self.charge_auto_btn.setText("Stop Auto")
            self.charge_auto_btn.setStyleSheet("background-color: #f8d7da; color: #721c24; border: 2px solid #721c24;")
            self.charge_once_btn.setEnabled(False)
            def do_start():
                self._send_charge_command(20)
                self._auto_charge_retry_timer.start()
            self._ensure_hw_then(do_start)

    def _auto_charge_retry(self):
        self._send_charge_command(20)

    def _stop_auto_charge(self):
        self._auto_charging = False
        self._auto_charge_retry_timer.stop()
        self.charge_auto_btn.setText("Auto Charge")
        self.charge_auto_btn.setStyleSheet("background-color: #ffe0b2; color: #7d3a00; border: 2px solid #7d3a00;")
        self.charge_once_btn.setEnabled(True)

    def stop_charging(self):
        self._stop_auto_charge()
        self._send_charge_command(22)

class NavigationConfirmDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Navigation Check")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint) # Remove title bar but keep dialog properties
        self.setModal(True)
        self.setStyleSheet("background-color: #FFFFFF; border: 2px solid #555555; border-radius: 10px;")
        # self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Image
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        
        # Path to dock_check.jpg
        # Assumes this file is in gui_launcher/assets/dock_check.jpg
        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "dock_check.jpg")
        
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            # Resize if needed to fit dialog comfortably
            pixmap = pixmap.scaledToHeight(300, Qt.SmoothTransformation)
            image_label.setPixmap(pixmap)
        else:
            image_label.setText("Image not found: " + image_path)
        
        layout.addWidget(image_label)

        # Text
        text_label = QLabel("กรุณานำหุ่นยนต์ไปที่ Dock Station และปลด Emergency ก่อนกดยืนยัน")
        text_label.setWordWrap(True)
        text_label.setAlignment(Qt.AlignCenter)
        # Use a large font for visibility
        text_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #333;")
        layout.addWidget(text_label)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(30)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(180, 80)
        cancel_btn.setStyleSheet("background-color: #ffcccc; color: #333; font-size: 24px; font-weight: bold; border-radius: 10px;")
        cancel_btn.clicked.connect(self.reject)
        
        confirm_btn = QPushButton("Confirm")
        confirm_btn.setFixedSize(180, 80)
        confirm_btn.setStyleSheet("background-color: #C1FFC1; color: #006600; font-size: 24px; font-weight: bold; border-radius: 10px;")
        confirm_btn.clicked.connect(self.accept)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(confirm_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
