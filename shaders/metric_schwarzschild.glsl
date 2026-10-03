// Schwarzschild black hole in Cartesian Kerr-Schild form (units G = c = 1):
//
//     g_{mu nu} = eta_{mu nu} + f l_mu l_nu,     l_mu = (1, L),  |L| = 1
//     g^{mu nu} = eta^{mu nu} - f l^mu l^nu,     l^mu = (-1, L)
//
// We use the *outgoing* form (L points inward, L = -x/r). Rays are traced
// backwards in time from the camera, and in these coordinates a backward ray
// crosses r = 2M smoothly instead of stalling at the horizon.
//
// This file is the only place the spacetime is defined. To add Kerr, provide
// the same functions for the Kerr f and L (with spin a).
//
// Written in the GLSL/C++ common subset: it is also #included by src/physics.h.

const float M = 1.0;

float metric_horizon() { return 2.0 * M; }
float metric_isco() { return 6.0 * M; }

// Angular velocity d(phi)/dt of a circular equatorial orbit of radius r.
float metric_omega(float r) { return sqrt(M / (r * r * r)); }

// f and L at x, plus the two gradients the geodesic equation needs:
// grad f, and grad (L . p) with the momentum p held fixed.
void metric_eval(vec3 x, vec3 p,
                 OUT(float) f, OUT(vec3) L,
                 OUT(vec3) gradf, OUT(vec3) gradLp) {
    float r = length(x);
    vec3 n = x / r;
    f = 2.0 * M / r;
    L = -n;
    gradf = -(2.0 * M / (r * r)) * n;
    gradLp = -(p - n * dot(n, p)) / r;
}
