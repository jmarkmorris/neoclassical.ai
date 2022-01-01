
Electric and Magnetic Field Modeling

Context and Assumptions
For the purposes of this noted, we will model distance as multiples of the radius of the point charge sphere of immutability.
At a radial distance of 1 radii, i.e., the surface of immutability for each point charge, the electric field strength is |e/6| / (1 squared) which is |e/6|.
At a radial distance of 2 radii, the electric field strength is |e/(6*2^2)| = |e/24|.

At any time t, the point charge electric field is emitting spherically from the point charge origin, i.e., the center of the sphere.

Assumptions : Clarifying speed of electromagnetic fields vs. speed of photons vs. speed of point charges
    Electromagnetic fields always propagate through Euclidean space at true C (capital C) as measured from absolute space and time.
    Individual point charges have a velocity in absolution space and time that may exceed C.
    Photon structures travel through spacetime aether with an absolute velocity equal to local c.
    All electrino : positrino dipoles maintain a relationship between their radius and frequency, such that their absolute diameter divided by period equals local c.
        This is how space contraction and time dilation is implemented.
    Electrino : positrino dipole frequency may range from zero to the Planck frequency.
    Each point charge is always emitting the electric field. 
    Each point charge creates a magnetic field if it is moving.
    Fields pass right through immutability spheres and their centers as if they were not there.

Simulation
    The simulation will be based on time slice units.
    We might want to model absolute time in units of Planck time, the inverse of Planck frequency.
    We might want to model each Planck time unit at a fine granularity time slice, say 1000th of a Planck time. We'll learn more as we continue as to what makes sense.
    For every time slice in the simulation, each point charge only moves a small distance. 
        This is likely to be computationally intense, so we may only be able to simulate very small systems at first until we learn more.

    At any time t, the simulation must be able to calculate the radius of the propagating spherical wave surface from the past absolute location and time of every point charge.
        Clever and efficient methods to reduce the computational intensity will be necessary. 
            Note : We must calculate the incident fields from all other particles emitted at points in their history.
            Note : Self interaction is possible if the speed of the point charge is > C.
            Note : At large distances, the field strength may fall below our threshold of computation.

    The simulation time evolves by absolute time slice and each particle may move a tiny bit according to its velocity and all the forces acting upon it. 
    We calculate the point charge's new absolute x,y,z,t coordinates.
    There is no fundamental need to calculate fields in empty Euclidean space.  
    We need to consider any in-elastic collisions between point charges.
    