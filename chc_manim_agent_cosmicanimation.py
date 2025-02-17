from manim import *
import numpy as np

class CosmicAnimation(Scene):
    def construct(self):
        self.intro_scene()
        self.minkowski_scene()
        self.wave_scene()
        self.maxwell_scene()
        self.qed_scene()
        self.feynman_scene()
        self.running_coupling_scene()
        self.finale_scene()

    def intro_scene(self):
        # Animated starfield background
        stars = VGroup(*[
            Dot(radius=0.02*np.random.random())
            .move_to(10*(np.random.random(3) - 0.5))
            .set_color(interpolate_color(WHITE, BLUE_E, np.random.random()))
            for _ in range(150)
        ])
        
        def update_stars(mob, dt):
            for star in mob:
                star.shift(0.02*RIGHT*dt + 0.01*(np.random.random(3)-0.5)*dt)
                if star.get_center()[0] > 7:
                    star.move_to([-7*np.random.random(), np.random.uniform(-4,4), 0])
        
        stars.add_updater(update_stars)
        self.add(stars)
        
        title = Text("Cosmic Animation", font_size=72, gradient=(YELLOW, ORANGE))
        title.set_stroke(width=3, color=YELLOW)
        self.play(
            title.animate.shift(UP),
            VFadeIn(title),
            run_time=2
        )
        self.wait(2)
        self.play(FadeOut(title))
        stars.clear_updaters()

    def minkowski_scene(self):
        axes = ThreeDAxes(
            x_range=[-3,3,1],
            y_range=[-3,3,1],
            z_range=[-3,3,1],
            axis_config={"stroke_width": 2}
        )
        
        # Proper light cone parametrization
        light_cone = ParametricSurface(
            lambda u,v: np.array([
                u*np.cos(v),
                u*np.sin(v),
                u
            ]),
            u_range=[0,2],
            v_range=[0,2*PI],
            checkerboard_colors=[BLUE_D, BLUE_E],
            resolution=(24,24)
        
        metric = MathTex(r"ds^2 = -dt^2 + dx^2 + dy^2 + dz^2")
        metric.to_corner(UL).set_color_by_gradient(BLUE, GREEN)
        
        self.move_camera(phi=75*DEGREES, theta=30*DEGREES)
        self.play(
            Create(axes),
            Write(metric),
            DrawBorderThenFill(light_cone),
            run_time=2
        )
        self.begin_ambient_camera_rotation(rate=0.15)
        self.wait(3)
        self.stop_ambient_camera_rotation()
        self.play(FadeOut(Group(axes, light_cone, metric)))

    def wave_scene(self):
        plane = NumberPlane(
            x_range=[0, 8],
            y_range=[-2, 2],
            background_line_style={
                "stroke_color": GREY_D,
                "stroke_width": 2
            }
        )
        
        wave = plane.plot(
            lambda x: np.sin(x) * np.exp(-0.2*x),
            color=TEAL,
            stroke_width=4
        )
        
        dot = Dot(color=RED).move_to(plane.c2p(0,0))
        wave_line = Line(ORIGIN, 0.1*UP, color=RED).move_to(dot)
        
        self.play(Create(plane), run_time=1.5)
        self.play(
            Create(wave),
            GrowFromCenter(dot),
            run_time=3,
            rate_func=rate_functions.ease_in_out_sine
        )
        
        def update_wave(mob, alpha):
            x = interpolate(0, 8, alpha)
            y = np.sin(x) * np.exp(-0.2*x)
            mob.move_to(plane.c2p(x, y))
            mob.rotate(20*DEGREES*dt)
        
        self.play(
            MoveAlongPath(dot, wave, rate_func=linear),
            UpdateFromAlphaFunc(wave_line, update_wave),
            run_time=8,
        )
        self.play(FadeOut(Group(plane, wave, dot)))

    def maxwell_scene(self):
        maxwell_eqs = MathTex(
            r"\nabla \cdot \mathbf{E} = \rho/\epsilon_0 \\",
            r"\nabla \cdot \mathbf{B} = 0 \\",
            r"\nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t} \\",
            r"\nabla \times \mathbf{B} = \mu_0\mathbf{J} + \mu_0\epsilon_0\frac{\partial \mathbf{E}}{\partial t}"
        ).arrange(DOWN, aligned_edge=LEFT)
        
        covariant_form = MathTex(
            r"\partial_\mu F^{\mu\nu} = J^\nu"
        ).scale(1.5).set_color_by_gradient(BLUE, GREEN)
        
        self.play(Write(maxwell_eqs), run_time=3)
        self.wait(2)
        self.play(
            TransformMatchingTex(
                maxwell_eqs,
                covariant_form,
                path_arc=30*DEGREES
            ),
            run_time=2
        )
        self.wait(2)
        self.play(FadeOut(covariant_form))

    def qed_scene(self):
        lagrangian = MathTex(
            r"\mathcal{L}_{\text{QED}} = ",
            r"-\frac{1}{4}F_{\mu\nu}F^{\mu\nu} ",
            r"+ \bar{\psi}(i\gamma^\mu D_\mu - m)\psi ",
            r"+ e\bar{\psi}\gamma^\mu A_\mu\psi"
        ).arrange(DOWN, aligned_edge=LEFT)
        
        gauge_transform = MathTex(
            r"A_\mu \to A_\mu + \partial_\mu \Lambda \\",
            r"\psi \to e^{ie\Lambda}\psi"
        ).next_to(lagrangian, DOWN, buff=1)
        
        box = SurroundingRectangle(lagrangian, buff=0.5, color=BLUE)
        
        self.play(
            Write(lagrangian[0]),
            Create(box),
            run_time=2
        )
        self.play(
            LaggedStart(
                *[Write(term) for term in lagrangian[1:]],
                lag_ratio=0.3
            ),
            run_time=3
        )
        self.wait()
        self.play(Write(gauge_transform))
        self.wait(3)
        self.play(FadeOut(Group(lagrangian, gauge_transform, box)))

    def feynman_scene(self):
        diagram = FeynmanDiagram(
            incoming_edges=[("e^-", LEFT), ("photon", UP)],
            outgoing_edges=[("e^-", RIGHT), ("photon", DOWN)],
            vertex_config={"radius": 0.2, "color": RED},
            edge_config={
                "e^-": {"color": BLUE, "stroke_width": 3},
                "photon": {"color": YELLOW, "stroke_width": 3}
            }
        ).scale(1.5)
        
        label = Text("QED Vertex", color=WHITE).next_to(diagram, UP)
        
        self.play(DrawBorderThenFill(diagram))
        self.play(Write(label))
        self.wait(2)
        self.play(FadeOut(Group(diagram, label)))

    def running_coupling_scene(self):
        ax = Axes(
            x_range=[1, 10], 
            y_range=[0, 1],
            x_axis_config={"numbers_to_include": np.arange(1,11)},
            y_axis_config={"numbers_to_include": np.arange(0,1.1,0.2)}
        ).add_coordinates()
        
        curve = ax.plot(
            lambda x: 1/np.log(x),
            color=GREEN,
            stroke_width=4
        )
        area = ax.get_area(curve, x_range=[2,10], color=GREEN_E, opacity=0.3)
        
        label = ax.get_graph_label(
            curve,
            label=MathTex(r"\alpha(\mu) \propto \frac{1}{\ln\mu}"),
            direction=UR
        )
        
        self.play(Create(ax), run_time=2)
        self.play(
            Create(curve),
            FadeIn(area),
            Write(label),
            run_time=3
        )
        self.wait(3)
        self.play(FadeOut(Group(ax, curve, area, label)))

    def finale_scene(self):
        elements = VGroup(
            Text("Minkowski Space", color=BLUE),
            Text("Maxwell's Equations", color=TEAL),
            Text("QED Lagrangian", color=GREEN),
            Text("Feynman Diagrams", color=YELLOW),
            Text("Running Coupling", color=RED)
        ).arrange_in_grid(3, 3, buff=1)
        
        self.play(
            LaggedStart(
                *[GrowFromCenter(e) for e in elements],
                lag_ratio=0.2
            ),
            run_time=3
        )
        self.wait(2)
        
        finis = Text("Finis", font_size=96, gradient=(RED, GOLD))
        self.play(
            Transform(elements, finis),
            run_time=3,
            rate_func=rate_functions.smooth
        )
        self.wait(3)

if __name__ == "__main__":
    module_name = os.path.basename(__file__)
    command = f"manim -pql {module_name} CosmicAnimation"
    print(f"Render with: {command}")