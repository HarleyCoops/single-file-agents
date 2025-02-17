from manim import *
import numpy as np

class QEDAnimation(Scene):
    def construct(self):
        # Star field backdrop
        stars = VGroup(*[
            Dot(point=np.array([np.random.uniform(-8,8), np.random.uniform(-4,4), 0]), radius=0.03, color=WHITE)
            for _ in range(150)
        ])
        self.add(stars)
        self.wait(0.5)

        # 3D axes with wireframe spacetime grid and light cone
        axes = ThreeDAxes(x_range=[-4,4,1], y_range=[-4,4,1], z_range=[-4,4,1])
        self.play(Create(axes), run_time=1)

        # Glowing title
        title = Text("Quantum Electrodynamics", font_size=48, color=YELLOW)
        title.set_stroke(width=2)
        self.play(FadeIn(title), run_time=1)
        self.wait(0.5)
        self.play(title.animate.scale(0.5).to_corner(UP + LEFT), run_time=1)
        
        # 3D wireframe spacetime grid (simulate with a grid of lines)
        grid_lines = VGroup()
        for x in np.linspace(-4,4,9):
            for z in np.linspace(-4,4,9):
                line = Line3D(start=[x, -4, z], end=[x, 4, z], color=BLUE)
                grid_lines.add(line)
        self.play(Create(grid_lines), run_time=2)
        
        # Light cone using ParametricFunction
        light_cone1 = ParametricFunction(
            lambda t: np.array([t, t, t]), t_range=[0,2],
            color=RED
        )
        light_cone2 = ParametricFunction(
            lambda t: np.array([t, t, -t]), t_range=[0,2],
            color=RED
        )
        self.play(Create(light_cone1), Create(light_cone2), run_time=1.5)
        
        # Relativistic metric equation overlay
        metric_eq = MathTex(r"ds^2 =", r"-c^2", r"\,dt^2", r"+dx^2", r"+dy^2", r"+dz^2", font_size=36)
        metric_eq.to_corner(UR)
        self.play(Write(metric_eq), run_time=2)
        self.wait(0.5)
        
        # Camera zoom into grid's origin
        self.play(self.camera.frame.animate.move_to(ORIGIN).set(width=6), run_time=2)
        self.wait(0.5)
        
        # Undulating E and B fields with labels and arrows
        # E field
        e_field = VGroup()
        for a in np.linspace(-3,3,15):
            curve = FunctionGraph(lambda t, a=a: 0.5*np.sin(2*t + a), x_range=[-3,3], color=TEAL)
            e_field.add(curve)
        e_label = MathTex(r"\vec{E}", font_size=36).next_to(e_field, RIGHT)
        e_arrow = Arrow(start=ORIGIN, end=RIGHT, color=TEAL)
        # B field
        b_field = VGroup()
        for a in np.linspace(-3,3,15):
            curve = FunctionGraph(lambda t, a=a: 0.5*np.cos(2*t + a), x_range=[-3,3], color=PURPLE)
            b_field.add(curve)
        b_label = MathTex(r"\vec{B}", font_size=36).next_to(b_field, RIGHT)
        b_arrow = Arrow(start=ORIGIN, end=RIGHT, color=PURPLE)

        self.play(FadeIn(e_field), Write(e_label), GrowArrow(e_arrow), run_time=2)
        self.play(FadeIn(b_field), Write(b_label), GrowArrow(b_arrow), run_time=2)
        self.wait(0.5)
        
        # Transition to Maxwell's equations transformation
        maxwell_classical = VGroup(
            MathTex(r"\nabla \cdot \vec{E} = \frac{\rho}{\epsilon_0}", font_size=28),
            MathTex(r"\nabla \cdot \vec{B} = 0", font_size=28),
            MathTex(r"\nabla \times \vec{E} = -\frac{\partial \vec{B}}{\partial t}", font_size=28),
            MathTex(r"\nabla \times \vec{B} = \mu_0 \vec{J} + \mu_0 \epsilon_0 \frac{\partial \vec{E}}{\partial t}", font_size=28)
        ).arrange(DOWN, aligned_edge=LEFT).to_edge(LEFT)
        maxwell_compact = MathTex(r"\partial_\mu F^{\mu\nu} = \mu_0 J^\nu", font_size=36).to_edge(RIGHT)
        self.play(Write(maxwell_classical), run_time=3)
        self.wait(0.5)
        self.play(Transform(maxwell_classical.copy(), maxwell_compact), run_time=2)
        self.wait(0.5)
        
        # QED Lagrangian density on semi-transparent plane with pulsating effect
        plane = Rectangle(width=6, height=2, fill_color=BLACK, fill_opacity=0.5)
        lagrangian = MathTex(r"\mathcal{L} =", r"-\frac{1}{4} F_{\mu\nu}F^{\mu\nu}", font_size=36)
        group_plane = VGroup(plane, lagrangian).to_edge(DOWN)
        self.play(FadeIn(group_plane), run_time=1)
        self.play(group_plane.animate.scale(1.1), run_time=0.5)
        self.play(group_plane.animate.scale(1/1.1), run_time=0.5)
        self.wait(0.5)
        
        # Gauge invariance hint: overlaid rotating circle
        gauge_circle = Circle(radius=1.5, color=GOLD, stroke_width=3)
        gauge_circle.move_to(plane.get_center())
        self.play(Create(gauge_circle), run_time=1)
        self.play(Rotate(gauge_circle, angle=TAU), run_time=2)
        self.wait(0.5)
        
        # Clear previous elements for Feynman diagram
        self.play(FadeOut(maxwell_classical), FadeOut(maxwell_compact), FadeOut(group_plane), FadeOut(gauge_circle), run_time=1)
        
        # Feynman diagram: two electron lines and a wavy photon line with label and coupling constant transformation
        electron1 = Line(LEFT, RIGHT, color=BLUE).shift(UP*0.5)
        electron2 = Line(LEFT, RIGHT, color=BLUE).shift(DOWN*0.5)
        photon = ParametricFunction(
            lambda t: np.array([t, 0.3*np.sin(4*t), 0]),
            t_range=[-1,1],
            color=RED
        )
        photon_label = MathTex(r"\gamma", font_size=28).next_to(photon, UP, buff=0.1)
        coupling_num = MathTex(r"0.0073", font_size=28).to_corner(UL)
        coupling_sym = MathTex(r"\alpha", font_size=28).to_corner(UL)
        feynman = VGroup(electron1, electron2, photon, photon_label)
        self.play(Create(electron1), Create(electron2), Create(photon), Write(photon_label), Write(coupling_num), run_time=2)
        self.wait(0.5)
        self.play(Transform(coupling_num, coupling_sym), run_time=1.5)
        self.wait(0.5)
        
        # 2D graph of running coupling constant vs. energy scale
        axes2d = Axes(x_range=[0,10,1], y_range=[0,0.1,0.02], x_length=6, y_length=3, tips=True).to_edge(LEFT, buff=1)
        graph = axes2d.plot(lambda x: 0.08/(1+0.3*x), color=GREEN)
        graph_label = axes2d.get_graph_label(graph, label=MathTex(r"\alpha(E)"))
        self.play(Create(axes2d), run_time=1.5)
        self.play(Create(graph), Write(graph_label), run_time=2)
        self.wait(0.5)
        
        # Collage summary text
        summary = VGroup(
            Text("Spacetime", font_size=24),
            Text("Fields", font_size=24),
            Text("Interactions", font_size=24),
            Text("Symmetries", font_size=24)
        ).arrange_in_grid(rows=2, buff=0.5).to_edge(RIGHT)
        self.play(FadeIn(summary), run_time=2)
        self.wait(1)
        
        # Graceful fade out
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=2)
        self.wait(1)
