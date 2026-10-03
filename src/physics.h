// Compiles the physics shaders as C++ so the CPU (camera tetrad, unit tests)
// runs exactly the code the GPU runs.
#pragma once
#include "math/vec.h"

#define OUT(T) T&
#define INOUT(T) T&

namespace {
#include "../shaders/metric_schwarzschild.glsl"
#include "../shaders/geodesic.glsl"
}
