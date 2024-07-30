# manim -pqh --disable_caching orbiting_point_charges.py OrbitingPointCharges -p

# 
# To do :
# 1. add argument handling
# manim -pqh emergence.py emergence -p --arg 1 2 3.14 4.56
# argv[1] : blah [default = x]
# argv[2] : 
# argv[3] : 
# argv[4] : 
#
# 2. convert units to field speed @


from manim import *
# from manim import RED, BLUE 
from manim import config

# animation
duration = 12
frame_rate = 60
paused = False # add pause feature?

total_rotation_angle_in_radians = 2*TAU

# powerpoint png export size
config.pixel_width = 2998
config.pixel_height = 1686
config.frame_rate = frame_rate
frame_width = 2  
frame_height = 2
frame_count = 0

#——————————————————————————————————————————————————————————————————————————————

def calculate_sphere_fade_values(Q):
    sphere_fade_values = []
    sphere_fade = 1
    sphere_fade_min = 0
    for _ in Q["potential_spheres"]:
        sphere_fade_values.insert(0, sphere_fade)
        sphere_fade = max(sphere_fade - Q["sphere_fade_delta"], sphere_fade_min)
    return sphere_fade_values

def draw_potential_sphere(sphere, sphere_fade, color):
    cx, cy, cr = sphere
    circle = Circle(radius=cr, color=color, stroke_width=2, fill_opacity=0).move_to([cx, cy, 0])
    circle.set_stroke(opacity=sphere_fade)
    return circle

def draw_recent_path(Q):
    angle = Q["angle_in_radians"] - Q["trailing_path_angle_in_radians"]
    radius = Q["dipole_orbit_radius"]
    points = [[np.cos(angle) * radius, np.sin(angle) * radius, 0]]
    
    for loop_angle in np.arange(angle, Q["angle_in_radians"], TAU/360):
        points.append([np.cos(loop_angle) * radius, np.sin(loop_angle) * radius, 0])
    
    recent_path = VGroup()
    n_segments = len(points) - 1
    for path_segment in range(n_segments):
        segment = Line(points[path_segment], points[path_segment+1])
        segment.set_color(Q["color"])
        segment.set_stroke(opacity=(path_segment+1)/n_segments)
        recent_path.add(segment)
    
    return recent_path

#——————————————————————————————————————————————————————————————————————————————

def update_path(mob, dt, Q):
    global frame_count
        
    Q["angle_in_radians"] += Q["per_frame_increment_angle_in_radians"]
    Q["opacity"] = max(0, Q["opacity"] - dt / 10)
    updated_path = draw_recent_path(Q)
    
    if (frame_count % Q["frames_between_tracer_origins"] == 0) :
        Q["potential_spheres"].append((Q["circle"].get_center()[0], Q["circle"].get_center()[1], 0))
        tracer_origin = Circle(color=Q["color"], radius=Q["tracer_origin_radius"], fill_opacity=1).move_to(Q["circle"].get_center())
        Q["tracer_origins"].append(tracer_origin)
        if (len(Q["tracer_origins"]) > Q["num_tracer_origins"]) :
            Q["tracer_origins"].pop(0)

    Q["sphere_fade_values"] = calculate_sphere_fade_values(Q)
    for index, potential_sphere in enumerate(Q["potential_spheres"]) :
        updated_path.add(draw_potential_sphere(potential_sphere, Q["sphere_fade_values"][index], interpolate_color(BLACK, Q["color"], Q["sphere_fade_values"][index])))

    Q["potential_spheres"] = [(cx, cy, cr + Q["potential_sphere_radius_increment"]/Q["frames_between_tracer_origins"]) for cx, cy, cr in Q["potential_spheres"] if cr < 5]

    dot = 0
    for tracer_origin in Q["tracer_origins"] :
        tracer_origin.set_color(interpolate_color(Q["color"], WHITE, (Q["num_tracer_origins"] - dot) / (2 * Q["num_tracer_origins"])))
        updated_path.add(tracer_origin)
        dot += 1

    if (frame_count > (duration - 2)*frame_rate):
        label_text = f"Orbiting Point Potentials — The Primal Assembly"
        # Calculate the opacity based on the time left
        seconds_remaining = duration - (frame_count / frame_rate)
        opacity = 1 - seconds_remaining/(2)
        rect = Rectangle(width=12, height=0.8, fill_color='#710193', fill_opacity=opacity)
        rect.to_edge(UP)
        text = Text(label_text, color=WHITE, font="Helvetica Neue", font_size=36, weight=BOLD, fill_opacity=opacity)
        text.move_to(rect.get_center())


        updated_path.add(rect)
        updated_path.add(text)

    mob.become(updated_path)
    
