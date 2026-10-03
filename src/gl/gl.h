// OpenGL 4.1 core declarations. macOS ships them in the system framework, so
// no loader is needed there; other platforms need a loader such as glad.
#pragma once
#ifdef __APPLE__
#define GL_SILENCE_DEPRECATION
#include <OpenGL/gl3.h>
#else
#error "Add an OpenGL function loader (e.g. glad) for this platform."
#endif
