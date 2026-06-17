import numpy as np
import transforms3d as t3d

for _ in range(100):
    q = np.random.rand(4)
    q /= np.linalg.norm(q)
    R = t3d.quaternions.quat2mat(q)
    r, p, y = t3d.euler.mat2euler(R)
    R_recon = t3d.euler.euler2mat(r, p, y)
    if not np.allclose(R, R_recon):
        print("MISMATCH!")
        print(R)
        print(R_recon)
        break
else:
    print("ALL MATCH")
