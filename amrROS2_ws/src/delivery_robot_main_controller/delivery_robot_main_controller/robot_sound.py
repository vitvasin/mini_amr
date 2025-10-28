#!/usr/bin/env python3
import math
import os
import subprocess
import threading
import time

import rclpy
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.time import Time

from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
from nav_msgs.msg import OccupancyGrid

import tf2_ros
from tf2_ros import TransformException
from typing import Optional, Tuple
from . import api_client


class RobotSoundNode(Node):
    def __init__(self):
        super().__init__('robot_sound_node')

        # LiDAR data for obstacle detection
        self.create_subscription(LaserScan, 'scan', self.lidar_callback, 10)

        # External commands to trigger sound manually
        self.create_subscription(String, 'robot_sound_command', self.command_callback, 10)

        # Static map to distinguish known vs. new obstacles
        self.create_subscription(OccupancyGrid, 'map', self.map_callback, 1)

        self.threshold = 0.6  # metres
        self.sound_alarm_for_obstacle_enabled = True
        self.settings_refresh_interval = 5.0
        self.settings_fetch_in_progress = False
        self.settings_fetch_fail_log_interval = 15.0
        self.last_settings_fetch_error_log = 0.0

        self.alert_cooldown = 10.0  # seconds
        self.last_alert_time = 0.0

        self.sound_dir = '/home/smr/workspaces/mini_amr/amrROS2_ws/sounds'
        self.sound_map = {
            'thank_you': 'robot_thankyou.wav',
            'arrive_delivery': 'robot_delivery.wav',
            'arrive_target': 'robot_target.wav',
            'obstacle_alert': 'robot_obstacle.wav',
        }

        self.tf_buffer = tf2_ros.Buffer(cache_time=Duration(seconds=10.0))
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.tf_timeout = Duration(seconds=0.2)
        self.map_frame = 'map'

        self.map_msg = None
        self.map_lock = threading.Lock()
        self.map_received_logged = False
        self.map_warn_interval = 5.0
        self.last_missing_map_log = 0.0
        self.occupied_threshold = 65
        self.map_padding_cells = 1

        self.obstacle_alarm_suppressed_log_interval = 5.0
        self.last_obstacle_alarm_suppressed_log = 0.0

        self.create_timer(self.settings_refresh_interval, self._refresh_settings_timer)
        self._refresh_settings_from_api(initial=True)

        state = 'enabled' if self.sound_alarm_for_obstacle_enabled else 'disabled'
        self.get_logger().info(f'Obstacle sound alarm is {state}.')
        self.get_logger().info('✅ robot_sound_node started using .wav files')

    # ============================================================
    # 🔊 Play sound helper
    # ============================================================
    def play_sound(self, filename: str) -> None:
        file_path = os.path.join(self.sound_dir, filename)
        if os.path.exists(file_path):
            self.get_logger().info(f'🔊 Playing sound: {file_path}')
            try:
                subprocess.Popen(['aplay', '-q', file_path])  # -q = quiet mode
            except Exception as exc:  # pragma: no cover
                self.get_logger().error(f'Failed to play sound: {exc}')
        else:
            self.get_logger().warn(f'Sound file not found: {file_path}')

    # ============================================================
    # 🗺️ Map callback
    # ============================================================
    def map_callback(self, msg: OccupancyGrid) -> None:
        with self.map_lock:
            self.map_msg = msg
        if not self.map_received_logged:
            self.map_received_logged = True
            width = msg.info.width
            height = msg.info.height
            resolution = msg.info.resolution
            self.get_logger().info(
                f'Received map (width={width}, height={height}, resolution={resolution:.3f} m/cell)'
            )

    # ============================================================
    # 🚨 LiDAR callback
    # ============================================================
    def lidar_callback(self, msg: LaserScan) -> None:
        obstacle_detected = False

        if self.map_available():
            transform = self.lookup_transform(msg.header)
            if transform is None:
                return
            obstacle_detected = self.is_new_obstacle(transform, msg)
        else:
            self.log_missing_map_once()
            obstacle_detected = self._has_close_obstacle(msg)

        if not obstacle_detected:
            return

        now = time.time()
        if now - self.last_alert_time < self.alert_cooldown:
            return

        if not self.sound_alarm_for_obstacle_enabled:
            self.last_alert_time = now
            self.log_obstacle_alarm_suppressed()
            return

        self.last_alert_time = now
        threading.Thread(
            target=self.play_sound,
            args=(self.sound_map['obstacle_alert'],),
            daemon=True,
        ).start()
        self.get_logger().warn('⚠️ New obstacle detected!')

    # ============================================================
    # 📣 Command callback
    # ============================================================
    def command_callback(self, msg: String) -> None:
        cmd = msg.data.strip()
        if cmd in self.sound_map:
            threading.Thread(
                target=self.play_sound,
                args=(self.sound_map[cmd],),
                daemon=True,
            ).start()
            self.get_logger().info(f'🔔 Received sound command: {cmd}')
        else:
            self.get_logger().warn(f'Unknown sound command: {cmd}')

    # ============================================================
    # 🔍 Helpers
    # ============================================================
    def map_available(self) -> bool:
        with self.map_lock:
            return self.map_msg is not None

    def log_missing_map_once(self) -> None:
        now = self.get_clock().now().nanoseconds / 1e9
        if now - self.last_missing_map_log > self.map_warn_interval:
            self.last_missing_map_log = now
            self.get_logger().warn('Map not available yet; skipping obstacle classification.')

    def lookup_transform(self, header) -> Optional[Tuple[float, float, float]]:
        try:
            transform = self.tf_buffer.lookup_transform(
                self.map_frame,
                header.frame_id,
                Time.from_msg(header.stamp),
                self.tf_timeout,
            )
        except TransformException as exc:
            self.get_logger().debug(f'Failed to lookup transform to {self.map_frame}: {exc}')
            return None

        translation = transform.transform.translation
        rotation = transform.transform.rotation
        yaw = self.quaternion_to_yaw(rotation)
        return (translation.x, translation.y, yaw)

    def is_new_obstacle(self, transform: Tuple[float, float, float], scan: LaserScan) -> bool:
        trans_x, trans_y, yaw = transform
        cos_yaw = math.cos(yaw)
        sin_yaw = math.sin(yaw)

        any_new = False
        for index, distance in enumerate(scan.ranges):
            if not math.isfinite(distance) or distance >= self.threshold:
                continue

            angle = scan.angle_min + index * scan.angle_increment
            base_x = distance * math.cos(angle)
            base_y = distance * math.sin(angle)

            map_x = trans_x + cos_yaw * base_x - sin_yaw * base_y
            map_y = trans_y + sin_yaw * base_x + cos_yaw * base_y

            if not self.is_known_obstacle((map_x, map_y)):
                any_new = True
                break

        return any_new

    def is_known_obstacle(self, point_xy: Tuple[float, float]) -> bool:
        with self.map_lock:
            map_msg = self.map_msg

        if map_msg is None:
            return False

        info = map_msg.info
        origin = info.origin
        resolution = info.resolution
        origin_yaw = self.quaternion_to_yaw(origin.orientation)
        cos_o = math.cos(origin_yaw)
        sin_o = math.sin(origin_yaw)

        dx = point_xy[0] - origin.position.x
        dy = point_xy[1] - origin.position.y

        # Rotate into map grid frame (inverse of origin orientation)
        map_x = cos_o * dx + sin_o * dy
        map_y = -sin_o * dx + cos_o * dy

        mx = int(math.floor(map_x / resolution))
        my = int(math.floor(map_y / resolution))

        width = info.width
        height = info.height

        for offset_x in range(-self.map_padding_cells, self.map_padding_cells + 1):
            for offset_y in range(-self.map_padding_cells, self.map_padding_cells + 1):
                gx = mx + offset_x
                gy = my + offset_y
                if gx < 0 or gy < 0 or gx >= width or gy >= height:
                    continue
                index = gy * width + gx
                value = map_msg.data[index]
                if value >= self.occupied_threshold:
                    return True

        return False

    @staticmethod
    def quaternion_to_yaw(quaternion) -> float:
        x = quaternion.x
        y = quaternion.y
        z = quaternion.z
        w = quaternion.w
        siny_cosp = 2.0 * (w * z + x * y)
        cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
        return math.atan2(siny_cosp, cosy_cosp)

    @staticmethod
    def _parameter_to_bool(value) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return value.strip().lower() in ('1', 'true', 'yes', 'on')
        return bool(value)

    def _refresh_settings_timer(self):
        self._refresh_settings_from_api()

    def _refresh_settings_from_api(self, initial: bool = False):
        if self.settings_fetch_in_progress:
            return
        self.settings_fetch_in_progress = True
        threading.Thread(
            target=self._fetch_settings_from_api,
            args=(initial,),
            daemon=True,
        ).start()

    def _fetch_settings_from_api(self, initial: bool = False) -> None:
        try:
            params = api_client.get_system_parameters()
            data = params.get('data', [])
            if isinstance(data, list) and data:
                config = data[0]
                new_value = self._parameter_to_bool(config.get('isSoundAlarmForObstacle', 0))
                if new_value != self.sound_alarm_for_obstacle_enabled or initial:
                    self.sound_alarm_for_obstacle_enabled = new_value
                    state = 'enabled' if new_value else 'disabled'
                    self.get_logger().info(f'Obstacle sound alarm {state} (API).')
        except Exception as exc:
            now = time.time()
            if now - self.last_settings_fetch_error_log >= self.settings_fetch_fail_log_interval:
                self.last_settings_fetch_error_log = now
                self.get_logger().warn(f'Failed to refresh obstacle sound setting: {exc}')
        finally:
            self.settings_fetch_in_progress = False



    def log_obstacle_alarm_suppressed(self) -> None:
        now = time.time()
        if now - self.last_obstacle_alarm_suppressed_log >= self.obstacle_alarm_suppressed_log_interval:
            self.last_obstacle_alarm_suppressed_log = now
            self.get_logger().info('Obstacle detected but sound alarm disabled.')


    def _has_close_obstacle(self, scan: LaserScan) -> bool:
        for distance in scan.ranges:
            if math.isfinite(distance) and distance < self.threshold:
                return True
        return False


def main(args=None) -> None:
    rclpy.init(args=args)
    node = RobotSoundNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('🔚 robot_sound_node stopped by user.')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
