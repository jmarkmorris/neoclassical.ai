from vpython import *
e = sphere(pos = vector(-1,0,0), radius = 1, color=color.blue)
p = sphere(pos = vector(1,0,0), radius = 1, color=color.red)

epos = vector(-1,0,0)
ppos = vector(1,0,0)
theta = 0
while theta <= 200*pi:
    theta = theta + 0.1
    x = sin(theta)
    y = cos(theta)
    rate(100)
    epos = vector(sin(theta),cos(theta),0)
    ppos = vector(sin(theta+pi),cos(theta+pi),0)
    e.pos = epos
    p.pos = ppos
    