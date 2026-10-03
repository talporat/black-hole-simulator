"""Episode 2: bending light in 2D.

The two rules from episode 1 become a first program (stages/01_rays_2d) that
traces rays on the CPU and draws them with OpenGL.
"""
from common import *

STAGE = "stages/01_rays_2d/main.cpp"


class E2_01_Recap(Video):
    def construct(self):
        rule1 = MathTex(r"\frac{d\mathbf{x}}{d\lambda} = \mathbf{p} - f A\,\mathbf{L}", font_size=54)
        rule2 = MathTex(r"\frac{d\mathbf{p}}{d\lambda} = \tfrac12 A^2\,\nabla f + f A\,\nabla(\mathbf{L}\cdot\mathbf{p})", font_size=54)
        rules = VGroup(rule1, rule2).arrange(DOWN, buff=0.7)
        frame = SurroundingRectangle(rules, color=GOLD, buff=0.35, corner_radius=0.15)
        with self.voice("Welcome back! Last time, we worked out why light bends near a black hole, and boiled it all"
                        " down to these two rules."):
            self.play(Write(rules), run_time=2.0)
            self.play(Create(frame), run_time=0.8)
        clip = Footage("stage1").scale_to_fit_height(config.frame_height)
        shade = Rectangle(width=15, height=9, stroke_width=0, fill_color=BLACK, fill_opacity=0.65)
        number = T("EPISODE 2", 26, ACCENT, weight=BOLD)
        title = T("Bending light in 2D", 64, weight=BOLD)
        promise = T("Today: about 200 lines of C++ that bend light around a black hole", 28, GOLD, weight=SEMIBOLD)
        card = VGroup(number, title, promise).arrange(DOWN, buff=0.4)
        with self.voice("Today, we turn them into code. By the end of this video, you'll have about two hundred "
                        "lines of C plus plus that bend light the way Einstein says it should, and you'll have drawn"
                        " it with OpenGL."):
            self.play(FadeOut(rules), FadeOut(frame), run_time=0.5)
            self.play(FadeIn(clip), FadeIn(shade), FadeIn(number), Write(title), run_time=1.5)
            self.play(FadeIn(promise, shift=UP * 0.2), run_time=0.6)
        self.play(FadeOut(card), FadeOut(shade), FadeOut(clip), run_time=0.8)
        self.remove(clip)


class E2_02_Plan(Video):
    def construct(self):
        self.tag("The plan")
        cpu = card("the processor\n\nfollows each ray\nwith the two rules", COOL)
        mid = card("a list of points\nfor every ray", INK)
        gpu = card("the graphics card\n\nconnects the points\ninto lines", GOLD)
        row, arrows = flow(cpu, mid, gpu)
        VGroup(row, arrows).move_to(UP * 0.8)
        with self.voice("Alright, enough theory. Let's turn those two rules into a real program. Stage one is simple"
                        " on purpose: a flat picture of light rays flying past a black hole."):
            pass
        with self.voice("The program has two halves. Half one is physics. For every ray, the processor runs our two "
                        "rules, step after step, and writes down where the ray went."):
            self.play(FadeIn(cpu, shift=UP * 0.2), run_time=0.8)
            self.play(GrowArrow(arrows[0]), FadeIn(mid), run_time=0.8)
        with self.voice("Half two is drawing. We hand those points to the graphics card and say: connect the dots. "
                        "And for that, we use OpenGL."):
            self.play(GrowArrow(arrows[1]), FadeIn(gpu, shift=UP * 0.2), run_time=0.8)

        opengl = T("OpenGL", 40, GOLD, weight=BOLD)
        dots = VGroup(*[Dot([x, y, 0], radius=0.07, color=INK) for x, y in [(-0.5, 0.2), (0, -0.2), (0.5, 0.25)]])
        line = VMobject(stroke_color=INK, stroke_width=4).set_points_as_corners([[-0.6, -0.2, 0], [-0.1, 0.25, 0], [0.6, -0.1, 0]])
        tri = Polygon([-0.5, -0.3, 0], [0.5, -0.3, 0], [0, 0.4, 0], color=INK, stroke_width=4, fill_color=INK, fill_opacity=0.25)
        shapes = VGroup(VGroup(dots, T("points", 22, MUTED)).arrange(DOWN, buff=0.3),
                        VGroup(line, T("lines", 22, MUTED)).arrange(DOWN, buff=0.3),
                        VGroup(tri, T("triangles", 22, MUTED)).arrange(DOWN, buff=0.3)).arrange(RIGHT, buff=1.2)
        VGroup(opengl, shapes).arrange(RIGHT, buff=1.2).move_to(DOWN * 2.0)
        with self.voice("So what is OpenGL? It's a standard way for your program to talk to the graphics card. And "
                        "honestly? All it can draw is points, lines and triangles. That's it. Every game you've ever"
                        " played is built out of those."):
            self.play(FadeIn(opengl), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(s, shift=UP * 0.2) for s in shapes], lag_ratio=0.5), run_time=2.5)
        with self.voice("We're writing this in C plus plus. One file, about two hundred lines. Physics first."):
            self.play(Indicate(cpu, color=COOL, scale_factor=1.05), run_time=1.5)
        self.clear()


