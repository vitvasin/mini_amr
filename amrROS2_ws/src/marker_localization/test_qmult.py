import numpy as np
import transforms3d as t3d

q1 = t3d.quaternions.mat2quat(t3d.euler.euler2mat(0, 0, np.pi/2)) # 90 deg yaw
q2 = t3d.quaternions.mat2quat(t3d.euler.euler2mat(0, np.pi/2, 0)) # 90 deg pitch

v = [1, 0, 0]
v_q2 = t3d.quaternions.rotate_vector(v, q2)
v_q1_q2 = t3d.quaternions.rotate_vector(v_q2, q1)

q_mult_12 = t3d.quaternions.qmult(q1, q2)
v_mult_12 = t3d.quaternions.rotate_vector(v, q_mult_12)

q_mult_21 = t3d.quaternions.qmult(q2, q1)
v_mult_21 = t3d.quaternions.rotate_vector(v, q_mult_21)

print("v_q1_q2:", v_q1_q2)
print("v_mult_12:", v_mult_12)
print("v_mult_21:", v_mult_21)
