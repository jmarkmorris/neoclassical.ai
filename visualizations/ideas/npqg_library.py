# This is a library of reusable NPQG software.
# 
# The intent is to have an object oriented hierarchy.
# First pass ideas...not sure if these are at the right granularity. attempting to build up from the fundamentals.
# point_charge : Fundamental
# binary : inherits  point_charge
# dual_binary : inherits binary
# tri_binary : inherits dual_binary (i.e., those characteristics and more, right?) 
# Noether_core : inherits tri_binary, adds pro and anti geometries
# personality_charge : inherits point_charge
# personality_duo : inherits personality_charge (using the right hand rule we can be specific on the geometry)
# personality : inherits personality_duo, color - where color corresponds to generation or number of binaries in the nest.
# I wonder if anyone has ever thought of mapping color charge to generations of quarks?  Hmmm, that's an interesting new mapping.
# fermion : inherits Noether_core, personality

# path : A fundamental concept that is emergent according to the evolution equation in absolute time and absolute space.
# path is such an awesome concept. I can see why Feynman resonated with it. Unfortunately, he was one level removed from nature.
# spherical potential emission rooted at (t, x, y, z) with point charge (q) velocity (v aka dx/dt, dy,dt, dz,dt)
# I would guess that some model components in analytical or simulation models may benefit from use of polar coordinates for the emissions.





# todo : ask Bai to explain how you can create and use a library


# todo : add 
# def frequency(f):