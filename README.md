TO DO
- Tune the collision monitor
- Port the new WP follower from ICE_LED
- HIGHSPEED ODOM FLIP problem!!


# 🚀 Compact Nav2 Useful Parameters / พารามิเตอร์ Nav2 ที่ควรรู้

File: nav2_param.yaml

| Node (ROS2)                | Parameter         | Meaning (EN / ภาษาไทย)                                     |
|-----------------------------|------------------|-----------------------------------------------------------|
| controller_server           | controller_frequency | Control loop frequency (Hz) / ความถี่ควบคุมหุ่นยนต์ |
| controller_server/goal_checker | xy_goal_tolerance | XY tolerance at goal (m) / ค่าคลาดเคลื่อนตำแหน่งที่เป้าหมาย |
| controller_server/goal_checker | yaw_goal_tolerance | Yaw tolerance at goal (rad) / ค่าคลาดเคลื่อนมุมที่เป้าหมาย |
| local_costmap               | width / height   | Size of local map window / ขนาดของ costmap ท้องถิ่น |
| local_costmap               | resolution       | Cell resolution of local map / ความละเอียดของ costmap ท้องถิ่น |
| global_costmap              | resolution       | Cell resolution of global map / ความละเอียด costmap รวม |
| local_costmap/inflation_layer | inflation_radius | Safety buffer (m) / ระยะกันชนรอบสิ่งกีดขวาง (ท้องถิ่น) |
| local_costmap/inflation_layer | cost_scaling_factor | Obstacle cost gradient / ค่าความชัน cost รอบสิ่งกีดขวาง |
| global_costmap/inflation_layer | inflation_radius | Safety buffer (m) / ระยะกันชนรอบสิ่งกีดขวาง (รวม) |
| global_costmap/inflation_layer | cost_scaling_factor | Obstacle cost gradient / ความชัน cost ใน global map |
| controller_server/FollowPath | v_linear_max    | Max forward velocity (m/s) / ความเร็วเชิงเส้นสูงสุด |
| controller_server/FollowPath | v_linear_min    | Min forward velocity (m/s) / ความเร็วเชิงเส้นต่ำสุด |
| controller_server/FollowPath | v_angular_max   | Max angular velocity (rad/s) / ความเร็วเชิงมุมสูงสุด |
| velocity_smoother           | max_velocity     | Velocity limits x,y,θ / ความเร็วสูงสุด (x,y,θ) |
| velocity_smoother           | min_velocity     | Minimum velocities / ค่าความเร็วต่ำสุด (รวมถอยหลัง) |
| velocity_smoother           | max_accel        | Max acceleration / การเร่งสูงสุด |
| velocity_smoother           | max_decel        | Max deceleration / การเบรกสูงสุด |
| planner_server/GridBased    | tolerance        | Goal tolerance in planner (m) / ค่าคลาดเคลื่อนของ global planner |