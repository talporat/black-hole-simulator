// Null geodesics from the Hamiltonian
//
//     H = 1/2 g^{mu nu} p_mu p_nu = 1/2 ( -p_t^2 + |p|^2 - f A^2 ),   A = l^mu p_mu = L.p - p_t
//
//     dx^i/dlambda =  dH/dp_i = p_i - f A L_i
//     dp_i/dlambda = -dH/dx^i = 1/2 A^2 grad f + f A grad(L.p)
//
// The metric is stationary, so p_t is constant along a ray and is passed in
// separately. Nothing here knows which spacetime it is integrating: all of
// that comes from metric_eval().
//
// Written in the GLSL/C++ common subset: it is also #included by src/physics.h.

float geodesic_hamiltonian(vec3 x, vec3 p, float pt) {
    float f; vec3 L; vec3 gf; vec3 gLp;
    metric_eval(x, p, f, L, gf, gLp);
    float A = dot(L, p) - pt;
    return 0.5 * (-pt * pt + dot(p, p) - f * A * A);
}

void geodesic_rhs(vec3 x, vec3 p, float pt,
                  OUT(vec3) dx, OUT(vec3) dp) {
    float f; vec3 L; vec3 gf; vec3 gLp;
    metric_eval(x, p, f, L, gf, gLp);
    float A = dot(L, p) - pt;
    dx = p - f * A * L;
    dp = 0.5 * A * A * gf + f * A * gLp;
}

// One classical Runge-Kutta 4 step of size h in the affine parameter.
void geodesic_rk4(INOUT(vec3) x, INOUT(vec3) p, float pt, float h) {
    vec3 k1x; vec3 k1p; vec3 k2x; vec3 k2p;
    vec3 k3x; vec3 k3p; vec3 k4x; vec3 k4p;
    geodesic_rhs(x, p, pt, k1x, k1p);
    geodesic_rhs(x + 0.5 * h * k1x, p + 0.5 * h * k1p, pt, k2x, k2p);
    geodesic_rhs(x + 0.5 * h * k2x, p + 0.5 * h * k2p, pt, k3x, k3p);
    geodesic_rhs(x + h * k3x, p + h * k3p, pt, k4x, k4p);
    x = x + (h / 6.0) * (k1x + 2.0 * k2x + 2.0 * k3x + k4x);
    p = p + (h / 6.0) * (k1p + 2.0 * k2p + 2.0 * k3p + k4p);
}

// Step length: proportional to r, so steps are short where spacetime is
// strongly curved and long far away. quality scales it (smaller = finer).
float geodesic_step(vec3 x, float quality) {
    return quality * max(0.02, 0.06 * length(x));
}

// Momentum of the photon that reaches the camera from local direction d.
//
// The camera carries an orthonormal tetrad e_0..e_3 (e_0 = its 4-velocity,
// e_1 = right, e_2 = up, e_3 = forward). tetT holds the four time components,
// s0..s3 the spatial parts. A photon seen in direction d travels along -d, so
// with unit energy its 4-momentum is k = e_0 - d^i e_i. Lowering the index
// with g_{mu nu} = eta + f l l gives the covariant p the integrator uses.
void camera_ray(vec3 d, vec3 camPos,
                vec4 tetT, vec3 s0, vec3 s1, vec3 s2, vec3 s3,
                OUT(float) pt, OUT(vec3) p) {
    float kt = tetT.x - (d.x * tetT.y + d.y * tetT.z + d.z * tetT.w);
    vec3 k = s0 - (d.x * s1 + d.y * s2 + d.z * s3);
    float f; vec3 L; vec3 gf; vec3 gLp;
    metric_eval(camPos, k, f, L, gf, gLp);
    float lk = kt + dot(L, k);
    pt = -kt + f * lk;
    p = k + f * lk * L;
}
