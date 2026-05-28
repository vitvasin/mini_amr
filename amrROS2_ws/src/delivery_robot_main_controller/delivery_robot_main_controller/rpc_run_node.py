import rclpy
from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup

from .rpc_server import RPCServer
from .rpc_fnc import (
    door_command,
    echo,
    dock_command_service,
    cancel_move_service,
    pause_move_service,
    configure_rpc_access,
    process_rpc_requests,
)


FUNCS = {
    "door_command": door_command,
    "echo": echo,
    "dock_command": dock_command_service,
    "cancel_move": cancel_move_service,
    "pause_move": pause_move_service,
}


class RPCRunNode(Node):
    """Node แยกสำหรับจัดการ RPC server และ bridge ไป ROS2 services/topics"""

    def __init__(self):
        super().__init__("rpc_run_node")
        self._reentrant_group = ReentrantCallbackGroup()

        configure_rpc_access(self)
        # ปลุก worker เป็นระยะ เผื่อมีกรณีพลาด event
        self.create_timer(0.5, process_rpc_requests, callback_group=self._reentrant_group)
        self.get_logger().info("RPC run node started; RPC bridge configured.")


def main(args=None):
    rclpy.init(args=args)
    node = RPCRunNode()
    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(node)

    server = RPCServer(host="localhost", port=6000, authkey=b"secret")
    server.register_funcs(FUNCS)
    server.start(daemon=True)

    try:
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info("RPC run node stopped by user.")
    finally:
        server.stop()
        executor.remove_node(node)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
