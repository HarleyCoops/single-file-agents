from manim import *

class QuantumMeasurementScene(Scene):
    def construct(self):
        # Display initial quantum state
        wavefunction = MathTex(r"\Psi = \frac{1}{\sqrt{2}}\left(|0\rangle + |1\rangle\right)")
        wavefunction.to_edge(UP)
        sphere = Sphere(radius=0.75, resolution=(16, 32)).shift(LEFT * 3)
        self.play(Create(wavefunction), Create(sphere))
        
        # Show branch states
        state0 = MathTex(r"|0\rangle")
        state1 = MathTex(r"|1\rangle")
        state0.next_to(sphere, RIGHT, buff=1)
        state1.next_to(state0, RIGHT, buff=1)
        arrow0 = Arrow(sphere.get_right(), state0.get_left(), buff=0.1, color=GREEN)
        arrow1 = Arrow(sphere.get_right(), state1.get_left(), buff=0.1, color=RED)
        self.play(Create(state0), Create(state1), Create(arrow0), Create(arrow1))
        self.wait(1)
        
        # Simulate measurement
        meas_box = Rectangle(width=2, height=2, color=YELLOW)
        meas_box.move_to(sphere.get_center() + UP * 0.5)
        self.play(Create(meas_box), run_time=1)
        self.wait(0.5)
        
        # Collapse: change sphere color, remove one branch
        self.play(sphere.animate.set_color(RED), FadeOut(state1), FadeOut(arrow1))
        self.play(meas_box.animate.shift(UP * 3), run_time=1)
        self.play(Indicate(state0))
        self.play(Wiggle(sphere), run_time=1)
        self.wait(0.5)
        
        # Create an observer eye using basic shapes
        eye_outline = Ellipse(width=2, height=1, color=WHITE)
        pupil = Circle(radius=0.3, color=BLACK, fill_color=BLACK, fill_opacity=1)
        pupil.move_to(eye_outline.get_center())
        eye = VGroup(eye_outline, pupil)
        eye.to_edge(DOWN, buff=1)
        self.play(Create(eye))
        self.wait(0.5)
        
        # Decoherence visualization with ripples
        ripple1 = Circle(radius=0.9, color=BLUE, stroke_width=2)
        ripple2 = Circle(radius=1.2, color=BLUE, stroke_width=2)
        ripple1.move_to(sphere.get_center())
        ripple2.move_to(sphere.get_center())
        self.play(Create(ripple1), run_time=1)
        self.play(Create(ripple2), run_time=1)
        self.wait(0.5)
        
        # Concluding text
        final_text = Text("Measurement Complete")
        final_text.to_edge(DOWN)
        self.play(Write(final_text))
        self.wait(2)
