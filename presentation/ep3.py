"""Episode 3: a ray tracer in 3D.

The stage-1 physics moves into a fragment shader (stages/02_raytracer_3d),
with a camera, one ray per pixel, and a sky to look at.
"""
from common import *

S1 = "stages/01_rays_2d/main.cpp"
MAIN = "stages/02_raytracer_3d/main.cpp"
FRAG = "stages/02_raytracer_3d/trace.frag"
VERT = "stages/02_raytracer_3d/fullscreen.vert"


class E3_01_Recap(Video):
    def construct(self):
        clip = Footage("stage1").scale_to_fit_height(config.frame_height)
        self.play(FadeIn(clip), run_time=0.8)
        with self.voice("Welcome back! Last time, we worked out the two rules light follows near a black hole, and "
                        "wrote a program that traces rays with them."):
            pass
        shade = Rectangle(width=15, height=9, stroke_width=0, fill_color=BLACK, fill_opacity=0.0)
        number = T("EPISODE 3", 26, ACCENT, weight=BOLD)
        title = T("A ray tracer in 3D", 64, weight=BOLD)
        VGroup(number, title).arrange(DOWN, buff=0.35)
        with self.voice("But all we got was a diagram. Lines on a flat page."):
            self.play(shade.animate.set_fill(opacity=0.65), FadeIn(number), Write(title), run_time=1.5)
        stars = Footage("stage2_stars").scale_to_fit_height(config.frame_height)
        with self.voice("Today we fix that. By the end of this video, you'll be flying a camera around a black hole,"
                        " in real time, and seeing what you'd actually see if you were there."):
            self.play(FadeOut(number), FadeOut(title), FadeOut(shade), FadeIn(stars), run_time=1.2)
            self.remove(clip)
        with self.voice("To pull that off, we need three new things. A camera. A ray of light for every single "
                        "pixel. And a way to run our physics on the graphics card."):
            pass
        self.play(FadeOut(stars), run_time=0.8)


