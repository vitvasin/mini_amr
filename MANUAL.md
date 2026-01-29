# Mini AMR Workspace Manual

This manual provides an overview of the configuration and operation of the Mini AMR workspace, including shell environment settings and autostart services.

## 1. Workspace Structure

The primary workspace is located at:
- **Root**: `/home/smr/workspaces/mini_amr`
- **ROS2 Workspace**: `$HOME/workspaces/mini_amr/amrROS2_ws` (Defined as `$ROS_WS`)
- **Scripts & Shortcuts**: `$HOME/workspaces/mini_amr/Shortcut`
- **UI Application**: `$HOME/workspaces/mini_amr/amrROS2_UI/ICEAMR` (Defined as `$AMR_UI`)

## 2. Environment Configuration (.bashrc)

The `.bashrc` file is configured to set up the ROS2 environment and provide convenient aliases for common tasks.

### Environment Variables
The following key variables are exported:
- `ROS_WS`: Points to the main ROS2 workspace (`/home/smr/workspaces/mini_amr/amrROS2_ws`).
- `AMR_UI`: Points to the UI directory.
- `ROS_DOMAIN_ID`: Set to `31`.
- `CYCLONEDDS_URI`: Points to `~/cyclonedds.xml` for DDS configuration.
- `RMW_IMPLEMENTATION`: Set to `rmw_cyclonedds_cpp`.

### Sourcing
The environment sources:
- ROS2 Jazzy: `/opt/ros/jazzy/setup.bash`
- Workspace Setup: `$ROS_WS/install/setup.bash`
- Traffic Editor Setup: `~/workspaces/mini_amr/traffic_editor/install/setup.bash`

### Essential Aliases

#### Navigation & Commands
- **`cw`**: Change directory to the ROS workspace (`$ROS_WS`).
- **`sb`**: Source `.bashrc` (`source ~/.bashrc`).
- **`eb`**: Edit `.bashrc` (`nano ~/.bashrc`).
- **`amr_nav`**: Launch AMCL Navigation (`./navigation_amcl.sh` in Shortcut).
- **`amr_nav_slam`**: Launch SLAM Localization Navigation (`./navigation_slam_localization.sh`).
- **`amr_map`**: Launch SLAM Mapping (`./navigation_slam.sh`).
- **`amr_save_map`**: Save the current map (`./save_map.sh`).
- **`amr_gui`**: Launch the AMR GUI (`./amr_GUI.sh`).

#### Docking
- **`dock`**: Send action goal to dock the robot.
- **`udock`**: Send action goal to undock the robot.
- **`dockserver`**: Launch the docking action server (`ros2 launch action_autodock auto_dock_launch.py`).

#### Drive Control
- **`drive_on`**: Enable motor state.
- **`drive_off`**: Disable motor state.
- **`drive_reset`**: Cycle motor state (Off -> Wait 1s -> On -> Wait 7s).

## 3. ROS2 App Autostart (Systemd Services)

The "ROS2 App" and background services are managed via **systemd**. These services are configured to start automatically on boot.

### Active Services

1.  **`robot_ctr_mode.service`**
    - **Description**: Manages robot control modes.
    - **Executes**: `/home/smr/workspaces/ctr_mode/ctr_mode_start.sh`
    - **User**: `smr`

2.  **`nav_gui_bridge.service`**
    - **Description**: Bridge for the Navigation GUI.
    - **Executes**: `/home/smr/workspaces/startup/nav_gui_bridge.sh`
    - **Working Dir**: `/home/smr/workspaces/startup`

3.  **`rosbridge.service`**
    - **Description**: ROS bridge server (WebSocket) for web-based UIs and external control.
    - **Executes**: `/home/smr/workspaces/startup/rosbridge_web.sh`

4.  **`ros_modbus_server.service`**
    - **Description**: ROS2 Modbus Server interface.
    - **Executes**: `/home/smr/workspaces/startup/ros_modbus_server.sh`

5.  **`sqlbackend-server.service`**
    - **Description**: SQLite Backend Server for data persistence.
    - **Executes**: `/home/smr/workspaces/apiSQLite/server__start.sh`
    - **Working Dir**: `/home/smr/workspaces/apiSQLite`

6.  **`map_pose_provider.service`**
    - **Description**: Provides map pose information.
    - **Executes**: `/home/smr/workspaces/startup/map_pose_provider.sh`

### Managing Services

You can manage these services using standard `systemctl` commands.

**Check Status:**
```bash
systemctl status robot_ctr_mode.service
systemctl status rosbridge.service
# ... and so on for other services
```

**Restart a Service:**
```bash
sudo systemctl restart robot_ctr_mode.service
```

**Stop a Service:**
```bash
sudo systemctl stop robot_ctr_mode.service
```

**View Logs:**
Use `journalctl` to view logs for a specific service:
```bash
journalctl -u robot_ctr_mode.service -f
```
