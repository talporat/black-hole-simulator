// Black hole ray tracer: window, input and the render pipeline
//   trace (HDR) -> bloom down/up chain -> tonemap.
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#include "gl/gl.h"
#define GLFW_INCLUDE_NONE
#include <GLFW/glfw3.h>

#include "camera.h"
#include "gl/framebuffer.h"
#include "gl/shader.h"
#include "png.h"

namespace {

const int BLOOM_LEVELS = 6;
const float PI = 3.14159265f;

struct Settings {
    Camera camera;
    bool disk = true, grid = false, doppler = true, bloom = true, paused = false;
    float quality = 1.0f;       // geodesic step scale
    float time = 0.0f;          // disk time, in units of M
    float timeRate = 4.0f;      // M per second
    float exposure = 1.0f;
    float renderScale = 0.0f;   // 0 = pick from the display's content scale
    std::string shaderDir = SHADER_DIR;
    std::string screenshot;     // if set: render one frame to this file and exit
    std::string sequence;       // if set: render `frames` frames to <sequence>NNNN.png and exit
    int frames = 0;
    float dAzim = 0, dIncl = 0, dDist = 0, dTime = 0, dRoll = 0;  // per-frame change for --sequence
    int width = 1280, height = 720;
};

struct Renderer {
    Shader trace, down, up, tonemap;
    Framebuffer scene, bloom[BLOOM_LEVELS], output;
    GLuint vao = 0;

    bool load(const std::string& dir) {
        std::string vert = dir + "/fullscreen.vert";
        return trace.load(vert, dir + "/trace.frag") && down.load(vert, dir + "/bloom_down.frag") &&
               up.load(vert, dir + "/bloom_up.frag") && tonemap.load(vert, dir + "/tonemap.frag");
    }

    // Renders one frame into framebuffer `target` (0 = the window) of size w x h.
    // The trace pass runs at traceW x traceH and is scaled up by the tonemap pass.
    void render(const Settings& s, int traceW, int traceH, GLuint target, int w, int h) {
        if (!vao) glGenVertexArrays(1, &vao);
        glBindVertexArray(vao);
        glDisable(GL_BLEND);

        scene.ensure(traceW, traceH, GL_RGBA16F);
        scene.bind();
        Tetrad tet = s.camera.tetrad();
        trace.use();
        trace.set("uResolution", vec2(float(traceW), float(traceH)));
        trace.set("uCamPos", s.camera.position());
        trace.set("uTetT", tet.t);
        trace.set("uTetS0", tet.s[0]);
        trace.set("uTetS1", tet.s[1]);
        trace.set("uTetS2", tet.s[2]);
        trace.set("uTetS3", tet.s[3]);
        trace.set("uTanHalfFov", std::tan(0.5f * s.camera.fovY));
        trace.set("uTime", s.time);
        trace.set("uEscapeR", std::fmax(60.0f, 1.5f * s.camera.dist));
        trace.set("uQuality", s.quality);
        trace.set("uMaxSteps", int(400.0f / s.quality));
        trace.set("uDisk", int(s.disk));
        trace.set("uGrid", int(s.grid));
        trace.set("uDoppler", int(s.doppler));
        trace.set("uDiskOuter", 20.0f);
        trace.set("uDiskTemp", 4800.0f);
        trace.set("uDiskBrightness", 1.8f);
        glDrawArrays(GL_TRIANGLES, 0, 3);

        if (s.bloom) {
            down.use();
            down.set("uSrc", 0);
            const Framebuffer* src = &scene;
            for (int i = 0; i < BLOOM_LEVELS; ++i) {
                bloom[i].ensure(src->width() / 2, src->height() / 2, GL_RGBA16F);
                bloom[i].bind();
                src->bindTexture(0);
                down.set("uTexel", vec2(1.0f / src->width(), 1.0f / src->height()));
                down.set("uThreshold", i == 0 ? 1.0f : 0.0f);
                glDrawArrays(GL_TRIANGLES, 0, 3);
                src = &bloom[i];
            }
            up.use();
            up.set("uSrc", 0);
            glEnable(GL_BLEND);
            glBlendFunc(GL_ONE, GL_ONE);
            for (int i = BLOOM_LEVELS - 1; i > 0; --i) {
                bloom[i - 1].bind();
                bloom[i].bindTexture(0);
                up.set("uTexel", vec2(1.0f / bloom[i].width(), 1.0f / bloom[i].height()));
                glDrawArrays(GL_TRIANGLES, 0, 3);
            }
            glDisable(GL_BLEND);
        }

        // ensure() binds the framebuffer it allocates, so do it before binding the target.
        bloom[0].ensure(traceW / 2, traceH / 2, GL_RGBA16F);
        glBindFramebuffer(GL_FRAMEBUFFER, target);
        glViewport(0, 0, w, h);
        tonemap.use();
        scene.bindTexture(0);
        bloom[0].bindTexture(1);
        tonemap.set("uScene", 0);
        tonemap.set("uBloom", 1);
        tonemap.set("uBloomStrength", s.bloom ? 0.35f : 0.0f);
        tonemap.set("uExposure", s.exposure);
        glDrawArrays(GL_TRIANGLES, 0, 3);
    }

