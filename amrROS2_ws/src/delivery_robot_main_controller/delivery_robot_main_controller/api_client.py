# api_client.py

import requests
import json

API_BASE_URL = "http://localhost:3000"

# Queue APIs
def get_pending_queue():
    url = f"{API_BASE_URL}/api/queue/list"
    response = requests.get(url, timeout=3)
    response.raise_for_status()
    return response.json()

def add_queue(data):
    url = f"{API_BASE_URL}/api/queue/add"
    payload = data if data is not None else {}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload, timeout=5)
    response.raise_for_status()
    return response.json()

def update_queue_status(queue_id, status):
    url = f"{API_BASE_URL}/api/queue/updateStatus"
    payload = {"id": queue_id, "status": status}
    response = requests.post(url, json=payload, timeout=3)
    response.raise_for_status()
    return response.json()

def remove_queue_by_id(queue_id):
    url = f"{API_BASE_URL}/api/queue/remove"
    headers = {"Content-Type": "application/json"}
    payload = {"id": queue_id}
    response = requests.post(url, headers=headers, json=payload, timeout=3)
    response.raise_for_status()
    return response.json()

def add_request_queue(target: str):
    """Add a Request queue for a given target station name.

    - Validates that `target` exists in /api/station/list
    - If station not found, return False
    - Checks /api/queue/list for an existing Request with same target; if found, do not add and return True
    - If not found, posts to /api/queue/add with action=Request and target

    Returns API response dict on success, True if already present, or False if station missing.
    """
    # Validate station exists
    try:
        stations_resp = get_station_list()
        stations = stations_resp.get("data", [])
        if isinstance(stations, str):
            stations = json.loads(stations)
        exists = any(s.get("name") == target for s in stations)
        if not exists:
            return False
    except Exception:
        # If listing stations fails, surface the exception to caller
        raise

    # Check if a Request for the same target already exists
    try:
        q_resp = get_pending_queue()
        q_list = q_resp.get("data", [])
        if isinstance(q_list, str):
            q_list = json.loads(q_list)
        for item in q_list:
            if item.get("target") == target and item.get("action", "Request") == "Request":
                return True
    except Exception:
        # If listing queues fails, let add proceed (server will enforce uniqueness if any)
        pass

    # Add queue as Request following Postman payload structure
    form = {
        "action": "Request",
        "target": target,
        "boxNumber": "1",
        "sender": "api_client",
        "status": "Pending",
    }
    return add_queue(form)

def remove_request_queue_by_target(target: str) -> int:
    """Remove all Request queues with matching target name.

    - Lists queues from /api/queue/list
    - Removes only entries where action == "Request" and target == target
    - Skips entries with action == "Delivery"

    Returns number of removed entries.
    """
    removed = 0
    # Fetch current queue list
    data = get_pending_queue()
    queue_list = data.get("data", [])
    if isinstance(queue_list, str):
        queue_list = json.loads(queue_list)

    for item in queue_list:
        try:
            if item.get("target") == target and item.get("action", "Request") == "Request":
                qid = item.get("_id") or item.get("id")
                if qid is not None:
                    remove_queue_by_id(qid)
                    removed += 1
        except Exception:
            # Continue attempting other removals even if one fails
            continue

    return removed

# Station APIs
def get_station_list():
    url = f"{API_BASE_URL}/api/station/list"
    response = requests.get(url, timeout=3)
    response.raise_for_status()
    return response.json()

def add_station(data):
    url = f"{API_BASE_URL}/api/station/add"
    response = requests.post(url, data=data, timeout=3)
    response.raise_for_status()
    return response.json()

def remove_station(station_id):
    url = f"{API_BASE_URL}/api/station/remove"
    payload = {"id": station_id}
    response = requests.post(url, json=payload, timeout=3)
    response.raise_for_status()
    return response.json()

