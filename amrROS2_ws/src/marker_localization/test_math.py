import numpy as np
import transforms3d as t3d

# Registration pose (Robot at origin, marker at [1, 0, 0] in front of camera)
# Camera is at origin, looking along X axis of world.
# World: X fwd, Y left, Z up.
# OpenCV Camera: Z fwd, X right, Y down.
# Camera aligned with world:
# OpenCV Z = World X. OpenCV X = -World Y. OpenCV Y = -World Z.
q_align = np.array([0.5, -0.5, 0.5, -0.5])
# Let camera be at origin, looking along X. So R_c2w_ros = I.
# q_c2w_opencv = q_c2w_ros * q_align = q_align
R_c2w_reg = t3d.quaternions.quat2mat(q_align)
t_c2w_reg = np.array([[0.0], [0.0], [0.0]])

# Marker is at [1, 0, 0] in World.
# In OpenCV camera, marker is at [0, 0, 1].
tvec_reg = np.array([[0.0], [0.0], [1.0]])

# Marker orientation is aligned with World.
R_m2w = np.eye(3)

# R_m2c_reg = R_c2w_reg^T * R_m2w = R_c2w_reg^T
R_m2c_reg = R_c2w_reg.T

# Registration math:
t_m2w_reg = np.dot(R_c2w_reg, tvec_reg) + t_c2w_reg
R_m2w_reg = np.dot(R_c2w_reg, R_m2c_reg)

print("Registered Marker Pos:", t_m2w_reg.flatten())

# Relocalization from a NEW pose: Robot at [0, 1, 0] (shifted left)
# Camera ROS orientation still I.
t_c2w_new_actual = np.array([[0.0], [1.0], [0.0]])
# Marker in world is [1, 0, 0].
# Vector from camera to marker in world is [1, -1, 0].
# In OpenCV camera frame:
tvec_new = np.dot(R_c2w_reg.T, np.array([[1.0], [-1.0], [0.0]]))
# Marker orientation in OpenCV camera frame:
R_m2c_new = R_c2w_reg.T # since marker is still aligned with world, and camera is still aligned with world.

# Relocalization math:
t_c2m = -np.dot(R_m2c_new.T, tvec_new)
t_c2w_calc = np.dot(R_m2w_reg, t_c2m) + t_m2w_reg

print("Calculated Camera Pos:", t_c2w_calc.flatten())
