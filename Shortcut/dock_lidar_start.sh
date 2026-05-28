#!/bin/bash

# ฟังก์ชัน: หยุด process เดิมถ้ามี
kill_old_autodock() {
  echo "🔍 Checking for existing dock_lidar_launch.py..."

  PID=$(pgrep -f "dock_lidar_launch.py")

  if [ -n "$PID" ]; then
    echo "⚠️  Found existing dock_lidar_launch.py process (PID: $PID), killing it..."
    kill "$PID"
    sleep 1
  else
    echo "✅ No existing dock_lidar_launch.py process found."
  fi
}

# เริ่มทำงาน
echo "🚀 Dock Lidar Launcher Script Starting..."
kill_old_autodock

# เปิด terminal เพื่อ launch ระบบ autodock
gnome-terminal -- bash -c "source ~/.bashrc; ros2 launch dock_lidar dock_lidar_launch.py; exec bash"

# รอ 2 วินาที
sleep 2

# เปิด terminal เพื่อส่ง action goal
gnome-terminal -- bash -c "source ~/.bashrc; ros2 topic pub --once /command_dock std_msgs/String 'data: start'; exec bash"

echo "✅ Done!"