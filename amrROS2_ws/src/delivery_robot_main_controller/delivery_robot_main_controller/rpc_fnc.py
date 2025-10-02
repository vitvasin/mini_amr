"""
ฟังก์ชันสำหรับให้ GUI เรียกใช้งาน (ผ่าน RPC) เพื่อสื่อสารกับ ROS 2 topic และ service
ไฟล์นี้ถูกออกแบบให้ขยายเพิ่มฟังก์ชันได้ในอนาคต โดยใช้ Node หลักของระบบเพื่อ publish / call service
"""

from typing import Optional, Dict
import threading
import time

from rclpy.node import Node
from std_msgs.msg import String, Int32MultiArray
from std_srvs.srv import SetBool


# สามารถปรับชื่อ topic ได้ที่นี่ให้เหมาะกับระบบของคุณ
ECHO_TOPIC = '/gui/echo'
DOOR_CMD_TOPIC = '/door/cmd'


class _RosAccess:
    """ตัวช่วยสำหรับจัดการ Node/Publisher/Client โดย reuse Node หลัก"""
    _lock = threading.Lock()
    _node: Optional[Node] = None
    _pubs: Dict[str, object] = {}
    _clients: Dict[str, object] = {}

    @classmethod
    def configure(cls, node: Node) -> None:
        with cls._lock:
            cls._node = node

    @classmethod
    def _ensure_node(cls) -> Node:
        node = cls._node
        if node is None:
            raise RuntimeError("ROS access for rpc_fnc is not configured. Call configure_rpc_access(node) first.")
        return node

    @classmethod
    def get_publisher(cls, topic: str, msg_type):
        with cls._lock:
            pub = cls._pubs.get(topic)
            if pub is None:
                node = cls._ensure_node()
                pub = node.create_publisher(msg_type, topic, 10)
                cls._pubs[topic] = pub
            return pub

    @classmethod
    def get_client(cls, service_name: str, srv_type):
        with cls._lock:
            client = cls._clients.get(service_name)
            if client is None:
                node = cls._ensure_node()
                client = node.create_client(srv_type, service_name)
                cls._clients[service_name] = client
            return client

    @classmethod
    def call_service(cls, service_name: str, srv_type, request, timeout_sec: float = 5.0):
        client = cls.get_client(service_name, srv_type)

        service_deadline = time.monotonic() + timeout_sec
        while not client.service_is_ready():
            if time.monotonic() >= service_deadline:
                raise RuntimeError(f"Service {service_name} not available")
            time.sleep(0.05)

        future = client.call_async(request)
        result_deadline = time.monotonic() + timeout_sec
        while not future.done():
            if time.monotonic() >= result_deadline:
                raise RuntimeError(f"Service call to {service_name} timed out")
            time.sleep(0.02)

        result = future.result()
        if result is None:
            raise RuntimeError(f"Service call to {service_name} failed")
        return result


def configure_rpc_access(node: Node) -> None:
    """กำหนด Node หลักที่ใช้สำหรับติดต่อ ROS 2"""
    _RosAccess.configure(node)


def echo(msg: str) -> str:
    """
    ส่งข้อความ echo ออก ROS 2 topic และคืนค่า string เดิมเพื่อแสดงผลที่ฝั่งเรียก
    - publish ไปที่ ECHO_TOPIC ด้วย std_msgs/String
    """
    try:
        pub = _RosAccess.get_publisher(ECHO_TOPIC, String)
        ros_msg = String()
        ros_msg.data = str(msg)
        pub.publish(ros_msg)
    except Exception as e:
        # พิมพ์ log ไว้ แต่ยังคงคืนค่าได้ตามปกติ
        print(f"[RPC][echo] publish failed: {e}")
    return f"echo: {msg}"


def door_command(number: int, cmd: int) -> bool:
    """
    สั่งเปิด/ปิดประตูผ่าน ROS 2 topic
    - cmd: 0 = close, 1 = open
    - publish ไปที่ DOOR_CMD_TOPIC ด้วย std_msgs/Int32MultiArray
      โดย data[0] = door number, data[1] = cmd
    return: True ถ้าสำเร็จในการส่งข้อความ, False ถ้าไม่สำเร็จ
    """
    try:
        if cmd not in (0, 1):
            print(f"[DOOR] Unknown command {cmd} for door #{number}")
            return False

        pub = _RosAccess.get_publisher(DOOR_CMD_TOPIC, Int32MultiArray)
        msg = Int32MultiArray()
        msg.data = [int(number), int(cmd)]
        pub.publish(msg)

        action_str = 'Opening' if cmd == 1 else 'Closing'
        print(f"[DOOR] {action_str} door #{number} (published)")
        return True

    except Exception as e:
        print(f"[DOOR] Error controlling door #{number}: {e}")
        return False


DOCK_SERVICE_NAME = 'dock_command'


def dock_command_service(should_dock: bool) -> bool:
    """
    เรียก ROS 2 service 'dock_command' (std_srvs/SetBool) เพื่อ dock หรือ undock
    - should_dock: True = dock, False = undock
    return: True ถ้าคำสั่งสำเร็จ, False ถ้าผิดพลาดหรือ service ไม่ตอบ
    """
    request = SetBool.Request()
    request.data = bool(should_dock)

    try:
        response = _RosAccess.call_service(DOCK_SERVICE_NAME, SetBool, request, timeout_sec=5.0)
        print(f"[DOCK] Service response success={response.success}, message='{response.message}'")
        return bool(response.success)
    except Exception as e:
        print(f"[DOCK] Error calling service {DOCK_SERVICE_NAME}: {e}")
        return False
