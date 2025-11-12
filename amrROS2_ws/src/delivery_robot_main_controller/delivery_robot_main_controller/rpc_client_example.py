# client_example.py
import os
from multiprocessing.connection import Client


RPC_HOST = 'localhost'
RPC_PORT =  6000


def call_remote(fn, *args, **kwargs):
    conn = Client((RPC_HOST,RPC_PORT), authkey=b"secret")
    conn.send({"fn": fn, "args": args, "kwargs": kwargs})
    resp = conn.recv()
    conn.close()
    if not resp.get("ok"):
        raise RuntimeError(resp.get("error"))
    return resp.get("result")

if __name__ == "__main__":
    print("Open door #1:", call_remote("door_command", 0, 0))
    print("Close door #2:", call_remote("door_command", 1, 0))
    #print("Dock robot:", call_remote("dock_command", True))
    #print("Undock robot:", call_remote("dock_command", False))
