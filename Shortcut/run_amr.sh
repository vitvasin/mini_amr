#!/usr/bin/env bash
set -e

# Terminal 1: MongoDB
gnome-terminal --title="MongoDB" \
  -- bash -lc "echo '>>> Starting MongoDB'; sudo systemctl start mongod; exec bash" &

# Terminal 2: Backend Server
gnome-terminal --title="Backend Server" \
  -- bash -lc "cd ~/workspaces/backend && echo '>>> npm run server'; npm run server; exec bash" &

# Terminal 3: Navigation AMCL
gnome-terminal --title="Navigation AMCL" \
  -- bash -lc "cd ~/workspaces/mini_amr/Shortcut && echo '>>> ./navigation_amcl.sh'; ./navigation_amcl.sh; exec bash" &

# Terminal 4: AutoDock
gnome-terminal --title="AutoDock" \
  -- bash -lc "echo '>>> ros2 launch action_autodock auto_dock_launch.py'; ros2 launch action_autodock auto_dock_launch.py; exec bash" &

# Terminal 5: Delivery Controller
gnome-terminal --title="Delivery Controller" \
  -- bash -lc "echo '>>> ros2 launch delivery_robot_main_controller delivery.launch.py'; ros2 launch delivery_robot_main_controller delivery.launch.py; exec bash" &