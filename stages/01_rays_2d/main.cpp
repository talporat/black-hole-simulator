// Stage 1: light rays bending around a black hole, in 2D.
//
// The CPU traces each ray step by step and OpenGL draws the paths as lines.
// Move the mouse up and down to aim the bright ray.
#include <cmath>
#include <cstdio>
#include <vector>

#define GL_SILENCE_DEPRECATION
#include <OpenGL/gl3.h>
#define GLFW_INCLUDE_NONE
#include <GLFW/glfw3.h>
#include "../common/capture.h"

// ---------------------------------------------------------------- vectors

struct Vec2 { float x, y; };
Vec2 operator+(Vec2 a, Vec2 b) { return {a.x + b.x, a.y + b.y}; }
Vec2 operator-(Vec2 a, Vec2 b) { return {a.x - b.x, a.y - b.y}; }
Vec2 operator*(float s, Vec2 a) { return {s * a.x, s * a.y}; }
float dot(Vec2 a, Vec2 b) { return a.x * b.x + a.y * b.y; }
float length(Vec2 a) { return std::sqrt(dot(a, a)); }

// ---------------------------------------------------------------- physics

const float M = 1.0f;  // the hole's mass; every distance is in units of M

// The two rules for light: how position x and momentum p change.
void derivatives(Vec2 x, Vec2 p, float pt, Vec2& dx, Vec2& dp) {
    float r = length(x);
    Vec2 L = (1.0f / r) * x;      // unit arrow, away from the hole
    float f = 2.0f * M / r;       // strength of gravity
    Vec2 gradF = (-f / r) * L;    // the inverse square
    Vec2 gradLp = (1.0f / r) * (p - dot(L, p) * L);
    float A = dot(L, p) - pt;

    dx = p - (f * A) * L;                             // rule 1
    dp = (0.5f * A * A) * gradF + (f * A) * gradLp;   // rule 2
}

// Light obeys H = 0. Given p, that pins down pt: a quadratic equation.
float photonEnergy(Vec2 x, Vec2 p) {
    float r = length(x);
    float f = 2.0f * M / r;
    float Lp = dot(x, p) / r;
    float a = -(1.0f + f);
    float b = 2.0f * f * Lp;
    float c = dot(p, p) - f * Lp * Lp;
    return (-b + std::sqrt(b * b - 4.0f * a * c)) / (2.0f * a);
}

// One Runge-Kutta 4 step of size h.
void rk4Step(Vec2& x, Vec2& p, float pt, float h) {
    Vec2 k1x, k1p, k2x, k2p, k3x, k3p, k4x, k4p;
    derivatives(x, p, pt, k1x, k1p);
    derivatives(x + 0.5f * h * k1x, p + 0.5f * h * k1p, pt, k2x, k2p);
    derivatives(x + 0.5f * h * k2x, p + 0.5f * h * k2p, pt, k3x, k3p);
    derivatives(x + h * k3x, p + h * k3p, pt, k4x, k4p);
    x = x + (h / 6.0f) * (k1x + 2.0f * k2x + 2.0f * k3x + k4x);
    p = p + (h / 6.0f) * (k1p + 2.0f * k2p + 2.0f * k3p + k4p);
}

struct Ray {
    std::vector<Vec2> points;
    bool captured = false;
};

// Follow one ray from `start`, heading in `direction`, until it ends.
Ray traceRay(Vec2 start, Vec2 direction) {
    Ray ray;
    Vec2 x = start;
    Vec2 p = direction;
    float pt = photonEnergy(x, p);
    ray.points.push_back(x);
    for (int i = 0; i < 5000; ++i) {
        float r = length(x);
        if (r < 2.0f * M) { ray.captured = true; break; }
        if (r > 60.0f) break;
        rk4Step(x, p, pt, 0.03f * r);
        ray.points.push_back(x);
    }
    return ray;
}

// ---------------------------------------------------------------- OpenGL

// Runs once per point: turns a position in units of M into a
// position on screen, where both axes go from -1 to 1.
const char* VERTEX_SHADER = R"(#version 410 core
layout(location = 0) in vec2 aPos;
uniform vec2 uViewSize;  // half-size of the view
void main() {
    gl_Position = vec4(aPos / uViewSize, 0.0, 1.0);
}
)";

// Runs once per pixel that a line or triangle covers: picks its colour.
const char* FRAGMENT_SHADER = R"(#version 410 core
uniform vec3 uColor;
out vec4 fragColor;
void main() {
    fragColor = vec4(uColor, 1.0);
}
)";