    bool savePng(const Settings& s, const std::string& path, int w, int h) {
        output.ensure(w, h, GL_RGBA8);
        output.bind();
        // The output framebuffer object id is private; it is the one bound now.
        GLint fbo = 0;
        glGetIntegerv(GL_FRAMEBUFFER_BINDING, &fbo);
        render(s, w, h, GLuint(fbo), w, h);
        glFinish();
        std::vector<uint8_t> pixels(size_t(w) * h * 3), flipped(pixels.size());
        glPixelStorei(GL_PACK_ALIGNMENT, 1);
        glReadPixels(0, 0, w, h, GL_RGB, GL_UNSIGNED_BYTE, pixels.data());
        for (int y = 0; y < h; ++y)  // GL rows are bottom-up
            std::memcpy(&flipped[size_t(y) * w * 3], &pixels[size_t(h - 1 - y) * w * 3], size_t(w) * 3);
        bool ok = writePng(path.c_str(), w, h, flipped.data());
        std::printf("%s %s (%dx%d)\n", ok ? "wrote" : "FAILED to write", path.c_str(), w, h);
        return ok;
    }
};

Settings settings;
Renderer renderer;
bool dragging = false, wantScreenshot = false;
double lastX = 0, lastY = 0;

void onKey(GLFWwindow* win, int key, int, int action, int) {
    if (action != GLFW_PRESS) return;
    Settings& s = settings;
    switch (key) {
        case GLFW_KEY_ESCAPE: glfwSetWindowShouldClose(win, 1); break;
        case GLFW_KEY_D: s.disk = !s.disk; break;
        case GLFW_KEY_G: s.grid = !s.grid; break;
        case GLFW_KEY_R: s.doppler = !s.doppler; break;
        case GLFW_KEY_B: s.bloom = !s.bloom; break;
        case GLFW_KEY_SPACE: s.paused = !s.paused; break;
        case GLFW_KEY_P: wantScreenshot = true; break;
        case GLFW_KEY_LEFT_BRACKET: s.quality = std::fmin(s.quality * 1.5f, 4.0f); break;
        case GLFW_KEY_RIGHT_BRACKET: s.quality = std::fmax(s.quality / 1.5f, 0.2f); break;
        case GLFW_KEY_MINUS: s.exposure /= 1.25f; break;
        case GLFW_KEY_EQUAL: s.exposure *= 1.25f; break;
        case GLFW_KEY_F5:
            if (renderer.load(s.shaderDir)) std::printf("shaders reloaded\n");
            break;
    }
}

void onMouseButton(GLFWwindow* win, int button, int action, int) {
    if (button != GLFW_MOUSE_BUTTON_LEFT) return;
    dragging = action == GLFW_PRESS;
    glfwGetCursorPos(win, &lastX, &lastY);
}

void onCursor(GLFWwindow*, double x, double y) {
    if (dragging) {
        Camera& c = settings.camera;
        c.azim -= float(x - lastX) * 0.006f;
        c.incl = clamp(c.incl - float(y - lastY) * 0.006f, 0.02f, PI - 0.02f);
    }
    lastX = x;
    lastY = y;
}

void onScroll(GLFWwindow*, double, double dy) {
    Camera& c = settings.camera;
    c.dist = clamp(c.dist * std::exp(-0.08f * float(dy)), 2.6f, 300.0f);
}

void usage() {
    std::puts(
        "usage: blackhole [options]\n"
        "  --preset NAME       default | faceon | edgeon | grid | nodisk | close\n"
        "  --dist D            camera distance in M        --incl DEG   angle from the disk axis\n"
        "  --azim DEG          camera azimuth              --fov DEG    vertical field of view\n"
        "  --time T            disk time in M              --quality Q  step scale (smaller = finer)\n"
        "  --exposure E        --scale S (render scale)    --size WxH\n"
        "  --no-disk  --grid  --no-doppler  --no-bloom\n"
        "  --screenshot FILE   render one frame to a PNG and exit\n"
        "  --roll DEG          tilt the camera about its viewing direction\n"
        "  --sequence PREFIX --frames N [--d-azim DEG --d-incl DEG --d-roll DEG --d-dist D --d-time T]\n"
        "                      render N frames to PREFIXnnnn.png, changing the camera per frame\n"
        "  --shaders DIR       shader directory\n"
        "keys: drag = orbit, scroll = zoom, D disk, G grid, R redshift/Doppler, B bloom,\n"
        "      [ ] quality, - = exposure, Space pause, P screenshot, F5 reload shaders, Esc quit");
}

bool applyPreset(Settings& s, const std::string& name) {
    const float deg = PI / 180.0f;
    if (name == "default") { s.camera.dist = 30; s.camera.incl = 80 * deg; }
    else if (name == "faceon") { s.camera.dist = 40; s.camera.incl = 12 * deg; }
    else if (name == "edgeon") { s.camera.dist = 30; s.camera.incl = 88.5f * deg; }
    else if (name == "grid") { s.camera.dist = 30; s.camera.incl = 80 * deg; s.grid = true; s.disk = false; }
    else if (name == "nodisk") { s.camera.dist = 30; s.camera.incl = 80 * deg; s.disk = false; }
    else if (name == "close") { s.camera.dist = 12; s.camera.incl = 84 * deg; s.camera.fovY = 80 * deg; s.exposure = 0.3f; }
    else return false;
    return true;
}

bool parseArgs(int argc, char** argv, Settings& s) {
    const float deg = PI / 180.0f;
    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        auto value = [&]() -> const char* { return i + 1 < argc ? argv[++i] : "0"; };
        if (a == "--preset") { if (!applyPreset(s, value())) return false; }
        else if (a == "--dist") s.camera.dist = float(std::atof(value()));
        else if (a == "--incl") s.camera.incl = float(std::atof(value())) * deg;
        else if (a == "--azim") s.camera.azim = float(std::atof(value())) * deg;
        else if (a == "--fov") s.camera.fovY = float(std::atof(value())) * deg;
        else if (a == "--roll") s.camera.roll = float(std::atof(value())) * deg;
        else if (a == "--d-roll") s.dRoll = float(std::atof(value())) * deg;
        else if (a == "--time") s.time = float(std::atof(value()));
        else if (a == "--quality") s.quality = float(std::atof(value()));
        else if (a == "--exposure") s.exposure = float(std::atof(value()));
        else if (a == "--scale") s.renderScale = float(std::atof(value()));
        else if (a == "--size") { if (std::sscanf(value(), "%dx%d", &s.width, &s.height) != 2) return false; }
        else if (a == "--no-disk") s.disk = false;
        else if (a == "--grid") s.grid = true;
        else if (a == "--no-doppler") s.doppler = false;
        else if (a == "--no-bloom") s.bloom = false;
        else if (a == "--screenshot") s.screenshot = value();
        else if (a == "--sequence") s.sequence = value();
        else if (a == "--frames") s.frames = std::atoi(value());
        else if (a == "--d-azim") s.dAzim = float(std::atof(value())) * deg;
        else if (a == "--d-incl") s.dIncl = float(std::atof(value())) * deg;
        else if (a == "--d-dist") s.dDist = float(std::atof(value()));
        else if (a == "--d-time") s.dTime = float(std::atof(value()));
        else if (a == "--shaders") s.shaderDir = value();
        else return false;
    }
    return s.camera.dist > 2.0f && s.quality > 0.0f && s.width > 0 && s.height > 0;
}

}  // namespace

