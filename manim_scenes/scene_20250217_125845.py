from manim import *
import numpy as np
import random

class QuantumFieldTheoryScene(ThreeDScene):
    def construct(self):
        # Create a star field backdrop
        star_field = VGroup(*[Dot3D(point=np.array([random.uniform(-5, 5), random.uniform(-5, 5), random.uniform(-5, 5)]), radius=0.05) for _ in range(100)])
        self.play(FadeIn(star_field, run_time=2))
        self.wait(1)
        
        # Introduce a 3D axis frame
        axes = ThreeDAxes()
        self.play(GrowFromCenter(axes), run_time=2)
        self.move_camera(phi=75 * DEGREES, theta=45 * DEGREES, run_time=2)
        
        # Display large glowing title that shrinks and moves to the upper left
        title = Text("Quantum Field Theory: A Journey into the Electromagnetic Interaction", color=YELLOW).scale(1.5)
        self.play(Write(title), run_time=2)
        self.play(title.animate.scale(0.5).to_corner(UL), run_time=2)
        
        # Show a rotating wireframe representation of 4D Minkowski spacetime (rendered in 3D) with a light cone
        grid = Surface(
            lambda u, v: np.array([u, np.sin(v * PI) * np.cos(u * PI), v]),
            u_range=[-2, 2],
            v_range=[-2, 2],
            resolution=(15, 15),
            checkerboard_colors=[BLUE_D, BLUE_E]
        )
        grid.set_style(stroke_color=WHITE, stroke_width=1)
        self.play(FadeIn(grid, run_time=2))
        
        light_cone = ParametricSurface(
            lambda u, v: np.array([u, v, np.sqrt(u ** 2 + v ** 2)]),
            u_range=[-2, 2],
            v_range=[-2, 2],
            resolution=(10, 10)
        )
        light_cone.set_style(fill_opacity=0.3, stroke_width=0.5)
        self.play(FadeIn(light_cone, run_time=2))
        
        # Overlay color-coded relativistic metric equation ds^2 = -c^2dt^2+dx^2+dy^2+dz^2
        metric = MathTex(r"ds^2 \;=\; -c^2dt^2 \;+\; dx^2 \;+\; dy^2 \;+\; dz^2", color=GREEN).to_edge(UL)
        self.play(Write(metric), run_time=2)
        self.wait(2)
        
        # Zoom into the wireframe's origin to introduce basic quantum fields
        self.play(self.camera.frame.animate.move_to([0, 0, 0]).set(width=4), run_time=2)
        
        # Show ghostly overlay of undulating plane waves for electric and magnetic fields
        plane_e = Rectangle(width=4, height=2, color=RED, fill_opacity=0.5).shift(LEFT * 2)
        plane_b = Rectangle(width=4, height=2, color=BLUE, fill_opacity=0.5).shift(RIGHT * 2)
        label_e = Text("E Field", color=RED).next_to(plane_e, UP)
        label_b = Text("B Field", color=BLUE).next_to(plane_b, UP)
        arrow_e = Arrow3D(start=np.array([0, 0, 0]), end=np.array([0, 1, 0]), color=RED)
        arrow_b = Arrow3D(start=np.array([0, 0, 0]), end=np.array([1, 0, 0]), color=BLUE)
        self.play(
            FadeIn(plane_e),
            FadeIn(plane_b),
            FadeIn(label_e),
            FadeIn(label_b),
            FadeIn(arrow_e),
            FadeIn(arrow_b),
            run_time=2
        )
        self.play(Rotate(plane_e, angle=TAU, axis=UP, run_time=3), Rotate(plane_b, angle=TAU, axis=UP, run_time=3))
        
        # Animate Maxwell's equations transitioning from classical vector form to relativistic compact form
        maxwell_classical = VGroup(
            MathTex(r"\nabla \cdot \vec{E} \;=\; \frac{\rho}{\varepsilon_0}"),
            MathTex(r"\nabla \times \vec{E} \;=\; -\frac{\partial \vec{B}}{\partial t}")
        ).arrange(DOWN).to_edge(DL)
        maxwell_relativistic = MathTex(r"\partial_\mu F^{\mu\nu} \;=\; \mu_0J^\nu").to_edge(DL)
        self.play(Write(maxwell_classical), run_time=3)
        self.wait(1)
        self.play(Transform(maxwell_classical, maxwell_relativistic), run_time=3)
        self.wait(1)
        
        # Display the QED Lagrangian density on a semi-transparent plane with color-coded symbols
        qed_lagrangian = MathTex(
            r"\mathcal{L}_{\text{QED}} \;=\; \bar{\psi}(i\gamma^\mu D_\mu - m)\psi \; - \; \frac{1}{4}F_{\mu\nu}F^{\mu\nu}",
            color=YELLOW
        ).to_edge(UR)
        lagrangian_plane = Rectangle(width=6, height=2, fill_opacity=0.3, color=WHITE).to_edge(UR)
        self.play(FadeIn(lagrangian_plane, run_time=2), Write(qed_lagrangian, run_time=2))
        self.play(qed_lagrangian.animate.scale(1.1).set_color(RED), run_time=1)
        self.play(qed_lagrangian.animate.scale(1/1.1).set_color(YELLOW), run_time=1)
        
        # Illustrate gauge invariance with a phase transformation on the Dirac field
        gauge_text = MathTex(r"\psi(x) \;\to\; e^{i\alpha(x)}\psi(x)", color=PURPLE).move_to(UP * 2)
        self.play(Write(gauge_text), run_time=2)
        self.wait(1)
        self.play(FadeOut(gauge_text), run_time=1)
        
        # Transition to a black background to show a simplified Feynman diagram
        self.play(FadeToColor(axes, color=BLACK), FadeOut(star_field), run_time=2)
        self.camera.background_color = BLACK
        
        # Feynman diagram: two electron lines and a wavy photon line
        electron_line_left = Line3D(np.array([-3, -1, 0]), np.array([-1, 0, 0]), color=BLUE)
        electron_line_right = Line3D(np.array([3, -1, 0]), np.array([1, 0, 0]), color=BLUE)
        photon_line = Arc3D(start_angle=PI, angle=-PI, radius=2, color=YELLOW).shift(np.array([0,0,0]))
        electron_label_left = Text("e^-", color=BLUE).next_to(electron_line_left, DOWN)
        electron_label_right = Text("e^-", color=BLUE).next_to(electron_line_right, DOWN)
        photon_label = Text("\gamma", color=YELLOW).next_to(photon_line, UP)
        self.play(
            FadeIn(electron_line_left),
            FadeIn(electron_line_right),
            FadeIn(photon_line),
            Write(electron_label_left),
            Write(electron_label_right),
            Write(photon_label),
            run_time=2
        )
        
        # Animate coupling constant transformation from numeric to symbolic
        coupling_numeric = Text("1/137", color=ORANGE).move_to(UP*2)
        coupling_symbolic = MathTex(r"\frac{e^2}{4\pi\varepsilon_0\hbar c}", color=ORANGE).move_to(UP*2)
        self.play(Write(coupling_numeric), run_time=2)
        self.wait(1)
        self.play(Transform(coupling_numeric, coupling_symbolic), run_time=2)
        self.wait(1)
        
        # Transition to a 2D graph showing the running coupling constant with energy scale
        graph = Axes(x_range=[0, 10, 1], y_range=[0, 5, 1], x_length=6, y_length=4).to_edge(DL)
        x_label = Text("Energy Scale", font_size=24).next_to(graph, DOWN)
        y_label = Text("Coupling Strength", font_size=24).rotate(90).next_to(graph, LEFT)
        graph_line = graph.plot(lambda x: 4/(1+0.3*x), color=TEAL)
        self.play(FadeIn(graph), FadeIn(x_label), FadeIn(y_label), Create(graph_line), run_time=3)
        
        # Final sequence: Collage of all elements with summary text
        summary_text = Text("QED: Unifying Light and Matter Through Gauge Theory", color=WHITE).scale(1.2)
        collage_sub = Text("Finis", color=WHITE).scale(0.8).next_to(summary_text, DOWN)
        self.play(FadeIn(summary_text), run_time=2)
        self.play(FadeIn(collage_sub), run_time=2)
        self.wait(2)
        
        # Zoom out to reveal the cosmic backdrop of star field
        self.play(FadeOut(summary_text), FadeOut(collage_sub), run_time=2)
        self.play(FadeIn(star_field, run_time=2))
        self.wait(2)

if __name__ == "__main__":
    scene = QuantumFieldTheoryScene()
    scene.render()