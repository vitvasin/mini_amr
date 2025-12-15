# rpc_server.py
from multiprocessing.connection import Listener
from threading import Thread, Event
import traceback
import logging
from typing import Callable, Dict, Any
from .rpc_net import resolve_rpc_host

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class RPCServer:
    """
    RPC server เบาๆ ด้วย multiprocessing.connection.Listener
    - รันใน background thread ได้
    - หยุดได้ด้วย stop()
    - ลงทะเบียนฟังก์ชันผ่าน .register_funcs(dict)
    Protocol:
      client ส่ง dict: {"fn": str, "args": list/tuple, "kwargs": dict}
      server ตอบ: {"ok": True, "result": obj} หรือ {"ok": False, "error": str}
    """

    def __init__(self, host: str | None = None, port: int = 6000, authkey: bytes = b"secret"):
        resolved_host = host or resolve_rpc_host(default="127.0.0.1")
        self.address = (resolved_host, port)
        self.authkey = authkey
        self._stop_event = Event()
        self._thread: Thread | None = None
        self._funcs: Dict[str, Callable[..., Any]] = {}
        self._listener: Listener | None = None

    def register_funcs(self, funcs: Dict[str, Callable[..., Any]]) -> None:
        """ลงทะเบียนชื่อฟังก์ชัน -> ตัวฟังก์ชัน"""
        self._funcs.update(funcs)

    def start(self, daemon: bool = True) -> None:
        """เริ่ม server ใน background thread"""
        if self._thread and self._thread.is_alive():
            logging.info("RPCServer already running.")
            return
        self._stop_event.clear()
        self._thread = Thread(target=self._serve_forever, name="RPCServerThread", daemon=daemon)
        self._thread.start()
        logging.info(f"RPCServer listening on {self.address[0]}:{self.address[1]}")

    def stop(self) -> None:
        """สั่งหยุด server แบบสุภาพ"""
        self._stop_event.set()
        # ปลุก listener.accept() ด้วยการสร้าง client ชั่วคราว (บางแพลตฟอร์มจำเป็น)
        try:
            from multiprocessing.connection import Client
            c = Client(self.address, authkey=self.authkey)
            c.send({"fn": "__noop__", "args": [], "kwargs": {}})
            c.close()
        except Exception:
            pass
        if self._thread:
            self._thread.join(timeout=3)
            logging.info("RPCServer stopped.")

    # -------------------- internal --------------------
    def _serve_forever(self):
        try:
            self._listener = Listener(self.address, authkey=self.authkey)
            while not self._stop_event.is_set():
                try:
                    conn = self._listener.accept()
                except (OSError, EOFError):
                    if self._stop_event.is_set():
                        break
                    continue

                # one-request-per-connection (ง่ายและพอสำหรับ use case ทั่วไป)
                try:
                    req = conn.recv()  # {"fn": "...", "args": [...], "kwargs": {...}}
                    if not isinstance(req, dict):
                        conn.send({"ok": False, "error": "Invalid request"})
                    else:
                        fn_name = req.get("fn")
                        args = req.get("args", ())
                        kwargs = req.get("kwargs", {})
                        if fn_name == "__noop__":
                            conn.send({"ok": True, "result": None})
                        elif fn_name not in self._funcs:
                            conn.send({"ok": False, "error": f"Unknown function: {fn_name}"})
                        else:
                            result = self._funcs[fn_name](*args, **kwargs)
                            conn.send({"ok": True, "result": result})
                except Exception:
                    conn.send({"ok": False, "error": traceback.format_exc()})
                finally:
                    conn.close()
        finally:
            try:
                if self._listener:
                    self._listener.close()
            except Exception:
                pass
