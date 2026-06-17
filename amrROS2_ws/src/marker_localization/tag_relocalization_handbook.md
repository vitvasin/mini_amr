# 📖 Ultimate Autonomous AMR Relocalization & Navigation Handbook

This handbook serves as the single, authoritative reference for the autonomous navigation, AprilTag marker-based relocalization, and AI visual recovery pipelines on the AMR platform. It details everything from generating physical tags to mapping, launching, triggering, and troubleshooting.

---

## 1. System Architecture & Relocalization Modes

The AMR platform utilizes a hybrid, switchable relocalization framework. If the robot becomes lost (due to LIDAR slippage, wheel odometry drift, or dynamic obstacles), it halts, triggers the visual sensors, and recovers its absolute position using the selected mode:

```mermaid
graph TD
    A[Robot Transitioned to LOST State] --> B{Recovery Method Selected}
    
    B -->|Method 1: AprilTag Markers| C[Marker Localizer Node]
    B -->|Method 2: AI Visual SfM| D[COLMAP Place Recognition]
    
    C -->|Detects tag in camera| E[Compute 6-DoF Camera Pose]
    D -->|Matches keypoints with gallery| E
    
    E -->|Compensate physical camera offset| F[Recovery Orchestrator Node]
    F -->|Inject base_link coordinates| G[/initialpose Topic]
    G -->|Reset EKF / AMCL filters| H[Healthy Localized State]
```

### Key Components

*   **Fiducial Marker Pipeline (`marker_localization` package)**:
    *   `generate_markers.py`: Generates mathematically perfect printable AprilTags using the `DICT_APRILTAG_36h11` dictionary.
    *   `register_markers.py`: Captures real-time camera frames and queries the TF tree to average and record marker coordinates in the `map` coordinate frame.
    *   `marker_localizer_node.py`: Captures live video, detects tags, solves 6-DoF camera poses, and publishes estimated robot coordinates.
    *   `publish_marker_debug.py`: Publishes live visual diagnostic frames overlaying detection boxes and 3D coordinate axes.
*   **AI Place Recognition Pipeline (`visual_robot_localization` package)**:
    *   Utilizes a pre-compiled 3D Structure-from-Motion (SfM) map generated offline using NetVLAD (global features), SuperPoint (local features), SuperGlue (feature matching), and COLMAP.
*   **Coordination & Recovery Stack (`visual_recovery` package)**:
    *   `recovery_node.py`: Orchestrates the recovery state machine, halts robot motion, queries the camera, calls the active localizer, injects the corrected coordinates to the EKF, and clears the costmaps.
*   **Localization Monitor (`localization_monitor` package)**:
    *   Monitors pose covariance values and updates the global `/localization_status` topic.

---

## 2. Startup Flow & Background Automation

To ensure startup stability and prevent race conditions on the resource-constrained ARM64 platform, the system relies on an automated pre-flight check and a staggered node launch sequence.

### Pre-Flight Checklist (`ensure_services.sh`)
Whenever the navigation stack is started, the background script `ensure_services.sh` performs the following safety checks:
1.  **RPLidar Auto-Reset**: Sends a soft-reboot code to `/dev/rplidar` using `reset_lidar.py` to prevent the LIDAR sensor from entering internal error lock states.
2.  **MongoDB Daemon**: Verifies MongoDB is running. If not, it boots the service.
3.  **Node.js Backend Server**: Verifies the database manager is running on Port `3000`. If offline, it boots the server and redirects output to `backend_server.log` to prevent Python UI startup crashes.

### Staggered Boot Sequence (`navigation.launch.py`)
To prevent the navigation planners and costmaps from starting before the localization transforms are published, the startup is staggered:
*   **0.0s**: EKF and hardware sensors boot up first.
*   **10.0s**: `slam_toolbox` loads the map and posegraph, publishing the `/map` -> `/odom` transform immediately (`map_start_at_dock: true`).
*   **45.0s**: Navigation costmaps and planners boot up. This 35-second gap allows `slam_toolbox` to fully deserialize the 28MB map file (`mapSLAM_008.posegraph`) and match the first laser scan before the `global_costmap` runs its TF availability check.
*   **65.0s**: The `delivery_robot_main_controller` starts (20s after Nav2 activates).
*   **75.0s**: The AMR User Interface boots up (10s after delivery controller).

