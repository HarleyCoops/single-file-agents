from manim import *
import numpy as np

class QuantumFieldTheoryAnimation(ThreeDScene):
    def construct(self):
        # Step 1: Panoramic star field backdrop
        dots = VGroup(*[Dot3D(point=[np.random.uniform(-7, 7), np.random.uniform(-4, 4), np.random.uniform(-1, 1)], radius=0.03, color=WHITE) for _ in range(100)])
        self.play(LaggedStart(*[FadeIn(dot, shift=DOWN, run_time=0.1) for dot in dots], lag_ratio=0.01))

        # Step 2: 3D Axis frame and title
        axes = ThreeDAxes()
        self.play(FadeIn(axes))
        title = Text(r"Quantum Field Theory: A Journey into the Electromagnetic Interaction", font_size=36, color=YELLOW)
        # As a placeholder for glowing, we simply use color effects
        self.play(FadeIn(title))
        self.play(title.animate.scale(0.5).to_corner(UL), run_time=2)

        # Step 3: Rotating wireframe 4D Minkowski spacetime proxy (grid) and light cone
        grid = Surface(
            lambda u, v: np.array([u, v, 0]),
            u_range=[-3, 3],
            v_range=[-3, 3],
            resolution=(10, 10),
            fill_opacity=0,
            stroke_color=BLUE,
            stroke_width=1
        )
        self.play(FadeIn(grid))
        light_cone = ParametricFunction(
            lambda t: np.array([t, t * np.tan(PI / 6), abs(t)]),
            t_range=[-2, 2],
            color=GREEN
        )
        self.play(ShowCreation(light_cone))
        self.play(Rotate(grid, angle=TAU, axis=OUT, run_time=4, rate_func=linear))

        # Step 4: Color-coded relativistic metric equation
        metric = MathTex(
            r"ds^2", "=", r"-c^2dt^2", "+", r"dx^2", "+", r"dy^2", "+", r"dz^2",
            tex_to_color_map={r"-c^2dt^2": RED, r"dx^2": BLUE, r"dy^2": BLUE, r"dz^2": BLUE}
        )
        metric.to_edge(UP)
        self.play(Write(metric))
        self.wait(1)

        # Step 5: Undulating plane waves for electric and magnetic fields
        e_wave = always_redraw(lambda: ParametricFunction(
            lambda z: np.array([0.5 * np.sin(2*z + self.renderer.time), 0, z]),
            t_range=[-4, 4],
            color=RED
        ))
        b_wave = always_redraw(lambda: ParametricFunction(
            lambda z: np.array([-0.5 * np.sin(2*z + self.renderer.time), 0, z]),
            t_range=[-4, 4],
            color=BLUE
        ))
        e_label = MathTex(r"\vec{E}", color=RED).next_to(e_wave, RIGHT)
        b_label = MathTex(r"\vec{B}", color=BLUE).next_to(b_wave, LEFT)
        arrow = always_redraw(lambda: Arrow3D(np.array([0, 0, -4]), np.array([0, 0, 4]), color=YELLOW, stroke_width=4))
        self.play(FadeIn(e_wave), FadeIn(b_wave), FadeIn(e_label), FadeIn(b_label), FadeIn(arrow))
        self.wait(2)

        # Step 6: Maxwell's equations transformation
        classical = MathTex(
            r"\nabla\cdot\vec{E}=", r"\frac{\rho}{\varepsilon_0}",
            r"\quad",
            r"\nabla\times\vec{B}-\frac{\partial \vec{E}}{\partial t}=", r"\mu_0\vec{J}"
        )
        classical.to_edge(DOWN)
        relativistic = MathTex(r"\partial_\mu F^{\mu\nu}=", r"\mu_0 J^\nu")
        relativistic.to_edge(DOWN)
        self.play(FadeIn(classical))
        self.wait(1)
        self.play(Transform(classical, relativistic, run_time=2))
        self.wait(1)

        # Step 7: QED Lagrangian with color-coded components
        qed = MathTex(
            r"\mathcal{L}_{QED}=", r"\bar{\psi}(i\gamma^\mu D_\mu - m)\psi - \frac{1}{4}F_{\mu\nu}F^{\mu\nu}",
            tex_to_color_map={r"\psi": ORANGE, r"D_\mu": GREEN, r"\gamma^\mu": TURQUOISE, r"F_{\mu\nu}": GOLD}
        )
        qed.to_edge(UP)
        psi_transform = MathTex(r"\psi \rightarrow e^{i\alpha(x)}\psi", color=WHITE)
        psi_transform.next_to(qed, DOWN)
        self.play(ReplacementTransform(classical.copy(), qed), run_time=2)
        self.wait(1)
        self.play(FadeIn(psi_transform))
        self.wait(1)

        # Fade out previous elements to transition scene
        self.play(FadeOut(VGroup(grid, light_cone, e_wave, b_wave, arrow, e_label, b_label, classical, metric, qed, psi_transform)), run_time=2)

        # Step 8: Feynman diagram on black background
        self.camera.background_color = BLACK
        electron1 = Arrow(LEFT, RIGHT, buff=0, color=WHITE).shift(UP*1)
        electron2 = Arrow(LEFT, RIGHT, buff=0, color=WHITE).shift(DOWN*1)
        photon = Arrow(RIGHT, LEFT, buff=0, color=YELLOW).shift(ORIGIN)
        electron_label1 = MathTex(r"e^-", color=WHITE).next_to(electron1, UP)
        electron_label2 = MathTex(r"e^-", color=WHITE).next_to(electron2, DOWN)
        photon_label = MathTex(r"\gamma", color=YELLOW).next_to(photon, UP)
        self.play(FadeIn(electron1), FadeIn(electron2), FadeIn(photon),
                  FadeIn(electron_label1), FadeIn(electron_label2), FadeIn(photon_label))
        self.wait(1)
        coupling_num = MathTex(r"0.3", color=WHITE).to_edge(LEFT)
        coupling_sym = MathTex(r"g", color=WHITE).to_edge(LEFT)
        self.play(FadeIn(coupling_num))
        self.wait(1)
        self.play(Transform(coupling_num, coupling_sym))
        self.wait(1)

        # Step 9: 2D Plot for running coupling constant
        axes2d = Axes(x_range=[0, 10, 1], y_range=[0, 10, 1], x_length=5, y_length=3, tips=True)
        axes2d.to_edge(RIGHT, buff=1)
        graph = axes2d.get_line_graph(x_values=[1,2,3,4,5,6,7,8,9], y_values=[1,2,3,4,5,6,7,8,9], line_color=GREEN)
        labels2d = axes2d.get_axis_labels(x_label=r"Energy Scale", y_label=r"Coupling Strength")
        self.play(FadeIn(axes2d), FadeIn(graph), FadeIn(labels2d))
        self.wait(1)

        # Step 10: Final collage and conclusion
        collage = VGroup(axes.copy(), title.copy(), grid.copy(), light_cone.copy(), metric.copy(), qed.copy())
        summary = Text(r"QED: Unifying Light and Matter Through Gauge Theory", font_size=32, color=WHITE)
        self.play(FadeIn(collage), FadeIn(summary))
        self.wait(2)
        finis = Text(r"Finis", font_size=48, color=WHITE)
        self.play(Transform(summary, finis))
        self.wait(2)
        self.play(FadeOut(VGroup(collage, finis, axes2d)))
        self.play(FadeIn(dots))
        self.wait(2)

if __name__ == '__main__':
    scene = QuantumFieldTheoryAnimation()
    scene.render()
