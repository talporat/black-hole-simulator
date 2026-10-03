// Minimal GLSL-style vector math. Names and semantics follow GLSL so that the
// physics shaders (shaders/metric_*.glsl, shaders/geodesic.glsl) also compile as C++.
#pragma once
#include <cmath>

struct vec2 {
    float x, y;
    vec2() : x(0), y(0) {}
    explicit vec2(float s) : x(s), y(s) {}
    vec2(float x_, float y_) : x(x_), y(y_) {}
};

struct vec3 {
    float x, y, z;
    vec3() : x(0), y(0), z(0) {}
    explicit vec3(float s) : x(s), y(s), z(s) {}
    vec3(float x_, float y_, float z_) : x(x_), y(y_), z(z_) {}
    vec3& operator+=(vec3 b) { x += b.x; y += b.y; z += b.z; return *this; }
    vec3& operator-=(vec3 b) { x -= b.x; y -= b.y; z -= b.z; return *this; }
    vec3& operator*=(float s) { x *= s; y *= s; z *= s; return *this; }
};

struct vec4 {
    float x, y, z, w;
    vec4() : x(0), y(0), z(0), w(0) {}
    explicit vec4(float s) : x(s), y(s), z(s), w(s) {}
    vec4(float x_, float y_, float z_, float w_) : x(x_), y(y_), z(z_), w(w_) {}
};

inline vec3 operator+(vec3 a, vec3 b) { return vec3(a.x + b.x, a.y + b.y, a.z + b.z); }
inline vec3 operator-(vec3 a, vec3 b) { return vec3(a.x - b.x, a.y - b.y, a.z - b.z); }
inline vec3 operator-(vec3 a) { return vec3(-a.x, -a.y, -a.z); }
inline vec3 operator*(vec3 a, vec3 b) { return vec3(a.x * b.x, a.y * b.y, a.z * b.z); }
inline vec3 operator*(vec3 a, float s) { return vec3(a.x * s, a.y * s, a.z * s); }
inline vec3 operator*(float s, vec3 a) { return a * s; }
inline vec3 operator/(vec3 a, float s) { return vec3(a.x / s, a.y / s, a.z / s); }

inline float dot(vec3 a, vec3 b) { return a.x * b.x + a.y * b.y + a.z * b.z; }
inline vec3 cross(vec3 a, vec3 b) {
    return vec3(a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x);
}
inline float length(vec3 a) { return std::sqrt(dot(a, a)); }
inline vec3 normalize(vec3 a) { return a / length(a); }

inline float min(float a, float b) { return a < b ? a : b; }
inline float max(float a, float b) { return a > b ? a : b; }
inline float clamp(float v, float lo, float hi) { return min(max(v, lo), hi); }
inline float mix(float a, float b, float t) { return a + (b - a) * t; }
inline vec3 mix(vec3 a, vec3 b, float t) { return a + (b - a) * t; }