GLuint compileShader(GLenum type, const char* source) {
    GLuint shader = glCreateShader(type);
    glShaderSource(shader, 1, &source, nullptr);
    glCompileShader(shader);
    GLint ok = 0;
    glGetShaderiv(shader, GL_COMPILE_STATUS, &ok);
    if (!ok) {
        char log[1024];
        glGetShaderInfoLog(shader, sizeof log, nullptr, log);
        std::fprintf(stderr, "shader error:\n%s\n", log);
    }
    return shader;
}

GLuint makeProgram(const char* vertexSource, const char* fragmentSource) {
    GLuint program = glCreateProgram();
    glAttachShader(program, compileShader(GL_VERTEX_SHADER, vertexSource));
    glAttachShader(program, compileShader(GL_FRAGMENT_SHADER, fragmentSource));
    glLinkProgram(program);
    return program;
}

// Send a list of points to the GPU and draw them in one colour.
// mode says how to connect them: GL_LINE_STRIP, GL_TRIANGLE_FAN, ...
void draw(GLuint program, GLenum mode, const std::vector<Vec2>& points,
          float red, float green, float blue) {
    glBufferData(GL_ARRAY_BUFFER, points.size() * sizeof(Vec2),
                 points.data(), GL_DYNAMIC_DRAW);
    glUniform3f(glGetUniformLocation(program, "uColor"), red, green, blue);
    glDrawArrays(mode, 0, GLsizei(points.size()));
}

std::vector<Vec2> circle(float radius) {
    std::vector<Vec2> points;
    for (int i = 0; i <= 96; ++i) {
        float angle = 6.2831853f * float(i) / 96.0f;
        points.push_back({radius * std::cos(angle), radius * std::sin(angle)});
    }
    return points;
}

// ---------------------------------------------------------------- main

int main(int argc, char** argv) {
    Capture capture(argc, argv);

    // 1. A window with an OpenGL 4.1 context.
    glfwInit();
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 1);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GLFW_TRUE);
    glfwWindowHint(GLFW_SAMPLES, 4);  // smoother lines
    capture.windowHints();
    GLFWwindow* window = glfwCreateWindow(capture.width, capture.height,
                                          "Stage 1: rays in 2D", nullptr, nullptr);
    glfwMakeContextCurrent(window);

    // 2. The shader program, and one buffer to hold points.
    GLuint program = makeProgram(VERTEX_SHADER, FRAGMENT_SHADER);
    GLuint vao, vbo;
    glGenVertexArrays(1, &vao);
    glBindVertexArray(vao);
    glGenBuffers(1, &vbo);
    glBindBuffer(GL_ARRAY_BUFFER, vbo);
    glEnableVertexAttribArray(0);  // attribute 0 is aPos
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, sizeof(Vec2), nullptr);

    // 3. Trace a fan of parallel rays, once.
    const float viewWidth = 26.0f;
    std::vector<Ray> rays;
    for (float y = -13.5f; y <= 13.5f; y += 1.0f)
        rays.push_back(traceRay({-viewWidth, y}, {1.0f, 0.0f}));

    // 4. Draw, over and over.
    while (!glfwWindowShouldClose(window)) {
        int width, height;
        glfwGetFramebufferSize(window, &width, &height);
        glViewport(0, 0, width, height);
        glClearColor(0.047f, 0.059f, 0.086f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);

        glUseProgram(program);
        float viewHeight = viewWidth * float(height) / float(width);
        glUniform2f(glGetUniformLocation(program, "uViewSize"), viewWidth, viewHeight);

        for (const Ray& ray : rays) {
            if (ray.captured) draw(program, GL_LINE_STRIP, ray.points, 1.0f, 0.37f, 0.43f);
            else              draw(program, GL_LINE_STRIP, ray.points, 0.36f, 0.78f, 1.0f);
        }

        // One more ray, aimed with the mouse.
        double mouseX, mouseY;
        int windowWidth, windowHeight;
        glfwGetCursorPos(window, &mouseX, &mouseY);
        glfwGetWindowSize(window, &windowWidth, &windowHeight);
        float aim = viewHeight * (1.0f - 2.0f * float(mouseY) / float(windowHeight));
        if (capture.on()) aim = 9.0f - 9.0f * capture.progress();
        Ray aimed = traceRay({-viewWidth, aim}, {1.0f, 0.0f});
        draw(program, GL_LINE_STRIP, aimed.points, 1.0f, 0.88f, 0.4f);

        draw(program, GL_LINE_STRIP, circle(3.0f * M), 0.54f, 0.58f, 0.65f);  // photon sphere
        draw(program, GL_TRIANGLE_FAN, circle(2.0f * M), 0.0f, 0.0f, 0.0f);
        draw(program, GL_LINE_STRIP, circle(2.0f * M), 1.0f, 0.71f, 0.33f);

        if (!capture.save()) break;
        glfwSwapBuffers(window);
        glfwPollEvents();
    }
    glfwTerminate();
    return 0;
}
