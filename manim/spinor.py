from manim import *


class Spinor(Scene):
    """Visualise the defining property of spinors: a 360° rotation picks up
    a factor of -1, and only after 720° does the state return to itself.

    Contrasts a classical vector (SO(3)) with a spinor (SU(2) double cover).
    """

    def construct(self):
        # ── Title ──
        title = Text("Spinors: the sign that won't go away", font_size=42, color=BLUE)
        self.play(Write(title))
        self.wait()
        self.play(title.animate.scale(0.5).to_corner(UL))

        # ── Set up two side-by-side circles ──
        left_center = 3 * LEFT
        right_center = 3 * RIGHT
        radius = 1.8

        vec_circle = Circle(radius=radius, color=GREY, stroke_opacity=0.3).move_to(left_center)
        spin_circle = Circle(radius=radius, color=GREY, stroke_opacity=0.3).move_to(right_center)

        vec_label = Text("Vector", font_size=28, color=GREEN).next_to(vec_circle, UP, buff=0.4)
        spin_label = Text("Spinor", font_size=28, color=YELLOW).next_to(spin_circle, UP, buff=0.4)

        self.play(
            Create(vec_circle), Create(spin_circle),
            Write(vec_label), Write(spin_label),
        )

        # ── Arrows ──
        vec_arrow = Arrow(
            left_center, left_center + radius * UP,
            color=GREEN, buff=0, stroke_width=6,
        )
        spin_arrow = Arrow(
            right_center, right_center + radius * UP,
            color=YELLOW, buff=0, stroke_width=6,
        )

        # Phase indicator for spinor: shows +1 or -1
        phase_val = MathTex(r"+1", font_size=36, color=WHITE)
        phase_val.next_to(spin_circle, DOWN, buff=0.5)
        phase_label = Text("phase", font_size=20, color=GREY_B)
        phase_label.next_to(phase_val, DOWN, buff=0.15)

        self.play(GrowArrow(vec_arrow), GrowArrow(spin_arrow), FadeIn(phase_val), FadeIn(phase_label))
        self.wait()

        # ── Angle tracker ──
        angle = ValueTracker(0)

        def update_vec(arrow):
            a = angle.get_value()
            end = left_center + radius * np.array([np.sin(a), np.cos(a), 0])
            new = Arrow(left_center, end, color=GREEN, buff=0, stroke_width=6)
            arrow.become(new)

        def update_spin(arrow):
            a = angle.get_value()
            # Spinor rotates at half the angle
            half_a = a / 2
            end = right_center + radius * np.array([np.sin(half_a), np.cos(half_a), 0])
            # Colour encodes sign: cos(a/2) > 0 → yellow, < 0 → red
            sign = np.cos(half_a)
            col = interpolate_color(RED, YELLOW, (sign + 1) / 2)
            new = Arrow(right_center, end, color=col, buff=0, stroke_width=6)
            arrow.become(new)

        vec_arrow.add_updater(update_vec)
        spin_arrow.add_updater(update_spin)

        # Angle readout
        angle_text = always_redraw(
            lambda: MathTex(
                rf"\theta = {int(np.degrees(angle.get_value()))}°",
                font_size=32, color=WHITE,
            ).to_edge(DOWN, buff=0.6)
        )
        self.add(angle_text)

        # ── First rotation: 0 → 360° ──
        section1 = Text("First rotation: 0° → 360°", font_size=28, color=TEAL)
        section1.to_edge(UP, buff=0.15).shift(2 * RIGHT)
        self.play(FadeIn(section1))

        self.play(angle.animate.set_value(TAU), run_time=5, rate_func=linear)

        # Vector is back, spinor is upside down
        vec_arrow.clear_updaters()
        spin_arrow.clear_updaters()

        result_360 = MathTex(r"-1", font_size=36, color=RED)
        result_360.move_to(phase_val)
        box_vec = SurroundingRectangle(vec_arrow, color=GREEN, buff=0.2)
        box_spin = SurroundingRectangle(spin_arrow, color=RED, buff=0.2)

        check = Text("✓ back", font_size=22, color=GREEN).next_to(box_vec, DOWN, buff=0.2)
        cross = Text("✗ flipped!", font_size=22, color=RED).next_to(box_spin, DOWN, buff=0.2)

        self.play(
            Create(box_vec), Create(box_spin),
            FadeIn(check), FadeIn(cross),
            Transform(phase_val, result_360),
        )
        self.wait(2)

        self.play(
            FadeOut(box_vec), FadeOut(box_spin),
            FadeOut(check), FadeOut(cross),
            FadeOut(section1),
        )

        # ── Second rotation: 360° → 720° ──
        section2 = Text("Second rotation: 360° → 720°", font_size=28, color=TEAL)
        section2.to_edge(UP, buff=0.15).shift(2 * RIGHT)
        self.play(FadeIn(section2))

        vec_arrow.add_updater(update_vec)
        spin_arrow.add_updater(update_spin)

        self.play(angle.animate.set_value(2 * TAU), run_time=5, rate_func=linear)

        vec_arrow.clear_updaters()
        spin_arrow.clear_updaters()

        # Now both are back
        result_720 = MathTex(r"+1", font_size=36, color=GREEN)
        result_720.move_to(phase_val)
        box_vec2 = SurroundingRectangle(vec_arrow, color=GREEN, buff=0.2)
        box_spin2 = SurroundingRectangle(spin_arrow, color=GREEN, buff=0.2)

        check2 = Text("✓ back", font_size=22, color=GREEN).next_to(box_vec2, DOWN, buff=0.2)
        check3 = Text("✓ back!", font_size=22, color=GREEN).next_to(box_spin2, DOWN, buff=0.2)

        self.play(
            Create(box_vec2), Create(box_spin2),
            FadeIn(check2), FadeIn(check3),
            Transform(phase_val, result_720),
        )
        self.wait(2)

        self.play(
            FadeOut(box_vec2), FadeOut(box_spin2),
            FadeOut(check2), FadeOut(check3),
            FadeOut(section2),
        )

        # ── Explanation ──
        self.play(
            FadeOut(vec_circle), FadeOut(spin_circle),
            FadeOut(vec_arrow), FadeOut(spin_arrow),
            FadeOut(vec_label), FadeOut(spin_label),
            FadeOut(phase_val), FadeOut(phase_label),
            FadeOut(angle_text), FadeOut(title),
        )

        explanation = VGroup(
            MathTex(r"\text{Vector: } R(2\pi) = +1", font_size=40, color=GREEN),
            MathTex(r"\text{Spinor: } R(2\pi) = -1, \quad R(4\pi) = +1", font_size=40, color=YELLOW),
            MathTex(r"\text{SU}(2) \xrightarrow{2:1} \text{SO}(3)", font_size=44, color=BLUE),
        ).arrange(DOWN, buff=0.6)

        for line in explanation:
            self.play(Write(line))
            self.wait(0.5)

        self.wait(2)
