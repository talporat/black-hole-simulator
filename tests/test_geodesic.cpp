// Checks the shader's geodesic code (compiled as C++ via physics.h) against
// known Schwarzschild results.
#include <cstdio>
#include <cmath>
#include "physics.h"
#include "camera.h"

static int failures = 0;

static void check(bool ok, const char* name, const char* fmt, double a = 0, double b = 0) {
    std::printf("[%s] %s: ", ok ? " ok " : "FAIL", name);
    std::printf(fmt, a, b);
    std::printf("\n");
    if (!ok) ++failures;
}

// Photon at (R, 0, 0) with p_t = -1 and impact parameter b = L_z / E, moving
// outward, so that tracing it backwards (h < 0) sends it towards the hole.
static void launch(float R, float b, vec3& x, vec3& p) {
    x = vec3(R, 0, 0);
    float f = 2.0f * M / R;
    float py = b / R;
    // H = 0 with L = -x/r:  (1-f) px^2 + 2 f px + (py^2 - 1 - f) = 0
    float disc = f * f - (1.0f - f) * (py * py - 1.0f - f);
    float px = (-f + std::sqrt(max(disc, 0.0f))) / (1.0f - f);
    p = vec3(px, py, 0);
}

enum Fate { CAPTURED, ESCAPED, UNDECIDED };

static Fate trace(vec3& x, vec3& p, float pt, float rEscape, float quality = 1.0f) {
    for (int i = 0; i < 200000; ++i) {
        float r = length(x);
        if (r < metric_horizon()) return CAPTURED;
        if (r > rEscape) return ESCAPED;
        geodesic_rk4(x, p, pt, -geodesic_step(x, quality));
    }
    return UNDECIDED;
}

int main() {
    const float pt = -1.0f;
    const float bCrit = 3.0f * std::sqrt(3.0f) * M;

    // 1. Conserved quantities along a strongly bent ray.
    {
        vec3 x, p;
        launch(30.0f, 6.0f, x, p);
        float maxH = 0, maxdL = 0;
        float L0 = x.x * p.y - x.y * p.x;
        for (int i = 0; i < 2000 && length(x) < 31.0f; ++i) {
            geodesic_rk4(x, p, pt, -geodesic_step(x, 1.0f));
            maxH = max(maxH, std::fabs(geodesic_hamiltonian(x, p, pt)));
            maxdL = max(maxdL, std::fabs(x.x * p.y - x.y * p.x - L0));
        }
        check(maxH < 1e-3f, "H stays zero", "max |H| = %.2e", maxH);
        check(maxdL < 1e-3f, "angular momentum conserved", "max |dL| = %.2e", maxdL);
    }

    // 2. Critical impact parameter b = 3 sqrt(3) M separates capture from escape.
    {
        vec3 x, p;
        launch(50.0f, bCrit * 1.01f, x, p);
        Fate above = trace(x, p, pt, 51.0f);
        launch(50.0f, bCrit * 0.99f, x, p);
        Fate below = trace(x, p, pt, 51.0f);
        check(above == ESCAPED, "b = 1.01 b_crit escapes", "fate %g", above);
        check(below == CAPTURED, "b = 0.99 b_crit is captured", "fate %g", below);
    }

    // 3. Photon sphere: a tangential ray at r = 3M stays there. The orbit is
    //    unstable (errors grow like e^phi), so in single precision we follow
    //    it for half a turn.
    {
        vec3 x, p;
        launch(3.0f * M, bCrit, x, p);
        float h = 0.01f, phi = 0, maxDev = 0;
        vec3 prev = x;
        while (phi < 3.14159265f) {
            geodesic_rk4(x, p, pt, -h);
            maxDev = max(maxDev, std::fabs(length(x) - 3.0f * M));
            phi += std::acos(clamp(dot(normalize(prev), normalize(x)), -1.0f, 1.0f));
            prev = x;
            if (maxDev > 1.0f) break;
        }
        check(maxDev < 0.02f, "photon sphere orbit at r = 3M", "max |r - 3M| = %.4f", maxDev);
    }

    // 4. Weak-field deflection 4M/b (+ 15 pi/4 (M/b)^2 at second order).
    {
        float b = 100.0f, R = 5000.0f;
        vec3 x, p, v0, v1, dp;
        launch(R, b, x, p);
        geodesic_rhs(x, p, pt, v0, dp);
        Fate fate = trace(x, p, pt, R * 1.0001f, 0.25f);
        geodesic_rhs(x, p, pt, v1, dp);
        float angle = std::acos(clamp(dot(normalize(v0), normalize(v1)), -1.0f, 1.0f));
        float expect = 4.0f * M / b + 3.75f * 3.14159265f * (M / b) * (M / b);
        check(fate == ESCAPED && std::fabs(angle - expect) < 0.05f * expect, "weak-field deflection",
              "angle = %.5f, expected %.5f", angle, expect);
    }

    // 5. Shadow edge seen by the camera: sin(alpha) = b_crit / D * sqrt(1 - 2M/D).
    //    Exercises the tetrad and camera_ray as well as the integrator.
    {
        Camera cam;
        cam.dist = 20.0f;
        cam.incl = 1.2f;
        cam.azim = 0.7f;
        Tetrad tet = cam.tetrad();
        float lo = 0.0f, hi = 0.6f;
        for (int i = 0; i < 20; ++i) {
            float a = 0.5f * (lo + hi);
            vec3 d(std::sin(a) * 0.6f, std::sin(a) * 0.8f, std::cos(a));
            vec3 x = cam.position(), p;
            float rayPt;
            camera_ray(d, x, tet.t, tet.s[0], tet.s[1], tet.s[2], tet.s[3], rayPt, p);
            if (trace(x, p, rayPt, 40.0f, 0.5f) == CAPTURED) lo = a; else hi = a;
        }
        float expect = std::asin(bCrit / cam.dist * std::sqrt(1.0f - 2.0f * M / cam.dist));
        check(std::fabs(lo - expect) < 2e-3f, "shadow angular radius", "alpha = %.5f, expected %.5f", lo, expect);
    }

    std::printf("%s\n", failures ? "FAILED" : "all tests passed");
    return failures ? 1 : 0;
}
