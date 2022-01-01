theese are screen scrapes of an issue from the old repo

Electric field fluctuation #5

Context:
At a radial distance of 1 Planck length, i.e., the surface of the Planck sphere, electric field is (e/6)/ (1 squared) which is e/6.
At a radial distance of 1.5 Planck lengths the field is e/(6*1.5^2).

Question:
Is time a factor in calculating the field using this equation?
Is velocity a factor in calculating the field using this equation?

Yes, time is a factor. It's going to get sort of complicated.

at any given simulation time T0 the electric field will start propagating from the current location of the electrino or positrino.
the electric field will propagate out spherically, but this may become distorted over time because of 3).
the electric field will propagate at the local speed of light, which will vary depending on some other dynamical factors to be determined later. for now just stub that out and presume it is always moving at constant speed of light 3 x 10^8 m/s.
Perhaps we should calibrate our simulation time so it is fine grained. i.e., for every clock tick in the simulation, the Planck particle only moves a fraction of a Planck length. This is going to make it very computationally intense, so we may only be able to simulate very small systems at first until we learn more.
so the wave that started at T0 we will need to keep track of and update it for all further T1, T2, etc. until it falls off below some threshold of significance that we set as a simulation parameter. That wave front will be important to understand how it influences other particles.
6.) Then simulation time evolves one tick to T1 and the particle moves a tiny bit according to its velocity and all the forces acting upon it. Once we figure out the particle's new x1,y1,z1 coordinates (again fine grained far less than a Planck length) then that particle is issuing another electric field from that point, as in 2).
This is going to be computationally intense.
We'll need to keep track of a lot of information for every x,y,z,t.
For the particles we really only need to keep track of current location and vector velocity. Charge is in the object definition.

at any given simulation time T0 the electric field will start propagating from the current location of the electrino or positrino.
In other words, propagating from the center of the planck sphere?

the electric field will propagate at the local speed of light, which will vary depending on some other dynamical factors to be determined later. for now just stub that out and presume it is always moving at constant speed of light 3 x 10^8 m/s.
Should we factor in the distortion that you mentioned in 2)?

so the wave that started at T0 we will need to keep track of and update it for all further T1, T2, etc. until it falls off below some threshold of significance that we set as a simulation parameter. That wave front will be important to understand how it influences other particles.
If this is a wave, does that mean the electric field only exists at the surface of the sphere of expanding electrical field? Meaning there is no electrical field inside the sphere?

6.) Then simulation time evolves one tick to T1 and the particle moves a tiny bit according to its velocity and all the forces acting upon it. Once we figure out the particle's new x1,y1,z1 coordinates (again fine grained far less than a Planck length) then that particle is issuing another electric field from that point, as in 2).
Do these electric fields expire? Do they weaken over time?

Also, do all these behaviors apply to magnetic fields?

Yes, the fields will always start propagating from the center of the sphere.

It will happen automatically because we will calculate the propagation rate across simulation cells according to the local electric and magnetic field from all sources as of the instant the propagating fields cross that cell.

I think the electric and magnetic fields would exist inside the sphere and we will need to calculate them to figure out how long it takes to propagate to the cells on the surface of the sphere.

Good question. The center of a sphere is always emitting the electric field. It is only creating a magnetic field if it is moving. If we think about everything tick by tick then it becomes easier to imagine what will happen. So say at T100 the particle is somewhere x,y,z then we need to start a new electric field propagation at T100 from the sphere center. If at T101 the particle is in the same place, we start a new electric field propagation. Same at T102. Now each of those fields will be moving outward on its original radial vector and reducing in magnitude at 1/radius-squared where the radius is measured from where that field started.

Yes, all of these are similar with magnetic fields, but I need to look it up and figure out how it propagates and the shape. We only see magnetic fields when the particle is moving.

This simulation is probably going to be prohibitively expensive to model every x,y,z cell and every tick t for the whole size and duration of the simulation. We probably don't really need to calculate every x,y,z,t fine grained simulation cell. It only really matters what each Planck particle encounters.

I haven't thought of what to do when a field has only partially propagated through a particle. We'll need to think about that and how much force will be exerted. There is no science on that so maybe we'll do some kind of heuristic based on the aggregate of the simulation cells inside the sphere. Yeah, that will probably get us going.

I am hoping that some day some professionals will join this project and help us clean up any wrong assumptions/decisions.

One way to do this is to keep track of the path of each particle's sphere center. Meaning all the simulation cells the center was in at each x,y,x and at what time t. From that we can always back track and calculate the field to some other x,y,z,t where another particle is, aggregate all of those fields (vectors), calculate the net electric and magnetic fields on the second particle and then calculate to which simulation cell it will move next.

So each particle is affected by all the other particles at all times in the past unless the field has passed by. That's a lot of calculation! There should be good ways to optimize it for efficiency though.

There are a lot of internet resources on "Magnetic Field of a Moving Point Charge"
https://academic.mu.edu/phys/matthysd/web004/l0220.htm < this one also starts talking about the forces exerted
and youtube too, same search string : https://youtu.be/waTF7kjmmt8

Likewise 'Electric field of a point charge'

When I think of the computational approach to NPQG there is no fundamental need to calculate fields in empty Euclidean space. It is only necessary to calculate the aggregate of all electromagnetic fields where a Planck particle sphere is located at a given time (x,y,z,t). The electromagnetic field will determine the electromagnetic force on the sphere. We must also consider the velocity and momentum of the sphere. Lastly we need to consider any in-elastic collisions between spheres that happen at that moment. The most challenging part here is the first part - calculating the impinging fields from all other Planck particles, because that involves working backwards through time at increasing incremental radius and identifying all other Planck particles lying on each incremental circle (t - n) where n represents the number of simulation ticks backwards in time.

An important set of questions is how electromagnetic fields emitted by a Planck sphere propagate over time.

Does the propagtion rate change depending on intervening particles? Let's simplify for now and say no.
Do the fields pass right through intervening particles like they aren't there? Let's simplify for now and say yes.
So what speed shall we assign to the propagation velocity of these fields. The most obvious choice is the asymptote of the speed of light in free space. I say asymptote because that is the speed in low energy spacetime where the spacetime particles are the largest, and would correspond to the speed of the photon when limited by the aether.

Do we want to keep track of particles and fields in x,y,z,t coordinates or in sphereical coordinates theta1, theta2, radius, t? Or translate between both depending on the calculation?

It would be way too much memory to keep track of all points in spacetime plus it would only allow us a tiny simulation world.
Instead, we can only track the particles. Each particle must have its history of where it was and when. So x,y,z,t. Then we need a very efficient way to compress this list, probably by expressing portions of that path as straight lines where we can skip all the intervening x,y,z between t1 and t2 because we can always calculate them. We may be able to find other clever methods later by looking at the paths taken and if we can approximate them as arcs.
