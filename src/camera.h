#pragma once
#include "math/vec.h"

// Orthonormal frame of a static observer: e_0 is the 4-velocity, e_1..e_3 are
// right / up / forward. t holds the time components, s[i] the spatial parts.
struct Tetrad {
    vec4 t;
    vec3 s[4];
};

// Orbit camera that always looks at the black hole. z is the disk axis.
struct Camera {
    float dist = 30.0f;        // in units of M
    float incl = 1.4f;         // angle from the +z axis, radians
    float azim = 0.0f;
    float fovY = 0.9f;         // vertical field of view, radians
    float roll = 0.0f;         // rotation about the viewing direction, radians

    vec3 position() const;
    Tetrad tetrad() const;
};
