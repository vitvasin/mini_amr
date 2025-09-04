# 🚀 Nav2 Key Parameters (English / ภาษาไทย)

| Node (ROS2)                | Parameter (EN)             | Thai Name (ชื่อภาษาไทย)       | Description (EN)                                      | คำอธิบาย (TH)                                   |
|-----------------------------|----------------------------|--------------------------------|------------------------------------------------------|-------------------------------------------------|
| `controller_server`        | `controller_frequency`     | ความถี่ควบคุมหุ่นยนต์           | Frequency of sending velocity commands               | ความถี่ที่หุ่นยนต์คำนวณและส่งคำสั่งความเร็ว (Hz) |
| `controller_server/goal_checker` | `xy_goal_tolerance`  | ค่าความคลาดเคลื่อน XY         | Position tolerance at goal                           | ระยะห่างที่ถือว่า "ถึงเป้าหมาย" ได้              |
| `controller_server/goal_checker` | `yaw_goal_tolerance` | ค่าความคลาดเคลื่อนมุม          | Orientation tolerance at goal                        | ค่าความคลาดเคลื่อนของการหมุนเมื่อถึงเป้าหมาย      |
| `local_costmap`            | `width / height`           | ขนาด costmap ท้องถิ่น           | Size of local costmap window                         | ขอบเขตของแผนที่ costmap ท้องถิ่น                 |
| `local_costmap`            | `resolution`               | ความละเอียด costmap (ท้องถิ่น)  | Resolution of local costmap                          | ความละเอียดของ grid ใน costmap ท้องถิ่น          |
| `global_costmap`           | `resolution`               | ความละเอียด costmap (รวม)       | Resolution of global costmap                         | ความละเอียดของ grid ใน costmap รวม               |
| `local_costmap/inflation_layer` | `inflation_radius`   | รัศมีขยายสิ่งกีดขวาง (ท้องถิ่น) | Safety buffer around obstacles                       | ระยะรอบสิ่งกีดขวางเพื่อความปลอดภัย                |
| `local_costmap/inflation_layer` | `cost_scaling_factor`| ตัวคูณการกระจายค่า (ท้องถิ่น)   | Gradient steepness of obstacle cost                  | กำหนดความชันของค่าอันตรายรอบสิ่งกีดขวาง           |
| `global_costmap/inflation_layer` | `inflation_radius`  | รัศมีขยายสิ่งกีดขวาง (รวม)      | Safety buffer in global map                          | ระยะรอบสิ่งกีดขวางเพื่อความปลอดภัย (global)       |
| `global_costmap/inflation_layer` | `cost_scaling_factor`| ตัวคูณการกระจายค่า (รวม)        | Gradient steepness in global map                     | ความชันของค่าอันตรายใน global costmap             |
| `controller_server/FollowPath` | `v_linear_max`       | ความเร็วเชิงเส้นสูงสุด          | Maximum linear speed                                 | ความเร็วเดินหน้าสูงสุดของหุ่นยนต์                |
| `controller_server/FollowPath` | `v_linear_min`       | ความเร็วเชิงเส้นต่ำสุด          | Minimum linear speed                                 | ความเร็วเดินหน้าต่ำสุด                            |
| `controller_server/FollowPath` | `v_angular_max`      | ความเร็วเชิงมุมสูงสุด           | Maximum angular speed                                | ความเร็วมุมสูงสุดในการหมุน                        |
| `velocity_smoother`        | `max_velocity`            | ความเร็วสูงสุด (x, y, θ)        | Max linear/angular speeds                            | ความเร็วสูงสุดทั้งเชิงเส้นและหมุน                 |
| `velocity_smoother`        | `min_velocity`            | ความเร็วต่ำสุด (x, y, θ)        | Min negative/backward speeds                         | ความเร็วต่ำสุด (รวมถอยหลัง)                       |
| `velocity_smoother`        | `max_accel`               | การเร่งสูงสุด                   | Maximum accel (x, y, θ)                              | ค่าสูงสุดของการเร่ง                               |
| `velocity_smoother`        | `max_decel`               | การเบรกสูงสุด                   | Maximum deceleration (x, y, θ)                       | ค่าสูงสุดของการเบรก                               |
| `planner_server/GridBased` | `tolerance`               | tolerance ของ global planner   | Goal acceptance distance for global path             | ระยะคลาดเคลื่อนของ global planner                 |