> [!NOTE]
> **Why 45s for Nav2?** Confirmed from boot logs (2026-06-11): slam_toolbox activates at T≈11.5s but the `global_costmap` starts its TF check immediately at T=25s (old timing). The 28MB posegraph takes additional time to produce reliable scan-matching output. At 25s, the TF was never published, causing `global_costmap` to timeout and abort after 62 seconds, killing the entire navigation stack.

---

## 3. Step-by-Step Operations Guide

### Step 1: Generating Printable AprilTag Markers

To deploy marker-based relocalization, you must generate and print physical AprilTags.

#### 1. Run the Generator Script
Open a terminal and run the generation script. By default, the images are saved in the package's `markers` folder:
```bash
python3 /home/smr/workspaces/mini_amr/amrROS2_ws/src/marker_localization/scripts/generate_markers.py --ids 1 2 37 --dict DICT_APRILTAG_36h11 --size 400
```
*   `--ids`: Space-separated list of marker IDs to generate (e.g., `1 2 37`).
*   `--dict`: The dictionary to use. **MUST be `DICT_APRILTAG_36h11`** for the highest reliability on this platform.
*   `--size`: Resolution of the output PNG file in pixels (default: `400`).
*   `--output_dir`: Output path (default: `/home/smr/workspaces/mini_amr/amrROS2_ws/src/marker_localization/markers`).

#### 2. Printing & Mounting Specifications
> [!IMPORTANT]
> *   **Exact Size**: Print the marker so that the **actual black border** measures exactly **`0.15` meters (15 cm)**.
> *   **Flat Mounting**: Mount the printed paper onto a flat, rigid board (e.g., acrylic or cardboard). Wrinkles or bends will skew the depth solver and cause coordinate offsets.
> *   **Quiet Zone**: Leave a white margin (at least 2–3 cm) around the outer black border. This helps the OpenCV detector locate the tag boundaries.

---

### Step 2: Mapping Physical Markers

Before the system can relocalize, you must save the absolute map coordinates of your physical markers.

#### 1. Initialize SLAM / Navigation
Start navigation and verify the robot is fully localized on the map:
```bash
/home/smr/workspaces/mini_amr/Shortcut/run_slam_launch.sh
```
Wait ~30 seconds for the staggered boot sequence to complete, and verify using RViz or the UI that the robot's coordinates on the map are correct.

#### 2. Run the Mapping Script
Position the robot so that the physical AprilTag marker is clearly in the center of the camera's view. The **recommended distance is 0.5m–2.5m**. Run the registration script (note the `--size` is the width of the black square in meters):

> [!NOTE]
> **Single-Point Registration:** You only need to configure the marker from **ONE point**. The relocalization pipeline uses a full 6-DoF (Degrees of Freedom) rigid body mathematical transformation. It will automatically calculate the robot's correct dynamic location and orientation regardless of the angle or distance the camera views it from later.

```bash
python3 /home/smr/workspaces/mini_amr/amrROS2_ws/src/marker_localization/scripts/register_markers.py --size 0.15 --dict DICT_APRILTAG_36h11 --min-obs 20
```

**Good detection log (accept these):**
```
[INFO] First sight of Marker ID: 37! dist=1.42m reproj=0.87px (need 20 obs to save)...
[INFO] Recording Marker 37: x=1.234, y=2.567 dist=1.42m reproj=0.87px (20 observations) ✓
```

**Bad detection log (automatic rejection):**
```
[WARN] Marker 37 rejected: reprojection error too high (5.2px > 4.0px)   ← blurry/noisy detection
[WARN] Marker 17 rejected: distance out of range (5.8m, valid: 0.10–5.00m) ← too far away
[WARN] Marker 1 rejected: too small (80px² < 100px²)                      ← move closer
```
> [!TIP]
> Use `--min-obs 20` (20 observations) or more when registering real tags. This forces the robot to look at a tag for an extended moment, ensuring that temporary sensor noise is averaged out and discarded.

#### 3. Save and Install the Coordinates
*   Press **`Ctrl + C`** in the terminal to stop recording. The pose will save directly to:
    `/home/smr/workspaces/mini_amr/amrROS2_ws/src/marker_localization/config/markers_auto.yaml`
*   Rebuild the workspace so the updated file is installed:
    ```bash
    cd /home/smr/workspaces/mini_amr/amrROS2_ws
    colcon build --packages-select marker_localization
    source install/setup.bash
    ```