class E3_02_RayTracing(Video):
    def construct(self):
        self.tag("Ray tracing")

        eye = np.array([-5.8, 0.0, 0])
        camera = VGroup(Dot(eye, radius=0.1, color=INK), T("camera", 22, MUTED).next_to(eye, DOWN, buff=0.3).shift(LEFT * 0.45))
        ys = np.linspace(-1.4, 1.4, 9)
        pixels = VGroup(*[
            Square(0.35, stroke_color=MUTED, stroke_width=1.5, fill_color=BG, fill_opacity=1).move_to([-3.8, y, 0])
            for y in ys])
        pixel_label = T("pixels", 22, MUTED).next_to(pixels, UP, buff=0.25)
        centre, radius = np.array([2.8, 0.0, 0]), 1.2
        ball = Circle(radius=radius, stroke_color=COOL, stroke_width=3, fill_color=COOL, fill_opacity=0.3).move_to(centre)

        def straight(y):
            d = np.array([-3.8, y, 0]) - eye
            d /= np.linalg.norm(d)
            oc = eye - centre
            b = np.dot(oc, d)
            disc = b * b - (np.dot(oc, oc) - radius**2)
            t = -b - np.sqrt(disc) if disc > 0 else min(12.6, 2.7 / max(abs(d[1]), 1e-6))
            return Line(eye, eye + t * d, stroke_width=3, color=COOL if disc > 0 else MUTED), disc > 0

        rays, hits = zip(*[straight(y) for y in ys])
        rays = VGroup(*rays)

        with self.voice("So how does a normal ray tracer make a picture? There's a camera, and in front of it, a "
                        "grid of pixels. That's your screen."):
            self.play(FadeIn(camera), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(p, scale=0.6) for p in pixels], lag_ratio=0.08), FadeIn(pixel_label),
                      FadeIn(ball), run_time=1.6)
        with self.voice("For every pixel, we shoot a ray from the camera, through that pixel, and ask: what does it "
                        "hit?"):
            self.play(LaggedStart(*[Create(r) for r in rays], lag_ratio=0.15), run_time=3.2)
            self.play(*[p.animate.set_fill(COOL, 0.9) for p, h in zip(pixels, hits) if h], run_time=0.6)
        with self.voice("Yes, that's backwards from how real light travels. But it's clever: we only bother with the"
                        " rays that actually reach the camera."):
            self.play(*[ShowPassingFlash(r.copy().set_stroke(GOLD, 6).reverse_direction(), time_width=0.4)
                        for r, h in zip(rays, hits) if h], run_time=2.0)

        formula = MathTex(r"\mathbf{x}(\lambda)", "=", r"\mathbf{o}", "+", r"\lambda\,", r"\mathbf{d}", font_size=54)
        formula.move_to([0, 3.3, 0])
        with self.voice("In normal space, light goes in straight lines. So a ray is just a start point plus a "
                        "direction, and hitting a sphere is one quadratic equation. Easy."):
            self.play(Write(formula), run_time=1.5)
            self.play(Indicate(formula[2], color=GOLD), Flash(eye, color=GOLD), run_time=1.0)
            self.play(Indicate(formula[5], color=GOLD), run_time=1.0)

        scale = 0.28
        hole = black_hole(scale, centre)
        bent, fates = [], []
        for y in ys:
            pts, fate = geo.trace((eye - centre) / scale, np.array([-3.8, y, 0]) - eye, r_escape=50)
            bent.append(ray_path(pts, scale, centre, color=HOT if fate == "captured" else MUTED,
                                 box=(-7.0, 7.0, -3.6, 3.6)))
            fates.append(fate)
        with self.voice("Now swap the sphere for a black hole."):
            self.play(FadeOut(formula), ReplacementTransform(ball, hole),
                      *[p.animate.set_fill(BG, 1) for p in pixels], run_time=1.2)
        with self.voice("And the rays bend. Some swing around the back. Some never come out."):
            self.play(*[Transform(r, b) for r, b in zip(rays, bent)], run_time=3.0)
            self.play(*[p.animate.set_fill(BLACK, 1).set_stroke(HOT, 2.5) for p, f in zip(pixels, fates)
                        if f == "captured"], run_time=0.6)
        probe = rays[2]
        with self.voice("There's no neat formula for these paths. To find out where a ray ends up, we have to walk "
                        "along it, one small step at a time."):
            self.play(*[r.animate.set_stroke(opacity=0.25) for r in rays if r is not probe],
                      probe.animate.set_stroke(GOLD, 4), run_time=0.8)
            dots = VGroup(*[Dot(probe.point_from_proportion(a), radius=0.06, color=GOLD) for a in np.linspace(0.02, 0.98, 26)])
            self.play(LaggedStart(*[FadeIn(d, scale=2) for d in dots], lag_ratio=0.25), run_time=3.5)
        with self.voice("The good news? We already know how to take a step. It's the two rules from last time."):
            a, b = dots[11].get_center(), dots[12].get_center()
            step = Arrow(a, b, buff=0, color=HOT, stroke_width=6, max_tip_length_to_length_ratio=0.5)
            q = T("rule 1, rule 2", 26, HOT, weight=BOLD).next_to(step, UP, buff=0.2)
            self.play(GrowArrow(step), FadeIn(q), run_time=0.8)
        self.clear()


