from manim import *

class QuantumMeasurement(Scene):
    def construct(self):
        # Setup wavefunction elements
        psi = MathTex(r"|\psi\rangle = \alpha|0\rangle + \beta|1\rangle").scale(0.9)
        sphere = Sphere(resolution=(24,24)).scale(1.2).set_color(BLUE_E)
        quantum_state = VGroup(psi, sphere).arrange(DOWN, buff=1)
        
        # Animate initial state
        self.play(
            Write(psi),
            Create(sphere),
            run_time=2
        )
        self.wait()
        
        # Show superposition
        up_arrow = Arrow(ORIGIN, UP, color=GREEN).next_to(sphere, UP)
        down_arrow = Arrow(ORIGIN, DOWN, color=RED).next_to(sphere, DOWN)
        superposition_text = Text("Superposition State", color=YELLOW).next_to(sphere, DOWN)
        
        self.play(
            GrowArrow(up_arrow),
            GrowArrow(down_arrow),
            Write(superposition_text),
        )
        self.wait(2)
        
        # Measurement animation
        measurement_box = Rectangle(height=2, width=4, color=WHITE)
        measure_text = Text("MEASURE", color=RED).scale(1.2)
        measurement = VGroup(measurement_box, measure_text)
        
        # Collapse animation
        def update_sphere(mob, alpha):
            mob.become(Sphere(resolution=(24,24)).scale(1.2 * (1 + 0.5 * alpha)))
            mob.set_color(interpolate_color(BLUE_E, WHITE, alpha))
            
        self.play(
            measurement.animate.shift(UP*2),
            UpdateFromAlphaFunc(sphere, update_sphere),
            run_time=3
        )
        
        # Final states
        collapsed_state = MathTex(r"|0\rangle").scale(1.5).set_color(GREEN)
        self.play(
            ReplacementTransform(sphere, collapsed_state),
            FadeOut(up_arrow),
            FadeOut(down_arrow),
            FadeOut(superposition_text)
        )
        self.wait()
        
        # Observer effect visualization
        eye = SVGMobject("eye.svg").scale(0.5).set_color(WHITE)
        observation_lines = VGroup(*[
            Line(eye.get_center(), collapsed_state.get_center(), color=WHITE, stroke_width=2)
            for _ in range(8)
        ])
        
        self.play(
            FadeIn(eye.next_to(collapsed_state, RIGHT*2)),
            Create(observation_lines),
            run_time=2
        )
        self.wait(2)
        
        # Decoherence metaphor
        ripples = VGroup()
        for i in range(1,6):
            circle = Circle(radius=i*0.3, color=BLUE_E, stroke_width=3).set_opacity(1/(i))
            ripples.add(circle)
        
        self.play(
            LaggedStart(*[Create(r) for r in ripples], lag_ratio=0.2),
            Wiggle(collapsed_state),
            run_time=3
        )
        self.wait(2)
        
        # Final text
        conclusion = Text("Measurement collapses\n the quantum state!", color=YELLOW)
        self.play(Write(conclusion))
        self.wait(3)