# Params APIs
def get_system_parameters():
    url = f"{API_BASE_URL}/api/params/list"
    response = requests.get(url, timeout=3)
    response.raise_for_status()
    return response.json()

def add_params(data):
    url = f"{API_BASE_URL}/api/params/add"
    response = requests.post(url, data=data, timeout=3)
    response.raise_for_status()
    return response.json()

def update_params(params):
    url = f"{API_BASE_URL}/api/params/update"
    response = requests.post(url, json=params, timeout=3)
    response.raise_for_status()
    return response.json()

# Mapping APIs
def add_mapping(data):
    url = f"{API_BASE_URL}/api/mapping/add"
    response = requests.post(url, data=data, timeout=3)
    response.raise_for_status()
    return response.json()

def list_mapping():
    url = f"{API_BASE_URL}/api/mapping/list"
    response = requests.get(url, timeout=3)
    response.raise_for_status()
    return response.json()

def update_mapping(mapping):
    url = f"{API_BASE_URL}/api/mapping/update"
    response = requests.post(url, json=mapping, timeout=3)
    response.raise_for_status()
    return response.json()

# History APIs
def add_history(data):
    url = f"{API_BASE_URL}/api/history/add"
    response = requests.post(url, data=data, timeout=3)
    response.raise_for_status()
    return response.json()

def list_history():
    url = f"{API_BASE_URL}/api/history/list"
    response = requests.get(url, timeout=3)
    response.raise_for_status()
    return response.json()

# Robot Status APIs
def get_robot_status():
    url = f'{API_BASE_URL}/api/robotstatus/list'
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.json()

def update_robot_status(status_id, state):
    url = f"{API_BASE_URL}/api/robotstatus/updatestatus"
    if not status_id:
        raise ValueError("status_id is required to update robot status")
    payload = {"id": status_id, "status": state}
    response = requests.post(url, json=payload, timeout=3)
    response.raise_for_status()
    return response.json()

def update_robot_position(status_id, position):
    url = f"{API_BASE_URL}/api/robotStatus/updateposition"
    if not status_id:
        raise ValueError("status_id is required to update robot position")
    payload = {"id": status_id, "position": position}
    response = requests.post(url, json=payload, timeout=3)
    response.raise_for_status()
    return response.json()

def update_robot_charging(status_id, charging):
    url = f"{API_BASE_URL}/api/robotStatus/updatecharging"
    if not status_id:
        raise ValueError("status_id is required to update robot charging")
    payload = {"id": status_id, "charging": charging}
    response = requests.post(url, json=payload, timeout=3)
    response.raise_for_status()
    return response.json()

def update_robot_door(status_id, door_payload):
    url = f"{API_BASE_URL}/api/robotStatus/updatedoor"
    if not status_id:
        raise ValueError("status_id is required to update robot door")
    payload = {"id": status_id, "door": door_payload}
    response = requests.post(url, json=payload, timeout=3)
    response.raise_for_status()
    return response.json()

def update_robot_box(status_id, box_payload):
    url = f"{API_BASE_URL}/api/robotStatus/updatebox"
    if not status_id:
        raise ValueError("status_id is required to update robot box")
    payload = {"id": status_id, "box": box_payload}
    response = requests.post(url, json=payload, timeout=3)
    response.raise_for_status()
    return response.json()

# State of Charge APIs
def add_soc(soc):
    url = f"{API_BASE_URL}/api/stateOfCharge/add"
    response = requests.post(url, data={"soc": soc}, timeout=3)
    response.raise_for_status()
    return response.json()

def update_soc(soc):
    url = f"{API_BASE_URL}/api/stateOfCharge/update"
    response = requests.post(url, json={"soc": soc}, timeout=3)
    response.raise_for_status()
    return response.json()

def list_soc():
    url = f"{API_BASE_URL}/api/stateOfCharge/list"
    response = requests.get(url, timeout=3)
    response.raise_for_status()
    return response.json()