int main(int argc, char** argv) {
    if (!parseArgs(argc, argv, settings)) {
        usage();
        return 2;
    }
    Settings& s = settings;
    bool headless = !s.screenshot.empty() || !s.sequence.empty();

    if (!glfwInit()) {
        std::fprintf(stderr, "failed to initialise GLFW\n");
        return 1;
    }
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 1);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GLFW_TRUE);
    if (headless) glfwWindowHint(GLFW_VISIBLE, GLFW_FALSE);
    GLFWwindow* win = glfwCreateWindow(headless ? 64 : s.width, headless ? 64 : s.height, "Black Hole", nullptr, nullptr);
    if (!win) {
        std::fprintf(stderr, "failed to create an OpenGL 4.1 window\n");
        glfwTerminate();
        return 1;
    }
    glfwMakeContextCurrent(win);
    if (!renderer.load(s.shaderDir)) return 1;

    if (headless) {
        bool ok = true;
        if (!s.screenshot.empty()) ok = renderer.savePng(s, s.screenshot, s.width, s.height);
        for (int i = 0; ok && i < s.frames && !s.sequence.empty(); ++i) {
            char name[16];
            std::snprintf(name, sizeof name, "%04d.png", i);
            ok = renderer.savePng(s, s.sequence + name, s.width, s.height);
            s.camera.azim += s.dAzim;
            s.camera.incl = clamp(s.camera.incl + s.dIncl, 0.02f, PI - 0.02f);
            s.camera.dist += s.dDist;
            s.camera.roll += s.dRoll;
            s.time += s.dTime;
        }
        glfwTerminate();
        return ok ? 0 : 1;
    }

    glfwSwapInterval(1);
    glfwSetKeyCallback(win, onKey);
    glfwSetMouseButtonCallback(win, onMouseButton);
    glfwSetCursorPosCallback(win, onCursor);
    glfwSetScrollCallback(win, onScroll);
    usage();

    double last = glfwGetTime(), fpsTime = last;
    int frames = 0, shotIndex = 0;
    while (!glfwWindowShouldClose(win)) {
        glfwPollEvents();
        double now = glfwGetTime();
        if (!s.paused) s.time += float(now - last) * s.timeRate;
        last = now;

        int fbW, fbH, winW, winH;
        glfwGetFramebufferSize(win, &fbW, &fbH);
        glfwGetWindowSize(win, &winW, &winH);
        if (fbW == 0 || fbH == 0) continue;
        // By default trace at window (not Retina) resolution and let the tonemap pass upscale.
        float scale = s.renderScale > 0.0f ? s.renderScale : float(winW) / float(fbW);
        renderer.render(s, int(fbW * scale), int(fbH * scale), 0, fbW, fbH);
        glfwSwapBuffers(win);

        if (wantScreenshot) {
            wantScreenshot = false;
            char name[64];
            std::snprintf(name, sizeof name, "blackhole_%03d.png", shotIndex++);
            renderer.savePng(s, name, fbW, fbH);
        }

        if (++frames, now - fpsTime > 0.5) {
            char title[128];
            std::snprintf(title, sizeof title, "Black Hole  |  %.0f fps  |  r = %.1f M  |  quality %.2f",
                          frames / (now - fpsTime), s.camera.dist, s.quality);
            glfwSetWindowTitle(win, title);
            frames = 0;
            fpsTime = now;
        }
    }
    glfwTerminate();
    return 0;
}
