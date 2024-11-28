
Electric and Magnetic Field Modeling

Context and Assumptions
For now, we will model distance of 1 as the radius of the point charge sphere of immutability.
At a radial distance of 1 radii, i.e., the surface of immutability for each point charge, the electric field strength is |e/6| / (1 squared) which is |e/6|.
At a radial distance of 2 radii, the electric field strength is |e/(6*2^2)| = |e/24|.

At any time t, the point charge electric field is emitting spherically from the point charge origin, i.e., the center of the sphere.
For a discrete time simulation, each tick creates a new spherical field object for each point charge. (x,y,z,t)
    That is a lot of objects, but we'll gain back in efficiency later with intersection operations that determine the action.

Assumptions : Clarifying speed of electromagnetic fields @ vs. speed of photons local c vs. speed of point charges v
    Electromagnetic fields always propagate through Euclidean space at @ as measured in absolute space and time.
    c <= @
    @ is the limit of local c as spacetime aether apparent energy approaches zero. 
    Individual point charges have a velocity in absolution space and time that may exceed local c and @.
    Photon structures travel through spacetime aether with an absolute velocity equalto local c.
    All electrino : positrino dipoles maintain a relationship between their radius and frequency, such that their absolute diameter divided by period equals local c.
        This is how space contraction and time dilation is implemented.
    Electrino : positrino dipole frequency may range from zero to the Planck frequency.
    Each point charge is always emitting the electric field. 
    Each point charge creates a magnetic field if it is moving.
    Fields pass right through immutability spheres and their centers as if they were not there.

Simulation
    The simulation will be based on discrete time slice units.
    We might want to model absolute time in units where 1 corresponds to the inverse of the Planck frequency.
    We might want to model each  time unit at a fine granularity time slice, say 1000th of a unit time. We'll learn more as we continue as to what makes sense.
    For every time slice in the simulation, each point charge only moves a small distance. 
        This is likely to be computationally intense, so we may only be able to simulate very small systems at first until we learn more.

    At any time t, the simulation must be able to calculate the radius of the propagating spherical wave surface from the past absolute location and time of every point charge.
        Clever and efficient methods to reduce the computational intensity will be necessary. 
            Note : We must calculate the incident fields from all other particles emitted at points in their history.
            Note : Self interaction is possible if the speed of the point charge is > @.
            Note : At large distances, the field strength may fall below our threshold of computation.

    The simulation time evolves by absolute time slice and each particle may move a tiny bit according to its velocity, momentum, and all the forces acting upon it. 
    We calculate the point charge's new absolute x,y,z,t coordinates.
    We need only calculate the intersecting field objects impinging on each point charge.
    Q : How do we calculate the action? How long does each passing wavefront act upon each point charge? 
    Maybe we need to calculate the average force during that interval instead of absolute time.
    We could model it like a geospatial intersection of each field object with each point charge during each absolute time interval.
    There is no need to calculate fields in empty Euclidean space.  
    We need to consider any in-elastic collisions between point charges.
    