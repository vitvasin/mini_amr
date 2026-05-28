
#!/usr/bin/env python3
import sys
from datetime import datetime

import rclpy
from rclpy.node import Node
from hgcr_interfaces.srv import SetHoldingRegs

from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PySide6.QtCore import QTimer


def now_str():
    """Return local time in ISO-8601 with timezone, seconds precision."""
    return datetime.now().astimezone().isoformat(timespec='seconds')


class SwitchClientNode(Node):
    """ROS 2 client node that calls SetHoldingRegs to switch ON/OFF."""

    def __init__(self, service_name: str = 'mservice/holding_regs'):
        super().__init__('switch_client_gui')
        self.service_name = service_name
        self.cli = self.create_client(SetHoldingRegs, self.service_name)

        # Non-blocking initial check (short timeout to avoid freezing GUI)
        available = self.cli.wait_for_service(timeout_sec=0.5)
        if available:
            self.get_logger().info(f"{now_str()} [INFO] Connected to service: {self.service_name}")
        else:
            self.get_logger().warn(
                f"{now_str()} [WARN] Service '{self.service_name}' not available yet. "
                f"You can still click buttons; calls will attempt when available."
            )

    def call_switch(self, address: int, on: bool):
        """Call the SetHoldingRegs service with True (ON) or False (OFF)."""
        # Quick check before calling
        if not self.cli.wait_for_service(timeout_sec=0.0):
            self.get_logger().warn(
                f"{now_str()} [BEFORE] Service '{self.service_name}' not available. "
                f"Cannot switch {'ON' if on else 'OFF'} right now."
            )
            return

        req = SetHoldingRegs.Request()
        if on:
            req.value = 1 
        else:
            req.value = 0
        req.address = address #1
        state_str = 'ON' if on else 'OFF'
        self.get_logger().info(f"{now_str()} [BEFORE] Calling service to switch {state_str}...")

        future = self.cli.call_async(req)
        # Ensure the "after" log includes the target state
        future.add_done_callback(lambda fut: self._on_response(fut, state_str))

    def _on_response(self, future, state_str: str):
        """Handle service response and print AFTER with timestamp."""
        try:
            resp = future.result()
        except Exception as e:
            self.get_logger().error(f"{now_str()} [AFTER] Service call failed when switching {state_str}: {e}")
            return

        self.get_logger().info(f"{now_str()} [AFTER] Successfully switched {state_str}. Message: '{resp.result}'")


class SwitchClientWindow(QWidget):
    """Simple PySide6 window with two buttons to switch ON/OFF."""

    def __init__(self, node: SwitchClientNode):
        super().__init__()
        self.node = node

        self.setWindowTitle('ROS 2 Switch Client (PySide6)')
        layout = QVBoxLayout(self)

        self.status = QLabel(f"Service: {self.node.service_name}")
        layout.addWidget(self.status)

        btn_on = QPushButton('Switch ON')
        btn_off = QPushButton('Switch OFF')

        # btn_on.clicked.connect(lambda: self.node.call_switch(True))
        # btn_off.clicked.connect(lambda: self.node.call_switch(False))
        btn_on.clicked.connect(lambda: self._door_open())
        btn_off.clicked.connect(lambda: self._door_close())

        layout.addWidget(btn_on)
        layout.addWidget(btn_off)

        # Spin rclpy periodically so async callbacks run.
        # This does NOT toggle the switch; it only processes ROS events.
        self.spin_timer = QTimer(self)
        self.spin_timer.setInterval(10)  # 10 ms
        self.spin_timer.timeout.connect(self._spin_once)
        self.spin_timer.start()

    def _spin_once(self):
        # Service callbacks (AFTER logs) will be executed during spin_once
        rclpy.spin_once(self.node, timeout_sec=0.0)
        
    def _door_open(self):
        self.node.call_switch(1, True)
        self.node.call_switch(2, True)
        self.node.call_switch(3, True)
        self.node.call_switch(4, True)
    
    def _door_close(self):
        self.node.call_switch(1, False)
        self.node.call_switch(2, False)
        self.node.call_switch(3, False)
        self.node.call_switch(4, False)

def main():
    rclpy.init()

    app = QApplication(sys.argv)

    # Optional: pass service name as first CLI argument
    service_name = 'mservice/holding_regs'
    if len(sys.argv) > 1:
        service_name = sys.argv[1]

    node = SwitchClientNode(service_name=service_name)
    window = SwitchClientWindow(node)
    window.show()

    exit_code = app.exec()

    node.destroy_node()
    rclpy.shutdown()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()

