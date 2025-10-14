#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
import subprocess
import threading
import time
import os


class RobotSoundNode(Node):
    def __init__(self):
        super().__init__('robot_sound_node')

        # 🔸 Subscribe LiDAR
        self.create_subscription(LaserScan, 'scan', self.lidar_callback, 10)

        # 🔸 Subscribe คำสั่งจาก Node อื่น
        self.create_subscription(String, 'robot_sound_command', self.command_callback, 10)

        # 🔸 ระยะตรวจจับสิ่งกีดขวาง
        self.threshold = 0.6  # เมตร
        self.alert_cooldown = 10.0  # วินาที (กันพูดซ้ำเร็วเกิน)
        self.last_alert_time = 0.0

        # 🔸 path เก็บไฟล์เสียง
        self.sound_dir = "/home/smr/workspaces/mini_amr/amrROS2_ws/sounds"

        # 🔸 map ชื่อคำสั่ง → ไฟล์เสียง
        self.sound_map = {
            "thank_you": "robot_thankyou.wav",
            "arrive_delivery": "robot_delivery.wav",
            "arrive_target": "robot_target.wav",
            "obstacle_alert": "robot_obstacle.wav",
            "start": "robot_start.wav"
        }
        self.get_logger().info("✅ robot_sound_node started using .wav files")

    # ============================================================
    # 🔊 ฟังก์ชันเล่นเสียง
    # ============================================================
    def play_sound(self, filename):
        """เล่นเสียงจากไฟล์ .wav"""
        file_path = os.path.join(self.sound_dir, filename)
        if os.path.exists(file_path):
            self.get_logger().info(f"🔊 Playing sound: {file_path}")
            try:
                subprocess.Popen(['aplay', '-q', file_path])  # -q = quiet mode
            except Exception as e:
                self.get_logger().error(f"Failed to play sound: {e}")
        else:
            self.get_logger().warn(f"Sound file not found: {file_path}")

    # ============================================================
    # 🚨 Callback: LiDAR พบสิ่งกีดขวาง
    # ============================================================
    def lidar_callback(self, msg: LaserScan):
        min_range = min(msg.ranges)
        if min_range < self.threshold:
            now = time.time()
            if now - self.last_alert_time > self.alert_cooldown:
                self.last_alert_time = now
                self.get_logger().warn(f"⚠️ Obstacle detected at {min_range:.2f} m!")
                threading.Thread(target=self.play_sound,
                                 args=(self.sound_map["obstacle_alert"],),
                                 daemon=True).start()

    # ============================================================
    # 📣 Callback: รับคำสั่งเสียงจาก Node อื่น
    # ============================================================
    def command_callback(self, msg: String):
        cmd = msg.data.strip()
        if cmd in self.sound_map:
            filename = self.sound_map[cmd]
            threading.Thread(target=self.play_sound, args=(filename,), daemon=True).start()
            self.get_logger().info(f"🔔 Received sound command: {cmd}")
        else:
            self.get_logger().warn(f"Unknown sound command: {cmd}")


def main(args=None):
    rclpy.init(args=args)
    node = RobotSoundNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("🔚 robot_sound_node stopped by user.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()