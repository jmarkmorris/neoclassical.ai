from manim import *
from tools import INDIGO, ELECTRIC_PURPLE
import random

class MovingAngle(Scene):
    def construct(self):
        self.camera.background_color = INDIGO
        
        # Add title and subtitle
        title = Text(
            "Grid of Moving Angles",
            font="Helvetica Neue",
            weight="LIGHT",
            font_size=36
        ).to_edge(UP, buff=0.5)
        
        subtitle = Text(
            "Multiple angle animations with different styles and behaviors",
            font="Helvetica Neue",
            weight="LIGHT",
            color=YELLOW,
            font_size=20
        ).next_to(title, DOWN, buff=0.1)
        
        self.add(title, subtitle)
        
        # Create a grid of 6 angles (2 rows, 3 columns)
        grid_positions = [
            # Row 1
            [-4, 1, 0],
            [0, 1, 0],
            [4, 1, 0],
            # Row 2
            [-4, -2, 0],
            [0, -2, 0],
            [4, -2, 0],
        ]
        
        # Different configurations for each angle
        angle_configs = [
            {
                "start_angle": 110,
                "end_angle": 350,
                "line1_style": {"stroke_color": BLUE},
                "line2_style": {"stroke_color": RED},
                "angle_style": {"color": YELLOW, "radius": 0.5},
                "dot_style": {"color": WHITE, "radius": 0.1},
                "label_style": {"color": WHITE},
                "clockwise": False,
                "rate_func": smooth
            },
            {
                "start_angle": 45,
                "end_angle": 315,
                "line1_style": {"stroke_color": GREEN, "stroke_width": 3},
                "line2_style": {"stroke_color": ORANGE, "stroke_width": 3},
                "angle_style": {"color": PURPLE, "radius": 0.7},
                "dot_style": {"color": YELLOW, "radius": 0.15},
                "label_style": {"color": YELLOW},
                "clockwise": True,
                "rate_func": there_and_back
            },
            {
                "start_angle": 180,
                "end_angle": 0,
                "line1_style": {"stroke_color": TEAL},
                "line2_style": {"stroke_color": PINK},
                "angle_style": {"color": GOLD, "radius": 0.6},
                "dot_style": {"color": PINK, "radius": 0.12},
                "label_style": {"color": GOLD},
                "clockwise": False,
                "rate_func": linear
            },
            {
                "start_angle": 90,
                "end_angle": 450,
                "line1_style": {"stroke_color": MAROON},
                "line2_style": {"stroke_color": PURPLE},
                "angle_style": {"color": GREEN, "radius": 0.4},
                "dot_style": {"color": MAROON, "radius": 0.08},
                "label_style": {"color": GREEN},
                "clockwise": True,
                "rate_func": rush_into
            },
            {
                "start_angle": 30,
                "end_angle": 330,
                "line1_style": {"stroke_color": ELECTRIC_PURPLE, "stroke_width": 2},
                "line2_style": {"stroke_color": BLUE, "stroke_width": 2},
                "angle_style": {"color": RED, "radius": 0.5, "other_angle": True},
                "dot_style": {"color": BLUE, "radius": 0.1},
                "label_style": {"color": RED},
                "clockwise": False,
                "rate_func": there_and_back_with_pause
            },
            {
                "start_angle": 0,
                "end_angle": 360,
                "line1_style": {"stroke_color": RED_E},
                "line2_style": {"stroke_color": BLUE_E},
                "angle_style": {"color": GREEN_E, "radius": 0.6},
                "dot_style": {"color": YELLOW_E, "radius": 0.1},
                "label_style": {"color": WHITE},
                "clockwise": True,
                "rate_func": wiggle
            }
        ]
        
        # Create all angle animations
        angle_groups = []
        trackers = []
        
        for i, (position, config) in enumerate(zip(grid_positions, angle_configs)):
            # Create a group for this angle animation
            angle_group = VGroup()
            
            # Set up angle components
            rotation_center = position + LEFT * 0.5
            theta_tracker = ValueTracker(config["start_angle"])
            trackers.append(theta_tracker)
            
            # Create lines with specified styles
            line1 = Line(rotation_center, rotation_center + RIGHT, **config["line1_style"])
            line_moving = Line(rotation_center, rotation_center + RIGHT, **config["line2_style"])
            
            # Apply dashed style if needed (for configs 3 and 4)
            if i == 2:  # Third config (index 2)
                line_moving.set_dash_pattern([0.1, 0.1])
            elif i == 3:  # Fourth config (index 3)
                line1.set_dash_pattern([0.1, 0.1])
            line_ref = line_moving.copy()
            
            # Add circle to hide joining artifact
            origin_dot = Circle(
                radius=config["dot_style"]["radius"], 
                color=config["dot_style"]["color"], 
                fill_opacity=1
            ).move_to(rotation_center)
            
            # Rotate the moving line
            line_moving.rotate(
                theta_tracker.get_value() * DEGREES, 
                about_point=rotation_center
            )
            
            # Create angle and label
            angle_kwargs = config["angle_style"].copy()
            if "other_angle" not in angle_kwargs:
                angle_kwargs["other_angle"] = False
            
            angle = Angle(line1, line_moving, **angle_kwargs)
            
            theta_label = MathTex(r"\theta", color=config["label_style"]["color"]).move_to(
                Angle(
                    line1, 
                    line_moving, 
                    radius=angle_kwargs["radius"] + 3 * SMALL_BUFF, 
                    other_angle=angle_kwargs["other_angle"]
                ).point_from_proportion(0.5)
            )
            
            # Add elements to the group
            angle_group.add(line1, line_moving, angle, theta_label, origin_dot)
            
            # Add a label for the configuration
            config_label = Text(
                f"Config {i+1}",
                font="Helvetica Neue",
                weight="LIGHT",
                font_size=16
            ).next_to(angle_group, DOWN, buff=0.2)
            angle_group.add(config_label)
            
            # Add updaters
            line_moving.add_updater(
                lambda x, lt=line_ref, tt=theta_tracker, rc=rotation_center: 
                x.become(lt.copy()).rotate(
                    tt.get_value() * DEGREES, 
                    about_point=rc
                )
            )
            
            angle.add_updater(
                lambda x, l1=line1, lm=line_moving, ak=angle_kwargs: 
                x.become(Angle(l1, lm, **ak))
            )
            
            theta_label.add_updater(
                lambda x, l1=line1, lm=line_moving, r=angle_kwargs["radius"], oa=angle_kwargs["other_angle"], c=config["label_style"]["color"]:
                x.move_to(
                    Angle(
                        l1, lm, radius=r + 3 * SMALL_BUFF, other_angle=oa
                    ).point_from_proportion(0.5)
                ).set_color(c)
            )
            
            # Add the group to the scene
            self.add(angle_group)
            angle_groups.append(angle_group)
        
        # Animate all angles with different behaviors
        animations = []
        for i, (tracker, config) in enumerate(zip(trackers, angle_configs)):
            end_value = config["end_angle"]
            if config["clockwise"] and end_value > config["start_angle"]:
                end_value = config["start_angle"] - (end_value - config["start_angle"])
            elif not config["clockwise"] and end_value < config["start_angle"]:
                end_value = config["start_angle"] + (config["start_angle"] - end_value)
                
            animations.append(
                tracker.animate.set_value(end_value).set_rate_func(config["rate_func"])
            )
        
        # Play all animations simultaneously with different durations
        self.play(
            *animations,
            run_time=5
        )
        
        # Add a second round of animations with color changes
        color_animations = []
        for i, angle_group in enumerate(angle_groups):
            # Change the color of the angle and label
            new_color = random.choice([RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE])
            angle = angle_group[2]  # The angle is the third element in the group
            label = angle_group[3]  # The label is the fourth element in the group
            
            color_animations.append(angle.animate.set_color(new_color))
            color_animations.append(label.animate.set_color(new_color))
        
        self.play(*color_animations, run_time=1)
        self.wait(2)
