#!/usr/bin/env python3
import os
import time

port = '/dev/rplidar'
print(f"Attempting to reset RPLidar on {port}...")
try:
    # Open serial port
    fd = os.open(port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    
    # Send reset command: 0xA5 0x40
    os.write(fd, b'\xa5\x40')
    print("Sent reset command (0xA5 0x40)")
    
    # Wait for reboot
    time.sleep(1.5)
    
    # Read any boot response
    try:
        response = os.read(fd, 1024)
        if response:
            print(f"Received response from Lidar:\n{response.decode(errors='ignore')}")
    except OSError:
        pass
        
    os.close(fd)
    print("Lidar reset sequence finished successfully.")
except Exception as e:
    print(f"Error resetting Lidar: {e}")
