"""Small helpers for resolving the IP address the RPC layer should use."""

from __future__ import annotations

import fcntl
import logging
import os
import socket
import struct

_SIOCGIFADDR = 0x8915  # ioctl request code for getting IPv4 address


def _ipv4_for_interface(ifname: str) -> str | None:
    """Return IPv4 address for a given interface name, or None if unavailable."""
    if not ifname:
        return None
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        data = fcntl.ioctl(sock.fileno(), _SIOCGIFADDR, struct.pack("256s", ifname[:15].encode("utf-8")))
        return socket.inet_ntoa(data[20:24])
    except OSError:
        return None
    finally:
        sock.close()


def resolve_rpc_host(default: str = "127.0.0.1") -> str:
    """
    Resolve the host IP to use for RPC.
    Preference order:
    1) RPC_HOST env var
    2) RPC_INTERFACE env var (e.g., eth0 / wlan0)
    3) Ethernet-like interfaces (eth*, enp*, eno*, enx*, end*)
    4) Wi-Fi-like interfaces (wl*, wlp*, wlx*)
    5) fallback default
    """
    env_host = os.getenv("RPC_HOST")
    if env_host:
        return env_host

    iface_hint = os.getenv("RPC_INTERFACE")
    if iface_hint:
        ip = _ipv4_for_interface(iface_hint)
        if ip:
            return ip
        logging.warning("RPC_INTERFACE=%s has no IPv4 address, falling back", iface_hint)

    eth_prefixes = ("eth", "enp", "eno", "enx", "end")  # include USB/bridged Ethernet naming
    wifi_prefixes = ("wl", "wlp", "wlx")

    for _, name in socket.if_nameindex():
        if name.startswith(eth_prefixes):
            ip = _ipv4_for_interface(name)
            if ip:
                return ip

    for _, name in socket.if_nameindex():
        if name.startswith(wifi_prefixes):
            ip = _ipv4_for_interface(name)
            if ip:
                return ip

    return default
