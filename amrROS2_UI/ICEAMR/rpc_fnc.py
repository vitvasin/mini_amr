"""
ฟังก์ชันสำหรับให้ GUI เรียกใช้งาน (ผ่าน RPC) และสื่อสารกับ ROS 2 topic
ไฟล์นี้ถูกออกแบบให้ขยายเพิ่มฟังก์ชันได้ในอนาคต โดยมีตัวช่วย publish ROS 2 แบบ lazy-init
"""

from typing import Optional, Dict
import threading

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Int32MultiArray


# สามารถปรับชื่อ topic ได้ที่นี่ให้เหมาะกับระบบของคุณ
ECHO_TOPIC = '/gui/echo'
DOOR_CMD_TOPIC = '/door/cmd'


class _RosPubHelper:
    """ตัวช่วยสำหรับจัดการ Node/Publisher แบบ singleton ในโมดูลนี้"""
    _lock = threading.Lock()
    _node: Optional[Node] = None
    _pubs: Dict[str, object] = {}

    @classmethod
    def _ensure_node(cls) -> Node:
        with cls._lock:
            if cls._node is not None:
                return cls._node
            # พยายามสร้าง node หากยังไม่มี
            try:
                # กรณี rclpy ยังไม่ถูก init จากภายนอก ให้ลอง init แบบเงียบ ๆ
                try:
                    # create_node จะล้มเหลวถ้ายังไม่ได้ init
                    node = rclpy.create_node('rpc_fnc_helper')
                except Exception:
                    rclpy.init(args=None)
                    node = rclpy.create_node('rpc_fnc_helper')
                cls._node = node
            except Exception as e:
                raise RuntimeError(f"Failed to initialize ROS node for rpc_fnc: {e}")
            return cls._node

    @classmethod
    def get_publisher(cls, topic: str, msg_type):
        node = cls._ensure_node()
        with cls._lock:
            if topic in cls._pubs:
                return cls._pubs[topic]
            pub = node.create_publisher(msg_type, topic, 10)
            cls._pubs[topic] = pub
            return pub


def echo(msg: str) -> str:
    """
    ส่งข้อความ echo ออก ROS 2 topic และคืนค่า string เดิมเพื่อแสดงผลที่ฝั่งเรียก
    - publish ไปที่ ECHO_TOPIC ด้วย std_msgs/String
    """
    try:
        pub = _RosPubHelper.get_publisher(ECHO_TOPIC, String)
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

        pub = _RosPubHelper.get_publisher(DOOR_CMD_TOPIC, Int32MultiArray)
        msg = Int32MultiArray()
        msg.data = [int(number), int(cmd)]
        pub.publish(msg)

        action_str = 'Opening' if cmd == 1 else 'Closing'
        print(f"[DOOR] {action_str} door #{number} (published)")
        return True

    except Exception as e:
        print(f"[DOOR] Error controlling door #{number}: {e}")
        return False

