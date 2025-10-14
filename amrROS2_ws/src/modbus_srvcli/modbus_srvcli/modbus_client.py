import sys

from hgcr_interfaces.srv import SetHoldingRegs
import rclpy
from rclpy.node import Node


class ModbusClientAsync(Node):

    def __init__(self):
        super().__init__('modbus_client_async')
        self.cli = self.create_client(SetHoldingRegs, 'mservice/holding_regs')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.req = SetHoldingRegs.Request()

    def send_request(self, address, value):
        self.req.address = address
        self.req.value = value
        return self.cli.call_async(self.req)


def main():
    rclpy.init()

    modbus_client = ModbusClientAsync()
    future = modbus_client.send_request(int(sys.argv[1]), int(sys.argv[2]))
    rclpy.spin_until_future_complete(modbus_client, future)
    response = future.result()
    modbus_client.get_logger().info(
        'Result of modbus client: Address=%d ,Value=%d ,Respones= %s' %
        (int(sys.argv[1]), int(sys.argv[2]), response.result))

    modbus_client.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()