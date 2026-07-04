# Run with: manim -pql examples/cup_trick.py CupTrick
# High quality: manim -pqh examples/cup_trick.py CupTrick

from manim import *


class CupTrick(ThreeDScene):
    """The cup-of-water trick: physical demonstration of pi_1(SO(3)) = Z/2Z.

    Hold a cup of water palm-up. Rotate 360 degrees going under your arm —
    your arm twists but the water stays level. Continue another 360 degrees
    going over your head — your arm untwists. 720 degrees total, water
    never spilled.

    This scene maps the cup trick onto the belt trick topology:
        cup  (inner cylinder) = your hand
        ribbons               = your arm
        outer frame            = your shoulder / body
    """

    def construct(self):
        R_IN = 0.6
        R_OUT = 2.5
        CUP_R = 0.35
        CUP_H = 0.5

        theta = ValueTracker(0)
        untwist = ValueTracker(0)

        self.set_camera_orientation(phi=65 * DEGREES, theta=-50 * DEGREES)

        # ── Cup (replaces the sphere from BeltTrick3D) ──
        cup_wall = Cylinder(
            radius=CUP_R,
            height=CUP_H,
            direction=OUT,
            color=GOLD_C,
            resolution=(24, 1),
        )
        cup_wall.set_opacity(0.85)

        # Water surface — a filled circle in the xy-plane near the cup top
        water = Circle(
            radius=CUP_R * 0.85,
            color=BLUE_D,
            fill_opacity=0.7,
            stroke_width=0,
        )
        water.shift(OUT * CUP_H * 0.35)

        # Cup rim highlight
        rim = Circle(radius=CUP_R, color=GOLD_A, stroke_width=3)
        rim.shift(OUT * CUP_H / 2)

        # Rotation marker — red dot on the rim so you can see the cup spin
        marker = Dot3D(
            point=np.array([CUP_R * 0.7, 0, CUP_H / 2]),
            color=RED,
            radius=0.06,
        )

        cup_group = VGroup(cup_wall, water, rim, marker)
        last_angle = [0.0]

        def rotate_cup(mob):
            a = theta.get_value()
            da = a - last_angle[0]
            if abs(da) > 1e-8:
                mob.rotate(da, axis=OUT, about_point=ORIGIN)
                last_angle[0] = a

        cup_group.add_updater(rotate_cup)

        # ── Outer frame (your shoulder / body — fixed) ──
        frame_ring = Circle(
            radius=R_OUT,
            color=GREY,
            stroke_width=1.5,
            stroke_opacity=0.3,
        )

        # ── Ribbons (your arm connecting shoulder to hand) ──
        ribbon_angles = [i * TAU / 4 for i in range(4)]
        ribbon_colors = [RED_C, BLUE_C, GREEN_C, GOLD_C]

        def ribbon_pt(phi0, t, th, s):
            """Point on a ribbon at parameter t in [0, 1].

            During rotation (s ~ 0): twist distributed linearly along ribbon.
            During untwist (s > 0, th fixed at 4pi): three-phase pass-over —

              Phase 1 (s < 0.25): Ribbons arch up/down. Twist unchanged.
                → Clearly NOT rotation: nothing unwinds, ribbons just lift.
              Phase 2 (0.25 < s < 0.75): While arched, twist releases.
                → The pass-over: ribbons slide to the untwisted config
                  while dramatically displaced in 3D.
              Phase 3 (s > 0.75): Ribbons settle back to the plane.
                → Already straight. Clean landing.
            """
            if s < 1e-3:
                phi = phi0 + th * (1 - t)
                r = R_IN + t * (R_OUT - R_IN)
                return np.array([r * np.cos(phi), r * np.sin(phi), 0])

            if s > 1 - 1e-3:
                phi = phi0
                r = R_IN + t * (R_OUT - R_IN)
                return np.array([r * np.cos(phi), r * np.sin(phi), 0])

            def sstep(x):
                x = float(np.clip(x, 0.0, 1.0))
                return x * x * (3 - 2 * x)

            # ── Arch envelope: 0 → 1 (rise), 1 → 1 (hold), 1 → 0 (fall) ──
            if s < 0.25:
                arch = sstep(s / 0.25)
            elif s < 0.75:
                arch = 1.0
            else:
                arch = sstep((1 - s) / 0.25)

            # ── Twist factor: 1 (hold), 1 → 0 (release), 0 (done) ──
            if s < 0.2:
                twist_factor = 1.0
            elif s < 0.8:
                twist_factor = 1 - sstep((s - 0.2) / 0.6)
            else:
                twist_factor = 0.0

            phi = phi0 + th * twist_factor * (1 - t)

            profile = np.sin(PI * t)  # peaks at middle of ribbon

            # Radial bulge — push outward while arched
            r = R_IN + t * (R_OUT - R_IN) + 2.5 * arch * profile

            # Vertical arch — tall enough to clearly pass over/under the cup
            z_sign = 1.0 if phi0 < PI else -1.0
            z_off = 3.5 * arch * profile * z_sign

            return np.array([r * np.cos(phi), r * np.sin(phi), z_off])

        def make_ribbon(phi0, col):
            n_pts = 150
            ts = np.linspace(0, 1, n_pts)
            ribbon = VMobject(color=col, stroke_width=5)
            pts = [ribbon_pt(phi0, t, 0, 0) for t in ts]
            ribbon.set_points_as_corners(pts)

            def update(mob, _ph=phi0, _ts=ts):
                th = theta.get_value()
                s = untwist.get_value()
                new_pts = [ribbon_pt(_ph, t, th, s) for t in _ts]
                mob.set_points_as_corners(new_pts)

            ribbon.add_updater(update)
            return ribbon

        ribbons = VGroup(
            *[make_ribbon(a, c) for a, c in zip(ribbon_angles, ribbon_colors)]
        )

        # Anchor dots on outer frame
        anchors = VGroup(
            *[
                Dot3D(
                    R_OUT * np.array([np.cos(a), np.sin(a), 0]),
                    color=c,
                    radius=0.05,
                )
                for a, c in zip(ribbon_angles, ribbon_colors)
            ]
        )

        # ── HUD: angle readout ──
        hud = always_redraw(
            lambda: MathTex(
                rf"\theta = {int(round(np.degrees(theta.get_value())))}°",
                font_size=32,
            ).to_corner(DL, buff=0.4)
        )

        # ══════════════════════════════════════════
        #  Title
        # ══════════════════════════════════════════
        title = Text("The Cup Trick", font_size=48, color=BLUE)
        sub = Text(
            "Hold a cup palm-up. Rotate 720°. Don't spill.",
            font_size=22,
            color=GREY_B,
        )
        tg = VGroup(title, sub).arrange(DOWN, buff=0.3)

        self.add_fixed_in_frame_mobjects(tg)
        self.play(Write(title), FadeIn(sub))
        self.wait()
        self.play(tg.animate.scale(0.45).to_corner(UL, buff=0.3))

        # ── Build the apparatus ──
        self.play(
            Create(frame_ring),
            FadeIn(cup_group),
            *[Create(r) for r in ribbons],
            *[GrowFromCenter(d) for d in anchors],
            run_time=2,
        )
        self.add_fixed_in_frame_mobjects(hud)
        self.wait(0.3)

        # Analogy labels
        analogy = VGroup(
            Text("ribbons = your arm", font_size=18, color=RED_C),
            Text("cup = your hand", font_size=18, color=GOLD_C),
            Text("frame = your shoulder", font_size=18, color=GREY_B),
        ).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        analogy.to_corner(DR, buff=0.4)
        self.add_fixed_in_frame_mobjects(analogy)
        self.play(FadeIn(analogy))
        self.wait(1)

        self.begin_ambient_camera_rotation(rate=0.06)

        # ══════════════════════════════════════════
        #  Phase 1: 0° → 360° — "going under your arm"
        # ══════════════════════════════════════════
        lbl1 = Text(
            "360° — going under your arm",
            font_size=24,
            color=YELLOW,
        )
        lbl1.to_edge(UP, buff=0.25)
        self.add_fixed_in_frame_mobjects(lbl1)
        self.play(FadeIn(lbl1))

        self.play(theta.animate.set_value(TAU), run_time=6, rate_func=linear)

        twist_note = VGroup(
            MathTex(r"\psi \;\to\; -\psi", font_size=36, color=RED),
            Text("Arm twisted — can't undo!", font_size=20, color=RED_B),
        ).arrange(DOWN, buff=0.2)
        twist_note.to_edge(RIGHT, buff=0.6)
        self.add_fixed_in_frame_mobjects(twist_note)
        self.play(FadeIn(twist_note))
        self.wait(2)
        self.play(FadeOut(twist_note), FadeOut(lbl1))
        self.remove_fixed_in_frame_mobjects(twist_note, lbl1)

        # ══════════════════════════════════════════
        #  Phase 2: 360° → 720° — "going over your head"
        # ══════════════════════════════════════════
        lbl2 = Text(
            "720° — continue over your head",
            font_size=24,
            color=YELLOW,
        )
        lbl2.to_edge(UP, buff=0.25)
        self.add_fixed_in_frame_mobjects(lbl2)
        self.play(FadeIn(lbl2))

        self.play(
            theta.animate.set_value(2 * TAU), run_time=6, rate_func=linear
        )

        pos_note = MathTex(r"\psi \;\to\; +\psi", font_size=36, color=GREEN)
        pos_note.to_edge(RIGHT, buff=0.8)
        self.add_fixed_in_frame_mobjects(pos_note)
        self.play(Write(pos_note))
        self.wait(1)

        # ══════════════════════════════════════════
        #  Phase 3: Untwist without rotating back
        # ══════════════════════════════════════════

        # Stop camera rotation and settle to a clear angle so the
        # viewer can see: the cup is NOT rotating, only the ribbons deform.
        self.stop_ambient_camera_rotation()
        self.move_camera(phi=60 * DEGREES, theta=-35 * DEGREES, run_time=1)

        ut_label = Text(
            "Cup frozen at 720° — only ribbons move",
            font_size=22,
            color=TEAL,
        )
        ut_label.next_to(pos_note, DOWN, buff=0.3)
        self.add_fixed_in_frame_mobjects(ut_label)
        self.play(FadeIn(ut_label))

        # Three-phase untwist: arch up → release twist → settle down
        # Slow and smooth so each phase is visible
        self.play(
            untwist.animate.set_value(1), run_time=10, rate_func=smooth
        )

        done = Text("Water never spilled!", font_size=26, color=GREEN)
        done.to_edge(DOWN, buff=0.5)
        self.add_fixed_in_frame_mobjects(done)
        self.play(FadeIn(done))
        self.wait(2)

        # ══════════════════════════════════════════
        #  Summary
        # ══════════════════════════════════════════
        self.play(*[FadeOut(m) for m in self.mobjects])
        for m in [hud, lbl2, pos_note, ut_label, done, tg, analogy]:
            try:
                self.remove_fixed_in_frame_mobjects(m)
            except Exception:
                pass

        summary = VGroup(
            Text("The cup trick = the belt trick = spinors", font_size=28),
            MathTex(
                r"360°: \;\text{twisted (cup fine, arm not)}",
                font_size=34,
                color=RED,
            ),
            MathTex(
                r"720°: \;\text{arm untwists smoothly}",
                font_size=34,
                color=GREEN,
            ),
            MathTex(
                r"\pi_1\!\left(\mathrm{SO}(3)\right)"
                r"= \mathbb{Z}/2\mathbb{Z}",
                font_size=40,
                color=BLUE,
            ),
            Text(
                "Your arm lives in SO(3). The twist lives in SU(2).",
                font_size=24,
                color=GREY_B,
            ),
        ).arrange(DOWN, buff=0.5)

        self.add_fixed_in_frame_mobjects(summary)
        for line in summary:
            anim = Write(line) if isinstance(line, MathTex) else FadeIn(line)
            self.play(anim)
            self.wait(0.4)
        self.wait(2)
