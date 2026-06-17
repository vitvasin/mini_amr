import numpy as np
import transforms3d as t3d

# Registration
q_align = np.array([0.5, -0.5, 0.5, -0.5])
R_c2w_reg = t3d.quaternions.quat2mat(q_align)
t_c2w_reg = np.array([[0.0], [0.0], [0.0]])
tvec_reg = np.array([[0.0], [0.0], [1.0]])
R_m2w = np.eye(3)
R_m2c_reg = R_c2w_reg.T
t_m2w_reg = np.dot(R_c2w_reg, tvec_reg) + t_c2w_reg
R_m2w_reg = np.dot(R_c2w_reg, R_m2c_reg)

# New pose: Robot at [0, 1, 0], yaw = 90 deg (facing Y axis)
# ROS Camera orientation is 90 deg yaw
q_c2w_ros_new = t3d.quaternions.mat2quat(t3d.euler.euler2mat(0, 0, np.pi/2))
q_c2w_new = t3d.quaternions.qmult(q_c2w_ros_new, q_align)
R_c2w_new = t3d.quaternions.quat2mat(q_c2w_new)
t_c2w_new_actual = np.array([[0.0], [1.0], [0.0]])

# Marker is at [1, 0, 0].
# Camera to Marker vector in world: [1, -1, 0]
# In new OpenCV camera frame:
tvec_new = np.dot(R_c2w_new.T, np.array([[1.0], [-1.0], [0.0]]))
# Marker orientation in new OpenCV camera frame:
R_m2c_new = np.dot(R_c2w_new.T, R_m2w_reg)

# Relocalization math:
t_c2m = -np.dot(R_m2c_new.T, tvec_new)
t_c2w_calc = np.dot(R_m2w_reg, t_c2m) + t_m2w_reg
R_c2w_calc = np.dot(R_m2w_reg, R_m2c_new.T)
q_c2w_calc = t3d.quaternions.mat2quat(R_c2w_calc)
q_c2w_ros_calc = t3d.quaternions.qmult(q_c2w_calc, t3d.quaternions.qinverse(q_align))
r, p, y = t3d.euler.quat2euler(q_c2w_ros_calc)

print("Calculated Camera Pos:", t_c2w_calc.flatten())
print("Calculated Camera Yaw:", np.degrees(y))
