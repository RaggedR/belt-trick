from manim import *


class BeltTrick(Scene):
    """The Dirac belt trick: a 360° rotation leaves ribbons twisted (topologically
    non-trivial), but a 720° rotation can be smoothly untwisted back to straight.

    The untwisting uses a wave homotopy: the twist slides outward along each
    ribbon and exits at the frame, rather than uniformly unwinding (which would
    look like reverse rotation).
    """

    def construct(self):
        R_IN = 0.7
        R_OUT = 2.5

        theta = ValueTracker(0)
        untwist = ValueTracker(0)

        # ── Belt geometry ──
        belt_angles = [0, PI / 2, PI, 3 * PI / 2]
        belt_colors = [RED_C, BLUE_C, GREEN_C, GOLD_C]

        def belt_point(phi, t, theta_val, s):
            """Compute a point on a belt at parameter t ∈ [0,1].

            During rotation (s=0): angle interpolates linearly from
            phi+theta at the disk to phi at the frame.

            During untwisting (s>0, theta fixed at 4π): the twist
            slides outward as a wave. The region [0, s] is already
            straight; the region [s, 1] carries the full compressed
            twist. As s→1 the twist compresses against the frame
            and vanishes.
            """
            if s < 0.001:
                # Normal rotation
                angle = phi + theta_val * (1 - t)
                r = R_IN + t * (R_OUT - R_IN)
            elif s > 0.999:
                # Fully untwisted
                angle = phi
                r = R_IN + t * (R_OUT - R_IN)
            else:
                # Wave homotopy: inner [0, s] straight, outer [s, 1] twisted
                if t <= s:
                    angle = phi
                else:
                    tc = (t - s) / (1 - s)
                    angle = phi + theta_val * (1 - tc)

                # Radial bulge — ribbons push outward during transition,
                # selling the visual of "passing around" the disk
                bulge = 2.0 * s * (1 - s) * np.sin(PI * t)
                r = R_IN + t * (R_OUT - R_IN) + bulge

            return np.array([r * np.cos(angle), r * np.sin(angle), 0])

        def make_belt(phi, color):
            return always_redraw(lambda _phi=phi, _col=color: ParametricFunction(
                lambda t: belt_point(
                    _phi, t, theta.get_value(), untwist.get_value(),
                ),
                t_range=[0, 1, 0.005],
                color=_col,
                stroke_width=5,
            ))

        belts = VGroup(*[make_belt(a, c) for a, c in zip(belt_angles, belt_colors)])

        # ── Central disk with arrow marker ──
        disk = Circle(
            radius=R_IN, fill_opacity=0.9,
            fill_color="#1a1a2e", color=WHITE, stroke_width=2,
        )
        ref_arrow = always_redraw(lambda: Line(
            ORIGIN,
            R_IN * 0.7 * np.array([
                np.sin(theta.get_value()),
                np.cos(theta.get_value()), 0,
            ]),
            color=WHITE, stroke_width=3,
        ))
        ref_tip = always_redraw(lambda: Dot(
            R_IN * 0.7 * np.array([
                np.sin(theta.get_value()),
                np.cos(theta.get_value()), 0,
            ]),
            color=WHITE, radius=0.05,
        ))

        # ── Outer frame and anchor dots ──
        frame = Circle(radius=R_OUT, color=GREY, stroke_opacity=0.3, stroke_width=2)
        anchors = VGroup(*[
            Dot(
                R_OUT * np.array([np.cos(a), np.sin(a), 0]),
                color=c, radius=0.08,
            )
            for a, c in zip(belt_angles, belt_colors)
        ])

        # ── HUD ──
        angle_hud = always_redraw(lambda: MathTex(
            rf"\theta = {int(round(np.degrees(theta.get_value())))}°",
            font_size=32, color=WHITE,
        ).to_corner(DL, buff=0.4))

        # ══════════════════════════════════════════
        #  Title
        # ══════════════════════════════════════════
        title = Text("The Belt Trick", font_size=50, color=BLUE)
        subtitle = Text("Why spinors need 720°", font_size=26, color=GREY_B)
        VGroup(title, subtitle).arrange(DOWN, buff=0.3)
        self.play(Write(title), FadeIn(subtitle, shift=UP))
        self.wait()
        self.play(
            title.animate.scale(0.45).to_corner(UL, buff=0.3),
            FadeOut(subtitle),
        )

        # ── Build apparatus ──
        self.play(
            Create(frame), Create(disk),
            *[Create(b) for b in belts],
            *[GrowFromCenter(d) for d in anchors],
            FadeIn(ref_arrow), FadeIn(ref_tip),
        )
        self.add(angle_hud)
        self.wait(0.5)

        # ══════════════════════════════════════════
        #  Phase 1: 0° → 360°
        # ══════════════════════════════════════════
        phase1 = Text("First full rotation", font_size=26, color=YELLOW)
        phase1.to_edge(UP, buff=0.2)
        self.play(FadeIn(phase1))
        self.play(theta.animate.set_value(2 * PI), run_time=5, rate_func=linear)

        twist_label = Text("Ribbons twisted!", font_size=24, color=RED)
        twist_label.to_edge(RIGHT, buff=0.5)
        phase_neg = MathTex(r"\psi \;\to\; -\psi", font_size=36, color=RED)
        phase_neg.next_to(twist_label, DOWN, buff=0.3)
        self.play(FadeIn(twist_label), Write(phase_neg))
        self.wait(2)
        self.play(FadeOut(twist_label), FadeOut(phase_neg), FadeOut(phase1))

        # ══════════════════════════════════════════
        #  Phase 2: 360° → 720°
        # ══════════════════════════════════════════
        phase2 = Text("Second full rotation", font_size=26, color=YELLOW)
        phase2.to_edge(UP, buff=0.2)
        self.play(FadeIn(phase2))
        self.play(theta.animate.set_value(4 * PI), run_time=5, rate_func=linear)

        phase_pos = MathTex(r"\psi \;\to\; +\psi", font_size=36, color=GREEN)
        phase_pos.to_edge(RIGHT, buff=0.5)
        self.play(Write(phase_pos))
        self.wait(1)

        # ══════════════════════════════════════════
        #  Phase 3: Wave untwist
        # ══════════════════════════════════════════
        untwist_label = Text(
            "Untwist — without rotating back!",
            font_size=24, color=TEAL,
        )
        untwist_label.next_to(phase_pos, DOWN, buff=0.4)
        self.play(FadeIn(untwist_label))
        self.wait(0.5)

        self.play(
            untwist.animate.set_value(1),
            run_time=5,
            rate_func=linear,
        )

        done_label = Text("Straight again!", font_size=28, color=GREEN)
        done_label.to_edge(RIGHT, buff=0.5).shift(DOWN)
        self.play(FadeIn(done_label))
        self.wait(2)

        # ══════════════════════════════════════════
        #  Summary
        # ══════════════════════════════════════════
        self.play(*[FadeOut(m) for m in self.mobjects])

        summary = VGroup(
            Text("The belt trick demonstrates:", font_size=30, color=WHITE),
            MathTex(
                r"360°: \;\text{twisted (cannot undo)}",
                font_size=36, color=RED,
            ),
            MathTex(
                r"720°: \;\text{untwists smoothly}",
                font_size=36, color=GREEN,
            ),
            MathTex(
                r"\pi_1\!\left(\mathrm{SO}(3)\right) = \mathbb{Z}/2\mathbb{Z}",
                font_size=44, color=BLUE,
            ),
            Text(
                "Spinors live in the double cover SU(2)",
                font_size=26, color=GREY_B,
            ),
        ).arrange(DOWN, buff=0.5)

        for line in summary:
            self.play(Write(line) if isinstance(line, MathTex) else FadeIn(line))
            self.wait(0.4)

        self.wait(2)
