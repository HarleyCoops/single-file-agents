from manim import *
import numpy as np

class PhotonSurfaceScene(Scene):
    def construct(self):
        surface = Surface(
            lambda u, v: np.array([
                np.sin(u) * np.cos(v),
                np.sin(u) * np.sin(v),
                np.cos(u)
            ]),
            u_range=[0, PI],
            v_range=[0, 2 * PI],
            resolution=(30, 60)
        )
        surface.set_style(
            fill_color=BLUE,
            fill_opacity=0.6,
            stroke_color=WHITE,
            stroke_width=0.5
        )
        photon_label = Tex(r"Photon: $\gamma$")
        photon_label.to_edge(UP)
        self.play(Create(surface))
        self.play(Write(photon_label))
        self.wait(1)
        self.play(Rotate(surface, angle=PI / 2, axis=RIGHT, run_time=3))
        self.wait(1)