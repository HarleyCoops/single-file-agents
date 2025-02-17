from manim import *

class QEDLagrangianScene(Scene):
    def construct(self):
        qed_lagrangian = MathTex(
            r"\begin{aligned}"
            r"\mathcal{L} &= -\frac{1}{4} F_{\mu\nu}F^{\mu\nu} \\"
            r"&\quad + \bar{\psi}(i\gamma^\mu D_\mu - m)\psi"
            r"\end{aligned}",
            tex_to_color_map={
                r"\mathcal{L}": YELLOW,
                r"F_{\mu\nu}": TEAL,
                r"F^{\mu\nu}": TEAL,
                r"\bar{\psi}": RED,
                r"\gamma^\mu": BLUE,
                r"D_\mu": GREEN,
            }
        )
        self.play(Write(qed_lagrangian))
        self.wait(2)

if __name__ == '__main__':
    scene = QEDLagrangianScene()
    scene.render()
