#include "gl/shader.h"

#include <cstdio>
#include <fstream>
#include <sstream>

namespace {

// Reads a file, splicing in `#include "x"` lines recursively.
bool readSource(const std::string& path, std::string& out, int depth = 0) {
    std::ifstream in(path);
    if (!in || depth > 8) {
        std::fprintf(stderr, "shader: cannot read %s\n", path.c_str());
        return false;
    }
    std::string dir = path.substr(0, path.find_last_of('/') + 1);
    std::string line;
    while (std::getline(in, line)) {
        size_t inc = line.find("#include");
        if (inc != std::string::npos && line.find_first_not_of(" \t") == inc) {
            size_t a = line.find('"'), b = line.rfind('"');
            if (a == std::string::npos || a == b) {
                std::fprintf(stderr, "shader: bad include in %s: %s\n", path.c_str(), line.c_str());
                return false;
            }
            if (!readSource(dir + line.substr(a + 1, b - a - 1), out, depth + 1)) return false;
        } else {
            out += line;
            out += '\n';
        }
    }
    return true;
}

void printNumbered(const std::string& src) {
    std::istringstream in(src);
    std::string line;
    for (int n = 1; std::getline(in, line); ++n) std::fprintf(stderr, "%4d| %s\n", n, line.c_str());
}

GLuint compile(GLenum type, const std::string& path) {
    std::string src;
    if (!readSource(path, src)) return 0;
    GLuint s = glCreateShader(type);
    const char* c = src.c_str();
    glShaderSource(s, 1, &c, nullptr);
    glCompileShader(s);
    GLint ok = 0;
    glGetShaderiv(s, GL_COMPILE_STATUS, &ok);
    if (!ok) {
        char log[4096];
        glGetShaderInfoLog(s, sizeof log, nullptr, log);
        printNumbered(src);
        std::fprintf(stderr, "shader: %s failed to compile (line numbers refer to the listing above):\n%s\n",
                     path.c_str(), log);
        glDeleteShader(s);
        return 0;
    }
    return s;
}

}  // namespace

bool Shader::load(const std::string& vertPath, const std::string& fragPath) {
    GLuint vs = compile(GL_VERTEX_SHADER, vertPath);
    GLuint fs = compile(GL_FRAGMENT_SHADER, fragPath);
    if (!vs || !fs) return false;
    GLuint prog = glCreateProgram();
    glAttachShader(prog, vs);
    glAttachShader(prog, fs);
    glLinkProgram(prog);
    glDeleteShader(vs);
    glDeleteShader(fs);
    GLint ok = 0;
    glGetProgramiv(prog, GL_LINK_STATUS, &ok);
    if (!ok) {
        char log[4096];
        glGetProgramInfoLog(prog, sizeof log, nullptr, log);
        std::fprintf(stderr, "shader: link failed for %s:\n%s\n", fragPath.c_str(), log);
        glDeleteProgram(prog);
        return false;
    }
    if (program_) glDeleteProgram(program_);
    program_ = prog;
    return true;
}

void Shader::set(const char* name, int v) const { glUniform1i(glGetUniformLocation(program_, name), v); }
void Shader::set(const char* name, float v) const { glUniform1f(glGetUniformLocation(program_, name), v); }
void Shader::set(const char* name, vec2 v) const { glUniform2f(glGetUniformLocation(program_, name), v.x, v.y); }
void Shader::set(const char* name, vec3 v) const { glUniform3f(glGetUniformLocation(program_, name), v.x, v.y, v.z); }
void Shader::set(const char* name, vec4 v) const {
    glUniform4f(glGetUniformLocation(program_, name), v.x, v.y, v.z, v.w);
}
