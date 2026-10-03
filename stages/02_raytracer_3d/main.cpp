// Stage 2: a 3D ray tracer. All the physics moves into trace.frag, which the
// GPU runs for every pixel. This file only sets up the window, tells the
// shader where the camera is, and draws one triangle.
// Drag to orbit, scroll to zoom, G toggles the grid.
#include <cmath>
#include <cstdio>
#include <fstream>
#include <sstream>
#include <string>

#define GL_SILENCE_DEPRECATION
#include <OpenGL/gl3.h>
#define GLFW_INCLUDE_NONE
#include <GLFW/glfw3.h>
#include "../common/capture.h"

struct Vec3 { float x, y, z; };
Vec3 operator*(float s, Vec3 a) { return {s * a.x, s * a.y, s * a.z}; }
Vec3 cross(Vec3 a, Vec3 b) {
    return {a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x};
}
Vec3 normalize(Vec3 a) {
    return (1.0f / std::sqrt(a.x * a.x + a.y * a.y + a.z * a.z)) * a;
}

// ---------------------------------------------------------------- shaders

std::string readFile(const std::string& path) {
    std::ifstream file(path);
    std::stringstream text;
    text << file.rdbuf();
    return text.str();
}

GLuint compileShader(GLenum type, const std::string& path) {
    std::string text = readFile(path);
    const char* source = text.c_str();
    GLuint shader = glCreateShader(type);
    glShaderSource(shader, 1, &source, nullptr);
    glCompileShader(shader);
    GLint ok = 0;
    glGetShaderiv(shader, GL_COMPILE_STATUS, &ok);
    if (!ok) {
        char log[2048];
        glGetShaderInfoLog(shader, sizeof log, nullptr, log);
        std::fprintf(stderr, "%s:\n%s\n", path.c_str(), log);
    }
    return shader;
}

GLuint makeProgram(const std::string& vertexPath, const std::string& fragmentPath) {
    GLuint program = glCreateProgram();
    glAttachShader(program, compileShader(GL_VERTEX_SHADER, vertexPath));
    glAttachShader(program, compileShader(GL_FRAGMENT_SHADER, fragmentPath));
    glLinkProgram(program);
    return program;
}

// ---------------------------------------------------------------- camera

// The camera orbits the hole: two angles and a distance.
float camYaw = 0.6f, camPitch = 0.25f, camDistance = 30.0f;
bool showGrid = true, dragging = false;
double lastX = 0, lastY = 0;

void onMouseButton(GLFWwindow* window, int button, int action, int) {
    if (button == GLFW_MOUSE_BUTTON_LEFT) dragging = (action == GLFW_PRESS);
    glfwGetCursorPos(window, &lastX, &lastY);
}

void onMouseMove(GLFWwindow*, double x, double y) {
    if (dragging) {
        camYaw -= 0.006f * float(x - lastX);
        camPitch += 0.006f * float(y - lastY);
        camPitch = std::fmax(-1.5f, std::fmin(1.5f, camPitch));
    }
    lastX = x;
    lastY = y;
}

void onScroll(GLFWwindow*, double, double amount) {
    camDistance *= std::exp(-0.08f * float(amount));
    camDistance = std::fmax(4.0f, std::fmin(60.0f, camDistance));
}

void onKey(GLFWwindow*, int key, int, int action, int) {
    if (key == GLFW_KEY_G && action == GLFW_PRESS) showGrid = !showGrid;
}

void setVec3(GLuint program, const char* name, Vec3 v) {
    glUniform3f(glGetUniformLocation(program, name), v.x, v.y, v.z);
}

// ---------------------------------------------------------------- main

int main(int argc, char** argv) {
    Capture capture(argc, argv);

    glfwInit();
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 1);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GLFW_TRUE);
    capture.windowHints();
    GLFWwindow* window = glfwCreateWindow(capture.width, capture.height,
                                          "Stage 2: ray tracer", nullptr, nullptr);
    glfwMakeContextCurrent(window);
    glfwSetMouseButtonCallback(window, onMouseButton);
    glfwSetCursorPosCallback(window, onMouseMove);
    glfwSetScrollCallback(window, onScroll);
    glfwSetKeyCallback(window, onKey);

    std::string dir = STAGE_DIR;
    GLuint program = makeProgram(dir + "/fullscreen.vert", dir + "/trace.frag");

    // The triangle's corners come from the vertex shader, so there is
    // no data to upload. OpenGL still wants a vertex array to be bound.
    GLuint vao;
    glGenVertexArrays(1, &vao);
    glBindVertexArray(vao);

    while (!glfwWindowShouldClose(window)) {
        if (capture.on()) {
            camYaw = 0.6f + 1.2f * capture.progress();
            for (int i = 1; i + 1 < argc; ++i)
                if (std::string(argv[i]) == "--grid") showGrid = argv[i + 1][0] == '1';
        }

        // Where the camera is, and which way its three axes point.
        Vec3 position = camDistance * Vec3{std::cos(camPitch) * std::cos(camYaw),
                                           std::cos(camPitch) * std::sin(camYaw),
                                           std::sin(camPitch)};
        Vec3 forward = normalize(-1.0f * position);
        Vec3 right = normalize(cross(forward, {0.0f, 0.0f, 1.0f}));
        Vec3 up = cross(right, forward);

        int width, height;
        glfwGetFramebufferSize(window, &width, &height);
        glViewport(0, 0, width, height);

        // Hand those to the shader as uniforms, then draw the triangle.
        glUseProgram(program);
        glUniform2f(glGetUniformLocation(program, "uResolution"), float(width), float(height));
        glUniform1i(glGetUniformLocation(program, "uGrid"), showGrid ? 1 : 0);
        setVec3(program, "uCamPos", position);
        setVec3(program, "uCamRight", right);
        setVec3(program, "uCamUp", up);
        setVec3(program, "uCamForward", forward);
        glDrawArrays(GL_TRIANGLES, 0, 3);

        if (!capture.save()) break;
        glfwSwapBuffers(window);
        glfwPollEvents();
    }
    glfwTerminate();
    return 0;
}
