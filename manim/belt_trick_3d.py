from manim import *


class BeltTrick3D(ThreeDScene):
    """3D belt trick: a sphere connected to an outer cage by ribbons.

    360° rotation leaves the ribbons twisted (topologically non-trivial).
    720° rotation allows a smooth untwist without rotating back — the
    ribbons loop around the sphere and straighten.

    This is the defining property of spinors:
        π₁(SO(3)) = Z/2Z,  covered by SU(2).

    Inspired by Jason Hise's animations.
    """

    def construct(self):
        R_IN = 0.7
        R_OUT = 2.8

        theta = ValueTracker(0)
        untwist = ValueTracker(0)

        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)

        # ── Inner sphere ──
        inner = Sphere(radius=R_IN, resolution=(24, 12))
        inner.set_color(BLUE_D).set_opacity(0.8)

        # Marker dot on the sphere surface to track orientation
        marker = Dot3D(R_IN * UP, color=WHITE, radius=0.08)

        inner_group = VGroup(inner, marker)
        last_angle = [0.0]

        def rotate_inner(mob):
            a = theta.get_value()
            da = a - last_angle[0]
            if abs(da) > 1e-8:
                mob.rotate(da, axis=OUT, about_point=ORIGIN)
                last_angle[0] = a

        inner_group.add_updater(rotate_inner)

        # ── Outer cage: three great circles ──
        cage_rings = VGroup(
            Circle(radius=R_OUT, color=GREY, stroke_width=1, stroke_opacity=0.25),
            Circle(
                radius=R_OUT, color=GREY, stroke_width=1, stroke_opacity=0.25,
            ).rotate(PI / 2, axis=RIGHT),
            Circle(
                radius=R_OUT, color=GREY, stroke_width=1, stroke_opacity=0.25,
            ).rotate(PI / 2, axis=UP),
        )

        # ── Belt configuration ──
        # Each belt is (latitude, longitude, color).
        # Three rings of 4 belts at different latitudes, offset in longitude.
        specs = []

        eq_colors = [RED_C, BLUE_C, GREEN_C, GOLD_C]
        for i in range(4):
            specs.append((0, i * TAU / 4, eq_colors[i]))

        up_colors = [PURPLE_C, TEAL_C, ORANGE, PINK]
        for i in range(4):
            specs.append((0.65, i * TAU / 4 + PI / 4, up_colors[i]))

        lo_colors = [MAROON_C, YELLOW_C, RED_B, GREEN_B]
        for i in range(4):
            specs.append((-0.65, i * TAU / 4 + PI / 8, lo_colors[i]))

        # ── Belt geometry ──
        def belt_pt(lat, phi0, t, th, s):
            """Position of a belt point at parameter t ∈ [0, 1].

            During rotation (s ≈ 0): twist is distributed linearly
            along the belt — full rotation at the inner sphere, none
            at the outer cage.

            During untwist (s > 0, th fixed at 4π): the twist angle
            decreases globally while belts arch over/under the sphere.
            This vertical displacement is the topological escape route:
            π₁(SO(3)) = Z/2Z means 4π (but not 2π) is contractible,
            and the contraction requires passing through 3D.
            """
            cl, sl = np.cos(lat), np.sin(lat)

            if s < 1e-3:
                # Pure rotation — twist distributed linearly along belt
                phi = phi0 + th * (1 - t)
                r = R_IN + t * (R_OUT - R_IN)
                return np.array([r * cl * np.cos(phi), r * cl * np.sin(phi), r * sl])

            if s > 1 - 1e-3:
                # Fully untwisted — straight radial belts
                phi = phi0
                r = R_IN + t * (R_OUT - R_IN)
                return np.array([r * cl * np.cos(phi), r * cl * np.sin(phi), r * sl])

            # ── Wave homotopy ──
            # [0, s] is straight; [s, 1] carries the compressed twist.
            # Both endpoints stay pinned at phi0 (no spurious rotation).
            if t <= s:
                phi = phi0
            else:
                tc = (t - s) / (1 - s)
                phi = phi0 + th * (1 - tc)

            profile = np.sin(PI * t)
            envelope = np.sin(PI * s)

            # Radial push — belts bulge outward to clear the sphere
            r = R_IN + t * (R_OUT - R_IN) + 2.2 * envelope * profile

            # Vertical arch — belts pass OVER/UNDER the sphere
            if abs(lat) > 0.1:
                z_sign = np.sign(lat)
            else:
                z_sign = 1.0 if np.sin(phi0) > 0 else -1.0
            z_off = 2.0 * envelope * profile * z_sign

            return np.array([r * cl * np.cos(phi), r * cl * np.sin(phi), r * sl + z_off])

        def make_belt(lat, phi0, col):
            n_pts = 200
            ts = np.linspace(0, 1, n_pts)
            belt = VMobject(color=col, stroke_width=4)
            pts = [belt_pt(lat, phi0, t, 0, 0) for t in ts]
            belt.set_points_as_corners(pts)

            def update(mob, _la=lat, _ph=phi0, _ts=ts):
                th = theta.get_value()
                s = untwist.get_value()
                new_pts = [belt_pt(_la, _ph, t, th, s) for t in _ts]
                mob.set_points_as_corners(new_pts)

            belt.add_updater(update)
            return belt

        belts = VGroup(*[make_belt(*s) for s in specs])

        # Anchor dots on outer cage
        anchor_dots = VGroup(*[
            Dot3D(
                R_OUT * np.array([
                    np.cos(la) * np.cos(ph),
                    np.cos(la) * np.sin(ph),
                    np.sin(la),
                ]),
                color=c,
                radius=0.05,
            )
            for la, ph, c in specs
        ])

        # ── HUD ──
        hud = always_redraw(
            lambda: MathTex(
                rf"\theta = {int(round(np.degrees(theta.get_value())))}°",
                font_size=32,
            ).to_corner(DL, buff=0.4)
        )

        # ═══════════════════════════════════════════
        #  Title
        # ═══════════════════════════════════════════
        title = Text("The Belt Trick", font_size=48, color=BLUE)
        sub = Text("Why spinors need 720°", font_size=24, color=GREY_B)
        tg = VGroup(title, sub).arrange(DOWN, buff=0.3)

        self.add_fixed_in_frame_mobjects(tg)
        self.play(Write(title), FadeIn(sub))
        self.wait()
        self.play(tg.animate.scale(0.45).to_corner(UL, buff=0.3))

        # ── Build apparatus ──
        self.play(
            Create(cage_rings),
            FadeIn(inner_group),
            *[Create(b) for b in belts],
            *[GrowFromCenter(d) for d in anchor_dots],
            run_time=2,
        )
        self.add_fixed_in_frame_mobjects(hud)
        self.wait(0.5)

        # Slow camera orbit for the 3D effect
        self.begin_ambient_camera_rotation(rate=0.06)

        # ═══════════════════════════════════════════
        #  Phase 1: 0° → 360°
        # ═══════════════════════════════════════════
        lbl1 = Text("First full rotation", font_size=24, color=YELLOW)
        lbl1.to_edge(UP, buff=0.25)
        self.add_fixed_in_frame_mobjects(lbl1)
        self.play(FadeIn(lbl1))

        self.play(theta.animate.set_value(TAU), run_time=6, rate_func=linear)

        neg = MathTex(r"\psi \;\to\; -\psi", font_size=36, color=RED)
        neg.to_edge(RIGHT, buff=0.8)
        self.add_fixed_in_frame_mobjects(neg)
        self.play(Write(neg))
        self.wait(2)
        self.play(FadeOut(neg), FadeOut(lbl1))
        self.remove_fixed_in_frame_mobjects(neg, lbl1)

        # ═══════════════════════════════════════════
        #  Phase 2: 360° → 720°
        # ═══════════════════════════════════════════
        lbl2 = Text("Second full rotation", font_size=24, color=YELLOW)
        lbl2.to_edge(UP, buff=0.25)
        self.add_fixed_in_frame_mobjects(lbl2)
        self.play(FadeIn(lbl2))

        self.play(theta.animate.set_value(2 * TAU), run_time=6, rate_func=linear)

        pos = MathTex(r"\psi \;\to\; +\psi", font_size=36, color=GREEN)
        pos.to_edge(RIGHT, buff=0.8)
        self.add_fixed_in_frame_mobjects(pos)
        self.play(Write(pos))
        self.wait(1)

        # ═══════════════════════════════════════════
        #  Phase 3: Untwist without rotating back
        # ═══════════════════════════════════════════
        utl = Text("Untwist — no rotation!", font_size=22, color=TEAL)
        utl.next_to(pos, DOWN, buff=0.3)
        self.add_fixed_in_frame_mobjects(utl)
        self.play(FadeIn(utl))

        self.play(untwist.animate.set_value(1), run_time=6, rate_func=smooth)

        done = Text("Straight again!", font_size=26, color=GREEN)
        done.to_edge(DOWN, buff=0.5)
        self.add_fixed_in_frame_mobjects(done)
        self.play(FadeIn(done))
        self.wait(2)

        self.stop_ambient_camera_rotation()

        # ═══════════════════════════════════════════
        #  Summary
        # ═══════════════════════════════════════════
        self.play(*[FadeOut(m) for m in self.mobjects])
        for m in [hud, lbl2, pos, utl, done, tg]:
            try:
                self.remove_fixed_in_frame_mobjects(m)
            except Exception:
                pass

        summary = VGroup(
            Text("The belt trick demonstrates:", font_size=28),
            MathTex(
                r"360°: \;\text{twisted (cannot undo)}",
                font_size=34, color=RED,
            ),
            MathTex(
                r"720°: \;\text{untwists smoothly}",
                font_size=34, color=GREEN,
            ),
            MathTex(
                r"\pi_1\!\left(\mathrm{SO}(3)\right) = \mathbb{Z}/2\mathbb{Z}",
                font_size=40, color=BLUE,
            ),
        ).arrange(DOWN, buff=0.5)

        self.add_fixed_in_frame_mobjects(summary)
        for line in summary:
            self.play(Write(line) if isinstance(line, MathTex) else FadeIn(line))
            self.wait(0.4)
        self.wait(2)
