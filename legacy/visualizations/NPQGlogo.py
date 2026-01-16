# manim -pqh --disable_caching NPQGlogo.py NPQGlogo -p

from manim import *

frame_rate = 60
config.pixel_width = 2998
config.pixel_height = 1686
config.frame_rate = frame_rate

ELECTRIC_PURPLE = "#8F00FF"
DEEP_PURPLE = "#47015D"
TRUE_PURPLE = "#6A0DAD"
INDIGO = "#4B0082"
NORTHWESTERN = "#4E2A84"



colors = [PURE_BLUE, PURE_RED, PURE_BLUE, PURE_RED]

class NPQGlogo(Scene):
    def construct(self):
        self.camera.background_color = INDIGO # looks good
        # self.camera.background_color = ?

        font_scaler = 2.4 * DEFAULT_FONT_SIZE
        letters = ["N", "P", "Q", "G"]
        circles = [Circle(radius=0.9, color=color).set_fill(color=color, opacity=1) for color in colors]
        texts = [Text(text=letter, color=color, font="Helvetica Neue", font_size=font_scaler, weight=BOLD) for letter, color in zip(letters, colors)]
        for circle, text in zip(circles, texts):
            circle.add(text)
        N, P, Q, G = circles

        N.move_to([-3.3,0,0])
        P.next_to(N, RIGHT, buff=0.4)        
        Q.next_to(P, RIGHT, buff=0.4)        
        G.next_to(Q, RIGHT, buff=0.4)  
        Logo = VGroup(N,P,Q,G)      
        NP_Group = VGroup(N,P)      
        QG_Group = VGroup(Q,G) 

        # grid = NumberPlane(
        #     x_range=[-7, 7],
        #     y_range=[-4, 4],
        #     axis_config={
        #         "stroke_color": WHITE,
        #         "stroke_width": 1,
        #         "include_ticks": False,
        #         "include_tip": False,
        #     },
        #     background_line_style={
        #         "stroke_color": ELECTRIC_PURPLE,
        #         "stroke_width": 1,
        #     }
        # )
        # self.add(grid)

        self.play(GrowFromPoint(Logo, ORIGIN, rate_func=rate_functions.rush_from), run_time=0.5)

        self.play(
            Rotating(NP_Group, radians = -2*TAU),
            Rotating(QG_Group, radians = 2*TAU),
            run_time = 1.5,
        )

        for circle, color in zip(circles, colors):
            self.play(
                UpdateFromAlphaFunc(
                    circle[1],
                    lambda mob, alpha: mob.set_color(interpolate_color(color, WHITE, alpha))
                ),
                run_time=0.1
            )

        N.generate_target()
        N.target.move_to([-3.5,2.85,0])
        P.generate_target()
        P.target.next_to(N.target, DOWN, buff=0.1)        
        Q.generate_target()
        Q.target.next_to(P.target, DOWN, buff=0.1)        
        G.generate_target()
        G.target.next_to(Q.target, DOWN, buff=0.1) 
        self.play(MoveToTarget(N), MoveToTarget(P), MoveToTarget(Q), MoveToTarget(G))

        font_scaler = 2.2*DEFAULT_FONT_SIZE

        circles = [N, P, Q, G]

        texts = ["eoclassical", "hysics &", "uantum", "ravity"]

        for circle, text in zip(circles, texts):
            text_right_of_circle = Text(text=text, color=WHITE, font="Helvetica Neue", font_size=font_scaler, weight=NORMAL)
            text_right_of_circle.next_to(circle, 0.6 * RIGHT)
            text_right_of_circle.shift(np.array([0, -0.12, 0]))
            self.play(Create(text_right_of_circle, run_time=0.5, rate_func=smooth))

        self.wait(0.5)
