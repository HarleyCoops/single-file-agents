from manim import *

class MyScene(Scene):
    def construct(self):
        equation = MathTex(
            r"\mathcal{L}_{\mathrm{QED}}",
            "=",
            r"\bar{\psi}",
            "(",
            r"i\gamma^\mu",
            r"D_\mu",
            "-",
            "m",
            ")",
            r"\psi",
            "-",
            r"\frac{1}{4}",
            r"F_{\mu\nu}",
            r"F^{\mu\nu}"
        )
        equation.set_color_by_tex(r"D_\mu", RED)
        equation.set_color_by_tex(r"F_{\mu\nu}", BLUE)
        equation.set_color_by_tex(r"F^{\mu\nu}", BLUE)
        equation.set_color_by_tex("psi", GREEN)
        equation.move_to(ORIGIN)
        self.play(Write(equation), run_time=3)
        self.wait(2)

if __name__ == '__main__':
    scene = MyScene()
    scene.render()
