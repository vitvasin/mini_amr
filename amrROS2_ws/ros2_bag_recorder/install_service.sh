#!/bin/bash
set -e

RECORDER_DIR="/home/smr/workspaces/mini_amr/amrROS2_ws/ros2_bag_recorder"
LAUNCH_SCRIPT="$RECORDER_DIR/start_recorder.sh"
SERVICE_FILE="/tmp/rolling_recorder.service"

echo "======================================"
echo "Installing Rolling Recorder Service..."
echo "======================================"

# 1. Create the ROS2 launcher script
echo "-> Creating launch wrapper script at $LAUNCH_SCRIPT"
cat << 'EOT' > "$LAUNCH_SCRIPT"
#!/bin/bash

# Source ROS 2 Jazzy
source /opt/ros/jazzy/setup.bash

# Source Workspace
source /home/smr/workspaces/mini_amr/amrROS2_ws/install/setup.bash

# Export Environment Variables
export ROS_DOMAIN_ID=31
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI=/home/smr/cyclonedds.xml
export QT_QPA_PLATFORM=xcb

# Allow the script to talk to the local UI (for Zenity popups)
export DISPLAY=:0

# Navigate to the correct directory and run the python script
cd /home/smr/workspaces/mini_amr/amrROS2_ws/ros2_bag_recorder
python3 rolling_recorder.py
EOT

chmod +x "$LAUNCH_SCRIPT"

# 2. Create the systemd service file
echo "-> Creating systemd service file"
cat << EOT > "$SERVICE_FILE"
[Unit]
Description=AMR Rolling Bag Recorder Service
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$RECORDER_DIR
ExecStart=/bin/bash $LAUNCH_SCRIPT
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOT

sudo mv "$SERVICE_FILE" /etc/systemd/system/rolling_recorder.service
sudo chmod 644 /etc/systemd/system/rolling_recorder.service

# 3. Enable and start the service
echo "-> Reloading systemd daemon"
sudo systemctl daemon-reload

echo "-> Enabling the service to start on boot"
sudo systemctl enable rolling_recorder.service

echo "-> Starting the service"
sudo systemctl restart rolling_recorder.service

echo ""
echo "======================================"
echo "Installation Complete!"
echo "Check status directly: systemctl status rolling_recorder.service"
echo "Tail background logs:  journalctl -u rolling_recorder.service -f"
echo "======================================"
