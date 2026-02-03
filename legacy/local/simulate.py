# #!/usr/bin/env python

################################################################
## contains code relevant to updating simulation
##   e.g. physics, integration
################################################################

from local.particle import *

# step particle simulation
def simStep(particles, k, dt, pMin, pMax):
    new_particles = []
    
    for i,p in enumerate(particles):
        
        # calculate electrostatic forces (Coulomb's law)
        emForce = np.array((0, 0, 0), dtype=np.float32)
        for j,p2 in enumerate(particles):
            if i != j:
                n = p.pos - p2.pos
                dist = np.sqrt(n.dot(n))
                emForce += p2.charge*n/(dist**3);
        emForce *= p.charge*k;
        
        # add forces and step velocity --> forward Euler integration
        pNew = p
        pNew.vel += emForce*dt
        pNew.pos += pNew.vel*dt
        for i in range(pNew.pos.size):
            while pNew.pos[i] < pMin[i]:
                pNew.pos[i] += pMax[i] - pMin[i]
            while pNew.pos[i] > pMax[i]:
                pNew.pos[i] -= pMax[i] - pMin[i]
        new_particles.append(pNew)

    return new_particles


