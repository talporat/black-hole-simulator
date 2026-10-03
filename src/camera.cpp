#include "camera.h"
#include "physics.h"

namespace {

struct Vec4 {
    float t;
    vec3 s;
};

// g(a, b) for the Kerr-Schild metric eta + f l l, with l_mu = (1, L).
float inner(const Vec4& a, const Vec4& b, float f, vec3 L) {
    return -a.t * b.t + dot(a.s, b.s) + f * (a.t + dot(L, a.s)) * (b.t + dot(L, b.s));
}

Vec4 axpy(const Vec4& a, float s, const Vec4& b) { return {a.t + s * b.t, a.s + s * b.s}; }

}  // namespace

vec3 Camera::position() const {
    return dist * vec3(std::sin(incl) * std::cos(azim), std::sin(incl) * std::sin(azim), std::cos(incl));
}

Tetrad Camera::tetrad() const {
    vec3 pos = position();
    float f;
    vec3 L, gf, gLp;
    metric_eval(pos, vec3(0.0f), f, L, gf, gLp);

    vec3 forward = normalize(-pos);
    vec3 right = normalize(cross(forward, vec3(0, 0, 1)));
    vec3 up = cross(right, forward);
    if (roll != 0.0f) {  // tilt the horizon
        vec3 r0 = right, u0 = up;
        right = std::cos(roll) * r0 + std::sin(roll) * u0;
        up = std::cos(roll) * u0 - std::sin(roll) * r0;
    }

    // Static observer: u = d/dt normalised with g_tt = -(1 - f).
    Vec4 e0{1.0f / std::sqrt(1.0f - f), vec3(0.0f)};

    // Gram-Schmidt against the metric. Works for any Kerr-Schild f, L.
    Vec4 e[3];
    vec3 seeds[3] = {forward, up, right};
    for (int i = 0; i < 3; ++i) {
        Vec4 w{0.0f, seeds[i]};
        w = axpy(w, inner(w, e0, f, L), e0);  // g(e0, e0) = -1
        for (int j = 0; j < i; ++j)
            w = axpy(w, -inner(w, e[j], f, L), e[j]);
        float n = std::sqrt(inner(w, w, f, L));
        e[i] = {w.t / n, w.s / n};
    }

    Tetrad tet;
    tet.t = vec4(e0.t, e[2].t, e[1].t, e[0].t);
    tet.s[0] = e0.s;
    tet.s[1] = e[2].s;
    tet.s[2] = e[1].s;
    tet.s[3] = e[0].s;
    return tet;
}