> [!TIP]
> **Growing Your Map:** When you run `register_markers.py`, it safely **merges/appends** new markers into the existing `markers_auto.yaml`! It does NOT overwrite or delete your old ones. You can map Room A, press `Ctrl+C`, drive to Room B, map again, and it will save both. If you ever want to reset completely, just delete the `markers_auto.yaml` file manually.

---

### Step 3: Default Autostart Behavior

By default, the system is configured to launch the AprilTag marker relocalization nodes automatically during bringup. When you start the robot (using the UI "Navigate" button or the `run_slam_launch.sh` script), the marker localization system is **already running** in the background and waiting for your trigger.

No additional launch options are required.

---

### Step 4: Triggering Relocalization (When Lost)

When the robot reports navigation obstacles or loses localization, trigger the recovery sequence manually:

#### Option A: Quick Alias (Recommended)
Open a terminal and run:
```bash
amr_recover
```

#### Option B: Manual Service Call
If you want to trigger it programmatically or via a script:
```bash
ros2 service call /visual_recovery_node/trigger_recovery std_srvs/srv/Trigger {}
```

#### What happens during recovery:
1.  The recovery node pauses the navigation planners and halts the robot.
2.  It captures camera frames and runs detection (Marker, AI, or Hybrid).
3.  Upon detection, it calculates the robot's coordinates in the `map` frame.
4.  It publishes the initial pose to `/initialpose` to reset the EKF and AMCL filters.
5.  It clears the navigation costmaps to delete transient ghost obstacles and resumes the planners.

---

## 4. Diagnostics & Live Visualization

To verify what the camera sees and ensure it detects the tags correctly:

### 1. Launch the Debug Visualization Node
Run the following command in a terminal:
```bash
ros2 run marker_localization publish_marker_debug.py
```

### 2. View in Foxglove / RViz
Open **Foxglove Studio** or **RViz** on your computer, add an **Image panel**, and subscribe to:
```
/marker_localization/annotated_image
```
You will see the camera stream with:
*   **Green boundary lines** around any detected tag.
*   The **detected Marker ID** text.
*   A **3D Coordinate Axis** (red = X, green = Y, blue = Z) representing the pose orientation.

---

## 5. Troubleshooting & Common Fixes

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| **`Map frame not available`** warning in mapping script | Mapping script was started before the navigation stack finished booting. | Wait ~80 seconds for the full staggered boot sequence to complete before running `register_markers.py`. |
| **`Extrapolation into the past`** TF errors | High CPU usage or clock skew between sensor nodes. | Ensure EKF update rate is set to `20Hz` or lower. The staggered boot sequence resolves this by giving the map transform time to warm up. |
| **`Failed to activate global_costmap` / Nav2 `Aborting bringup`** | `slam_toolbox` hadn't produced a reliable `map→odom` TF before Nav2's lifecycle manager ran the costmap activation check (62s timeout). Caused by Nav2 starting at 25s when the 28MB posegraph takes longer to match. | **Fixed (2026-06-11)**: Nav2 delayed to `45s` in `navigation.launch.py`. Delivery controller to `65s`, UI to `75s` in `slam_localization_sequential_launch.py`. |
| **False positive detections (markers detected in empty room)** | Random textures/patterns matching the marker structure temporarily. | **Fixed (2026-06-11)**: Reverted to OpenCV default parameters for robust real-world detection, but implemented strict post-PnP validation (reprojection error ≤ 4.0px, distance 0.1m–5.0m, area ≥ 100px²) and a high multi-frame observation filter (`--min-obs 20`) to permanently filter out background noise. |
| **No markers detected / Incorrect ID** | Lack of a white quiet zone, low camera resolution, or screen glare. | **Fixed (2026-06-11)**: Re-added 50px white quiet-zone padding in the detector code (shifting corners back to align with camera matrix K) to ensure 100% accurate identification. Add a 2–3 cm white border around printed markers to further assist. |
| **Markers registered with wrong coordinates** | Mapping script was run when the robot's own localization was drifting. | Ensure the robot is accurately localized on the map (e.g. by manual alignment in RViz) before running the mapping script. |
| **Robot relocates to the exact registration point from any angle** | Stale code. The Python files were modified but the workspace was not rebuilt, causing ROS 2 to run the old, buggy matrix math. | Rebuild the workspace with `colcon build --packages-select marker_localization` and source `install/setup.bash` to ensure the new `t_c2m` matrix inversions are executed. |
| **Updated configs not taking effect** | The workspace was not built after updating `markers_auto.yaml`. | Run `colcon build --packages-select marker_localization` to copy the new coordinates to the install space. |