def get_updater(self, Q_key):
    def updater(mob, dt):
        update_path(mob, dt, self.Q[Q_key])
    return updater

class OrbitingPointCharges(Scene):
    
    # the construct is called once per animation.
    def construct(self):
        global frame_count

        # Add the initial circles and tracer_origins to the dictionary.
        self.Q = {
            "blue": {
                "circle": [],
                "angle_in_radians": PI,
                "trailing_path_angle_in_radians": 130*TAU/360,
                "potential_sphere_radius_increment": 0.06,
                "per_frame_increment_angle_in_radians": total_rotation_angle_in_radians / (duration * frame_rate ),
                "frames_between_tracer_origins": 6,
                "num_tracer_origins": 1,
                "opacity": 1,
                "color": PURE_BLUE,
                "tracer_origins": [],
                "dipole_orbit_radius": 2.0,
                "point_charge_representation_radius": 0.1,
                "tracer_origin_radius": 0.02,
                "sphere_fade_delta": 0.010,
                "initial_position": LEFT,
                "potential_spheres": []
            },
            "red": {
                "circle": [],
                "angle_in_radians": 0,
                "trailing_path_angle_in_radians": 130*TAU/360,
                "potential_sphere_radius_increment": 0.06,
                "per_frame_increment_angle_in_radians": total_rotation_angle_in_radians / (duration * frame_rate ),
                "frames_between_tracer_origins": 6,
                "num_tracer_origins": 1,
                "opacity": 1,
                "color": PURE_RED,
                "tracer_origins": [],
                "dipole_orbit_radius": 2.0,
                "point_charge_representation_radius": 0.1,
                "tracer_origin_radius": 0.02,
                "sphere_fade_delta": 0.010,
                "initial_position": RIGHT,
                "potential_spheres": []
            }
            
        }
        for Q_key in self.Q:
            self.Q[Q_key]["circle"] = Circle(color=self.Q[Q_key]["color"], radius=self.Q[Q_key]["point_charge_representation_radius"], fill_opacity=1).shift(self.Q[Q_key]["initial_position"] * self.Q[Q_key]["dipole_orbit_radius"])
            self.Q[Q_key]["sphere_fade_values"] = calculate_sphere_fade_values(self.Q[Q_key])
            self.Q[Q_key]["num_tracer_origins"] = self.Q[Q_key]["trailing_path_angle_in_radians"] / (self.Q[Q_key]["frames_between_tracer_origins"]*self.Q[Q_key]["per_frame_increment_angle_in_radians"]) - 3

            self.add(self.Q[Q_key]["circle"])
            self.Q[Q_key]['recent_path'] = draw_recent_path(self.Q[Q_key])
            self.add(self.Q[Q_key]['recent_path'])
        

        # for Q_key in self.Q:
            updater = get_updater(self, Q_key)
            self.Q[Q_key]['recent_path'].add_updater(updater)

        self.add_updater(self.increment_frame_count)

        self.play(
            Rotate(self.Q["blue"]["circle"], angle=total_rotation_angle_in_radians, about_point=ORIGIN),
            Rotate(self.Q["red"]["circle"], angle=total_rotation_angle_in_radians, about_point=ORIGIN),
            run_time=duration,
            rate_func=linear,
        )

        for Q_key in self.Q:
            updater = get_updater(self, Q_key)
            self.Q[Q_key]['recent_path'].remove_updater(updater)

    def increment_frame_count(self, dt):
        global frame_count
        frame_count += 1
