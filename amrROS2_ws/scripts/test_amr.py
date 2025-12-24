#!/usr/bin/env python3
import sys
import requests
import time
import random
from typing import List, Dict, Any

# Import the API client from the project
# Try normal import first (works if PYTHONPATH includes `src` or package is installed)
try:
    from delivery_robot_main_controller import api_client
except Exception:
    # Fallback for running directly from repo without PYTHONPATH set
    import os
    repo_root = os.path.dirname(os.path.dirname(__file__))  # project root (parent of scripts)
    src_path = os.path.join(repo_root, "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    try:
        from delivery_robot_main_controller import api_client
    except Exception as e:
        print(f"Error: cannot import api_client: {e}")
        sys.exit(1)


def _normalize_list_payload(payload: Dict[str, Any], key: str) -> List[Dict[str, Any]]:
    """Safely extract a list from API responses that sometimes return JSON strings.

    The API often returns {"data": [...]}, but in some places it may be a JSON string.
    """
    data = payload.get(key, [])
    if isinstance(data, str):
        try:
            import json
            data = json.loads(data)
        except Exception:
            data = []
    if not isinstance(data, list):
        return []
    return data


def list_queue_targets() -> List[str]:
    resp = api_client.get_pending_queue()
    queues = _normalize_list_payload(resp, "data")
    targets = []
    for q in queues:
        try:
            targets.append(q.get("target", ""))
        except Exception:
            continue
    return targets


def add_to_queue(target_station: str) -> bool:
    """Add a Request queue using the higher-level helper.

    Uses `api_client.add_request_queue` which validates station existence and
    avoids duplicates. Returns True if request exists or is added, False if
    station not found or on error.
    """
    try:
        result = api_client.add_request_queue(target_station)
        if result is False:
            print(f"Station not found: {target_station}")
            return False
        return True
    except requests.HTTPError as e:
        resp = getattr(e, "response", None)
        code = getattr(resp, "status_code", "?")
        body = getattr(resp, "text", "")
        print(f"HTTP {code} while adding '{target_station}': {body}")
        return False
    except Exception as e:
        print(f"Add queue failed for '{target_station}': {e}")
        return False


def list_station_names() -> List[str]:
    try:
        resp = api_client.get_station_list()
        stations = _normalize_list_payload(resp, "data")
        names = []
        for s in stations:
            try:
                names.append(s.get("name", ""))
            except Exception:
                continue
        return [n for n in names if n]
    except Exception as e:
        print(f"Error fetching station list: {e}")
        return []


def run_single_station(target_station: str) -> int:
    print(f"Queueing station: {target_station} (action=Request)")
    ok = add_to_queue(target_station)
    if ok:
        print("Add queue: SUCCESS or already exists")
        # Show all current targets in queue
        targets = list_queue_targets()
        if targets:
            print("Current queue targets:")
            for i, t in enumerate(targets, 1):
                print(f"  {i}. {t}")
        else:
            print("Queue is empty.")
        return 0
    else:
        print("Add queue: FAILED")
        return 2


def run_random_mode(max_queue: int = 2, poll_sec: float = 1.0) -> int:
    stations = list_station_names()
    if not stations:
        print("No stations available. Aborting random mode.")
        return 3

    print(f"Random mode: keeping queue size <= {max_queue}. Ctrl+C to stop.")
    print(f"Available stations: {', '.join(stations)}")

    try:
        prev_targets: List[str] = []
        while True:
            # Try to top-up queue if below threshold
            current_targets = list_queue_targets()
            if len(current_targets) < max_queue:
                target_station = random.choice(stations)
                if add_to_queue(target_station):
                    print(f"Added: {target_station}")
                    # Refresh quickly to reflect change
                    current_targets = list_queue_targets()

            # Notify on queue changes
            if current_targets != prev_targets:
                if current_targets:
                    print("Queue updated:")
                    for i, t in enumerate(current_targets, 1):
                        print(f"  {i}. {t}")
                else:
                    print("Queue is now empty.")
                prev_targets = current_targets

            time.sleep(poll_sec)

    except KeyboardInterrupt:
        print("\nStopped random mode.")
        return 0
    except Exception as e:
        print(f"Random mode error: {e}")
        return 4


def clear_all_queues() -> int:
    print("Clearing all queue entries.")
    try:
        resp = api_client.get_pending_queue()
        queues = _normalize_list_payload(resp, "data")
    except Exception as e:
        print(f"Error fetching queue list: {e}")
        return 5

    if not queues:
        print("Queue already empty.")
        return 0

    removed = 0
    errors = 0
    for item in queues:
        qid = item.get("_id") or item.get("id")
        if not qid:
            continue
        try:
            api_client.remove_queue_by_id(qid)
            removed += 1
        except Exception as e:
            errors += 1
            print(f"Failed to remove queue {qid}: {e}")

    print(f"Removed {removed} queue entries.")
    if errors:
        print(f"Encountered {errors} errors while removing queues.")
        return 6
    return 0


def check_queue() -> int:
    """Print current pending queues. Returns 0 even if empty."""
    try:
        resp = api_client.get_pending_queue()
        queues = _normalize_list_payload(resp, "data")
    except Exception as e:
        print(f"Error fetching queue list: {e}")
        return 5

    if not queues:
        print("Queue is empty.")
        return 0

    print("Current queue:")
    for idx, item in enumerate(queues, 1):
        target = item.get("target", "")
        action = item.get("action", "Request")
        status = item.get("status", "")
        qid = item.get("_id") or item.get("id") or ""
        print(f"  {idx}. target={target} action={action} status={status} id={qid}")
    return 0


def main(argv: List[str]) -> int:
    if len(argv) < 2:
        return check_queue()

    target = argv[1].strip()
    if not target:
        print("Error: empty station name.")
        return 1

    if target.lower() == "random":
        return run_random_mode()
    if target.lower() == "clearall":
        return clear_all_queues()
    if target.lower() == "queue":
        return check_queue()
    else:
        return run_single_station(target)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
