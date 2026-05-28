#!/usr/bin/env python3
import os
import subprocess
import threading
import time

SOUND_CARD = 0  # ALSA card number (ดูได้จาก: aplay -l)

import rclpy
from rclpy.node import Node

from std_msgs.msg import String

from . import api_client


class RobotSoundNode(Node):
    def __init__(self):
        super().__init__('robot_sound_node')

        # External commands to trigger sound (sent by main_controller_node)
        self.create_subscription(String, 'robot_sound_command', self.command_callback, 10)

        self.settings_refresh_interval = 5.0
        self.settings_fetch_in_progress = False
        self.settings_fetch_fail_log_interval = 15.0
        self.last_settings_fetch_error_log = 0.0

        self.sound_dir = '/home/smr/workspaces/mini_amr/amrROS2_ws/sounds'
        self.sound_map = {
            'thank_you': 'robot_thankyou.wav',
            'arrive_delivery': 'robot_delivery.wav',
            'arrive_target': 'robot_target.wav',
            'obstacle_alert': 'robot_obstacle.wav',
            'safe_stop': 'robot_safestop.wav',
            'lost': 'robot_lost.wav',
        }

        self.soundLevel = 50

        self.create_timer(self.settings_refresh_interval, self._refresh_settings_timer)
        self._refresh_settings_from_api(initial=True)

        self.get_logger().info('✅ robot_sound_node started using .wav files')

    # ============================================================
    # 🔊 Play sound helper
    # ============================================================
    def play_sound(self, filename: str) -> None:
        file_path = os.path.join(self.sound_dir, filename)
        if os.path.exists(file_path):
            # 🔥 สำคัญมาก: ตั้ง volume ให้ USB speaker ทุกครั้งก่อนเล่น
            try:
                volume_str = f"{self.soundLevel}%"
                subprocess.call(["amixer", "-c", str(SOUND_CARD), "sset", "PCM", volume_str, "unmute"])
            except Exception as e:
                self.get_logger().error(f"Failed to set volume: {e}")

            self.get_logger().info(f'🔊 Playing sound: {file_path}')
            # ใช้ aplay ตรงผ่าน ALSA/USB (การ์ด 1) เพราะ paplay ไม่ออกเสียงบนเครื่องนี้
            try:
                subprocess.Popen([
                    'aplay',
                    '-D', f'plughw:{SOUND_CARD},0',
                    '-c', '2',
                    '-f', 'S16_LE',
                    '-r', '48000',
                    file_path
                ])
            except Exception as e:
                self.get_logger().error(f"Failed to play sound with aplay: {e}")
        else:
            self.get_logger().warn(f'Sound file not found: {file_path}')

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
    # ⚙️ Settings
    # ============================================================
    @staticmethod
    def _parameter_to_int_range(value, minimum: int = 0, maximum: int = 100):
        if value is None:
            return None
        try:
            if isinstance(value, str):
                value = value.strip()
                if not value:
                    return None
                numeric = float(value)
            else:
                numeric = float(value)
        except (TypeError, ValueError):
            return None
        return max(minimum, min(maximum, int(numeric)))

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
                sound_level = self._parameter_to_int_range(config.get('soundLevel'))
                if sound_level is not None and (initial or sound_level != self.soundLevel):
                    self.soundLevel = sound_level
                    self.get_logger().info(f'Sound volume set to {sound_level}% (API).')
        except Exception as exc:
            now = time.time()
            if now - self.last_settings_fetch_error_log >= self.settings_fetch_fail_log_interval:
                self.last_settings_fetch_error_log = now
                self.get_logger().warn(f'Failed to refresh sound settings: {exc}')
        finally:
            self.settings_fetch_in_progress = False


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
