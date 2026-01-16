#!/usr/env python
import numpy as np

################################################################
## Particle
##   contains state of a single particle
##     --> currently 3D position/velocity and 1D charge
################################################################
class Particle:
    def __init__(self, p, v, q):
        self.pos = np.array(p, dtype=np.float32)
        self.vel = np.array(v, dtype=np.float32)
        self.charge = q
    
