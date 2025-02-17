from manim import *
import numpy as np

class MyScene(Scene):
    def construct(self):
        # Step 1: Create a star field as background
        stars = VGroup(*[
            Dot(point=np.array([
                np.random.uniform(-config.frame_width/2, config.frame_width/2),
                np.random.uniform(-config.frame_height/2, config.frame_height/2),
                0
            ]), radius=0.02, color=WHITE)
            for _ in range(100)
        ])
        self.play(FadeIn(stars, run_time=2))

        # Step 2: Introduce 3D axes and a glowing title
        axes3d = ThreeDAxes()
        title = Text("Quantum Field Theory: A Journey into the Electromagnetic Interaction", font_size=48, color=YELLOW).to_edge(UP)
        self.play(Create(axes3d), FadeIn(title, run_time=2))
        self.play(title.animate.scale(0.5).to_corner(UL), run_time=2)

        # Step 3: Create a rotating wireframe grid (proxy for 4D Minkowski spacetime) and a light cone
        grid = NumberPlane(x_range=[-5,5,1], y_range=[-3,3,1]).rotate(PI/4, axis=OUT)
        self.play(Create(grid))
        cone_line1 = Line(ORIGIN, RIGHT+UP, color=YELLOW)
        cone_line2 = Line(ORIGIN, LEFT+UP, color=YELLOW)
        light_cone = VGroup(cone_line1, cone_line2)
        self.play(Create(light_cone))
        self.play(Rotate(grid, angle=TAU, axis=OUT, run_time=4, rate_func=linear))

        # Step 4: Display the metric equation with color coding
        metric = MathTex(r"ds^2 = -c^2\,dt^2 + dx^2 + dy^2 + dz^2", font_size=36, 
                          tex_to_color_map={"-c^2\,dt^2": RED, "dx^2": BLUE, "dy^2": BLUE, "dz^2": BLUE})
        metric.to_edge(DOWN)
        self.play(Write(metric))
        self.wait(1)

        # Step 5: Animate plane waves representing electric and magnetic fields
        electric_wave = MathTex(r"E = E_0\cos(kx - \omega t)", font_size=30).shift(2*UP+2*LEFT)
        magnetic_wave = MathTex(r"B = B_0\cos(kx - \omega t)", font_size=30).shift(2*UP+2*RIGHT)
        self.play(Write(electric_wave), Write(magnetic_wave))
        
        # Step 6: Display Maxwell's equations and transform to relativistic form
        classical = VGroup(
            MathTex(r"\nabla \cdot \mathbf{E} = \frac{\rho}{\varepsilon_0}", font_size=28),
            MathTex(r"\nabla \times \mathbf{B} - \frac{\partial \mathbf{E}}{\partial t} = \mu_0 \mathbf{J}", font_size=28)
        ).arrange(DOWN, buff=0.3).to_edge(LEFT)
        self.play(Write(classical))
        self.wait(1)
        relativistic = MathTex(r"\partial_\mu F^{\mu\nu} = \mu_0 J^\nu", font_size=32).next_to(classical, RIGHT, buff=1)
        self.play(ReplacementTransform(classical.copy(), relativistic, run_time=2))
        self.wait(1)

        # Step 7: Show the QED Lagrangian and a gauge transformation
        lagrangian = MathTex(r"\mathcal{L}_{QED} = \bar{\psi}(i\gamma^\mu D_\mu - m)\psi - \frac{1}{4}F_{\mu\nu}F^{\mu\nu}", font_size=28, 
                             tex_to_color_map={"\psi": ORANGE, "D_\mu": GREEN, "\gamma^\mu": TURQUOISE, "F_{\mu\nu}": GOLD}).to_edge(UP)
        gauge = MathTex(r"\psi \rightarrow e^{i\alpha(x)}\psi", font_size=28).next_to(lagrangian, DOWN)
        self.play(Write(lagrangian), Write(gauge))
        self.wait(1)

        # Transition: Fade out previous elements
        self.play(FadeOut(VGroup(grid, light_cone, electric_wave, magnetic_wave, classical, metric, lagrangian, gauge, relativistic)), run_time=2)
        
        # Step 8: Present a simplified Feynman diagram on a black background
        black_bg = FullScreenRectangle(fill_color=BLACK, fill_opacity=1)
        self.play(FadeIn(black_bg, run_time=1))
        feyn_electron1 = Line(np.array([-3,1,0]), ORIGIN, color=BLUE, stroke_width=3)
        feyn_electron2 = Line(np.array([-3,-1,0]), ORIGIN, color=BLUE, stroke_width=3)
        feyn_photon = DashedLine(ORIGIN, np.array([3,0,0]), color=YELLOW, stroke_width=3)
        vertex = Dot(point=ORIGIN, radius=0.1, color=WHITE)
        feynman_diagram = VGroup(feyn_electron1, feyn_electron2, feyn_photon, vertex).shift(DOWN*2)
        electron_label1 = MathTex(r"e^-", font_size=24, color=BLUE).next_to(feyn_electron1, UP)
        electron_label2 = MathTex(r"e^-", font_size=24, color=BLUE).next_to(feyn_electron2, DOWN)
        photon_label = MathTex(r"\gamma", font_size=24, color=YELLOW).next_to(feyn_photon, UP)
        self.play(Create(feynman_diagram), Write(electron_label1), Write(electron_label2), Write(photon_label))
        self.wait(1)
        coupling_numeric = MathTex(r"g \approx 2.0", font_size=30, color=WHITE).to_edge(UP)
        self.play(Write(coupling_numeric))
        self.wait(1)
        coupling_symbolic = MathTex(r"g = \frac{e^2}{4\pi\varepsilon_0\hbar c}", font_size=30, color=WHITE).move_to(coupling_numeric)
        self.play(ReplacementTransform(coupling_numeric, coupling_symbolic))
        self.wait(1)
        self.play(FadeOut(VGroup(feynman_diagram, electron_label1, electron_label2, photon_label, coupling_symbolic)), run_time=1)
        self.play(FadeOut(black_bg), run_time=1)
        
        # Step 9: Transition to a 2D graph showing running coupling constant
        graph_axes = Axes(x_range=[0,10,2], y_range=[0,5,1], x_length=5, y_length=3).to_edge(RIGHT)
        self.play(Create(graph_axes))
        graph_line = graph_axes.plot(lambda x: 0.5*x, color=PURPLE)
        self.play(Create(graph_line))
        labels2d = graph_axes.get_axis_labels(x_label=r"Energy Scale", y_label=r"Coupling Strength")
        self.play(Write(labels2d))
        self.wait(1)

        # Step 10: Final collage and conclusion
        collage = VGroup(axes3d.copy(), title.copy(), grid.copy(), light_cone.copy(), metric.copy()).arrange_in_grid(2,3, buff=0.5).scale(0.6)
        summary = Text("QED: Unifying Light and Matter Through Gauge Theory", font_size=32, color=WHITE).to_edge(UP)
        self.play(FadeIn(collage), Write(summary))
        self.wait(2)
        finis = Text("Finis", font_size=48, color=WHITE)
        self.play(Transform(summary, finis))
        self.wait(2)
        self.play(FadeOut(VGroup(collage, finis, graph_axes, graph_line, labels2d)))
        self.play(FadeIn(stars, run_time=1))
        self.wait(2)

if __name__ == '__main__':
    scene = MyScene()
    scene.render()
