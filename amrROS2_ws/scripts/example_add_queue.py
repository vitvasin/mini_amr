#!/usr/bin/env python3
"""
Example: add a Request queue without external parameters.

Adjust TARGET_STATION below as needed.
"""

from delivery_robot_main_controller import api_client
import requests

# Change this to the desired station name
TARGET_STATION = "canteen"


def main() -> int:
    try:
        result = api_client.add_request_queue(TARGET_STATION)
        #result = api_client.remove_request_queue_by_target(TARGET_STATION)
    except requests.HTTPError as e:
        resp = getattr(e, "response", None)
        code = getattr(resp, "status_code", "?")
        body = getattr(resp, "text", "")
        print(f"HTTP {code} while adding Request queue: {body}")
        return 2
    except Exception as e:
        print(f"Error while adding Request queue: {e}")
        return 2

    if result is False:
        print(f"Station not found: {TARGET_STATION}")
        return 1
    if result is True:
        print(f"Request already exists for target: {TARGET_STATION}")
        return 0

    print(f"Added Request queue for target '{TARGET_STATION}': {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

