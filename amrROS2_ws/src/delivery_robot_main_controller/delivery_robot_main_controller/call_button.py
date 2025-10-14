#!/usr/bin/env python3
from __future__ import annotations

import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Optional, Set

import rclpy
from rclpy.node import Node

from . import api_client

_LOGGER = logging.getLogger(__name__)
_REQUEST_ACTION = "Request"
_ACTIVE_STATUS = True
_INACTIVE_STATUS = False


def _ensure_iterable_queue(raw_queue: object) -> list[dict]:
    """Normalise queue data from the API into a list of dicts."""
    if raw_queue is None:
        return []
    if isinstance(raw_queue, list):
        return raw_queue
    if isinstance(raw_queue, dict):
        return [raw_queue]
    if isinstance(raw_queue, str):
        try:
            loaded = json.loads(raw_queue)
        except json.JSONDecodeError:
            return []
        return _ensure_iterable_queue(loaded)
    return []


def _get_request_stations(logger: Optional[logging.Logger] = None) -> Set[str]:
    """Fetch pending queue entries and return station identifiers for Request action."""
    try:
        response = api_client.get_pending_queue()
    except Exception as exc:  # pragma: no cover - network errors are runtime concerns
        if logger:
            logger.error("Failed to fetch pending queue: %s", exc)
        else:
            _LOGGER.error("Failed to fetch pending queue: %s", exc)
        return set()

    queue_entries = _ensure_iterable_queue(response.get("data"))
    stations: Set[str] = set()
    for item in queue_entries:
        if item.get("action", _REQUEST_ACTION) != _REQUEST_ACTION:
            continue
        target = item.get("target") or item.get("station") or item.get("no_switch")
        if target is None:
            continue
        stations.add(str(target))
    return stations


def enqueue_request_for_station(
    station_id: str,
    *,
    status: bool = True,
    logger: Optional[logging.Logger] = None,
) -> bool:
    """Add a Request queue entry for the given station if one is not already pending."""
    if not status:
        if logger:
            logger.debug("Skip enqueue for station %s because status is False.", station_id)
        return False

    current_requests = _get_request_stations(logger=logger)
    if station_id in current_requests:
        if logger:
            logger.info("Station %s already has a pending Request queue.", station_id)
        return False

    payload = {
        "action": _REQUEST_ACTION,
        "target": station_id,
        "boxNumber": "1",
        "sender": "call_button",
        "status": "Pending",
    }

    try:
        api_client.add_queue(payload)
    except Exception as exc:  # pragma: no cover - network errors are runtime concerns
        if logger:
            logger.error("Failed to enqueue Request for station %s: %s", station_id, exc)
        else:
            _LOGGER.error("Failed to enqueue Request for station %s: %s", station_id, exc)
        raise

    if logger:
        logger.info("Enqueued Request queue for station %s.", station_id)
    return True


def enqueue_request_from_switch(station: str, status: bool) -> bool:
    """Convenience helper for external scripts (e.g., call_ros.py)."""
    return enqueue_request_for_station(str(station), status=status, logger=_LOGGER)


def _resolve_call_switch_path() -> Optional[Path]:
    """Locate the call_switch.py script in the ctr_mode workspace."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        candidate = parent / "ctr_mode" / "call_switch.py"
        if candidate.exists():
            return candidate
    return None


class CallRobotButton(Node):
    """ROS 2 node that monitors Request queues and notifies switch listeners."""

    def __init__(self) -> None:
        super().__init__("call_robot_button")
        self.poll_interval = self.declare_parameter("queue_poll_interval", 2.0).value
        self.call_switch_script = _resolve_call_switch_path()
        if not self.call_switch_script:
            self.get_logger().warning(
                "call_switch.py not found. Queue notification will be disabled."
            )
        self._active_requests: Set[str] = set()
        self.create_timer(self.poll_interval, self._check_queue_and_notify)

    def handle_button_event(self, station_id: str, status: bool) -> bool:
        """Queue a Request entry originating from a hardware button event."""
        return enqueue_request_for_station(station_id, status=status, logger=self.get_logger())

    def _check_queue_and_notify(self) -> None:
        pending_requests = _get_request_stations(logger=self.get_logger())
        if pending_requests == self._active_requests:
            return

        newly_active = pending_requests - self._active_requests
        cleared = self._active_requests - pending_requests

        for station in newly_active:
            self._publish_to_switch(station, _ACTIVE_STATUS)

        for station in cleared:
            self._publish_to_switch(station, _INACTIVE_STATUS)

        self._active_requests = pending_requests

    def _publish_to_switch(self, station: str, status: bool) -> None:
        if not self.call_switch_script:
            self.get_logger().debug(
                "call_switch.py missing. Skip publishing status %s for station %s.",
                status,
                station,
            )
            return

        status_arg = "True" if status else "False"
        try:
            subprocess.run(
                [sys.executable, str(self.call_switch_script), station, status_arg],
                check=True,
                timeout=5,
            )
            self.get_logger().info(
                "call_switch notified: station=%s status=%s.", station, status_arg
            )
        except subprocess.CalledProcessError as exc:  # pragma: no cover - runtime concern
            self.get_logger().error(
                "call_switch.py returned non-zero exit status for station %s: %s",
                station,
                exc,
            )
        except subprocess.TimeoutExpired:  # pragma: no cover - runtime concern
            self.get_logger().error(
                "call_switch.py timed out for station %s with status %s.", station, status_arg
            )
        except FileNotFoundError:  # pragma: no cover - runtime concern
            self.get_logger().error("Python interpreter not found when calling call_switch.py.")


def main(args: Optional[Iterable[str]] = None) -> None:
    rclpy.init(args=args)
    node = CallRobotButton()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:  # pragma: no cover - runtime concern
        node.get_logger().info("CallRobotButton interrupted by user.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
