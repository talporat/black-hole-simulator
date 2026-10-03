"""Episode 1: why light bends.

The physics of light near a black hole, from Newton and Pythagoras to the
two rules for light that the programs in later episodes run.
"""
from common import *

STAGE = "stages/01_rays_2d/main.cpp"


class E1_01_Hook(Video):
    def construct(self):
        self.shot = None

        def cut(name, hold):
            """Hard cut to another camera angle, shown for `hold` seconds. The clip is
            stretched to last slightly longer than that, so it never runs out and freezes."""
            clip = Footage(name, span=hold + 0.8).scale_to_fit_height(config.frame_height)
            self.add(clip)
            if self.shot is not None:
                self.remove(self.shot)
            self.shot = clip

        def montage(seconds, *names):
            for name in names:
                cut(name, seconds / len(names))
                self.wait(seconds / len(names))

        with self.voice("This is a black hole. And no, it's not from a movie, and it's not from NASA. It's a "
                        "program, running live on my laptop.") as seconds:
            montage(seconds * 0.45, "hook_1")
            montage(seconds * 0.55, "hook_2")
        promise = T("By the end, you will have built this.", 40, weight=BOLD).to_edge(DOWN, buff=0.7)
        promise_back = BackgroundRectangle(promise, color=BLACK, fill_opacity=0.65, buff=0.25)
        with self.voice("And here's my promise: by the end of this series, you'll have built this yourself. From an "
                        "empty file. And you'll understand every single line.") as seconds:
            cut("hook_3", seconds * 0.5)
            self.add(promise_back, promise)
            self.wait(seconds * 0.5)
            cut("hook_4", seconds * 0.5)
            self.add(promise_back, promise)
            self.wait(seconds * 0.5)
        self.remove(promise_back, promise)
        with self.voice("Because here's what blows my mind. Nobody drew that glowing halo. Nobody painted that "
                        "shadow. There's no 3D model in here. Every pixel just asks one question: if light landed "
                        "here, where did it come from?") as seconds:
            montage(seconds * 0.5, "hook_5")
            cut("hook_6", seconds * 0.5 + 15.0)  # keeps moving under the title
            self.wait(seconds * 0.5)

        shade = Rectangle(width=15, height=9, stroke_width=0, fill_color=BLACK, fill_opacity=0.0)
        title = T("Ray Tracing a Black Hole", 68, weight=BOLD)
        sub = T("from scratch, in C++ and OpenGL", 30, ACCENT, weight=MEDIUM)
        VGroup(title, sub).arrange(DOWN, buff=0.35)
        with self.voice("So let's build it. The physics and the code, side by side."):
            self.play(shade.animate.set_fill(opacity=0.7), run_time=0.6)
            self.play(Write(title), run_time=1.2)
            self.play(FadeIn(sub, shift=UP * 0.2), run_time=0.5)

        steps = [("physics.jpg", "1", "The physics"), ("stage1.jpg", "2", "Light rays in 2D"),
                 ("stage2.jpg", "3", "A 3D ray tracer"), ("stage3.jpg", "4", "The spinning disk")]
        tiles = Group()
        for name, number, label in steps:
            img = ImageMobject(str(ASSETS / name)).scale_to_fit_width(3.05)
            frame = SurroundingRectangle(img, color="#2b3345", buff=0, stroke_width=2)
            text = VGroup(T(number, 26, ACCENT, weight=BOLD), T(label, 22, weight=SEMIBOLD)).arrange(RIGHT, buff=0.2)
            text.next_to(img, DOWN, buff=0.22)
            tiles.add(Group(img, frame, text))
        tiles.arrange(RIGHT, buff=0.3).move_to(UP * 0.3)
        today = T("Today: why light bends, and the two equations our program runs on", 28, GOLD, weight=SEMIBOLD)
        today.to_edge(DOWN, buff=0.9)
        with self.voice("We'll do it in four episodes. And from episode two on, every single one ends with a program"
                        " you can actually run."):
            self.play(FadeOut(title), FadeOut(sub), shade.animate.set_fill(opacity=0.92), run_time=0.6)
        with self.voice("Episode one, that's today, is the physics. Stick with me to the end of this video, and "
                        "you'll know exactly why light bends, and the two equations our whole program runs on."):
            self.play(FadeIn(tiles[0], shift=UP * 0.3), run_time=0.6)
            self.play(FadeIn(today, shift=UP * 0.2), run_time=0.6)
        with self.voice("Episode two: we turn those equations into real code, and draw light rays bending around a "
                        "black hole."):
            self.play(FadeIn(tiles[1], shift=UP * 0.3), run_time=0.6)
        with self.voice("Episode three: a full three-dimensional ray tracer, on your graphics card. And episode "
                        "four: the glowing disk of gas, spinning.") as seconds:
            self.play(FadeIn(tiles[2], shift=UP * 0.3), run_time=0.6)
            self.wait(max(seconds * 0.56 - 0.6, 0))  # "And episode four" starts 56% into this sentence
            self.play(FadeIn(tiles[3], shift=UP * 0.3), run_time=0.6)
        with self.voice("Now, quick heads up: some of this physics is university level. Don't worry about that. "
                        "Every piece has a high-school version, and that's where we start."):
            self.play(Circumscribe(tiles[0], color=GOLD, buff=0.1), run_time=2.0)
        self.play(FadeOut(tiles), FadeOut(today), shade.animate.set_fill(opacity=1.0), run_time=0.6)
        self.remove(self.shot)


