"""
ฟังก์ชัน RPC สำหรับให้ GUI เรียกใช้ จากฝั่ง ROS2 main controller
- ส่งข้อความไปยัง topic ที่ต้องการ
- เรียก ROS2 service ผ่าน Node หลัก (หลีกเลี่ยงการสร้าง executor ใหม่)
"""

from __future__ import annotations

import threading
from collections import deque
from dataclasses import dataclass
from typing import Any, Dict, Optional

from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import SetBool
from hgcr_interfaces.srv import SetHoldingRegs

# ชื่อ topic / service ที่ใช้บ่อย
ECHO_TOPIC = '/gui/echo'
DOOR_SERVICE = 'mservice/holding_regs'
DOCK_SERVICE_NAME = 'dock_command'


@dataclass
class _ServiceRequest:
    service_name: str
    srv_type: type
    request: Any
    timeout_sec: float
    event: threading.Event
    result_holder: Dict[str, Any]


class _RosBridge:
    """ตัวช่วยจัดการ Node หลัก, publisher และ service queue"""

    _lock = threading.Lock()
    _node: Optional[Node] = None
    _pubs: Dict[str, Any] = {}
    _clients: Dict[str, Any] = {}
    _service_queue: deque[_ServiceRequest] = deque()

    @classmethod
    def configure(cls, node: Node) -> None:
        with cls._lock:
            cls._node = node

    @classmethod
    def _ensure_node(cls) -> Node:
        node = cls._node
        if node is None:
            raise RuntimeError("RPC bridge ไม่ได้รับการ configure ด้วย Node หลัก")
        return node

    @classmethod
    def get_publisher(cls, topic: str, msg_type):
        with cls._lock:
            pub = cls._pubs.get(topic)
            if pub is None:
                pub = cls._ensure_node().create_publisher(msg_type, topic, 10)
                cls._pubs[topic] = pub
            return pub

    @classmethod
    def _get_or_create_client(cls, service_name: str, srv_type):
        client = cls._clients.get(service_name)
        if client is None:
            client = cls._ensure_node().create_client(srv_type, service_name)
            cls._clients[service_name] = client
        return client

    @classmethod
    def queue_service_call(cls, service_name: str, srv_type, request, timeout_sec: float):
        event = threading.Event()
        holder: Dict[str, Any] = {}
        work = _ServiceRequest(service_name, srv_type, request, timeout_sec, event, holder)
        with cls._lock:
            cls._service_queue.append(work)
        if not event.wait(timeout_sec):
            raise RuntimeError(f"Service call to {service_name} timed out")
        if 'error' in holder:
            raise holder['error']
        return holder.get('result')

    @classmethod
    def process_pending_requests(cls) -> None:
        while True:
            with cls._lock:
                if not cls._service_queue:
                    return
                call = cls._service_queue.popleft()

            try:
                client = cls._get_or_create_client(call.service_name, call.srv_type)
                if not client.service_is_ready():
                    raise RuntimeError(f"Service {call.service_name} not available")

                future = client.call_async(call.request)

                def _on_done(fut, *, call=call):
                    try:
                        call.result_holder['result'] = fut.result()
                    except Exception as exc:  # pylint: disable=broad-except
                        call.result_holder['error'] = exc
                    finally:
                        call.event.set()

                future.add_done_callback(_on_done)

            except Exception as exc:  # pylint: disable=broad-except
                call.result_holder['error'] = exc
                call.event.set()


def configure_rpc_access(node: Node) -> None:
    """เรียกครั้งเดียวจาก main controller เพื่อบอกให้ RPC ใช้ node นี้"""
    _RosBridge.configure(node)


def process_rpc_requests() -> None:
    """เรียกภายใน timer ของ main controller เพื่อประมวลผล service queue"""
    _RosBridge.process_pending_requests()


# ---------- ฟังก์ชัน RPC ที่ export ----------

def echo(msg: str) -> str:
    """publish ข้อความ echo ออก topic และคืนค่า string"""
    try:
        pub = _RosBridge.get_publisher(ECHO_TOPIC, String)
        ros_msg = String()
        ros_msg.data = str(msg)
        pub.publish(ros_msg)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"[RPC][echo] publish failed: {exc}")
    return f"echo: {msg}"


def door_command(number: int, cmd: int) -> bool:
    """
    ส่งคำสั่งผ่าน service Modbus (SetHoldingRegs)
    - number เป็น address, cmd (0 ปิด / 1 เปิด)
    """
    if cmd not in (0, 1):
        print(f"[DOOR] Unknown command {cmd} for door #{number}")
        return False

    request = SetHoldingRegs.Request()
    request.address = int(number)
    request.value = int(cmd)
    
    print(f"[Door]---Address : {request.address} -- Values : {request.value}") 

    try:
        response = _RosBridge.queue_service_call(DOOR_SERVICE, SetHoldingRegs, request, timeout_sec=10.0)
        action_str = 'Opening' if cmd == 1 else 'Closing'
        print(f"[DOOR] {action_str} door #{number} (service result: {getattr(response, 'result', 'N/A')})")
        return True
    except Exception as exc:  # pylint: disable=broad-except
        print(f"[DOOR] Error controlling door #{number}: {exc}")
        return False


def dock_command_service(should_dock: bool) -> bool:
    """เรียก service dock_command (SetBool)"""
    request = SetBool.Request()
    request.data = bool(should_dock)

    try:
        response = _RosBridge.queue_service_call(DOCK_SERVICE_NAME, SetBool, request, timeout_sec=5.0)
        print(f"[DOCK] Service response success={response.success}, message='{response.message}'")
        return bool(response.success)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"[DOCK] Error calling service {DOCK_SERVICE_NAME}: {exc}")
        return False
