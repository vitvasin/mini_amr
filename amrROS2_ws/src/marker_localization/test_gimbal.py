import numpy as np
import transforms3d as t3d

# Pitch of exactly pi/2
R_orig = t3d.euler.euler2mat(0.1, np.pi/2, 0.3)
r, p, y = t3d.euler.mat2euler(R_orig)
R_recon = t3d.euler.euler2mat(r, p, y)

print("Original:")
print(np.round(R_orig, 4))
print("Reconstructed:")
print(np.round(R_recon, 4))