class E2_03_CodePhysics(Video):
    def construct(self):
        self.tag("Stage 1: the physics")
        vec = CodePanel(excerpt(STAGE, ("struct Vec2", "float length")), "stages/01_rays_2d/main.cpp",
                        language="cpp", max_width=11.0)
        vec.move_to(ORIGIN)
        with self.voice("We start tiny: a two-dimensional vector. An x and a y. We can add them, subtract them, "
                        "scale them, take a dot product, and get the length. That's all the vector maths we need."):
            self.play(FadeIn(vec, shift=UP * 0.3), run_time=0.8)
            self.play(vec.focus("float dot", "float length"), run_time=0.8)
        self.play(FadeOut(vec), run_time=0.5)

        # derivatives(): every line next to the piece of maths it implements.
        panel = CodePanel(excerpt(STAGE, ("void derivatives", "}")), "stages/01_rays_2d/main.cpp",
                          language="cpp", max_width=8.3)
        panel.to_edge(LEFT, buff=0.3).shift(DOWN * 0.1)
        eqs = VGroup(
            MathTex(r"f = \frac{2M}{r}", font_size=36),
            MathTex(r"\nabla f = -\frac{2M}{r^2}\,\mathbf{L}", font_size=36),
            MathTex(r"A = \mathbf{L}\cdot\mathbf{p} - p_t", font_size=36),
            MathTex(r"\frac{d\mathbf{x}}{d\lambda} = \mathbf{p} - f A\,\mathbf{L}", font_size=36),
            MathTex(r"\frac{d\mathbf{p}}{d\lambda} = \tfrac12 A^2\,\nabla f + f A\,\nabla(\mathbf{L}\cdot\mathbf{p})", font_size=32),
        ).arrange(DOWN, buff=0.38).move_to([4.45, -1.25, 0])
        centre = np.array([3.3, 2.45, 0])
        hole = black_hole(0.18, centre)
        point = centre + np.array([1.7, 0.7, 0])
        away = (point - centre) / np.linalg.norm(point - centre)
        radius = DashedLine(centre, point, color=MUTED, stroke_width=2)
        r_label = MathTex("r", font_size=32, color=MUTED).next_to(radius.get_center(), UP, buff=0.1)
        x_dot = Dot(point, radius=0.08, color=INK)
        x_label = MathTex(r"\mathbf{x}", font_size=32).next_to(point, DOWN, buff=0.15)
        l_arrow = Arrow(point, point + 0.9 * away, buff=0, color=COOL, stroke_width=5)
        l_label = MathTex(r"\mathbf{L}", font_size=32, color=COOL).next_to(l_arrow.get_end(), UP, buff=0.08)

        def link(eq):
            return Line(panel.bar.get_right(), eq.get_left() + LEFT * 0.12, color=GOLD, stroke_width=2)

        with self.voice("And this is the heart of the whole thing: a function called derivatives. You give it where "
                        "the ray is, x, and its momentum, p. It tells you how fast each one is changing."):
            self.play(FadeIn(panel, shift=UP * 0.3), run_time=0.8)
            self.play(panel.focus(1), run_time=0.6)
        with self.voice("r is the distance from the hole. Easy."):
            self.play(panel.focus("float r"), FadeIn(hole), FadeIn(x_dot), FadeIn(x_label), Create(radius),
                      FadeIn(r_label), run_time=1.0)
        with self.voice("L is our arrow of length one, pointing away from the hole. That's just the position divided"
                        " by its own length."):
            self.play(panel.focus("Vec2 L"), GrowArrow(l_arrow), FadeIn(l_label), run_time=1.0)
        with self.voice("f is how strong gravity is here: two M over r."):
            self.play(panel.focus("float f"), run_time=0.5)
            wire = link(eqs[0])
            self.play(Write(eqs[0]), Create(wire), run_time=1.0)
        with self.voice("Then the two gradients that rule two needs. The first one is our inverse-square pull."):
            self.play(FadeOut(wire), panel.focus("Vec2 gradF", "Vec2 gradLp"), run_time=0.5)
            wire = link(eqs[1])
            self.play(Write(eqs[1]), Create(wire), run_time=1.0)
        with self.voice("A is the helper: L dot p, minus p t."):
            self.play(FadeOut(wire), panel.focus("float A"), run_time=0.5)
            wire = link(eqs[2])
            self.play(Write(eqs[2]), Create(wire), run_time=1.0)
        with self.voice("And now, the two rules, exactly like they were on the board. Rule one: how the position "
                        "changes."):
            self.play(FadeOut(wire), panel.focus("dx = p"), run_time=0.5)
            wire = link(eqs[3])
            self.play(Write(eqs[3]), Create(wire), run_time=1.2)
        with self.voice("Rule two: how the momentum changes. Seriously, compare them term by term. The code is the "
                        "equation."):
            self.play(FadeOut(wire), panel.focus("dp = "), run_time=0.5)
            wire = link(eqs[4])
            self.play(Write(eqs[4]), Create(wire), run_time=1.2)
            self.play(Indicate(eqs[4], color=GOLD, scale_factor=1.05), run_time=1.2)
        self.clear()

        # photonEnergy(): H = 0 is a quadratic in p_t.
        self.tag("Stage 1: the physics")
        energy = CodePanel(excerpt(STAGE, ("float photonEnergy", "}")), "stages/01_rays_2d/main.cpp",
                           language="cpp", max_width=9.2)
        energy.to_edge(DOWN, buff=0.35)
        h_eq = MathTex(r"H = 0:", r"\quad", r"-(1+f)", r"\,p_t^2 +", r"2f\,(\mathbf{L}\cdot\mathbf{p})", r"\,p_t +",
                       r"|\mathbf{p}|^2 - f\,(\mathbf{L}\cdot\mathbf{p})^2", r"= 0", font_size=40).move_to(UP * 2.6)
        names = VGroup(*[VGroup(Brace(h_eq[i], DOWN, color=GOLD), MathTex(n, font_size=36, color=GOLD))
                         for i, n in [(2, "a"), (4, "b"), (6, "c")]])
        for brace, name in names:
            name.next_to(brace, DOWN, buff=0.08)
        root = MathTex(r"p_t = \frac{-b + \sqrt{b^2 - 4ac}}{2a}", font_size=40).move_to(UP * 0.75)
        with self.voice("We're missing one thing though: p t. Remember, for light, H has to be zero. Write that out "
                        "and, surprise, it's a quadratic equation, with p t as the unknown."):
            self.play(Write(h_eq), run_time=2.5)
            self.play(LaggedStart(*[FadeIn(n) for n in names], lag_ratio=0.3), run_time=1.5)
        with self.voice("And you already know how to solve a quadratic. It's the formula from school."):
            self.play(Write(root), run_time=1.5)
        with self.voice("So that's this function. It works out a, b and c, and returns the root. And now our ray "
                        "really is a ray of light."):
            self.play(FadeIn(energy, shift=UP * 0.3), run_time=0.8)
            self.play(energy.focus("float a =", "float c ="), run_time=0.8)
            self.wait(1.0)
            self.play(energy.focus("return"), run_time=0.8)
        self.clear()

        # rk4Step(): Euler against Runge-Kutta 4.
        self.tag("Stage 1: taking a step")
        scale = 0.27
        origin = np.array([4.5, -0.3, 0])
        start, d = [-8.5, 5.6, 0], [1, 0, 0]
        hole = black_hole(scale, origin)

        def clip(pts):
            keep = (np.abs(pts[:, 0]) < 9.0) & (pts[:, 1] < 8.5) & (pts[:, 1] > -11.5)
            return pts[:max(int(np.argmin(keep)) if not keep.all() else len(pts), 2)]

        h = 0.9
        ref = clip(geo.trace(start, d, r_escape=30, quality=0.1)[0])
        eul = clip(geo.trace(start, d, r_escape=30, fixed_h=h, stepper=geo.euler, max_steps=80)[0])
        rk4 = clip(geo.trace(start, d, r_escape=30, fixed_h=h, max_steps=80)[0])
        ref_path = ray_path(ref, scale, origin, color=INK, width=7).set_stroke(opacity=0.3)
        eul_path = ray_path(eul, scale, origin, color=HOT, width=3)
        rk4_path = ray_path(rk4, scale, origin, color=GOOD, width=3)
        eul_dots = VGroup(*[Dot(q, radius=0.05, color=HOT) for q in to_scene(eul, scale, origin)])
        rk4_dots = VGroup(*[Dot(q, radius=0.05, color=GOOD) for q in to_scene(rk4, scale, origin)])
        legend = VGroup(
            VGroup(Line(ORIGIN, RIGHT * 0.6, color=INK, stroke_width=7, stroke_opacity=0.4), T("true path", 22)).arrange(RIGHT, buff=0.2),
            VGroup(Line(ORIGIN, RIGHT * 0.6, color=HOT, stroke_width=4), T("Euler", 22)).arrange(RIGHT, buff=0.2),
            VGroup(Line(ORIGIN, RIGHT * 0.6, color=GOOD, stroke_width=4), T("Runge-Kutta 4", 22)).arrange(RIGHT, buff=0.2),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to([5.6, 3.1, 0])
        euler_eq = MathTex(r"\text{new} = \text{old} + h \times \text{rate of change}", font_size=40).move_to([-3.0, 0.6, 0])
        with self.voice("Okay. We know how fast x and p are changing, so let's take a step. The obvious way is "
                        "Euler's method. It's what you'd do in a spreadsheet: new value equals old value, plus the "
                        "rate of change, times a step size h."):
            self.play(FadeIn(hole), Create(ref_path), FadeIn(legend[0]), run_time=1.2)
            euler_pic = portrait("euler", "Leonhard Euler", "1707 - 1783").move_to([-3.0, -1.7, 0])
            self.play(Write(euler_eq), FadeIn(euler_pic), run_time=1.5)
        with self.voice("But there's a catch. The rate of change keeps changing during the step. So Euler slowly "
                        "drifts off the true path. And near a black hole, that error grows fast."):
            self.play(Create(eul_path), LaggedStart(*[FadeIn(q, scale=2) for q in eul_dots], lag_ratio=0.3),
                      FadeIn(legend[1]), run_time=4.0, rate_func=linear)
        rk = CodePanel(excerpt(STAGE, ("void rk4Step", "}")), "stages/01_rays_2d/main.cpp", language="cpp", max_width=8.2)
        rk.to_edge(LEFT, buff=0.3).shift(DOWN * 0.1)
        with self.voice("So we use something much better: Runge-Kutta four. It measures the rate of change four "
                        "times: once at the start, twice in the middle, and once at the end."):
            self.play(FadeOut(euler_eq), FadeOut(euler_pic), FadeIn(rk, shift=UP * 0.3), run_time=0.9)
            self.play(rk.focus("derivatives(x, p, pt, k1x"), run_time=0.7)
            self.play(rk.focus("k2x, k2p);", "k3x, k3p);"), run_time=0.9)
            self.play(rk.focus("k4x, k4p);"), run_time=0.7)
        with self.voice("Then it averages the four, with the middle ones counting double."):
            self.play(rk.focus("x = x +", "p = p +"), run_time=0.7)
        with self.voice("Same step size. Same number of steps. And look at that: right on the true path."):
            self.play(Create(rk4_path), LaggedStart(*[FadeIn(q, scale=2) for q in rk4_dots], lag_ratio=0.3),
                      FadeIn(legend[2]), run_time=3.5, rate_func=linear)
        self.clear()

        # traceRay(): the loop, with a ray stepping alongside.
        self.tag("Stage 1: following a ray")
        trace = CodePanel(excerpt(STAGE, ("Ray traceRay", "}")), "stages/01_rays_2d/main.cpp", language="cpp", max_width=8.2)
        trace.to_edge(LEFT, buff=0.3).shift(DOWN * 0.1)
        scale = 0.21
        origin = np.array([4.9, -0.2, 0])
        box = (1.9, 7.05, -3.6, 3.6)
        hole = black_hole(scale, origin)
        fallen = geo.trace([-16, 3.5, 0], [1, 0, 0], r_escape=30, quality=0.5)[0]
        free = geo.trace([-15, 7.5, 0], [1, 0, 0], r_escape=40, quality=0.5)[0]
        fall_line, fall_dots = step_dots(fallen, scale, origin, HOT, box)
        free_line, free_dots = step_dots(free, scale, origin, COOL, box)
        with self.voice("Last one: trace ray, which puts everything together. It starts at a point, heading in some "
                        "direction. The direction is the momentum, and photon energy gives us p t."):
            self.play(FadeIn(trace, shift=UP * 0.3), FadeIn(hole), run_time=0.8)
            self.play(trace.focus("Vec2 x = start", "float pt"), run_time=0.7)
        with self.voice("Then it loops. And every time around, it asks: how far is this ray from the hole?"):
            self.play(trace.focus("float r = length"), run_time=0.6)
        with self.voice("Closer than two M? It's crossed the horizon. Mark it as captured. Done."):
            self.play(trace.focus("if (r < 2.0f"), run_time=0.6)
            self.play(Create(fall_line), LaggedStart(*[FadeIn(q) for q in fall_dots], lag_ratio=0.3), run_time=3.0, rate_func=linear)
        with self.voice("Really far away? It's gone. Done."):
            self.play(trace.focus("if (r > 60.0f"), VGroup(fall_line, fall_dots).animate.set_opacity(0.3), run_time=0.6)
        with self.voice("Otherwise, take one Runge-Kutta step and save the new point. And check out the step size: "
                        "it's proportional to r. Small, careful steps near the hole, and big strides far away."):
            self.play(trace.focus("rk4Step(x, p, pt", "ray.points.push_back(x);"), run_time=0.6)
            self.play(Create(free_line), LaggedStart(*[FadeIn(q, scale=2) for q in free_dots], lag_ratio=0.3),
                      run_time=5.0, rate_func=linear)
        with self.voice("And what comes back is a list of points: the path of one ray of light."):
            self.play(trace.focus("return ray"), run_time=0.6)
        self.clear()


class E2_04_CodeOpenGL(Video):
    def construct(self):
        self.tag("Stage 1: drawing with OpenGL")
        window = CodePanel(excerpt(STAGE, ("glfwInit();", "glfwMakeContextCurrent(window);"), skip=("capture.windowHints",)),
                           "stages/01_rays_2d/main.cpp", language="cpp", max_width=11.5)
        window.move_to(DOWN * 0.1)
        with self.voice("Now the fun half: drawing. Step one, we need a window. OpenGL can't open one on its own, so"
                        " we use a small library called G L F W."):
            self.play(FadeIn(window, shift=UP * 0.3), run_time=0.8)
            self.play(window.focus("glfwInit"), run_time=0.6)
        with self.voice("These lines ask for OpenGL version four point one, in its modern flavour, called the core "
                        "profile."):
            self.play(window.focus("GLFW_CONTEXT_VERSION_MAJOR", "GLFW_SAMPLES"), run_time=0.7)
        with self.voice("Create window opens the window. And make context current says: from now on, OpenGL commands"
                        " draw into this one."):
            self.play(window.focus("GLFWwindow* window", "glfwMakeContextCurrent"), run_time=0.7)
        self.play(FadeOut(window), run_time=0.5)

        # The two shaders.
        stages = [card("our points", INK, 22), card("vertex shader\n\nwhere on the\nscreen?", COOL, 22),
                  card("connect\ninto lines", INK, 22), card("fragment shader\n\nwhat colour?", GOLD, 22),
                  card("pixels", INK, 22)]
        row, arrows = flow(*stages, buff=0.5)
        VGroup(row, arrows).move_to(UP * 0.3)
        with self.voice("Step two. The graphics card has no idea what to do with our points, until we hand it two "
                        "small programs called shaders. They're written in a language that looks a lot like C, "
                        "called G L S L."):
            self.play(FadeIn(stages[0]), run_time=0.6)
            self.play(LaggedStart(*[AnimationGroup(GrowArrow(a), FadeIn(s)) for a, s in zip(arrows, stages[1:])],
                                  lag_ratio=0.4), run_time=3.0)
        with self.voice("The vertex shader runs once for every point, and answers one question: where on the screen "
                        "does this point go?"):
            self.play(Indicate(stages[1], color=COOL, scale_factor=1.08), run_time=1.5)
        with self.voice("The fragment shader runs once for every pixel a line covers, and answers: what colour is "
                        "it?"):
            self.play(Indicate(stages[3], color=GOLD, scale_factor=1.08), run_time=1.5)
        self.play(FadeOut(row), FadeOut(arrows), run_time=0.5)

        vert = CodePanel(excerpt(STAGE, ("layout(location = 0)", "}")), "vertex shader", max_width=8.2)
        vert.to_edge(LEFT, buff=0.3).shift(UP * 0.9)
        world = Rectangle(width=3.6, height=2.0, color=COOL, stroke_width=3).move_to([4.6, 2.0, 0])
        world_label = T("our world: 52 M wide", 20, COOL).next_to(world, UP, buff=0.1)
        ray = VMobject(stroke_color=GOLD, stroke_width=3).set_points_smoothly(
            [world.get_center() + np.array(q) for q in [(-1.8, 0.5, 0), (-0.5, 0.45, 0), (0.3, 0.1, 0), (0.9, -0.95, 0)]])
        hole = Dot(world.get_center(), radius=0.14, color=BLACK).set_stroke(ACCENT, 2)
        screen = Rectangle(width=3.6, height=2.0, color=INK, stroke_width=3).move_to([4.6, -1.6, 0])
        screen_label = T("OpenGL's screen", 20, INK).next_to(screen, DOWN, buff=0.1)
        corners = VGroup(MathTex("-1", font_size=26).next_to(screen.get_left(), LEFT, buff=0.1),
                         MathTex("+1", font_size=26).next_to(screen.get_right(), RIGHT, buff=0.1),
                         MathTex("+1", font_size=26).next_to(screen.get_top(), UP, buff=0.05).shift(RIGHT * 1.4),
                         MathTex("-1", font_size=26).next_to(screen.get_bottom(), UP, buff=0.05).shift(RIGHT * 1.4))
        mapping = Arrow(world.get_bottom(), screen.get_top(), buff=0.35, color=MUTED, stroke_width=4)
        map_label = MathTex(r"\div\ \text{uViewSize}", font_size=30).next_to(mapping, RIGHT, buff=0.15)
        with self.voice("Here's our vertex shader. Its input, a pos, is one point of a ray, measured in units of M."):
            self.play(FadeIn(vert, shift=UP * 0.3), run_time=0.8)
            self.play(vert.focus("in vec2 aPos"), Create(world), FadeIn(world_label), Create(ray), FadeIn(hole), run_time=1.2)
        with self.voice("Now, OpenGL's screen always goes from minus one to plus one, across and up. So the shader "
                        "just divides by the size of the area we want to see. That's literally the whole job."):
            self.play(Create(screen), FadeIn(screen_label), FadeIn(corners), run_time=1.0)
            self.play(vert.focus("gl_Position"), GrowArrow(mapping), FadeIn(map_label), run_time=1.0)
            self.play(TransformFromCopy(VGroup(ray, hole), VGroup(ray, hole).copy().move_to(screen)), run_time=1.5)
        with self.voice("u view size is what's called a uniform: a value our C plus plus program sets, and it's the "
                        "same for every point."):
            self.play(vert.focus("uniform vec2 uViewSize"), run_time=0.7)
        frag = CodePanel(excerpt(STAGE, ("uniform vec3 uColor;", "}")), "fragment shader", max_width=8.2)
        frag.next_to(vert, DOWN, buff=0.7, aligned_edge=LEFT)
        with self.voice("The fragment shader is even shorter. Every pixel on the line gets the colour stored in "
                        "another uniform, u color."):
            self.play(vert.unfocus(), FadeIn(frag, shift=UP * 0.3), run_time=0.8)
            self.play(frag.focus("fragColor = vec4"), run_time=0.7)
        self.clear()

        self.tag("Stage 1: drawing with OpenGL")
        compiler = CodePanel(excerpt(STAGE, ("GLuint compileShader", "}"), ("GLuint makeProgram", "}")),
                             "stages/01_rays_2d/main.cpp", language="cpp", max_width=11.5, max_height=6.6)
        compiler.move_to(DOWN * 0.25)
        with self.voice("Fun fact: shaders get compiled while your program is running. Compile shader hands the "
                        "source text to OpenGL, and compiles it."):
            self.play(FadeIn(compiler, shift=UP * 0.3), run_time=0.8)
            self.play(compiler.focus("glCreateShader", "glCompileShader"), run_time=0.7)
        with self.voice("Then it checks if that worked. If we made a typo, it prints the compiler's message. Trust "
                        "me, you want this. Without it, a broken shader just gives you a black window, and zero "
                        "clues."):
            self.play(compiler.focus("GLint ok", "std::fprintf"), run_time=0.7)
        with self.voice("Make program compiles both shaders and links them into one program we can draw with."):
            self.play(compiler.focus("GLuint program = glCreateProgram", "glLinkProgram"), run_time=0.7)
        self.play(FadeOut(compiler), run_time=0.5)

        buffers = CodePanel(excerpt(STAGE, ("GLuint vao, vbo;", "glVertexAttribPointer")), "stages/01_rays_2d/main.cpp",
                            language="cpp", max_width=11.5)
        buffers.move_to(UP * 1.4)
        cells = VGroup()
        for i, name in enumerate(["x_0", "y_0", "x_1", "y_1", "x_2", "y_2", "x_3", "y_3"]):
            cell = VGroup(Square(0.85, color=COOL if (i // 2) % 2 == 0 else GOOD, stroke_width=3,
                                 fill_color=PANEL, fill_opacity=1), MathTex(name, font_size=32))
            cells.add(cell)
        cells.arrange(RIGHT, buff=0).move_to(DOWN * 2.0)
        point_braces = VGroup(*[VGroup(Brace(cells[2 * i:2 * i + 2], DOWN, color=MUTED),
                                       T(f"point {i}", 20, MUTED)).arrange(DOWN, buff=0.05) for i in range(4)])
        for i, pb in enumerate(point_braces):
            pb.next_to(cells[2 * i:2 * i + 2], DOWN, buff=0.1)
        memory = T("a vertex buffer: memory on the graphics card", 22, MUTED).next_to(cells, UP, buff=0.2)
        with self.voice("Step three: getting our points onto the graphics card. A vertex buffer is a chunk of the "
                        "card's memory that holds them."):
            self.play(FadeIn(buffers, shift=UP * 0.3), run_time=0.8)
            self.play(buffers.focus("glGenBuffers", "glBindBuffer"), FadeIn(memory),
                      LaggedStart(*[FadeIn(c) for c in cells], lag_ratio=0.1), run_time=1.5)
        with self.voice("But it's just a row of numbers. So we also need a vertex array, which remembers how to read"
                        " them. Here we're saying: attribute zero, our a pos, is two floats per point."):
            self.play(buffers.focus("glEnableVertexAttribArray", "glVertexAttribPointer"), run_time=0.7)
            self.play(LaggedStart(*[FadeIn(b) for b in point_braces], lag_ratio=0.3), run_time=1.5)
        self.clear()

        self.tag("Stage 1: drawing with OpenGL")
        drawing = CodePanel(excerpt(STAGE, ("void draw(", "}")), "stages/01_rays_2d/main.cpp", language="cpp", max_width=8.6)
        drawing.to_edge(LEFT, buff=0.3).shift(UP * 0.3)
        pts = [np.array([3.2, 1.9, 0]), np.array([4.3, 2.5, 0]), np.array([5.3, 2.0, 0]), np.array([6.2, 2.6, 0])]
        strip_dots = VGroup(*[Dot(q, radius=0.08, color=INK) for q in pts])
        strip = VMobject(stroke_color=COOL, stroke_width=4).set_points_as_corners(pts)
        strip_label = T("GL_LINE_STRIP", 20, COOL, font="Menlo").move_to([4.7, 1.3, 0])
        fan_c = np.array([4.7, -1.5, 0])
        fan_pts = [fan_c + 1.0 * np.array([np.cos(a), np.sin(a), 0]) for a in np.linspace(0, TAU, 9)]
        fan = VGroup(*[Polygon(fan_c, fan_pts[i], fan_pts[i + 1], color=ACCENT, stroke_width=2, fill_color=ACCENT,
                               fill_opacity=0.25) for i in range(8)])
        fan_label = T("GL_TRIANGLE_FAN", 20, ACCENT, font="Menlo").move_to([4.7, -2.9, 0])
        with self.voice("With all that in place, drawing one ray is just three calls. Buffer data copies the ray's "
                        "points into the vertex buffer."):
            self.play(FadeIn(drawing, shift=UP * 0.3), run_time=0.8)
            self.play(drawing.focus("glBufferData", "points.data()"), FadeIn(strip_dots), run_time=0.8)
        with self.voice("Uniform three f sets the colour for the fragment shader."):
            self.play(drawing.focus("glUniform3f"), run_time=0.7)
        with self.voice("And draw arrays says: go, draw them. The mode says how to connect the points. Line strip "
                        "joins each point to the next one. And that's a ray."):
            self.play(drawing.focus("glDrawArrays"), run_time=0.7)
            self.play(Create(strip), FadeIn(strip_label), run_time=1.5)
        with self.voice("Triangle fan makes a filled shape out of triangles that all share one corner. That's how we"
                        " draw the black disc of the hole."):
            self.play(LaggedStart(*[FadeIn(t) for t in fan], lag_ratio=0.15), FadeIn(fan_label), run_time=2.0)
        self.clear()

        self.tag("Stage 1: drawing with OpenGL")
        loop = CodePanel(excerpt(STAGE, ("while (!glfwWindowShouldClose(window)) {", "else              draw("),
                                 ("draw(program, GL_TRIANGLE_FAN", "glfwPollEvents();"),
                                 skip=("capture.save", "int width, height", "glfwGetFramebufferSize", "glViewport")),
                         "stages/01_rays_2d/main.cpp", language="cpp", max_width=12.6, max_height=6.4)
        loop.move_to(DOWN * 0.25)
        with self.voice("Last piece: the main loop. It runs once per frame, until you close the window."):
            self.play(FadeIn(loop, shift=UP * 0.3), run_time=0.8)
            self.play(loop.focus(1), run_time=0.6)
        with self.voice("Clear the screen to a dark colour. Switch on our shader program, and tell it how much of "
                        "the world to show."):
            self.play(loop.focus("glClearColor", "glUniform2f"), run_time=0.7)
        with self.voice("Then draw every ray we traced: red if it got captured, blue if it escaped."):
            self.play(loop.focus("for (const Ray& ray", "else  "), run_time=0.7)
        with self.voice("Draw the hole on top. Swap buffers puts the finished frame on screen. And poll events lets "
                        "the window react to your mouse and keyboard."):
            self.play(loop.focus("draw(program, GL_TRIANGLE_FAN", "glfwPollEvents"), run_time=0.7)
        self.clear()


class E2_05_Result(Video):
    def construct(self):
        clip = Footage("stage1").scale_to_fit_height(config.frame_height)
        label = T("stage 1, running", 22, MUTED).to_corner(UL, buff=0.35)
        back = BackgroundRectangle(label, color=BG, fill_opacity=0.8, buff=0.12)
        self.play(FadeIn(clip), run_time=0.8)
        self.add(back, label)
        with self.voice("And here it is, running! Every curve you're looking at is one ray of light, traced with our"
                        " two rules."):
            pass
        with self.voice("Rays far from the hole bend just a little. The red ones got too close, and crossed the "
                        "horizon."):
            pass
        with self.voice("The gold ray follows the mouse. Now watch what happens as it moves toward the centre."):
            pass
        with self.voice("Whoa. Right at the edge, it wraps all the way around the hole before it escapes. It's "
                        "skimming the photon sphere at three M. That's the grey circle."):
            pass
        self.play(FadeOut(clip), FadeOut(back), FadeOut(label), run_time=0.8)
        self.remove(clip)

        self.tag("What the rays tell us")
        scale = 0.3
        origin = np.array([0.0, -0.5, 0])
        box = (-7.2, 7.2, -3.8, 3.0)
        hole = black_hole(scale, origin)
        rays = VGroup()
        for y in np.arange(-10.5, 10.6, 1.5):
            pts, fate = geo.trace([-40, y, 0], [1, 0, 0], r_escape=60)
            rays.add(ray_path(pts, scale, origin, color=HOT if fate == "captured" else COOL, width=2.5, box=box))
        rays.set_stroke(opacity=0.25)
        lo, hi = 5.0, 5.4
        for _ in range(30):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if geo.trace([-40, mid, 0], [1, 0, 0], r_escape=60)[1] == "captured" else (lo, mid)
        pts, _ = geo.trace([-40, hi + 2e-4, 0], [1, 0, 0], r_escape=60, quality=0.15)
        critical = glow(ray_path(pts, scale, origin, color=GOLD, width=4, box=box))
        ring = DashedVMobject(Circle(radius=3 * scale, color=INK, stroke_width=2).move_to(origin), num_dashes=30)
        with self.voice("Let's zoom in on that boundary. There's one exact aim where a ray doesn't fall in, and "
                        "doesn't fly past either. It just circles the photon sphere."):
            self.play(FadeIn(hole), FadeIn(rays), run_time=0.8)
            self.play(Create(critical, lag_ratio=0), run_time=4.0, rate_func=linear)
            self.play(Create(ring), run_time=0.6)
        x = -6.2
        axis = DashedLine([-7.2, origin[1], 0], [origin[0], origin[1], 0], color=MUTED, stroke_width=2)
        b_arrow = DoubleArrow([x, origin[1], 0], [x, origin[1] + geo.B_CRIT * scale, 0], buff=0, color=GOLD,
                              stroke_width=4, tip_length=0.2)
        b_label = MathTex(r"b_c = 3\sqrt{3}\,M \approx 5.2\,M", font_size=44, color=GOLD).move_to([3.6, 3.3, 0])
        b_label.add_to_back(BackgroundRectangle(b_label, color=BG, fill_opacity=0.85, buff=0.12))
        with self.voice("That ray starts out aimed off-centre by three times the square root of three, times M. "
                        "About five point two M."):
            self.play(Create(axis), GrowArrow(b_arrow), run_time=1.0)
            self.play(Write(b_label), run_time=1.2)
        disc = DoubleArrow([x - 0.5, origin[1] - geo.B_CRIT * scale, 0], [x - 0.5, origin[1] + geo.B_CRIT * scale, 0],
                           buff=0, color=HOT, stroke_width=4, tip_length=0.2)
        disc_label = T("shadow", 24, HOT, weight=SEMIBOLD).rotate(PI / 2).next_to(disc, LEFT, buff=0.1)
        with self.voice("Anything aimed closer than that is gone. So from far away, the hole blacks out a disc more "
                        "than two and a half times wider than its horizon. That disc is the black hole's shadow."):
            self.play(GrowFromCenter(disc), FadeIn(disc_label), run_time=1.0)
        self.clear()

        nxt = ImageMobject(str(ASSETS / "stage2.jpg")).scale_to_fit_height(5.6).move_to(DOWN * 0.4)
        title = T("Next: a ray tracer in 3D", 40, weight=BOLD).to_edge(UP, buff=0.5)
        with self.voice("So that's the promise kept: a program that bends light correctly, in about two hundred "
                        "lines. But let's be honest, it's a diagram. It's not a picture yet."):
            self.play(FadeIn(title), run_time=0.8)
        with self.voice("In the next episode, we drop a camera into this world, and trace one ray for every pixel, "
                        "on the graphics card. That's where it starts to look real. See you there."):
            self.play(FadeIn(nxt), run_time=1.2)
        self.wait(1.0)
        self.play(FadeOut(nxt), FadeOut(title), run_time=1.0)