class E1_02_WhyLightBends(Video):
    def construct(self):
        self.chapter("PART 1", "The physics")
        self.tag("Why light bends")
        newton = MathTex(r"F = \frac{G\,M\,", r"m", r"}{r^2}", font_size=72)
        massless = MathTex(r"m_{\text{light}} = 0", font_size=56, color=HOT)
        VGroup(newton, massless).arrange(DOWN, buff=0.8)
        with self.voice("Let's kick off with something you already know: Newton's law of gravity. The heavier "
                        "something is, the harder gravity pulls on it."):
            newton_pic = portrait("newton", "Isaac Newton", "1643 - 1727").move_to([5.0, 0.2, 0])
            self.play(Write(newton), FadeIn(newton_pic), run_time=1.5)
            self.play(Indicate(newton[1], color=GOLD, scale_factor=1.5), run_time=1.2)
        with self.voice("But wait. Light has no mass. Literally zero. So according to Newton, gravity shouldn't do "
                        "anything to it."):
            self.play(Write(massless), run_time=1.2)
        with self.voice("Except it does! In 1919, astronomers photographed stars right next to the Sun during an "
                        "eclipse. And the starlight was bent."):
            self.play(Circumscribe(massless, color=HOT, buff=0.15), run_time=1.5)
        self.clear(0.5)

        def warp(p):
            r2 = p[0] ** 2 + p[1] ** 2
            return p * (1 - 0.62 * np.exp(-r2 / 4.5))

        def grid(fn):
            lines = VGroup()
            for x in np.arange(-7.2, 7.21, 0.6):
                lines.add(VMobject().set_points_smoothly([fn(np.array([x, y, 0.0])) for y in np.linspace(-4.2, 4.2, 50)]))
            for y in np.arange(-4.2, 4.21, 0.6):
                lines.add(VMobject().set_points_smoothly([fn(np.array([x, y, 0.0])) for x in np.linspace(-7.2, 7.2, 70)]))
            return lines.set_stroke(COOL, 1.3, opacity=0.45)

        self.tag("Why light bends")
        flat, curved = grid(lambda p: p), grid(warp)
        scale = 0.225
        hole = black_hole(scale, ORIGIN)
        straight = Line([-7.2, 1.6, 0], [7.2, 1.6, 0], color=GOLD, stroke_width=4)
        pts, _ = geo.trace([-40, 1.6 / scale, 0], [1, 0, 0], r_escape=60)
        bent = ray_path(pts, scale, ORIGIN, color=GOLD, width=4, box=(-7.2, 7.2, -4.1, 4.1))
        with self.voice("So what's going on? Einstein's answer sounds crazy: gravity isn't a force at all. Mass "
                        "bends space and time themselves."):
            einstein_pic = portrait("einstein", "Albert Einstein", "1879 - 1955").to_corner(UR, buff=0.35)
            self.play(Create(flat, lag_ratio=0.02), FadeIn(einstein_pic), run_time=1.5)
            self.play(Create(straight), run_time=0.8)
            self.play(FadeIn(hole, scale=0.3), Transform(flat, curved), run_time=2.0)
        with self.voice("Light still travels as straight as it possibly can. It's the space that's bent. So to us, "
                        "the path looks curved."):
            self.play(Transform(straight, bent), run_time=2.5)
        with self.voice("It's like a plane flying dead straight over the round Earth. Draw that route on a flat map,"
                        " and you get an arc. Same thing."):
            self.play(ShowPassingFlash(bent.copy().set_stroke(INK, 8), time_width=0.3), run_time=2.5)

        # Pythagoras -> metric
        veil = Rectangle(width=15, height=9, stroke_width=0, fill_color=BG, fill_opacity=1.0)
        a, b, c = np.array([-5.4, -1.0, 0]), np.array([-2.6, -1.0, 0]), np.array([-2.6, 0.9, 0])
        tri = Polygon(a, b, c, color=INK, stroke_width=3)
        legs = VGroup(MathTex("dx", font_size=40, color=COOL).next_to(Line(a, b), DOWN, buff=0.15),
                      MathTex("dy", font_size=40, color=GOOD).next_to(Line(b, c), RIGHT, buff=0.15),
                      MathTex("ds", font_size=40, color=GOLD).move_to((a + c) / 2 + np.array([-0.35, 0.3, 0])))
        pyth = MathTex(r"ds^2", "=", r"dx^2 + dy^2", font_size=60).move_to([2.6, 0, 0])
        pyth[0].set_color(GOLD)
        with self.voice("Okay, but we want to calculate stuff. So we need a formula for that bending. And we'll "
                        "start with an old friend: Pythagoras."):
            self.play(FadeIn(veil), FadeOut(einstein_pic), run_time=0.6)
            self.play(Create(tri), FadeIn(legs), run_time=1.2)
            self.play(Write(pyth), run_time=1.5)
        with self.voice("Take a tiny step across, and call it d x. And a tiny step up, d y. That little d just "
                        "means: a tiny change in. So the tiny distance you've covered is d s."):
            d_note = VGroup(MathTex("d", font_size=44, color=GOLD), T("=  a tiny change in", 26, MUTED)).arrange(RIGHT, buff=0.25)
            d_note.move_to([2.6, -1.4, 0])
            self.play(FadeIn(d_note, shift=UP * 0.2), run_time=0.8)
            self.play(Indicate(legs[2], color=GOLD), Indicate(pyth[0], color=GOLD), run_time=1.5)
        flat_eq = MathTex(r"ds^2", "=", r"dx^2 + dy^2 + dz^2", r"-\,dt^2", font_size=56)
        flat_eq[0].set_color(GOLD)
        flat_eq[3].set_color(HOT)
        flat_label = T("the metric of flat, empty space", 26, MUTED).next_to(flat_eq, DOWN, buff=0.5)
        with self.voice("Add a third dimension, easy. Now add time. And this is the weird part: time goes in with a "
                        "minus sign."):
            self.play(FadeOut(tri), FadeOut(legs), FadeOut(d_note), ReplacementTransform(pyth, flat_eq), run_time=1.5)
            self.play(Indicate(flat_eq[3], color=HOT), run_time=1.2)
        with self.voice("A formula like this has a name: a metric. It's the rulebook for measuring distances in "
                        "space and time together. This one describes flat, empty space."):
            self.play(FadeIn(flat_label), run_time=0.6)

        sch = MathTex(r"ds^2 = -", r"\left(1-\frac{2M}{r}\right)", r"dt^2 +", r"\left(1-\frac{2M}{r}\right)^{-1}",
                      r"dr^2 + r^2\,d\Omega^2", font_size=48)
        sch_label = VGroup(
            T("the metric around a mass M", 26, MUTED),
            VGroup(*[VGroup(MathTex(sym, font_size=34, color=GOLD), T(meaning, 22, MUTED)).arrange(RIGHT, buff=0.22)
                     for sym, meaning in [("d", "a tiny change in"), ("r", "distance from the centre"),
                                          (r"\Omega", "direction around the hole")]]).arrange(RIGHT, buff=0.8),
        ).arrange(DOWN, buff=0.35).next_to(sch, DOWN, buff=0.5)
        with self.voice("Near a mass, the rulebook changes. A physicist called Karl Schwarzschild figured out how, "
                        "in 1915. Same idea, just written with r, the distance from the centre, and capital omega, "
                        "which is the direction you're in, around the hole."):
            self.play(FadeOut(flat_eq), FadeOut(flat_label), run_time=0.5)
            sch_pic = portrait("schwarzschild", "Karl Schwarzschild", "1873 - 1916", height=1.8).move_to(UP * 2.5)
            self.play(Write(sch), FadeIn(sch_label), FadeIn(sch_pic), run_time=2.5)
        boxes = VGroup(SurroundingRectangle(sch[1], color=GOLD, buff=0.08), SurroundingRectangle(sch[3], color=GOLD, buff=0.08))
        with self.voice("But look closely: two terms picked up an extra factor. One minus two M over r. Far away, r "
                        "is huge, the factor is basically one, and space is flat again. Up close? Clocks tick "
                        "differently, and rulers measure differently."):
            self.play(Create(boxes), FadeOut(sch_pic), run_time=1.0)
        units = MathTex(r"M \;\text{means}\; \frac{G\,M}{c^2}", r"\qquad \text{Sun: } 1.5\ \text{km}",
                        r"\qquad \text{Earth: } 4.4\ \text{mm}", font_size=40).next_to(sch, DOWN, buff=1.0)
        with self.voice("Quick word on units. M here is the mass turned into a length: G times M, over c squared. "
                        "For the Sun, that's about one and a half kilometres. For the Earth? About four millimetres."
                        " Tiny."):
            self.play(FadeOut(sch_label), Write(units[0]), run_time=1.5)
            self.wait(2.5)
            self.play(FadeIn(units[1]), run_time=0.6)
            self.wait(1.0)
            self.play(FadeIn(units[2]), run_time=0.6)

        scale = 0.42
        origin = np.array([-3.6, -0.45, 0])
        hole2 = black_hole(scale, origin)
        rings = [
            (INK, r"r = 2M", "event horizon", "nothing gets out"),
            (GOLD, r"r = 3M", "photon sphere", "light can orbit here"),
            (COOL, r"r = 6M", "innermost stable orbit", "the disk starts here"),
        ]
        with self.voice("Now, there are three distances I want you to remember."):
            self.play(FadeOut(boxes), FadeOut(units), FadeOut(flat), FadeOut(straight), FadeOut(hole),
                      sch.animate.scale(0.7).to_edge(UP, buff=0.75), run_time=1.0)
            self.remove(veil)
            self.play(FadeIn(hole2), run_time=0.5)
        rows = VGroup()
        for color, tex, name, why in rings:
            rows.add(VGroup(MathTex(tex, font_size=40, color=color),
                            VGroup(T(name, 28, weight=SEMIBOLD), T(why, 22, MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
                            ).arrange(RIGHT, buff=0.5))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.7).scale(1.1).move_to([3.1, -0.45, 0])
        escape = MathTex(r"v_{\text{escape}} = \sqrt{\frac{2GM}{r}} = c", r"\quad\Rightarrow\quad r = \frac{2GM}{c^2}",
                         font_size=36, color=MUTED).to_edge(DOWN, buff=0.3)
        with self.voice("Number one: r equals two M. That's the event horizon. Cross it, and nothing gets back out. "
                        "Not even light."):
            self.play(FadeIn(rows[0], shift=LEFT * 0.3), Flash(origin, color=INK, flash_radius=2 * scale + 0.1), run_time=1.0)
        with self.voice("Here's a nice way to remember it. Take the escape velocity formula from school, and ask: "
                        "where does it reach the speed of light? You land on exactly this radius."):
            self.play(Write(escape[0]), run_time=1.5)
            self.wait(2.0)
            self.play(Write(escape[1]), run_time=1.2)
        photon = DashedVMobject(Circle(radius=3 * scale, color=GOLD, stroke_width=3).move_to(origin), num_dashes=36)
        orbiter = Dot(color=GOLD, radius=0.07).move_to(origin + RIGHT * 3 * scale)
        with self.voice("Number two: three M. Gravity is so strong here that light itself can go around in circles. "
                        "That's the photon sphere."):
            self.play(FadeOut(escape), Create(photon), FadeIn(rows[1], shift=LEFT * 0.3), run_time=1.0)
            self.add(orbiter)
            self.play(Rotate(orbiter, TAU, about_point=origin), run_time=2.5, rate_func=linear)
            self.remove(orbiter)
        isco = DashedVMobject(Circle(radius=6 * scale, color=COOL, stroke_width=3).move_to(origin), num_dashes=60)
        with self.voice("And number three: six M. That's the closest anything can orbit safely. Our disk of gas is "
                        "going to start right there."):
            self.play(Create(isco), FadeIn(rows[2], shift=LEFT * 0.3), run_time=1.2)
        self.clear()


class E1_03_TwoRules(Video):
    def construct(self):
        self.tag("How light moves")
        scale = 0.3
        origin = np.array([0.0, -0.5, 0])
        box = (-7.2, 7.2, -3.8, 2.3)
        hole = black_hole(scale, origin)

        pts, _ = geo.trace([-40, 7.0, 0], [1, 0, 0], r_escape=60)
        path = ray_path(pts, scale, origin, color=GOLD, width=3.5, box=box)
        t = ValueTracker(0.02)
        dot = always_redraw(lambda: Dot(path.point_from_proportion(t.get_value()), radius=0.1, color=INK))
        name = VGroup(T("geodesic", 40, GOLD, weight=BOLD), T("the straightest possible path", 26, MUTED))
        name.arrange(DOWN, buff=0.15).to_edge(UP, buff=0.6)
        with self.voice("So how does light actually move through bent space? The path has a fancy name: a geodesic. "
                        "All it means is the straightest path available."):
            self.play(FadeIn(hole), Create(path.copy().set_stroke(opacity=0.35)), run_time=1.2)
            self.add(dot)
            self.play(t.animate.set_value(0.97), FadeIn(name), run_time=5.0, rate_func=linear)
        self.clear(0.5)

        # A thrown ball next to a ray of light: same two-rule pattern.
        self.tag("How light moves")
        divider = Line(UP * 2.6, DOWN * 2.9, color="#2b3345", stroke_width=2)
        ball_title = T("a thrown ball", 30, COOL, weight=SEMIBOLD).move_to([-3.6, 2.7, 0])
        ball_state = MathTex(r"\text{position } x \qquad \text{velocity } v", font_size=36).move_to([-3.6, 1.7, 0])
        ball_dx = MathTex(r"\frac{dx}{dt} = v", font_size=52).move_to([-3.6, 0.2, 0])
        ball_dv = MathTex(r"\frac{dv}{dt} = \frac{F}{m}", font_size=52).move_to([-3.6, -1.6, 0])
        with self.voice("To compute one, think about how you'd simulate a ball flying through the air. You only "
                        "track two things: where it is, and how fast it's going."):
            self.play(FadeIn(ball_title), run_time=0.6)
            self.play(Write(ball_state), run_time=1.5)
        with self.voice("And you only need two rules. Rule one: the velocity changes the position."):
            self.play(Write(ball_dx), run_time=1.2)
        with self.voice("Rule two: the force changes the velocity. Run those two rules again and again, in tiny "
                        "steps, and you get the ball's whole path."):
            self.play(Write(ball_dv), run_time=1.2)

        light_title = T("a ray of light", 30, GOLD, weight=SEMIBOLD).move_to([3.6, 2.7, 0])
        light_state = MathTex(r"\text{position } \mathbf{x} \qquad \text{momentum } \mathbf{p}", font_size=36).move_to([3.6, 1.7, 0])
        light_dx = MathTex(r"\frac{d\mathbf{x}}{d", r"\lambda", r"} = \frac{\partial H}{\partial \mathbf{p}}", font_size=52).move_to([3.6, 0.2, 0])
        light_dp = MathTex(r"\frac{d\mathbf{p}}{d", r"\lambda", r"} = -\frac{\partial H}{\partial \mathbf{x}}", font_size=52).move_to([3.6, -1.6, 0])
        ham = MathTex(r"H = \tfrac12\, g^{\mu\nu} p_\mu p_\nu", font_size=40, color=MUTED).move_to([3.6, -3.1, 0])
        with self.voice("For light, it's exactly the same game, with a position x and a momentum p. The momentum "
                        "tells you which way the light is going, and how much energy it's carrying."):
            self.play(Create(divider), FadeIn(light_title), run_time=0.8)
            self.play(Write(light_state), run_time=1.5)
        with self.voice("And both rules come out of one single function, called H. It's built from the metric. Think"
                        " of it as the photon's energy."):
            self.play(Write(ham), run_time=1.5)
        with self.voice("Rule one: the position changes with the slope of H, as you vary the momentum."):
            self.play(Write(light_dx), run_time=1.5)
        with self.voice("Rule two: the momentum changes with minus the slope of H, as you vary the position."):
            self.play(Write(light_dp), run_time=1.5)
        with self.voice("These are Hamilton's equations. That's university physics, and no, we're not deriving them "
                        "today. Just look at the shape: two rules, applied over and over. Exactly like the ball."):
            hamilton_pic = portrait("hamilton", "William Rowan Hamilton", "1805 - 1865", height=1.4, label_side=RIGHT)
            hamilton_pic.move_to([-4.2, -3.15, 0])
            self.play(FadeIn(hamilton_pic), run_time=0.6)
            self.play(Circumscribe(VGroup(ball_dx, ball_dv), color=COOL, buff=0.2),
                      Circumscribe(VGroup(light_dx, light_dp), color=GOLD, buff=0.2), run_time=2.0)
        with self.voice("One small thing. Light doesn't carry a clock. So instead of time, we use lambda. Think of "
                        "it as a distance marker along the ray."):
            self.play(Indicate(light_dx[1], color=HOT, scale_factor=1.6), Indicate(light_dp[1], color=HOT, scale_factor=1.6),
                      run_time=1.8)
        self.clear()


class E1_04_Formula(Video):
    def construct(self):
        self.tag("A formula the computer can use")
        term = MathTex(r"\left(1-\frac{2M}{r}\right)^{-1}", font_size=60, color=HOT).move_to([-3.6, 0.6, 0])
        zero = MathTex(r"r = 2M:\quad \frac{1}{0}", font_size=48, color=HOT).next_to(term, DOWN, buff=0.7)
        axes = Axes(x_range=[0, 10, 2], y_range=[0, 10, 5], x_length=5.2, y_length=3.8, tips=False,
                    axis_config={"color": MUTED, "stroke_width": 2, "include_ticks": False}).move_to([3.0, 0.0, 0])
        curve = axes.plot(lambda r: 1 / (1 - 2 / r), x_range=[2.223, 10, 0.01], color=HOT, stroke_width=4)
        wall = DashedLine(axes.c2p(2, 0), axes.c2p(2, 10), color=INK, stroke_width=2)
        wall_label = MathTex(r"r = 2M", font_size=30).next_to(wall, DOWN, buff=0.15)
        r_label = MathTex("r", font_size=32, color=MUTED).next_to(axes.c2p(10, 0), DOWN, buff=0.15)
        with self.voice("Now, before we write any code, we've got a problem. Look at this factor in Schwarzschild's "
                        "formula. At r equals two M, it becomes one divided by zero. Uh oh."):
            self.play(Write(term), run_time=1.2)
            self.play(Create(axes), FadeIn(r_label), Create(wall), FadeIn(wall_label), run_time=1.0)
            self.play(Create(curve.reverse_direction()), Write(zero), run_time=2.0)
        with self.voice("Here's the thing though: nothing is actually broken in space there. It's the coordinates "
                        "that break. Like longitude at the North Pole. It just stops meaning anything."):
            self.play(Indicate(wall, color=HOT), run_time=1.2)
        with self.voice("But a computer following a ray doesn't care about that. It would crash straight into the "
                        "division by zero."):
            self.play(Indicate(zero, color=HOT), run_time=1.2)
        self.clear(0.5)

        self.tag("A formula the computer can use")
        ks = MathTex(r"g_{\mu\nu}", "=", r"\eta_{\mu\nu}", "+", r"f", r"\,l_\mu l_\nu", font_size=64).to_edge(UP, buff=1.0)
        ks[4].set_color(ACCENT)
        ks[5].set_color(COOL)
        whole = Brace(ks[0], DOWN, color=MUTED)
        whole_text = T("the metric", 22, MUTED).next_to(whole, DOWN, buff=0.1)
        flat_brace = Brace(ks[2], DOWN, color=MUTED)
        flat_text = T("flat space", 22, MUTED).next_to(flat_brace, DOWN, buff=0.1)
        corr_brace = Brace(ks[4:], DOWN, color=MUTED)
        corr_text = T("one correction", 22, MUTED).next_to(corr_brace, DOWN, buff=0.1)
        with self.voice("So here's the fix: describe the same space with better coordinates. They're called Kerr-"
                        "Schild coordinates, and they use plain old x, y and z."):
            self.play(Write(ks), run_time=2.0)
            self.play(GrowFromCenter(whole), FadeIn(whole_text), run_time=0.7)
        with self.voice("And in these coordinates, the metric is just flat space, plus one correction for gravity. "
                        "That's all."):
            self.play(GrowFromCenter(flat_brace), FadeIn(flat_text), run_time=0.7)
            self.play(GrowFromCenter(corr_brace), FadeIn(corr_text), run_time=0.7)

        scale = 0.3
        origin = np.array([-4.3, -1.3, 0])
        hole = black_hole(scale, origin)
        field = VGroup()
        for gx in np.arange(-2.1, 2.11, 0.7):
            for gy in np.arange(-2.1, 2.11, 0.7):
                q = np.array([gx, gy, 0.0])
                r = np.linalg.norm(q) / scale
                if r < 3.0:
                    continue
                d = q / np.linalg.norm(q)
                strength = np.clip(2.0 / r * 3.2, 0.2, 1.0)
                field.add(Arrow(origin + q - 0.2 * d, origin + q + 0.2 * d, buff=0, color=COOL, stroke_width=3.5,
                                max_tip_length_to_length_ratio=0.45).set_opacity(strength))
        f_def = MathTex(r"f", r"= \frac{2M}{r}", font_size=46)
        f_def[0].set_color(ACCENT)
        f_text = T("how strong gravity is here", 24, MUTED)
        l_def = MathTex(r"\mathbf{L}", font_size=46, color=COOL)
        l_text = T("an arrow of length 1, pointing away from the hole", 24, MUTED)
        defs = VGroup(VGroup(f_def, f_text).arrange(RIGHT, buff=0.5), VGroup(l_def, l_text).arrange(RIGHT, buff=0.5))
        defs.arrange(DOWN, aligned_edge=LEFT, buff=0.7).move_to([2.6, -1.2, 0])
        with self.voice("The correction has two ingredients. First, f. It's a number that says how strong gravity is"
                        " where you are: two M over r. Huge near the hole, fading out as you move away."):
            self.play(*[FadeOut(m) for m in (whole, whole_text, flat_brace, flat_text, corr_brace, corr_text)], run_time=0.4)
            self.play(FadeIn(hole), FadeIn(defs[0], shift=LEFT * 0.2), Indicate(ks[4], color=ACCENT), run_time=1.2)
        with self.voice("Second, L. It's an arrow of length one, that always points straight away from the hole."):
            self.play(LaggedStart(*[GrowArrow(a) for a in field], lag_ratio=0.02), FadeIn(defs[1], shift=LEFT * 0.2),
                      Indicate(ks[5], color=COOL), run_time=2.0)

        a_eq = MathTex(r"A = \mathbf{L}\cdot\mathbf{p} - p_t", font_size=44)
        dx = MathTex(r"\frac{d\mathbf{x}}{d\lambda} = \mathbf{p} - f A\,\mathbf{L}", font_size=46)
        dp = MathTex(r"\frac{d\mathbf{p}}{d\lambda} = \tfrac12 A^2\,", r"\nabla f", r"+ f A\,\nabla(\mathbf{L}\cdot\mathbf{p})", font_size=46)
        result = VGroup(a_eq, dx, dp).arrange(DOWN, buff=0.6, aligned_edge=LEFT).move_to([-2.9, -1.0, 0])
        notes = VGroup(
            T("how much of p points away from\nthe hole, plus the photon's energy", 22, MUTED, line_spacing=0.8),
            T("rule 1: move along p,\nnudged by gravity", 22, MUTED, line_spacing=0.8),
            T("rule 2: gravity turns\nthe momentum", 22, MUTED, line_spacing=0.8),
        )
        for n, eq in zip(notes, result):
            n.scale(0.92).move_to([4.3, eq.get_center()[1], 0]).align_to([1.7, 0, 0], LEFT)
        with self.voice("Now we plug that into H and work out the slopes. That's a full page of calculus, and I'm "
                        "going to save you from it. Here's the result."):
            self.play(FadeOut(hole), FadeOut(field), FadeOut(defs), run_time=0.6)
            self.play(Write(result), run_time=2.5)
        with self.voice("First, a little helper called A. L dot p is a dot product: how much of the momentum points "
                        "away from the hole. And p t is the photon's energy. That one never changes."):
            self.play(Indicate(a_eq, color=GOLD, scale_factor=1.08), FadeIn(notes[0]), run_time=1.5)
        with self.voice("Rule one. The light moves along its momentum, with a small nudge along L from gravity."):
            self.play(Indicate(dx, color=GOLD, scale_factor=1.08), FadeIn(notes[1]), run_time=1.5)
        with self.voice("Rule two. Gravity turns the momentum. And that, right there, is what bends the ray."):
            self.play(Indicate(dp, color=GOLD, scale_factor=1.08), FadeIn(notes[2]), run_time=1.5)
        grad = MathTex(r"\nabla f", r"= -\frac{2M}{r^2}\,\hat{\mathbf{n}}", font_size=44, color=GOLD).move_to([3.9, -2.3, 0])
        grad_note = T("inverse square, like Newton", 22, GOLD).next_to(grad, DOWN, buff=0.25)
        with self.voice("See that upside-down triangle? It's called a gradient. It's just an arrow pointing in the "
                        "direction where something grows fastest."):
            self.play(FadeOut(notes), dp[1].animate.set_color(GOLD), run_time=0.8)
            self.play(Circumscribe(dp[1], color=GOLD, buff=0.08), run_time=1.5)
        with self.voice("And the gradient of f comes out as two M over r squared, pointing at the hole. An inverse-"
                        "square pull. Sound familiar? Newton's gravity was hiding in there the whole time."):
            self.play(Write(grad), run_time=1.5)
            self.play(FadeIn(grad_note), run_time=0.6)
        frame = SurroundingRectangle(VGroup(dx, dp), color=GOLD, buff=0.3, corner_radius=0.15)
        with self.voice("So this is what we've got: two short vector equations, in ordinary x, y, z, and nothing in "
                        "them blows up at the horizon. These are the equations we're going to code."):
            self.play(Create(frame), run_time=1.2)
        self.clear()


class E1_05_Next(Video):
    def construct(self):
        self.tag("Where we are")
        rule1 = MathTex(r"\frac{d\mathbf{x}}{d\lambda} = \mathbf{p} - f A\,\mathbf{L}", font_size=54)
        rule2 = MathTex(r"\frac{d\mathbf{p}}{d\lambda} = \tfrac12 A^2\,\nabla f + f A\,\nabla(\mathbf{L}\cdot\mathbf{p})", font_size=54)
        rules = VGroup(rule1, rule2).arrange(DOWN, buff=0.7).move_to(UP * 0.4)
        frame = SurroundingRectangle(rules, color=GOLD, buff=0.35, corner_radius=0.15)
        with self.voice("So, that's the physics. Light takes the straightest path through bent space, and we've "
                        "boiled that down to two rules a computer can step through."):
            self.play(Write(rules), run_time=2.0)
            self.play(Create(frame), run_time=0.8)
        things = VGroup(T("the shadow", 28, weight=SEMIBOLD), T("the halo", 28, weight=SEMIBOLD),
                        T("the glowing disk", 28, weight=SEMIBOLD)).arrange(RIGHT, buff=1.0).to_edge(DOWN, buff=1.0)
        with self.voice("And here's the cool part: everything you'll see from now on, the shadow, the halo, the "
                        "glowing disk, all of it comes out of these two equations."):
            self.play(LaggedStart(*[FadeIn(x, shift=UP * 0.2) for x in things], lag_ratio=0.5), run_time=2.0)
        self.clear(0.5)
        nxt = ImageMobject(str(ASSETS / "stage1.jpg")).scale_to_fit_height(5.4).move_to(DOWN * 0.4)
        title = T("Next: bending light in code", 40, weight=BOLD).to_edge(UP, buff=0.5)
        with self.voice("Next episode, we turn them into real code. About two hundred lines of C plus plus, and your"
                        " first steps with OpenGL. See you there."):
            self.play(FadeIn(title), run_time=0.6)
            self.play(FadeIn(nxt), run_time=1.0)
        self.wait(1.0)
        self.play(FadeOut(nxt), FadeOut(title), run_time=1.0)
