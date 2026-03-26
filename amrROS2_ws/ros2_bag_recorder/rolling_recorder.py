import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from action_msgs.msg import GoalStatusArray
import subprocess
import os
import time
import shutil
import signal
import sys
from datetime import datetime

class RollingRecorder(Node):
    def __init__(self):
        super().__init__('rolling_recorder')

        # --- CONFIGURATION ---
        self.declare_parameter('bag_dir', '/media/smr/LaCie/ROS_LOG/rosbag/robot_recordings')
        self.declare_parameter('chunk_duration_sec', 300)
        self.declare_parameter('keep_buffer_sec', 600)
        self.declare_parameter('min_disk_space_gb', 1.0)
        
        self.bag_dir = self.get_parameter('bag_dir').value
        self.chunk_duration = self.get_parameter('chunk_duration_sec').value
        self.keep_buffer_sec = self.get_parameter('keep_buffer_sec').value
        self.min_disk_space_bytes = self.get_parameter('min_disk_space_gb').value * 1024 * 1024 * 1024
        
        # We only create the dir if we're not pointing to a missing root mount
        try:
            if not os.path.exists(self.bag_dir):
                os.makedirs(self.bag_dir)
        except OSError as e:
            self.get_logger().error(f"Failed to create bag directory {self.bag_dir}: {e}")

        # --- STATE ---
        self.last_activity_time = time.time()  # Start with a grace period
        self.bag_proc = None
        self.current_output_path = None
        self.last_state = "ACTIVE"

        # --- SUBSCRIPTIONS ---
        self.cmd_sub = self.create_subscription(Twist, '/cmd_vel', self.cmd_cb, 10)
        self.nav_sub = self.create_subscription(GoalStatusArray, '/navigate_to_pose/_action/status', self.nav_cb, 10)

        # Check disk space initially before starting
        if self.check_disk_space():
            self.start_bag_process("ACTIVE_RUN")

        # Timer to clean up unneeded files every 30 seconds
        self.create_timer(30.0, self.cleanup_loop)
        
        # Timer for real-time terminal status updating
        self.create_timer(1.0, self.status_loop)
        
        self.get_logger().info(f"Rolling Recorder Started. Saving to {self.bag_dir}")

    def cmd_cb(self, msg):
        if abs(msg.linear.x) > 0.01 or abs(msg.angular.z) > 0.01:
            self.last_activity_time = time.time()

    def nav_cb(self, msg):
        # 1 = STATUS_ACCEPTED, 2 = STATUS_EXECUTING
        if any(s.status in [1, 2] for s in msg.status_list): 
            self.last_activity_time = time.time()

    def check_disk_space(self):
        try:
            free_space = shutil.disk_usage(self.bag_dir).free
        except FileNotFoundError:
            # SSD Disconnected Vulnerability Fix
            self.get_logger().fatal("SSD DISCONNECTED! ROS Bag Record Stop.")
            print("\n=======================================================")
            print("= SSD DISCONNECTED! ROS BAG RECORD STOP. EXITING NODE =")
            print("=======================================================\n")
            try:
                subprocess.Popen(['zenity', '--error', '--text', 'SSD Disconnected! ROS Bag Record Stopped.'])
            except Exception:
                pass
            
            self.stop_bag_process()
            os._exit(1)
            return False

        if free_space < self.min_disk_space_bytes:
            self.get_logger().warn(f"Disk space low! ({free_space/(1024**3):.2f} GB free). Minimum required: {self.min_disk_space_bytes/(1024**3):.2f} GB.")
            return False
        return True

    def start_bag_process(self, prefix="RUN"):
        if self.bag_proc is not None:
            return

        # Separate directory by date
        date_str = datetime.now().strftime("%Y_%m_%d")
        date_folder = os.path.join(self.bag_dir, date_str)
        try:
            if not os.path.exists(date_folder):
                os.makedirs(date_folder)
        except OSError as e:
            self.get_logger().error(f"\nFailed to create date directory {date_folder}: {e}")
            return

        # Determine highest existing run number
        run_id = 1
        try:
            existing_runs = [d for d in os.listdir(date_folder) if os.path.isdir(os.path.join(date_folder, d)) and d.startswith("run_")]
            run_numbers = []
            for d in existing_runs:
                try:
                    num = int(d.split("_")[1])
                    run_numbers.append(num)
                except ValueError:
                    pass
            if run_numbers:
                run_id = max(run_numbers) + 1
        except OSError:
            pass
            
        time_str = datetime.now().strftime("%H_%M_%S")
        output_path = os.path.join(date_folder, f"{prefix}_{run_id}_{time_str}")
        self.current_output_path = output_path

        cmd = [
            'ros2', 'bag', 'record',
            '-s', 'mcap',
            '-o', output_path,
            '--max-bag-duration', str(self.chunk_duration),
            '-e', "(.*)/costmap(.*)|(.*)/voxels(.*)|(.*)/visualization_marker(.*)",
            '--topics', '/scan', '/tf', '/tf_static', '/imu', '/odom', '/initialpose', '/cmd_vel', '/map', '/map_metadata'
        ]
        
        self.bag_proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.get_logger().info(f"\nStarted new ros2 bag record in: {output_path}")

    def stop_bag_process(self):
        if self.bag_proc is not None:
            self.get_logger().info("\nStopping ros2 bag record process...")
            if self.bag_proc.poll() is None:
                self.bag_proc.send_signal(signal.SIGINT)
                try:
                    self.bag_proc.wait(timeout=5.0)
                except subprocess.TimeoutExpired:
                    self.get_logger().warn("ros2 bag record did not stop gracefully, killing it.")
                    self.bag_proc.kill()
                    self.bag_proc.wait() # Zombie Process Fix
            self.bag_proc = None

    def prune_old_data(self, current_time, force_prune=False):
        """ Deletes files exactly older than the keep buffer """
        pruned_anything = False
        cutoff_age_sec = self.chunk_duration if force_prune else self.keep_buffer_sec
        
        for root, dirs, files in os.walk(self.bag_dir, topdown=False):
            # Only look in subdirectories
            if root == self.bag_dir:
                continue
                
            # NEVER DELETE ACTIVE MISSION LOGS OR SAVED PRE-EVENT BUFFERS!
            if not force_prune:
                if 'ACTIVE_RUN' in root or 'ACTIVE_BUFFER_SAVED' in files:
                    continue

            for file in files:
                if file.endswith('.mcap') or file.endswith('.db3'):
                    file_path = os.path.join(root, file)
                    mtime = os.path.getmtime(file_path)
                    
                    if (current_time - mtime) > cutoff_age_sec:
                        try:
                            # Catch OSError to prevent Brittle loop exits
                            os.remove(file_path)
                            self.get_logger().info(f"\nDeleting old bag file: {file}")
                            pruned_anything = True
                        except OSError as e:
                            self.get_logger().warn(f"\nFailed to delete {file}: {e}")
            
            if os.path.exists(root):
                try:
                    contents = os.listdir(root)
                    if len(contents) == 0:
                        shutil.rmtree(root)
                        self.get_logger().info(f"\nDeleting empty folder: {os.path.basename(root)}")
                        pruned_anything = True
                    # Also clean up folders that ONLY have metadata.yaml left over (all mcap files were pruned)
                    elif len(contents) == 1 and contents[0] == 'metadata.yaml':
                        shutil.rmtree(root)
                        self.get_logger().info(f"\nDeleting leftover metadata folder: {os.path.basename(root)}")
                        pruned_anything = True
                except OSError as e:
                    self.get_logger().warn(f"\nFailed to delete directory {root}: {e}")
                
        return pruned_anything

    def status_loop(self):
        current_time = time.time()
        time_since = current_time - self.last_activity_time
        state_str = "ACTIVE" if time_since <= self.keep_buffer_sec else "IDLE  "
        
        # Detect state transitions and restart bags to isolate records
        if self.last_state == "IDLE  " and state_str == "ACTIVE":
            self.get_logger().info("\n*** ROBOT ACTIVATED! Locking previous idle buffer to save pre-event data. ***")
            if self.current_output_path and os.path.exists(self.current_output_path):
                with open(os.path.join(self.current_output_path, 'ACTIVE_BUFFER_SAVED'), 'w') as f:
                    f.write("Saved pre-trigger idle buffer.")
            self.stop_bag_process()
            self.start_bag_process("ACTIVE_RUN")
            
        elif self.last_state == "ACTIVE" and state_str == "IDLE  ":
            self.get_logger().info("\n*** ROBOT ENTERED IDLE COOLDOWN. Activating garbage collector. ***")
            self.stop_bag_process()
            self.start_bag_process("IDLE_RUN")
            
        self.last_state = state_str

        # Subprocess crash check (Fake Recording Illusion fix)
        if self.bag_proc is not None:
            if self.bag_proc.poll() is not None:
                self.get_logger().error("\nrosbag process crashed unexpectedly! Resetting state...")
                self.bag_proc = None
        
        try:
            free_space = shutil.disk_usage(self.bag_dir).free / (1024**3)
        except Exception:
            free_space = 0.0
            
        recording_str = "YES" if self.bag_proc is not None else "NO "
        
        sys.stdout.write(f"\r[Rolling Recorder] Status: {state_str} | Idle for: {int(time_since):4d}s | Free Disk: {free_space:.2f} GB | Recording: {recording_str}    ")
        sys.stdout.flush()

    def cleanup_loop(self):
        current_time = time.time()
        time_since_activity = current_time - self.last_activity_time
        
        # 1. Disk Space Check
        has_space = self.check_disk_space()
        
        if not has_space:
            self.stop_bag_process()
            self.get_logger().info("\nAggressively pruning old files due to low disk space...")
            self.prune_old_data(current_time, force_prune=True)
            return

        # 2. Activity Check & Pruning
        if time_since_activity > self.keep_buffer_sec:
            # self.get_logger().info("\nRobot idle: Scanning for old buffers to prune...")
            self.prune_old_data(current_time, force_prune=False)
            
        # 3. Ensure recording is active if we have space
        if self.bag_proc is None and has_space:
            self.start_bag_process("ACTIVE_RUN" if time_since_activity <= self.keep_buffer_sec else "IDLE_RUN")


def main(args=None):
    rclpy.init(args=args)
    node = RollingRecorder()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_bag_process()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()