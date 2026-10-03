// Frame grabbing for the video tooling. Not part of the lessons.
//
//   ./stage --capture out/frame --frames 120 --size 1280x720
//
// writes out/frame0000.ppm, out/frame0001.ppm, ... and exits.
#pragma once
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

struct Capture {
    std::string prefix;
    int frames = 1, index = 0, width = 1280, height = 720;

    Capture(int argc, char** argv) {
        for (int i = 1; i + 1 < argc; ++i) {
            if (!std::strcmp(argv[i], "--capture")) prefix = argv[i + 1];
            if (!std::strcmp(argv[i], "--frames")) frames = std::atoi(argv[i + 1]);
            if (!std::strcmp(argv[i], "--size")) std::sscanf(argv[i + 1], "%dx%d", &width, &height);
        }
    }
    bool on() const { return !prefix.empty(); }
    // 0..1 through the capture, for animating something while recording.
    float progress() const { return frames > 1 ? float(index) / float(frames - 1) : 0.0f; }

    // Call before glfwCreateWindow: an invisible window with exactly width x height pixels.
    void windowHints() const {
        if (!on()) return;
        glfwWindowHint(GLFW_VISIBLE, GLFW_FALSE);
        glfwWindowHint(GLFW_COCOA_RETINA_FRAMEBUFFER, GLFW_FALSE);
    }

    // Call after drawing a frame. Returns false once the last frame is saved.
    bool save() {
        if (!on()) return true;
        std::vector<unsigned char> px(size_t(width) * height * 3);
        glPixelStorei(GL_PACK_ALIGNMENT, 1);
        glReadBuffer(GL_BACK);
        glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE, px.data());
        char name[32];
        std::snprintf(name, sizeof name, "%04d.ppm", index);
        if (std::FILE* f = std::fopen((prefix + name).c_str(), "wb")) {
            std::fprintf(f, "P6\n%d %d\n255\n", width, height);
            for (int y = height - 1; y >= 0; --y) std::fwrite(&px[size_t(y) * width * 3], 1, size_t(width) * 3, f);
            std::fclose(f);
        }
        return ++index < frames;
    }
};
