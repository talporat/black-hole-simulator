#pragma once
#include <string>
#include "gl/gl.h"
#include "math/vec.h"

// A linked vertex + fragment program. Sources are read from disk and may use
// `#include "file"` (resolved relative to the including file).
class Shader {
public:
    // Returns false (and prints the compiler log) on failure.
    bool load(const std::string& vertPath, const std::string& fragPath);
    void use() const { glUseProgram(program_); }

    void set(const char* name, int v) const;
    void set(const char* name, float v) const;
    void set(const char* name, vec2 v) const;
    void set(const char* name, vec3 v) const;
    void set(const char* name, vec4 v) const;

private:
    GLuint program_ = 0;
};
