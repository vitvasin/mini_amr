import subprocess
import time
import os

def check_hz(topic):
    print(f"Checking {topic}...")
    cmd = ["ros2", "topic", "hz", "--window", "3", topic]
    # Force line buffering if possible? No easy way for via subprocess alone without stdbuf
    # But let's see what raw popen gives.
    
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    try:
        outs, errs = proc.communicate(timeout=5)
        print("Communicate returned.")
        print("STDOUT:", outs)
        print("STDERR:", errs)
    except subprocess.TimeoutExpired:
        print("Timeout expired!")
        proc.kill()
        outs, errs = proc.communicate()
        print("Captured after kill:")
        print("STDOUT:", outs)
        print("STDERR:", errs)

# Use a topic that we saw in the list, e.g. /rosout if available, or just check /odom
# The user's trace showed these topics missing recently, so this test might just confirm they are missing.
# Let's check /rosout or /parameter_events which usually exist.
check_hz("/rosout")
