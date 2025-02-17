from manim import *
import numpy as np

class QEDAnimation(Scene):
    def construct(self):
        # Star Field
        stars = VGroup(*[Dot(point=[np.random.uniform(-8,8),np.random.uniform(-4.5,4.5),0], radius=0.02, color=WHITE) for _ in range(100)])
        self.add(stars)
        self.play(LaggedStartMap(FadeOut, stars, lag_ratio=0.02), run_time=2)
        self.play(LaggedStartMap(FadeIn, stars, lag_ratio=0.02), run_time=2)
        self.wait(0.5)

        # 3D Axis Frame
        axes = ThreeDAxes(x_range=[-5,5,1], y_range=[-5,5,1], z_range=[-5,5,1])
        self.play(Write(axes), run_time=2)
        self.wait(0.5)

        # Glowing Title
        title = Text("Quantum Electrodynamics", font_size=48, color=YELLOW).set_stroke(width=5, color=YELLOW)
        self.play(Write(title), run_time=2)
        self.play(title.animate.scale(0.5).to_corner(UL), run_time=2)
        self.wait(0.5)

        # Rotating 3D Wireframe Spacetime Grid with Light Cone
        grid = Surface(
            lambda u, v: np.array([u, v, 0]),
            u_range=[-3,3],
            v_range=[-3,3],
            resolution=(10,10),
            fill_opacity=0,
            stroke_color=BLUE,
            stroke_width=1
        )
        cone = ParametricSurface(
            lambda u, v: np.array([v * np.cos(u), v * np.sin(u), v]),
            u_range=[0, TAU],
            v_range=[0, 3],
            resolution=(20,20),
            fill_opacity=0,
            stroke_color=RED,
            stroke_width=2
        )
        grid_group = VGroup(grid, cone)
        self.play(Write(grid_group), run_time=3)
        self.play(Rotate(grid_group, angle=PI/2, axis=UP), run_time=3)
        self.wait(0.5)

        # Relativistic Metric Equation Overlay
        metric = MathTex(r"ds^2 = -c^2\,dt^2 + dx^2 + dy^2 + dz^2", font_size=36).to_edge(UP)
        self.play(Write(metric), run_time=2)
        self.wait(0.5)

        # Zoom into Region with Undulating E and B Fields
        self.play(self.camera.frame.animate.set_width(4).move_to([0,0,0]), run_time=2)
        e_field = VMobject()
        e_field.set_points_smoothly([np.array([x, 0.5*np.sin(x), 0]) for x in np.linspace(-3,3,100)])
        b_field = VMobject()
        b_field.set_points_smoothly([np.array([x, 0.5*np.cos(x), 0]) for x in np.linspace(-3,3,100)])
        e_field.set_color(ORANGE)
        b_field.set_color(PURPLE)
        e_label = MathTex(r"\mathbf{E}", font_size=24).next_to(e_field, UP)
        b_label = MathTex(r"\mathbf{B}", font_size=24).next_to(b_field, DOWN)
        self.play(Create(e_field), Write(e_label), run_time=2)
        self.play(Create(b_field), Write(b_label), run_time=2)
        self.wait(0.5)

        # Animated Transformation of Maxwell's Equations
        maxwell_eq1 = MathTex(r"\nabla \cdot \mathbf{E} = \frac{\rho}{\epsilon_0}", font_size=28).to_edge(LEFT).shift(UP*1.5)
        maxwell_eq2 = MathTex(r"\nabla \cdot \mathbf{B} = 0", font_size=28).next_to(maxwell_eq1, DOWN, aligned_edge=LEFT)
        maxwell_eq3 = MathTex(r"\nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}", font_size=28).next_to(maxwell_eq2, DOWN, aligned_edge=LEFT)
        maxwell_eq4 = MathTex(r"\nabla \times \mathbf{B} = \mu_0 \mathbf{J}+\mu_0 \epsilon_0 \frac{\partial \mathbf{E}}{\partial t}", font_size=28).next_to(maxwell_eq3, DOWN, aligned_edge=LEFT)
        maxwell_group = VGroup(maxwell_eq1, maxwell_eq2, maxwell_eq3, maxwell_eq4)
        self.play(Write(maxwell_group), run_time=3)
        new_maxwell = MathTex(
            r"\nabla \cdot \mathbf{E} = \frac{\rho}{\epsilon_0}", 
            r"\nabla \cdot \mathbf{B} = 0", 
            r"\nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}",
            r"\nabla \times \mathbf{B} = \mu_0 \mathbf{J}+\mu_0 \epsilon_0 \frac{\partial \mathbf{E}}{\partial t}",
            font_size=28
        ).arrange(DOWN, aligned_edge=LEFT).to_edge(LEFT).shift(DOWN*0.5)
        self.play(Transform(maxwell_group, new_maxwell), run_time=3)
        self.wait(0.5)

        # QED Lagrangian Density on Semi-transparent Plane with Pulsating Effect
        lagrangian = MathTex(
            r"\mathcal{L}_{\text{QED}} = \bar{\psi}(i\gamma^\mu D_\mu - m)\psi - \frac{1}{4}F_{\mu\nu}F^{\mu\nu}",
            font_size=32
        ).to_edge(DOWN)
        plane = Rectangle(width=lagrangian.width+1, height=lagrangian.height+1, fill_color=BLACK, fill_opacity=0.5)
        lagrangian_group = VGroup(plane, lagrangian)
        self.play(FadeIn(lagrangian_group), run_time=2)
        self.play(lagrangian_group.animate.scale(1.1), run_time=1)
        self.play(lagrangian_group.animate.scale(1/1.1), run_time=1)
        self.wait(0.5)

        # Transition to Feynman Diagram
        self.play(FadeOut(maxwell_group), FadeOut(plane), FadeOut(lagrangian), FadeOut(e_field), FadeOut(b_field), FadeOut(e_label), FadeOut(b_label), FadeOut(metric), FadeOut(grid_group), run_time=2)
        self.play(self.camera.frame.animate.set_width(14).move_to(ORIGIN), run_time=2)
        electron1 = Line(start=[-3,1,0], end=[0,0,0], color=BLUE, stroke_width=4)
        electron2 = Line(start=[-3,-1,0], end=[0,0,0], color=BLUE, stroke_width=4)
        photon = ParametricFunction(lambda t: np.array([t, 0.5*np.sin(5*t), 0]), t_range=[0,3], color=RED, stroke_width=4)
        feynman = VGroup(electron1, electron2, photon)
        self.play(Write(electron1), Write(electron2), Write(photon), run_time=3)
        coupling_num = MathTex(r"\alpha = \frac{1}{137}", font_size=32).next_to(photon, UP)
        self.play(Write(coupling_num), run_time=2)
        coupling_sym = MathTex(r"\alpha", font_size=32).next_to(photon, UP)
        self.play(Transform(coupling_num, coupling_sym), run_time=2)
        self.wait(0.5)

        # 2D Graph Showing Running Coupling Constant
        axes2 = Axes(x_range=[0,10,2], y_range=[0,1,0.2], x_length=6, y_length=3).to_edge(RIGHT)
        graph = axes2.plot(lambda x: 1/(1+np.sqrt(x)), x_range=[0,10], color=GREEN)
        self.play(Create(axes2), run_time=2)
        self.play(Create(graph), run_time=3)
        self.wait(0.5)

        # Collage Summary Text
        summary = Tex("QED: The Symphony of Quantum Electrodynamics", font_size=36, color=WHITE).move_to(ORIGIN)
        self.play(FadeIn(summary), run_time=3)
        self.wait(2)
        self.play(FadeOut(summary))
        self.wait(1)