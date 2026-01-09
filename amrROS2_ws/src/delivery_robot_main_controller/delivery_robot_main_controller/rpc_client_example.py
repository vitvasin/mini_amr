# client_example.py
import os
import time
from multiprocessing.connection import Client
from multiprocessing.connection import Connection

try:
    from .rpc_net import resolve_rpc_host
except ImportError:  # Allows running as a standalone script
    from rpc_net import resolve_rpc_host

# Use env overrides; fallback to localhost
RPC_HOST = os.getenv("RPC_HOST", "localhost")
RPC_PORT = int(os.getenv("RPC_PORT", "6000"))
print("IP:", RPC_HOST)

_conn: Connection | None = None
_CONNECT_RETRIES = 3
_CONNECT_RETRY_DELAY = 1.0  # seconds


def _get_conn() -> Connection:
    """Keep a single connection open; reconnect lazily if closed/broken."""
    global _conn
    if _conn is not None and not _conn.closed:
        return _conn

    last_exc: Exception | None = None
    for _ in range(_CONNECT_RETRIES):
        try:
            _conn = Client((RPC_HOST, RPC_PORT), authkey=b"secret")
            return _conn
        except ConnectionRefusedError as exc:
            last_exc = exc
            time.sleep(_CONNECT_RETRY_DELAY)

    raise ConnectionRefusedError(
        f"Cannot connect to RPC server at {RPC_HOST}:{RPC_PORT}. Is it running?"
    ) from last_exc


def call_remote(fn, *args, **kwargs):
    payload = {"fn": fn, "args": args, "kwargs": kwargs}
    conn = _get_conn()
    try:
        conn.send(payload)
        resp = conn.recv()
    except (EOFError, BrokenPipeError, ConnectionResetError, ConnectionRefusedError):
        # reconnect once and retry
        try:
            conn.close()
        except Exception:
            pass
        _reset_conn()
        conn = _get_conn()
        conn.send(payload)
        resp = conn.recv()

    if not resp.get("ok"):
        raise RuntimeError(resp.get("error"))
    return resp.get("result")


def _reset_conn():
    global _conn
    _conn = None

if __name__ == "__main__":
    print("Open door #1:", call_remote("door_command", 1, 0))
    print("Close door #2:", call_remote("door_command", 2, 0))
    print("Close door #2:", call_remote("door_command", 3, 0))
    print("Close door #2:", call_remote("door_command", 4, 0))
    #print("Dock robot:", call_remote("dock_command", True))
    #print("Undock robot:", call_remote("dock_command", False))
