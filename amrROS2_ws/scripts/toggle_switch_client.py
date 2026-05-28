#!/usr/bin/env python3
import sys
import rclpy
from rclpy.node import Node
from datetime import datetime
from hgcr_interfaces.srv import SetHoldingRegs

def now_str():
    """Return local time in ISO-8601 with timezone, seconds precision."""
    return datetime.now().astimezone().isoformat(timespec='seconds')

class ToggleSwitchClient(Node):
    def __init__(self, service_name: str = 'mservice/holding_regs'):
        super().__init__('toggle_switch_client')

        self.cli = self.create_client(SetHoldingRegs, service_name)

        # Wait for service to be available
        if not self.cli.wait_for_service(timeout_sec=5.0):
            self.get_logger().error(f"{now_str()} [ERROR] Service '{service_name}' not available after 5s. Exiting.")
            raise RuntimeError(f"Service '{service_name}' not available")

        self.get_logger().info(f"{now_str()} [INFO] Connected to service: {service_name}")

        # Toggle state: True = ON, False = OFF
        self.current_state = False

        # Timer to call every 2 seconds
        self.timer = self.create_timer(10.0, self.call_service_periodically)

    def call_service_periodically(self):
        # Prepare request
        self.current_state = not self.current_state
        req = SetHoldingRegs.Request()
        if self.current_state:
            req.value = 1
        else:
            req.value = 0
        req.address = 1;

        state_str = 'ON' if self.current_state else 'OFF'
        self.get_logger().info(f"{now_str()} [BEFORE] Calling service to switch {state_str}...")

        # Call async and wait for result via callback
        future = self.cli.call_async(req)
        future.add_done_callback(self._on_response)

    def _on_response(self, future):
        try:
            resp = future.result()
        except Exception as e:
            self.get_logger().error(f"{now_str()} [AFTER] Service call failed: {e}")
            return

        state_str = 'ON' if self.current_state else 'OFF'
        '''
        if resp.success:
            self.get_logger().info(f"{now_str()} [AFTER] Successfully switched {state_str}. Message: '{resp.message}'")
        else:
            self.get_logger().warn(f"{now_str()} [AFTER] Service reported failure switching {state_str}. Message: '{resp.message}'")
        '''
        self.get_logger().info(f"{now_str()} [AFTER] Successfully switched {state_str}. Message: '{resp.result}'")
        
def main():
    rclpy.init()
    node = None
    try:
        node = ToggleSwitchClient(service_name='mservice/holding_regs')  # Change if your service name differs
        rclpy.spin(node)
    except Exception as e:
        # If service not available or other init errors
        print(f"{now_str()} [ERROR] Node error: {e}")
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

