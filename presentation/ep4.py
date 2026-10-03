"""Episode 4: the spinning disk.

Stage 3 (stages/03_disk) adds a disk of orbiting gas to the ray tracer:
where rays cross it, how fast it moves, the Doppler and redshift factor,
and an off-screen floating-point image with tone mapping.
"""
from common import *

MAIN = "stages/03_disk/main.cpp"
FRAG = "stages/03_disk/trace.frag"
TONE = "stages/03_disk/tonemap.frag"


class E4_01_Recap(Video):
    def construct(self):
        clip = Footage("stage2_stars").scale_to_fit_height(config.frame_height)
        self.play(FadeIn(clip), run_time=0.8)
        with self.voice("Welcome back! Last time, we built a ray tracer. One ray for every pixel, bent by the black "
                        "hole, running on the graphics card."):
            pass
        shade = Rectangle(width=15, height=9, stroke_width=0, fill_color=BLACK, fill_opacity=0.0)
        number = T("EPISODE 4", 26, ACCENT, weight=BOLD)
        title = T("The spinning disk", 64, weight=BOLD)
        VGroup(number, title).arrange(DOWN, buff=0.35)
        with self.voice("But a real black hole is almost never alone. Gas spirals in toward it, and on the way down,"
                        " it heats up until it glows."):
            self.play(shade.animate.set_fill(opacity=0.65), FadeIn(number), Write(title), run_time=1.5)
        disk = Footage("stage3").scale_to_fit_height(config.frame_height)
        with self.voice("Today we add that disk. And by the end of this video, you'll have the full picture from the"
                        " start of the series, and you'll know exactly where the halo and that lopsided glow come "
                        "from."):
            self.play(FadeOut(number), FadeOut(title), FadeOut(shade), FadeIn(disk), run_time=1.2)
            self.remove(clip)
        self.play(FadeOut(disk), run_time=0.8)


