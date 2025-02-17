from manim import *
import numpy as np
import random

class QEDAnimation(Scene):
    def construct(self):
        star_field = VGroup(*[
            Dot(point=np.array([random.uniform(-config.frame_width/2, config.frame_width/2), 
                                  random.uniform(-config.frame_height/2, config.frame_height/2), 
                                  random.uniform(-1, 1)]), radius=0.03, color=WHITE)
            for _ in range(100)
        ])
        self.play(FadeIn(star_field, lag_ratio=0.01), run_time=2)
        axes = ThreeDAxes().scale(0.8)
        self.play(FadeIn(axes), run_time=2)
        title = Text("QED", font_size=72, color=BLUE).set_gloss(1)
        self.play(FadeIn(title))
        self.play(title.animate.to_corner(UP + RIGHT), run_time=2)
        grid = Surface(
            lambda u, v: np.array([u, v, 0]),
            u_range=[-3, 3],
            v_range=[-3, 3],
            resolution=(15, 15)
        ).set_style(fill_opacity=0, stroke_color=YELLOW, stroke_width=1)
        light_cone = Cone(base_radius=1, height=3, direction=UP, fill_opacity=0, stroke_color=ORANGE)
        spacetime = VGroup(grid, light_cone).rotate(angle=PI/6, axis=RIGHT)
        self.play(ShowCreation(spacetime), run_time=3)
        metric_eq = MathTex(r"ds^2 \;=\; -c^2 dt^2 \;+\; dx^2 \;+\; dy^2 \;+\; dz^2")
        metric_eq.to_edge(UP)
        self.play(Write(metric_eq), run_time=2)
        def e_field_func(pos):
            x, y = pos[:2]
            return np.array([np.sin(x+y), np.cos(x-y), 0])
        e_field = ArrowVectorField(e_field_func, x_range=[-2,2], y_range=[-2,2], length_func=lambda norm: 0.5)
        b_field = ArrowVectorField(lambda pos: np.array([-np.cos(pos[0]), np.sin(pos[1]), 0]), x_range=[-2,2], y_range=[-2,2], length_func=lambda norm: 0.5)
        e_label = MathTex(r"\vec{E}").next_to(e_field[0], UP)
        b_label = MathTex(r"\vec{B}").next_to(b_field[0], DOWN)
        self.play(FadeIn(e_field, shift=UP), FadeIn(b_field, shift=DOWN), run_time=3)
        self.play(Write(e_label), Write(b_label), run_time=2)
        maxwell1 = MathTex(r"\nabla \cdot \vec{E} \;=\; \frac{\rho}{\varepsilon_0}").shift(UP*1.5)
        maxwell2 = MathTex(r"\nabla \cdot \vec{B} \;=\; 0").next_to(maxwell1, DOWN)
        maxwell3 = MathTex(r"\nabla \times \vec{E} \;=\; -\frac{\partial \vec{B}}{\partial t}").next_to(maxwell2, DOWN)
        maxwell4 = MathTex(r"\nabla \times \vec{B} \;=\; \mu_0 \vec{J}+\mu_0\varepsilon_0\frac{\partial \vec{E}}{\partial t}").next_to(maxwell3, DOWN)
        maxwell_group = VGroup(maxwell1, maxwell2, maxwell3, maxwell4)
        self.play(Write(maxwell_group), run_time=3)
        new_maxwell = MathTex(
            r"\nabla \cdot \vec{E} \;=\; \frac{\rho}{\varepsilon_0}", 
            r"\nabla \cdot \vec{B} \;=\; 0", 
            r"\nabla \times \vec{E} \;=\; -\frac{\partial \vec{B}}{\partial t}", 
            r"\nabla \times \vec{B} \;=\; \mu_0 \vec{J}+\mu_0\varepsilon_0\frac{\partial \vec{E}}{\partial t}"
        ).arrange(DOWN, aligned_edge=LEFT).shift(LEFT*3)
        self.play(Transform(maxwell_group.copy(), new_maxwell), run_time=3)
        plane = Square(side_length=4, fill_opacity=0.3, fill_color=BLACK).to_edge(DOWN)
        lagrangian = MathTex(r"\mathcal{L} \;=\; -\frac{1}{4} F_{\mu\nu}F^{\mu\nu} \;+\; \bar{\psi}(i\gamma^\mu D_\mu - m)\psi")
        lagrangian.move_to(plane.get_center())
        self.play(FadeIn(plane), Write(lagrangian), run_time=3)
        self.play(lagrangian.animate.scale(1.2), run_time=0.5)
        self.play(lagrangian.animate.scale(1/1.2), run_time=0.5)
        gauge_circle = Circle(radius=1.5, color=GREEN).move_to(lagrangian.get_center())
        self.play(ShowCreation(gauge_circle), run_time=2)
        self.play(Rotate(gauge_circle, angle=TAU, about_point=gauge_circle.get_center()), run_time=3)
        self.play(FadeOut(gauge_circle), run_time=1)
        feynman_diag = VGroup()
        electron1 = Arrow(LEFT*2+DOWN, LEFT*0.5+DOWN, buff=0, stroke_width=3, color=WHITE)
        electron2 = Arrow(LEFT*0.5+DOWN, RIGHT*0.5+DOWN, buff=0, stroke_width=3, color=WHITE)
        electron3 = Arrow(RIGHT*0.5+DOWN, RIGHT*2+DOWN, buff=0, stroke_width=3, color=WHITE)
        photon = CurvedArrow(LEFT*0.5+DOWN, RIGHT*0.5+DOWN+UP*1, angle=PI/3, stroke_width=3, color=YELLOW)
        diag_label = MathTex(r"\gamma", color=YELLOW).next_to(photon, UP)
        feynman_diag.add(electron1, electron2, electron3, photon, diag_label)
        self.play(FadeOut(plane, lagrangity=True), FadeOut(lagrangian, lagrangity=True),
                  FadeOut(maxwell_group, lagrangity=True), FadeOut(e_field, lagrangity=True),
                  FadeOut(b_field, lagrangity=True), FadeOut(e_label, lagrangity=True),
                  FadeOut(b_label, lagrangity=True), run_time=2)
        self.play(Transform(star_field.copy(), feynman_diag), run_time=2)
        self.play(Write(feynman_diag), run_time=3)
        coupling_numeric = MathTex(r"0.3")
        coupling_symbolic = MathTex(r"g")
        coupling_numeric.to_edge(UP)
        coupling_symbolic.to_edge(UP)
        self.play(Write(coupling_numeric), run_time=2)
        self.play(Transform(coupling_numeric, coupling_symbolic), run_time=2)
        axes_2d = Axes(x_range=[0,10,1], y_range=[0,5,1], x_length=6, y_length=4).to_edge(DOWN)
        graph = axes_2d.get_graph(lambda x: 4/(1+np.exp(-0.5*(x-5))), color=RED)
        self.play(Create(axes_2d), run_time=2)
        self.play(Create(graph), run_time=3)
        summary_title = Text("Summary of QED", font_size=48, color=PURPLE)
        summary_text = Text("Gauge Invariance, Feynman Diagrams, Running Coupling", font_size=32)
        summary_group = VGroup(summary_title, summary_text).arrange(DOWN, buff=0.5).to_edge(LEFT)
        subtitle = Text("Concluding Remarks", font_size=36, color=TEAL).to_edge(DOWN)
        self.play(FadeIn(summary_group), FadeIn(subtitle), run_time=3)
        self.wait(2)