from manim import *

class QEDAnimation(MovingCameraScene):
    def construct(self):
        eq1 = MathTex(r"E=mc^2")
        aligned_eq = MathTex(r"\begin{aligned} ax + b &= c \\ d x - e &= f \end{aligned}")
        matrix = MathTex(r"\begin{bmatrix} 1 & 0 \\ 0 & 1 \end{bmatrix}")
        eq1.to_edge(UP)
        self.play(FadeIn(eq1))
        self.wait(1)
        aligned_eq.next_to(eq1, DOWN, buff=1)
        self.play(Write(aligned_eq))
        self.wait(1)
        matrix.next_to(aligned_eq, DOWN, buff=1)
        self.play(Write(matrix))
        self.wait(1)
        self.play(eq1.animate.shift(LEFT * 2),
                  aligned_eq.animate.shift(LEFT * 2),
                  matrix.animate.shift(LEFT * 2))
        self.wait(1)
        self.play(self.camera.frame.animate.scale(0.5).move_to(matrix))
        self.wait(1)
        self.play(self.camera.frame.animate.move_to(aligned_eq))
        self.wait(1)
        self.play(self.camera.frame.animate.move_to(eq1))
        self.wait(1)
        self.play(FadeOut(eq1), FadeOut(aligned_eq), FadeOut(matrix))
        self.wait(1)