class E4_02_ThreeImages(Video):
    def construct(self):
        self.tag("One disk, three images")
        scale = 0.235
        origin = np.array([-1.6, 0.0, 0])
        hole = black_hole(scale, origin)
        disk = VGroup(*[Line(origin + scale * np.array([s * 6, 0, 0]), origin + scale * np.array([s * 20, 0, 0]),
                             color=ACCENT, stroke_width=8) for s in (-1, 1)])
        cam_m = 30 * np.array([np.cos(np.radians(4)), np.sin(np.radians(4)), 0])
        cam = Triangle(color=INK, fill_opacity=1, stroke_width=0).scale(0.16).rotate(PI / 2).move_to(origin + scale * cam_m)
        cam_label = T("camera", 22, MUTED).next_to(cam, UP, buff=0.15)
        disk_label = T("disk, edge-on", 22, ACCENT).next_to(disk[0], DOWN, buff=0.2, aligned_edge=LEFT)

        aim = -cam_m / np.linalg.norm(cam_m)
        found = {}
        for a in np.linspace(-0.42, 0.42, 421):
            c, s = np.cos(a), np.sin(a)
            pts, _ = geo.trace(cam_m, [c * aim[0] - s * aim[1], s * aim[0] + c * aim[1], 0], r_escape=45, quality=0.2)
            z = pts[:, 1]
            for i in np.nonzero(z[:-1] * z[1:] < 0)[0]:
                hit = pts[i] + z[i] / (z[i] - z[i + 1]) * (pts[i + 1] - pts[i])
                if 6.0 < abs(hit[0]) < 20.0:
                    kind = ("near" if hit[0] > 0 else "far") + ("_top" if z[i] > 0 else "_under")
                    found.setdefault(kind, []).append(np.vstack([pts[:i + 1], hit]))
                    break
        pick = lambda kind: found[kind][len(found[kind]) // 2]
        direct = glow(ray_path(pick("near_top"), scale, origin, color=INK, width=3.5))
        over = glow(ray_path(pick("far_top"), scale, origin, color=GOLD, width=3.5))
        under = glow(ray_path(pick("far_under"), scale, origin, color=COOL, width=3.5))

        with self.voice("Our disk is thin and flat. It sits in one plane, and stretches from six M, the innermost "
                        "stable orbit, out to twenty M. Here it is from the side, with the camera just above that "
                        "plane."):
            self.play(FadeIn(hole), Create(disk), FadeIn(disk_label), run_time=1.2)
            self.play(FadeIn(cam), FadeIn(cam_label), run_time=0.6)
        with self.voice("One ray goes straight to the near side of the disk. Nothing weird there."):
            self.play(Create(direct, lag_ratio=0), run_time=1.8)
        with self.voice("But a ray aimed above the hole gets bent down, onto the far side. So we see the back of the"
                        " disk, lifted up over the shadow."):
            self.play(Create(over, lag_ratio=0), run_time=3.0)
        with self.voice("And a ray aimed below the hole gets bent up, and hits the far side from underneath."):
            self.play(Create(under, lag_ratio=0), run_time=3.0)

        img = ImageMobject(str(ASSETS / "edgeon.jpg")).scale_to_fit_height(5.6).move_to([0, -0.2, 0])
        px = lambda x, y: img.get_center() + np.array([(x - 960) * 5.6 / 1080, (540 - y) * 5.6 / 1080, 0])
        notes = [
            ("the back, over the top", GOLD, px(960, 250), [-4.3, 3.2, 0], DOWN),
            ("the back, from underneath", COOL, px(960, 825), [-4.3, -3.5, 0], UP),
            ("the near side", INK, px(1500, 560), [5.0, 3.2, 0], DOWN),
        ]
        labels = VGroup()
        for text, color, target, where, edge in notes:
            label = T(text, 24, color, weight=SEMIBOLD).move_to(where)
            labels.add(VGroup(label, Arrow(label.get_edge_center(edge), target, buff=0.12, color=color, stroke_width=4,
                                           max_tip_length_to_length_ratio=0.08)))
        with self.voice("So we should see three images of one flat disk. That's the picture we're about to build. "
                        "And here's my favourite part: we don't write any special code for the halo. It just shows "
                        "up."):
            self.play(*[FadeOut(m) for m in (hole, disk, disk_label, cam, cam_label, direct, over, under)], FadeIn(img),
                      run_time=1.0)
            self.play(LaggedStart(*[FadeIn(l) for l in labels], lag_ratio=0.5), run_time=2.4)
        self.play(FadeOut(img), FadeOut(labels), run_time=0.6)
        self.clear()


class E4_03_CodeCrossing(Video):
    def construct(self):
        self.tag("Stage 3: did the ray hit the disk?")
        loop = CodePanel(excerpt(FRAG, ("for (int i = 0; i < 400", "    }")), "stages/03_disk/trace.frag",
                         max_width=8.0, max_height=6.6)
        loop.to_edge(LEFT, buff=0.25).shift(DOWN * 0.2)
        scale = 0.2
        origin = np.array([4.7, -0.2, 0])
        box = (1.7, 7.0, -3.2, 3.0)
        hole = black_hole(scale, origin)
        disk = VGroup(*[Line(origin + scale * np.array([s * 6, 0, 0]),
                             origin + scale * np.array([s * (11.5 if s > 0 else 14.5), 0, 0]),
                             color=ACCENT, stroke_width=6) for s in (-1, 1)])
        z_label = MathTex("z = 0", font_size=28, color=ACCENT).next_to(disk[1], DOWN, buff=0.15)
        cam = 30 * np.array([np.cos(np.radians(8)), np.sin(np.radians(8)), 0])
        aim = -cam / np.linalg.norm(cam)
        c, s = np.cos(-0.26), np.sin(-0.26)
        pts = geo.trace(cam, [c * aim[0] - s * aim[1], s * aim[0] + c * aim[1], 0], r_escape=60, quality=1.0)[0]
        z = pts[:, 1]
        hit = next(i for i in np.nonzero(z[:-1] * z[1:] < 0)[0]
                   if 6 < abs(pts[i][0] + z[i] / (z[i] - z[i + 1]) * (pts[i + 1][0] - pts[i][0])) < 20)
        hit_x = pts[hit][0] + z[hit] / (z[hit] - z[hit + 1]) * (pts[hit + 1][0] - pts[hit][0])
        before_line, before_dots = step_dots(pts[:hit + 1], scale, origin, GOLD, box)
        cross_line, cross_dots = step_dots(pts[hit:hit + 2], scale, origin, GOLD, box)
        after_line, after_dots = step_dots(pts[hit + 1:], scale, origin, GOLD, box)
        hit_point = origin + scale * np.array([hit_x, 0, 0])

        with self.voice("The disk is thin and flat, so finding it is easy. Here's the loop from last time, with the "
                        "new lines added."):
            self.play(FadeIn(loop, shift=UP * 0.3), FadeIn(hole), FadeIn(disk), FadeIn(z_label), run_time=1.0)
        with self.voice("Before each step, we remember where the ray was."):
            self.play(loop.focus("vec3 before", "rk4Step"), run_time=0.6)
            self.play(Create(before_line), LaggedStart(*[FadeIn(q, scale=2) for q in before_dots], lag_ratio=0.3),
                      run_time=3.0, rate_func=linear)
        with self.voice("After the step, we compare the two heights. The disk lies in the plane z equals zero. So if"
                        " z changed sign, the ray must have gone through that plane."):
            self.play(loop.focus("if (before.z * x.z < 0.0)"), run_time=0.6)
            self.play(Create(cross_line), FadeIn(cross_dots[-1], scale=2), run_time=0.8)
            self.play(Indicate(z_label, color=GOLD), run_time=1.0)
        with self.voice("Where exactly? t is the fraction of the step where the height hit zero, and mix slides "
                        "between the two positions by that fraction."):
            self.play(loop.focus("float t =", "vec4 disk ="), run_time=0.6)
            self.play(Flash(hit_point, color=GOLD, flash_radius=0.3), FadeIn(Dot(hit_point, radius=0.09, color=INK)), run_time=0.8)
        with self.voice("Disk light gives back a colour, and how opaque the gas is at that spot. We add the colour, "
                        "and shrink 'remaining': the share of light that can still come from further away."):
            self.play(loop.focus("colour += remaining", "remaining *="), run_time=0.6)
        with self.voice("And then the ray just keeps going. It might reach the stars. Or it might swing around and "
                        "cross the disk again. That's where the extra images come from. No extra code."):
            self.play(loop.unfocus(), run_time=0.5)
            self.play(Create(after_line), LaggedStart(*[FadeIn(q, scale=2) for q in after_dots], lag_ratio=0.3),
                      run_time=3.5, rate_func=linear)
        self.clear()


class E4_04_Rotation(Video):
    def construct(self):
        self.tag("Stage 3: making it spin")
        centre = np.array([3.9, 0.0, 0])
        scale = 0.16
        hole = black_hole(scale, centre)
        rng = np.random.default_rng(3)
        gas = VGroup()
        for _ in range(110):
            r = rng.uniform(6.0, 20.0)
            dot = Dot(radius=0.045, color=interpolate_color(ManimColor(GOLD), ManimColor(ACCENT), (r - 6) / 14))
            dot.r, dot.phase = r, rng.uniform(0, TAU)
            gas.add(dot)
        clock = ValueTracker(0.0)

        def place(group):
            for d in group:
                a = d.phase + clock.get_value() * 14.0 * d.r ** -1.5
                d.move_to(centre + scale * d.r * np.array([np.cos(a), np.sin(a), 0]))

        gas.add_updater(place)
        place(gas)
        force = MathTex(r"\frac{m v^2}{r}", "=", r"\frac{G M m}{r^2}", font_size=50).move_to([-3.4, 1.9, 0])
        labels = VGroup(T("needed to move in a circle", 20, COOL).next_to(force[0], UP, buff=0.2),
                        T("supplied by gravity", 20, GOLD).next_to(force[2], DOWN, buff=0.2))
        speed = MathTex(r"v = \sqrt{\frac{G M}{r}}", font_size=50).move_to([-3.4, -0.2, 0])
        omega = MathTex(r"\omega = \frac{v}{r} = \sqrt{\frac{G M}{r^3}}", font_size=50, color=GOLD).move_to([-3.4, -2.2, 0])
        with self.voice("Now let's make it spin. The gas is in orbit, and you can work out how fast with school "
                        "physics."):
            self.play(FadeIn(hole), FadeIn(gas), run_time=1.0)
            self.play(clock.animate.increment_value(4.0), run_time=4.0, rate_func=linear)
        with self.voice("To move in a circle, something has to supply the centripetal force: m v squared over r. "
                        "Here, gravity does that job."):
            self.play(Write(force), clock.animate.increment_value(2.5), run_time=2.5, rate_func=linear)
            self.play(FadeIn(labels), clock.animate.increment_value(3.5), run_time=3.5, rate_func=linear)
        with self.voice("Cancel the small mass, solve for v, and the orbital speed is the square root of G M over r."):
            self.play(Write(speed), clock.animate.increment_value(2.0), run_time=2.0, rate_func=linear)
            self.play(clock.animate.increment_value(3.0), run_time=3.0, rate_func=linear)
        with self.voice("Divide by r and you get the angular speed, omega: how fast the gas goes around. Gas close "
                        "in goes around way faster than gas further out. Watch the inner dots overtake the outer "
                        "ones."):
            self.play(Write(omega), clock.animate.increment_value(2.0), run_time=2.0, rate_func=linear)
            self.play(clock.animate.increment_value(7.0), run_time=7.0, rate_func=linear)
        with self.voice("And here's something lovely: Einstein's theory gives exactly the same formula for circular "
                        "orbits around a black hole."):
            self.play(Indicate(omega, color=GOLD, scale_factor=1.06), clock.animate.increment_value(4.0), run_time=4.0,
                      rate_func=linear)
        gas.clear_updaters()
        self.clear()

        self.tag("Stage 3: making it spin")
        code = CodePanel(excerpt(FRAG, ("float r = length(hit.xy);", "vec3 v = omega")), "stages/03_disk/trace.frag  ·  diskLight()",
                         max_width=11.5)
        code.move_to(UP * 2.0)
        o = np.array([0.0, -1.9, 0])
        pos = Arrow(o, o + np.array([2.2, 0.9, 0]), buff=0, color=INK, stroke_width=4)
        vel = Arrow(o + np.array([2.2, 0.9, 0]), o + np.array([2.2, 0.9, 0]) + 0.6 * np.array([-0.9, 2.2, 0]), buff=0,
                    color=GOLD, stroke_width=5)
        pos_label = MathTex("(x,\\ y)", font_size=32).next_to(pos.get_center(), DOWN, buff=0.15)
        vel_label = MathTex(r"\omega\,(-y,\ x)", font_size=32, color=GOLD).next_to(vel.get_center(), RIGHT, buff=0.2)
        hole2 = black_hole(0.12, o)
        with self.voice("Into the shader. If the crossing point is inside six M, or beyond twenty M, there's no disk"
                        " there, so we return nothing."):
            self.play(FadeIn(code, shift=UP * 0.3), run_time=0.8)
            self.play(code.focus("float r = length", "if (r < DISK_INNER"), run_time=0.7)
        with self.voice("Otherwise, omega is the formula we just found. Remember, our M already has the G built in."):
            self.play(code.focus("float omega"), run_time=0.7)
        with self.voice("And the velocity is omega times the position, turned through a right angle. Swap x and y, "
                        "and flip one sign."):
            self.play(code.focus("vec3 v = omega"), FadeIn(hole2), GrowArrow(pos), FadeIn(pos_label), run_time=1.0)
            self.play(GrowArrow(vel), FadeIn(vel_label), run_time=1.0)
        with self.voice("At the inner edge of the disk, that works out to roughly half the speed of light. Half!"):
            pass
        self.play(*[FadeOut(m) for m in (code, pos, vel, pos_label, vel_label, hole2)], run_time=0.6)

        cpp = CodePanel(excerpt(MAIN, ("float time = float(glfwGetTime());", "float time = float(glfwGetTime());"),
                                ('glUniform1f(glGetUniformLocation(program, "uTime"), time);',
                                 'glUniform1f(glGetUniformLocation(program, "uTime"), time);')),
                        "stages/03_disk/main.cpp", language="cpp", max_width=10.5)
        streaks = CodePanel(excerpt(FRAG, ("// Streaks of gas that rotate", "float density")), "stages/03_disk/trace.frag",
                            max_width=11.5)
        VGroup(cpp, streaks).arrange(DOWN, buff=0.9).move_to(DOWN * 0.2)
        with self.voice("To see the motion, the shader needs to know what time it is. So every frame, the program "
                        "reads the clock and sends it down as one more uniform."):
            self.play(FadeIn(cpp, shift=UP * 0.3), run_time=0.8)
            self.play(cpp.focus("float time"), run_time=0.7)
            self.play(cpp.focus("glUniform1f"), run_time=0.7)
        with self.voice("The shader paints streaks on the disk with a noise pattern. Each point's angle gets shifted"
                        " by omega times the time. So every ring turns at its own orbital speed."):
            self.play(FadeIn(streaks, shift=UP * 0.3), run_time=0.8)
            self.play(streaks.focus("float angle"), run_time=0.7)
        self.clear()


class E4_05_Doppler(Video):
    def construct(self):
        self.tag("Stage 3: colour and brightness")
        ring_c = np.array([0.0, 0.9, 0])
        ring = VGroup(
            AnnularSector(inner_radius=0.7, outer_radius=2.2, angle=PI, start_angle=PI / 2, color="#cfe8ff", fill_opacity=0.85),
            AnnularSector(inner_radius=0.7, outer_radius=2.2, angle=PI, start_angle=-PI / 2, color="#a8621f", fill_opacity=0.6),
        ).move_to(ring_c)
        ring.stretch(0.45, 1)
        core = Dot(ring_c, radius=0.2, color=BLACK).set_stroke(ACCENT, 2)
        spin = CurvedArrow(ring_c + np.array([-1.5, -0.95, 0]), ring_c + np.array([1.5, -0.95, 0]), angle=0.6,
                           color=INK, stroke_width=3, tip_length=0.2)
        toward = T("coming toward us:\nbluer, brighter", 24, COOL, line_spacing=0.8).move_to([-4.3, 0.9, 0])
        away = T("moving away:\nredder, dimmer", 24, HOT, line_spacing=0.8).move_to([4.3, 0.9, 0])
        eye = T("we are looking from here", 20, MUTED).move_to([0, -1.2, 0])
        with self.voice("Now the colour. You know the Doppler effect from an ambulance driving past. The siren "
                        "sounds higher coming toward you, and lower going away. Light does exactly the same thing."):
            doppler_pic = portrait("doppler", "Christian Doppler", "1803 - 1853", height=1.8).move_to([-5.4, -2.3, 0])
            self.play(FadeIn(ring), FadeIn(core), Create(spin), FadeIn(eye), FadeIn(doppler_pic), run_time=1.5)
        with self.voice("Gas coming toward us looks bluer and brighter. Gas moving away looks redder and dimmer."):
            self.play(FadeIn(toward), run_time=0.8)
            self.wait(1.5)
            self.play(FadeIn(away), run_time=0.8)
        with self.voice("And there's a second effect. Light climbing away from the hole loses energy, like a ball "
                        "thrown upward. But light can't slow down. So it turns redder instead."):
            self.play(Indicate(core, color=HOT, scale_factor=1.8), run_time=1.5)
        g_big = MathTex(r"g = \frac{\text{energy we receive}}{\text{energy the gas sent out}}", font_size=46).move_to(DOWN * 2.6)
        with self.voice("We can pack both effects into a single number, g: the energy of the light when it reaches "
                        "us, divided by its energy when it left the gas."):
            self.play(FadeOut(eye), Write(g_big), run_time=2.0)
        self.clear()

        self.tag("Stage 3: colour and brightness")
        code = CodePanel(excerpt(FRAG, ("float gasClock", "float g = uDoppler")), "stages/03_disk/trace.frag  ·  diskLight()",
                         max_width=11.5)
        code.move_to(UP * 1.6)
        with self.voice("Here it is in the shader. First, two clock factors. Near a black hole, clocks run slow: a "
                        "lot for the fast-moving gas, and a little for our camera."):
            self.play(FadeIn(code, shift=UP * 0.3), run_time=0.8)
            self.play(code.focus("float gasClock", "float cameraClock"), run_time=0.7)
        o = np.array([-2.0, -2.0, 0])
        v_arrow = Arrow(o, o + RIGHT * 2.4, buff=0, color=GOLD, stroke_width=5)
        p_arrow = Arrow(o, o + np.array([1.9, 1.1, 0]), buff=0, color=COOL, stroke_width=5)
        v_label = T("gas velocity v", 22, GOLD).next_to(v_arrow, DOWN, buff=0.12)
        p_label = T("light's momentum p", 22, COOL).next_to(p_arrow.get_end(), UP, buff=0.1)
        proj = DashedLine(o + np.array([1.9, 1.1, 0]), o + np.array([1.9, 0, 0]), color=MUTED, stroke_width=2)
        dot_note = T("dot(p, v): how much of the light's\nmotion is along the gas's motion", 22, MUTED, line_spacing=0.8)
        dot_note.move_to([3.6, -1.7, 0])
        with self.voice("Emitted is the light's energy, as the gas measures it. See the dot product of p and v? "
                        "That's how much the light's motion lines up with the motion of the gas. That's your Doppler"
                        " effect, right there."):
            self.play(code.focus("float emitted"), run_time=0.7)
            self.play(GrowArrow(v_arrow), FadeIn(v_label), GrowArrow(p_arrow), FadeIn(p_label), run_time=1.2)
            self.play(Create(proj), FadeIn(dot_note), run_time=1.0)
        with self.voice("Why the minus sign? Good question. Our ray runs from the camera to the gas. The real light "
                        "went the other way. So its momentum is flipped."):
            self.play(Rotate(p_arrow, PI, about_point=p_arrow.get_center()), run_time=1.2)
        with self.voice("Received is the energy as our camera measures it. And g is one divided by the other."):
            self.play(code.focus("float received", "float g ="), run_time=0.7)
        self.play(*[FadeOut(m) for m in (code, v_arrow, p_arrow, v_label, p_label, proj, dot_note)], run_time=0.6)

        glow_code = CodePanel(excerpt(FRAG, ("// Hot near the inner edge", "vec3 light = glowColour")),
                              "stages/03_disk/trace.frag  ·  diskLight()", max_width=11.5)
        glow_code.move_to(UP * 1.5)
        bar = VGroup(*[Rectangle(width=0.09, height=0.7, stroke_width=0, fill_opacity=1, fill_color=c) for c in
                       color_gradient(["#ff3b00", "#ff8a1f", "#ffd9a0", "#ffffff", "#cfe0ff"], 90)]).arrange(RIGHT, buff=0)
        bar.move_to(DOWN * 2.2)
        ends = VGroup(T("cooler", 22, MUTED).next_to(bar, LEFT, buff=0.25), T("hotter", 22, MUTED).next_to(bar, RIGHT, buff=0.25))
        with self.voice("Now, hot things glow. Think of a stove element going from dull red, to orange, to white. "
                        "The gas is hottest near the inner edge, and cooler further out."):
            self.play(FadeIn(glow_code, shift=UP * 0.3), run_time=0.8)
            self.play(glow_code.focus("float s =", "float temperature"), FadeIn(bar, lag_ratio=0.02), FadeIn(ends), run_time=1.5)
        with self.voice("What we see is that temperature multiplied by g. Glow colour turns it into a colour. And "
                        "the brightness is scaled by g to the fourth power. So a small change in g means a big "
                        "change in brightness."):
            self.play(glow_code.focus("float seen", "vec3 light"), run_time=0.7)
        self.clear()

        off = ImageMobject(str(ASSETS / "stage3_plain.jpg")).scale_to_fit_height(6.2).move_to(DOWN * 0.3)
        on = ImageMobject(str(ASSETS / "stage3.jpg")).scale_to_fit_height(6.2).move_to(DOWN * 0.3)
        off_label = MathTex(r"g = 1", font_size=40).to_edge(UP, buff=0.3)
        on_label = MathTex(r"\text{with } g", font_size=40, color=GOLD).to_edge(UP, buff=0.3)
        with self.voice("Here's the disk with g switched off. Evenly lit, all the way around. Kind of boring."):
            self.play(FadeIn(off), FadeIn(off_label), run_time=1.0)
        with self.voice("And here it is with g. The side spinning toward us blazes, and the other side fades. You'll"
                        " find that lopsided glow in every real image of a black hole."):
            self.play(FadeIn(on), ReplacementTransform(off_label, on_label), run_time=1.5)
            self.remove(off)
        self.clear()


class E4_06_Brightness(Video):
    def construct(self):
        self.tag("Stage 3: too bright for the screen")
        axes = Axes(x_range=[0, 4, 1], y_range=[0, 70, 10], x_length=7.5, y_length=4.6, tips=False,
                    axis_config={"color": MUTED, "stroke_width": 2, "include_ticks": False}).move_to([-1.2, -0.2, 0])
        values = [("stars", 0.4, INK), ("dim side", 2.0, ACCENT), ("bright side", 60.0, GOLD)]
        bars, names = VGroup(), VGroup()
        for i, (name, value, color) in enumerate(values):
            base = axes.c2p(i + 1, 0)
            bar = Rectangle(width=1.0, height=max(axes.c2p(0, value)[1] - axes.c2p(0, 0)[1], 0.04), stroke_width=0,
                            fill_color=color, fill_opacity=0.9).move_to(base, aligned_edge=DOWN)
            bars.add(bar)
            names.add(T(name, 22, color).next_to(base, DOWN, buff=0.2))
        limit = DashedLine(axes.c2p(0, 1), axes.c2p(4, 1), color=HOT, stroke_width=3)
        limit_label = T("the most a\nscreen can show", 22, HOT, line_spacing=0.8).next_to(limit, RIGHT, buff=0.2)
        with self.voice("One problem left. The bright side of the disk is dozens of times brighter than the dim "
                        "side, and way brighter than the stars."):
            self.play(Create(axes), run_time=0.6)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.4), FadeIn(names), run_time=2.5)
        with self.voice("But a normal image stores each colour as a number between zero and one. Anything brighter "
                        "gets cut off, and turns into flat, boring white."):
            self.play(Create(limit), FadeIn(limit_label), run_time=1.2)
        self.clear()

        self.tag("Stage 3: an image that can hold bright values")
        make = CodePanel(excerpt(MAIN, ("glBindTexture(GL_TEXTURE_2D, image);", "GL_TEXTURE_2D, image, 0);"),
                                 skip=("glTexParameteri",)), "stages/03_disk/main.cpp", language="cpp", max_width=11.5)
        make.move_to(UP * 1.4)
        tex = card("texture\nan image on the graphics card,\nfloating-point colours", GOLD, 22)
        fbo = card("framebuffer\nwhere drawing goes", COOL, 22)
        VGroup(fbo, tex).arrange(RIGHT, buff=1.4).move_to(DOWN * 2.1)
        attach = Arrow(fbo.get_right(), tex.get_left(), buff=0.1, color=INK, stroke_width=4)
        attach_label = T("draws into", 20, MUTED).next_to(attach, UP, buff=0.08)
        with self.voice("So we stop drawing straight to the screen. First we create a texture: an image that lives "
                        "on the graphics card. The format, R G B A sixteen F, means each colour is a floating-point "
                        "number, so values way above one survive."):
            self.play(FadeIn(make, shift=UP * 0.3), run_time=0.8)
            self.play(make.focus("glBindTexture", "GL_RGBA, GL_FLOAT"), FadeIn(tex), run_time=1.0)
        with self.voice("Then a framebuffer. Normally OpenGL draws into the window. A framebuffer lets us point it "
                        "somewhere else. Here we attach our texture, so the drawing lands in that image."):
            self.play(make.focus("glBindFramebuffer", "GL_TEXTURE_2D, image, 0"), FadeIn(fbo), GrowArrow(attach),
                      FadeIn(attach_label), run_time=1.2)
        self.play(*[FadeOut(m) for m in (make, tex, fbo, attach, attach_label)], run_time=0.6)

        passes = CodePanel(excerpt(MAIN, ("// Pass 1: trace into", "glUseProgram(program);"),
                                   ("// Pass 2: read that image", "glDrawArrays(GL_TRIANGLES, 0, 3);")),
                           "stages/03_disk/main.cpp", language="cpp", max_width=12.6)
        passes.move_to(DOWN * 0.1)
        with self.voice("Each frame now has two passes. Pass one: bind our framebuffer, and trace the picture "
                        "exactly like before. It lands in the texture, with all its brightness intact."):
            self.play(FadeIn(passes, shift=UP * 0.3), run_time=0.8)
            self.play(passes.focus("// Pass 1", "glUseProgram(program);"), run_time=0.7)
        with self.voice("Pass two: bind framebuffer zero, which means the window. Then draw the big triangle again, "
                        "with a second, tiny shader that reads the texture."):
            self.play(passes.focus("// Pass 2", "glDrawArrays"), run_time=0.7)
        self.play(FadeOut(passes), run_time=0.5)

        tone = CodePanel(excerpt(TONE, ("void main()", "}")), "stages/03_disk/tonemap.frag", max_width=8.4)
        tone.to_edge(LEFT, buff=0.25).shift(UP * 0.3)
        axes = Axes(x_range=[0, 8, 2], y_range=[0, 1.2, 1], x_length=4.6, y_length=3.4, tips=False,
                    axis_config={"color": MUTED, "stroke_width": 2, "include_ticks": False}).move_to([4.7, -0.2, 0])
        film = lambda c: min((c * (2.51 * c + 0.03)) / (c * (2.43 * c + 0.59) + 0.14), 1.0)
        clipped = axes.plot(lambda c: min(c, 1.0), x_range=[0, 8, 0.02], color=HOT, stroke_width=3)
        curve = axes.plot(film, x_range=[0, 8, 0.02], color=GOLD, stroke_width=4)
        x_label = T("brightness in the texture", 18, MUTED).next_to(axes, DOWN, buff=0.15)
        y_label = T("on screen", 18, MUTED).next_to(axes, LEFT, buff=0.1).rotate(PI / 2)
        legend = VGroup(T("cut off at 1", 20, HOT), T("our curve", 20, GOLD)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        legend.next_to(axes, UP, buff=0.2)
        with self.voice("That shader looks up this pixel in the texture, and runs it through a curve."):
            self.play(FadeIn(tone, shift=UP * 0.3), run_time=0.8)
            self.play(tone.focus("vec3 c = texture"), run_time=0.7)
        with self.voice("If we just chopped everything off at one, all the bright parts would go flat. The curve "
                        "squeezes large values smoothly toward one instead, so you can still see detail inside the "
                        "glare."):
            self.play(tone.focus("c = (c * (2.51"), Create(axes), FadeIn(x_label), FadeIn(y_label), run_time=1.0)
            self.play(Create(clipped), FadeIn(legend[0]), run_time=1.2)
            self.play(Create(curve), FadeIn(legend[1]), run_time=1.5)
        with self.voice("The last line corrects for how monitors display brightness, and writes the final colour."):
            self.play(tone.focus("fragColor"), run_time=0.7)
        self.clear()


class E4_07_Result(Video):
    def construct(self):
        clip = Footage("stage3").scale_to_fit_height(config.frame_height)
        self.play(FadeIn(clip), run_time=1.0)

        def caption(text):
            label = T(text, 26, weight=SEMIBOLD).to_edge(DOWN, buff=0.4)
            return VGroup(BackgroundRectangle(label, color=BLACK, fill_opacity=0.7, buff=0.2), label)

        with self.voice("And there it is. Stage three, running."):
            pass
        cap = caption("the halo: the far side of the disk, seen over and under the hole")
        with self.voice("The halo over the top is the far side of the disk, its light bent toward us. The thin arc "
                        "underneath is the far side again, seen from below."):
            self.play(FadeIn(cap), run_time=0.5)
        new = caption("the bright side: gas moving toward us")
        with self.voice("The left side blazes because that gas is rushing toward us. And the whole disk turns, each "
                        "ring at its own speed."):
            self.play(FadeOut(cap), FadeIn(new), run_time=0.5)
        with self.voice("And remember: nothing here was drawn by hand. Two rules for light, a flat disk, and one "
                        "number for the colour. That's it."):
            self.play(FadeOut(new), run_time=0.5)

        shade = Rectangle(width=15, height=9, stroke_width=0, fill_color=BLACK, fill_opacity=0.0)
        steps = [("stage1.jpg", "1", "the two rules, on the processor"), ("stage2.jpg", "2", "a ray per pixel, in a shader"),
                 ("stage3.jpg", "3", "a disk, its motion, its glow")]
        tiles = Group()
        for name, number, label in steps:
            img = ImageMobject(str(ASSETS / name)).scale_to_fit_width(4.1)
            text = VGroup(T(number, 28, ACCENT, weight=BOLD), T(label, 22, weight=SEMIBOLD)).arrange(RIGHT, buff=0.2)
            text.next_to(img, DOWN, buff=0.25)
            tiles.add(Group(img, text))
        tiles.arrange(RIGHT, buff=0.4)
        with self.voice("Look how far we've come. Stage one: the two rules, traced on the processor and drawn as "
                        "lines. Stage two: the same rules in a shader, one ray per pixel. Stage three: a disk, its "
                        "motion, and its glow."):
            self.play(shade.animate.set_fill(opacity=0.92), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.3) for t in tiles], lag_ratio=0.8), run_time=6.0)
        self.play(FadeOut(tiles), run_time=0.6)

        output = subprocess.run([str(ROOT / "build" / "test_geodesic")], capture_output=True, text=True).stdout
        rows = VGroup(*[Text(line, font="Menlo", font_size=17, color=INK, t2c={"[ ok ]": GOOD, "all tests passed": GOOD})
                        for line in output.strip().split("\n")]).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        term_bg = RoundedRectangle(width=rows.width + 0.6, height=rows.height + 0.5, corner_radius=0.12,
                                   fill_color="#07090d", fill_opacity=1, stroke_color="#2b3345", stroke_width=1.5)
        term = VGroup(term_bg, rows).move_to(DOWN * 0.6)
        extra = T("the full simulator, in src/", 30, weight=BOLD).to_edge(UP, buff=0.6)
        with self.voice("The repository also has a more polished version of this program. It adds a soft glow around"
                        " the bright areas, and a camera that properly accounts for curved space."):
            self.play(FadeIn(extra), run_time=0.8)
        with self.voice("And it has tests. They check the code against things you can work out by hand: that light "
                        "orbits at three M, that the shadow's edge is at five point two M, and that distant rays "
                        "bend by the textbook amount."):
            self.play(FadeIn(term_bg), LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in rows], lag_ratio=0.5), run_time=6.0)
        final = Footage("orbit").scale_to_fit_height(config.frame_height)
        with self.voice("And that's a whole black hole, built from scratch. If you made it this far, go run the "
                        "code, break it, and make it yours. Thanks for watching!"):
            self.play(FadeOut(term), FadeOut(extra), FadeOut(shade), FadeIn(final), run_time=1.2)
            self.remove(clip)
        self.wait(2.5)
        self.play(FadeOut(final), run_time=1.5)
