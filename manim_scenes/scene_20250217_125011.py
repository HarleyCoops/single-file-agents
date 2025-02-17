from manim import *

class MyScene(Scene):
    def construct(self):
        lagrangian = MathTex(
            r"\begin{aligned}",
            r"\mathcal{L}_{\text{QED}} &= \bar{\psi}\,(i\gamma^\mu D_\mu - m)\psi \\",
            r"&\quad - \frac{1}{4}F_{\mu\nu}F^{\mu\nu}",
            r"\end{aligned}",
            tex_environment="aligned",
            tex_to_color_map={
                r"D_\mu": TEAL,
                r"F_{\mu\nu}": TEAL
            }
        )
        self.play(Write(lagrangian))
        self.wait(2)

if __name__ == '__main__':
    scene = MyScene()
    scene.render()
