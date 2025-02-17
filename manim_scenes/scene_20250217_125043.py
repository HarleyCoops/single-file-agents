from manim import *

class QEDLagrangianScene(Scene):
    def construct(self):
        lagrangian = MathTex(
            r"\mathcal{L}_{QED}",
            r"=",
            r"\bar{\psi}\left(i\gamma^\mu D_\mu - m\right)\psi",
            r"-\frac{1}{4}F_{\mu\nu}F^{\mu\nu}",
            tex_to_color_map={
                r"\psi": YELLOW,
                r"\gamma": RED,
                r"D": BLUE,
                r"m": GREEN,
                r"F": PURPLE
            }
        )
        self.play(Write(lagrangian))
        self.wait(2)