class E3_03_WhyGPU(Video):
    def construct(self):
        self.tag("Why the graphics card")
        rows = VGroup(
            MathTex(r"1280 \times 720 \;\approx\; 1\ \text{million pixels}", font_size=46),
            MathTex(r"\times\; 150\ \text{steps for each ray}", font_size=46),
            MathTex(r"\times\; 60\ \text{pictures every second}", font_size=46),
            MathTex(r"\approx\; 9\ \text{billion steps per second}", font_size=52, color=GOLD),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        with self.voice("But one ray per pixel adds up fast. Even a small window has about a million pixels."):
            self.play(Write(rows[0]), run_time=1.5)
        with self.voice("Each ray needs a hundred steps or more."):
            self.play(Write(rows[1]), run_time=1.0)
        with self.voice("And for smooth motion, we want sixty pictures every second."):
            self.play(Write(rows[2]), run_time=1.0)
        with self.voice("Do the maths. That's billions of Runge-Kutta steps, every single second."):
            self.play(Write(rows[3]), run_time=1.2)
        self.clear(0.5)

        self.tag("Why the graphics card")

        def pixels(where):
            g = VGroup(*[Square(0.34, stroke_color="#2b3345", stroke_width=1.5, fill_color=PANEL, fill_opacity=1)
                         for _ in range(14 * 8)]).arrange_in_grid(rows=8, cols=14, buff=0.04)
            return g.move_to(where)

        cpu, gpu = pixels([-3.5, -0.3, 0]), pixels([3.5, -0.3, 0])
        cpu_label = T("processor: a few at a time", 26, COOL, weight=SEMIBOLD).next_to(cpu, UP, buff=0.35)
        gpu_label = T("graphics card: all at once", 26, GOLD, weight=SEMIBOLD).next_to(gpu, UP, buff=0.35)
        with self.voice("A processor grinds through them a few at a time. Way too slow."):
            self.play(FadeIn(cpu), FadeIn(cpu_label), FadeIn(gpu), run_time=0.8)
            self.play(LaggedStart(*[sq.animate.set_fill(COOL, 0.9) for sq in cpu[:40]], lag_ratio=0.3), run_time=3.0)
        with self.voice("A graphics card is a different beast. It has thousands of small cores, and it runs the same"
                        " little program on every pixel, all at once."):
            self.play(FadeIn(gpu_label), run_time=0.5)
            self.play(*[sq.animate.set_fill(GOLD, 0.9) for sq in gpu], run_time=1.0)
        with self.voice("And you've already met that little program. It's the fragment shader! Last time, all it did"
                        " was return a colour. This time, it does the physics."):
            self.play(Indicate(gpu_label, color=GOLD), run_time=1.5)
        self.clear()


class E3_04_Triangle(Video):
    def construct(self):
        self.tag("Stage 2: covering the screen")
        vert = CodePanel(excerpt(VERT, ("void main()", "}")), "stages/02_raytracer_3d/fullscreen.vert", max_width=11.0)
        vert.move_to(UP * 2.3)
        unit = 0.95
        c = np.array([-1.3, -2.0, 0])
        ndc = lambda x, y: c + unit * np.array([x * 16 / 9, y, 0]) * 0.75
        screen = Polygon(ndc(-1, -1), ndc(1, -1), ndc(1, 1), ndc(-1, 1), color=INK, stroke_width=3,
                         fill_color=COOL, fill_opacity=0.12)
        screen_label = T("screen", 22, INK).move_to(screen)
        tri = Polygon(ndc(-1, -1), ndc(3, -1), ndc(-1, 3), color=GOLD, stroke_width=4, fill_color=GOLD, fill_opacity=0.10)
        ids = VGroup(*[T(t, 22, GOLD, weight=BOLD).next_to(p, d, buff=0.12) for t, p, d in
                       [("0: (-1,-1)", ndc(-1, -1), DL), ("1: (3,-1)", ndc(3, -1), DR), ("2: (-1,3)", ndc(-1, 3), UL)]])
        with self.voice("One catch: a fragment shader only runs where something is being drawn. So we draw one shape"
                        " that covers the entire screen: a single, oversized triangle."):
            self.play(Create(screen), FadeIn(screen_label), run_time=1.0)
            self.play(Create(tri), run_time=1.5)
        with self.voice("Its vertex shader doesn't even need a buffer of points. It makes up the three corners from "
                        "the vertex number: zero, one, and two."):
            self.play(FadeIn(vert, shift=UP * 0.3), run_time=0.8)
            self.play(vert.focus("vec2 corner"), FadeIn(ids), run_time=1.0)
        with self.voice("They land outside the screen, which only goes from minus one to one. OpenGL trims off the "
                        "extra, and what's left is exactly the screen. Neat trick, right?"):
            self.play(vert.focus("gl_Position"), screen.animate.set_fill(GOLD, 0.35), run_time=1.0)
        self.play(*[FadeOut(m) for m in (vert, screen, screen_label, tri, ids)], run_time=0.6)

        cpp = CodePanel(excerpt(MAIN, ("// The triangle's corners come", "glBindVertexArray(vao);"),
                                ("glDrawArrays(GL_TRIANGLES, 0, 3);", "glDrawArrays(GL_TRIANGLES, 0, 3);")),
                        "stages/02_raytracer_3d/main.cpp", language="cpp", max_width=11.5)
        cpp.move_to(ORIGIN)
        with self.voice("On the C plus plus side, that's an empty vertex array, and one draw call with three "
                        "vertices."):
            self.play(FadeIn(cpp, shift=UP * 0.3), run_time=0.8)
            self.play(cpp.focus("GLuint vao", "glBindVertexArray"), run_time=0.8)
            self.play(cpp.focus("glDrawArrays"), run_time=0.8)
        with self.voice("From now on, the fragment shader runs once for every pixel in the window. Whatever colour "
                        "it returns, that's what you see."):
            pass
        self.clear()


class E3_05_Port(Video):
    def construct(self):
        self.tag("Stage 2: the physics moves to the shader")
        old = CodePanel(excerpt(S1, ("void derivatives", "}")), "stage 1  ·  C++, on the processor", language="cpp", max_width=6.85)
        new = CodePanel(excerpt(FRAG, ("void derivatives", "}")), "stage 2  ·  GLSL, on the graphics card", max_width=6.85)
        old.to_edge(LEFT, buff=0.2).shift(UP * 0.4)
        new.to_edge(RIGHT, buff=0.2).align_to(old, UP)
        with self.voice("Now the physics has to move out of C plus plus and into the shader. Here's our derivatives "
                        "function from last time."):
            self.play(FadeIn(old, shift=UP * 0.3), run_time=0.8)
        with self.voice("And here's the shader version."):
            self.play(FadeIn(new, shift=UP * 0.3), run_time=0.8)
        with self.voice("Look how little changes! Vec two becomes vec three. And the outputs are marked with the "
                        "word out, instead of being references."):
            self.play(old.focus(1), new.focus(1), run_time=0.8)
        with self.voice("The body? Identical. Line for line."):
            self.play(old.focus("float r", "float A"), new.focus("float r", "float A"), run_time=0.8)
        note_text = T("the two rules are written with vectors,\nso they work in any number of dimensions", 26, GOLD,
                      line_spacing=0.8).to_edge(DOWN, buff=0.6)
        with self.voice("And that's not luck. Our two rules never said how many dimensions there are. They're "
                        "written with vectors and dot products, so three dimensions comes for free."):
            self.play(old.focus("dx = p", "dp = "), new.focus("dx = p", "dp = "), FadeIn(note_text), run_time=0.8)
        with self.voice("Photon energy and the Runge-Kutta step move over in exactly the same way."):
            self.play(old.unfocus(), new.unfocus(), run_time=0.8)
        self.clear()


class E3_06_Camera(Video):
    def construct(self):
        self.tag("Stage 2: the camera")
        centre = np.array([3.9, 1.5, 0])
        orbit = DashedVMobject(Ellipse(width=6.0, height=2.2, color=MUTED, stroke_width=2).move_to(centre), num_dashes=50)
        hole = black_hole(0.16, centre)
        foot = centre + np.array([3.0 * np.cos(-2.6), 1.1 * np.sin(-2.6), 0])
        cam_at = foot + UP * 1.1
        height = DashedLine(foot, cam_at, color=MUTED, stroke_width=2)
        cam = Dot(cam_at, radius=0.1, color=INK)
        cam_label = T("camera", 20, MUTED).next_to(cam, LEFT, buff=0.15)
        to_hole = (centre - cam_at) / np.linalg.norm(centre - cam_at)
        forward = Arrow(cam_at, cam_at + 1.25 * to_hole, buff=0, color=COOL, stroke_width=5)
        right = Arrow(cam_at, cam_at + np.array([0.7, -0.75, 0]), buff=0, color=HOT, stroke_width=5)
        up = Arrow(cam_at, cam_at + np.array([0.12, 1.15, 0]), buff=0, color=GOOD, stroke_width=5)
        axis_labels = VGroup(T("forward", 20, COOL).next_to(forward.get_end(), UP, buff=0.1),
                             T("right", 20, HOT).next_to(right.get_end(), DOWN, buff=0.08),
                             T("up", 20, GOOD).next_to(up.get_end(), RIGHT, buff=0.1))
        with self.voice("Next up: the camera. It circles the hole, and we describe where it is with two angles and a"
                        " distance. Those are what your mouse changes."):
            self.play(FadeIn(hole), Create(orbit), run_time=1.0)
            self.play(Create(height), FadeIn(cam), FadeIn(cam_label), run_time=1.0)

        code = CodePanel(excerpt(MAIN, ("Vec3 position = camDistance", "Vec3 up = cross(right, forward);")),
                         "stages/02_raytracer_3d/main.cpp", language="cpp", max_width=7.6)
        code.to_edge(LEFT, buff=0.25).shift(DOWN * 1.2)
        with self.voice("Every frame, the program turns those into a position, with sines and cosines."):
            self.play(FadeIn(code, shift=UP * 0.3), run_time=0.8)
            self.play(code.focus("Vec3 position", "std::sin(camPitch)"), run_time=0.8)
        with self.voice("Then it needs three directions. Forward points from the camera to the hole."):
            self.play(code.focus("Vec3 forward"), GrowArrow(forward), FadeIn(axis_labels[0]), run_time=1.0)
        with self.voice("Right has to be perpendicular to forward, and to the vertical. And a cross product gives "
                        "you exactly that: a vector at right angles to two others."):
            self.play(code.focus("Vec3 right"), GrowArrow(right), FadeIn(axis_labels[1]), run_time=1.0)
        with self.voice("And up is perpendicular to both of those."):
            self.play(code.focus("Vec3 up"), GrowArrow(up), FadeIn(axis_labels[2]), run_time=1.0)

        uniforms = CodePanel(excerpt(MAIN, ('setVec3(program, "uCamPos"', "glDrawArrays(GL_TRIANGLES, 0, 3);")),
                             "stages/02_raytracer_3d/main.cpp", language="cpp", max_width=7.6)
        uniforms.move_to(code, aligned_edge=LEFT).align_to(code, UP)
        with self.voice("These get sent to the shader as uniforms. Remember: a uniform is a value the program sends "
                        "to the shader, the same for every pixel."):
            self.play(FadeOut(code), FadeIn(uniforms, shift=UP * 0.3), run_time=0.8)
            self.play(uniforms.focus('setVec3(program, "uCamPos"', 'setVec3(program, "uCamForward"'), run_time=0.8)
        with self.voice("So when you drag the mouse, the angles change, the uniforms change, and the next frame gets"
                        " traced from the new spot."):
            self.play(Rotate(VGroup(cam, cam_label, forward, right, up, axis_labels, height), 0.25, about_point=centre),
                      run_time=2.0)
        self.clear()

        self.tag("Stage 2: one ray per pixel")
        shader = CodePanel(excerpt(FRAG, ("vec2 uv = gl_FragCoord", "float pt = photonEnergy(x, p);"),
                                   skip=("// Where is this pixel", "// The ray through this pixel")),
                           "stages/02_raytracer_3d/trace.frag", max_width=12.5)
        shader.move_to(UP * 1.6)
        eye = np.array([-4.5, -2.2, 0])
        plane = VGroup(*[Square(0.3, stroke_color=MUTED, stroke_width=1.5).move_to([-2.2, y, 0])
                         for y in np.linspace(-3.2, -1.2, 7)])
        picked = plane[5]
        ray = Arrow(eye, eye + 1.9 * (picked.get_center() - eye), buff=0, color=GOLD, stroke_width=4,
                    max_tip_length_to_length_ratio=0.06)
        fwd = Arrow(eye, eye + RIGHT * 2.3, buff=0, color=COOL, stroke_width=4, max_tip_length_to_length_ratio=0.1)
        upv = Arrow(eye + RIGHT * 2.3, picked.get_center(), buff=0, color=GOOD, stroke_width=4,
                    max_tip_length_to_length_ratio=0.25)
        legend = VGroup(T("forward", 20, COOL), T("+ a bit of up and right", 20, GOOD), T("= this pixel's ray", 20, GOLD))
        legend.arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to([3.0, -2.2, 0])
        with self.voice("Now we're inside the fragment shader. First, each pixel works out where it sits on the "
                        "screen, from minus one to plus one."):
            self.play(FadeIn(shader, shift=UP * 0.3), run_time=0.8)
            self.play(shader.focus("vec2 uv", "uv.x *="), FadeIn(Dot(eye, radius=0.09, color=INK)), FadeIn(plane), run_time=1.0)
            self.play(picked.animate.set_fill(GOLD, 0.9), run_time=0.6)
        with self.voice("Its ray starts at the camera. And its direction is forward, plus a bit of right and a bit "
                        "of up, depending on where the pixel is."):
            self.play(shader.focus("vec3 x = uCamPos", "vec3 p = normalize"), run_time=0.8)
            self.play(GrowArrow(fwd), FadeIn(legend[0]), run_time=0.7)
            self.play(GrowArrow(upv), FadeIn(legend[1]), run_time=0.7)
            self.play(GrowArrow(ray), FadeIn(legend[2]), run_time=0.7)
        with self.voice("That direction is the ray's momentum, p. And photon energy gives us p t, exactly like in "
                        "stage one."):
            self.play(shader.focus("float pt"), run_time=0.8)
        with self.voice("One honest confession: this treats space as flat right where the camera sits. That's a fine"
                        " approximation, as long as the camera keeps its distance from the hole."):
            self.play(shader.unfocus(), run_time=0.6)
        self.clear()


class E3_07_Loop(Video):
    def construct(self):
        self.tag("Stage 2: one ray per pixel")
        loop = CodePanel(excerpt(FRAG, ("for (int i = 0; i < 400", "fragColor = vec4(sky(")),
                         "stages/02_raytracer_3d/trace.frag", max_width=7.9)
        loop.to_edge(LEFT, buff=0.25).shift(DOWN * 0.1)
        scale = 0.2
        origin = np.array([4.6, -0.2, 0])
        box = (1.55, 7.0, -3.2, 3.0)
        hole = black_hole(scale, origin)
        cam = 30 * np.array([np.cos(np.radians(8)), np.sin(np.radians(8)), 0])
        aim = -cam / np.linalg.norm(cam)

        def shoot(angle):
            c, s = np.cos(angle), np.sin(angle)
            return geo.trace(cam, [c * aim[0] - s * aim[1], s * aim[0] + c * aim[1], 0], r_escape=60, quality=1.0)[0]

        fall_line, fall_dots = step_dots(shoot(-0.08), scale, origin, HOT, box)
        free_line, free_dots = step_dots(shoot(-0.26), scale, origin, GOLD, box)
        with self.voice("Then comes the same loop as trace ray from last time, with one difference. Instead of "
                        "saving a path, it picks a colour."):
            self.play(FadeIn(loop, shift=UP * 0.3), FadeIn(hole), run_time=1.0)
            self.play(loop.focus(1, 2), run_time=0.6)
        with self.voice("Inside the horizon? No light comes out of there. This pixel is black. Done."):
            self.play(loop.focus("if (r < 2.0 * M)", "return;"), run_time=0.6)
            self.play(Create(fall_line), LaggedStart(*[FadeIn(q) for q in fall_dots], lag_ratio=0.3), run_time=2.5, rate_func=linear)
        with self.voice("Far away? The ray escaped. Stop stepping."):
            self.play(loop.focus("if (r > 70.0)"), VGroup(fall_line, fall_dots).animate.set_opacity(0.3), run_time=0.6)
        with self.voice("Otherwise, take one Runge-Kutta step, and go around again."):
            self.play(loop.focus("rk4Step"), run_time=0.6)
            self.play(Create(free_line), LaggedStart(*[FadeIn(q, scale=2) for q in free_dots], lag_ratio=0.3),
                      run_time=4.0, rate_func=linear)
        star = Star(n=5, outer_radius=0.2, color=INK, fill_opacity=1, stroke_width=0).move_to(free_dots[-1])
        with self.voice("After the loop, we ask: which way is the escaped ray heading now? Rule one gives us its "
                        "velocity. Then we look up that direction in the sky."):
            self.play(loop.focus("vec3 dx, dp;", "fragColor = vec4(sky("), FadeIn(star, scale=2), run_time=0.8)
        self.clear()

        self.tag("Stage 2: the sky")
        stars = ImageMobject(str(ASSETS / "stage2_stars.jpg")).scale_to_fit_width(6.5)
        grid = ImageMobject(str(ASSETS / "stage2.jpg")).scale_to_fit_width(6.5)
        Group(stars, grid).arrange(RIGHT, buff=0.4)
        labels = VGroup(T("stars", 26, weight=SEMIBOLD).next_to(stars, DOWN, buff=0.2),
                        T("a grid of latitude and longitude", 26, weight=SEMIBOLD).next_to(grid, DOWN, buff=0.2))
        with self.voice("The sky function turns a direction into a colour. It can paint stars."):
            self.play(FadeIn(stars), FadeIn(labels[0]), run_time=1.0)
        with self.voice("Or it can paint a grid, like the lines of latitude and longitude on a globe, with the top "
                        "half blue and the bottom half red. That makes the bending so much easier to see."):
            self.play(FadeIn(grid), FadeIn(labels[1]), run_time=1.0)
        self.clear()


class E3_08_Result(Video):
    def construct(self):
        clip = Footage("stage2").scale_to_fit_height(config.frame_height)
        self.play(FadeIn(clip), run_time=0.8)

        def caption(text):
            label = T(text, 26, weight=SEMIBOLD).to_edge(DOWN, buff=0.4)
            return VGroup(BackgroundRectangle(label, color=BLACK, fill_opacity=0.7, buff=0.2), label)

        cap = caption("stage 2, running")
        self.play(FadeIn(cap), run_time=0.4)
        with self.voice("And here it is! That black disc in the middle is the shadow. Every ray aimed in there fell "
                        "into the hole."):
            pass
        new = caption("shadow radius = 5.2 M")
        with self.voice("Its edge is exactly the critical aim we found last time: five point two M. Way bigger than "
                        "the hole itself."):
            self.play(FadeOut(cap), FadeIn(new), run_time=0.5)
        cap = new
        new = caption("the whole sky, a second time, in a thin ring")
        with self.voice("Around it, the grid gets stretched and folded. And just outside the shadow, you can see the"
                        " entire sky a second time, squeezed into a thin ring. That light went all the way around "
                        "the hole."):
            self.play(FadeOut(cap), FadeIn(new), run_time=0.5)
        cap = new
        new = caption("blue below the hole: those rays went over the top")
        with self.voice("And check out the colours. The top of the sky is blue, right? But there's blue below the "
                        "hole. Those rays got bent right over the top."):
            self.play(FadeOut(cap), FadeIn(new), run_time=0.5)
        stars = Footage("stage2_stars").scale_to_fit_height(config.frame_height)
        with self.voice("Swap in the stars, and it looks like this. A million rays, a few hundred steps each, re-"
                        "traced every single frame."):
            self.play(FadeOut(new), FadeIn(stars), run_time=1.0)
            self.remove(clip)

        shade = Rectangle(width=15, height=9, stroke_width=0, fill_color=BLACK, fill_opacity=0.0)
        title = T("Next: the spinning disk", 44, weight=BOLD).to_edge(UP, buff=0.5)
        nxt = ImageMobject(str(ASSETS / "stage3.jpg")).scale_to_fit_height(5.6).move_to(DOWN * 0.4)
        with self.voice("Still, a black hole on its own looks a bit empty. Next time, we give it something to light "
                        "it up: a disk of hot gas, orbiting at half the speed of light. Don't miss that one."):
            self.play(shade.animate.set_fill(opacity=0.85), FadeIn(title), run_time=0.8)
            self.play(FadeIn(nxt), run_time=1.2)
        self.wait(1.0)
        self.play(FadeOut(nxt), FadeOut(title), shade.animate.set_fill(opacity=1.0), run_time=1.0)
