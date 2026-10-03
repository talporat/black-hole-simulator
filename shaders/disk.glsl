// Thin accretion disk in the equatorial plane, between the ISCO and uDiskOuter.

// Approximate colour of a blackbody at temperature T (kelvin), linear RGB,
// normalised to max component ~1 (after Tanner Helland's fit).
vec3 blackbody(float T) {
    float t = clamp(T, 1000.0, 40000.0) / 100.0;
    vec3 c;
    if (t <= 66.0) {
        c.r = 1.0;
        c.g = 0.39008158 * log(t) - 0.63184144;
        c.b = t <= 19.0 ? 0.0 : 0.54320679 * log(t - 10.0) - 1.19625409;
    } else {
        c.r = 1.29293619 * pow(t - 60.0, -0.1332047592);
        c.g = 1.12989086 * pow(t - 60.0, -0.0755148492);
        c.b = 1.0;
    }
    return pow(clamp(c, 0.0, 1.0), vec3(2.2));
}

// Gas pattern at (r, phi) after shearing by the Keplerian rotation for a time tau.
float diskPattern(float r, float phi, float tau) {
    float a = phi - metric_omega(r) * tau;
    return fbm(vec3(cos(a) * 3.0, sin(a) * 3.0, r * 1.6));
}

// Emission and opacity where a ray with momentum (pt, p) crosses the disk at hit.
// The photon energy seen by the camera is 1 (see camera_ray), so the redshift
// factor is g = E_observed / E_emitted = -1 / (p_mu u^mu), with u the
// 4-velocity of the orbiting gas. g contains both the Doppler shift and the
// gravitational redshift.
vec4 diskShade(vec3 hit, vec3 p, float pt) {
    float r = length(hit.xy);
    float rin = metric_isco();
    if (r < rin || r > uDiskOuter) return vec4(0.0);

    // Circular orbit: u = u^t (1, v), with u^t fixed by g(u, u) = -1.
    vec3 v = metric_omega(r) * vec3(-hit.y, hit.x, 0.0);
    float f; vec3 L; vec3 gf; vec3 gLp;
    metric_eval(hit, v, f, L, gf, gLp);
    float lv = 1.0 + dot(L, v);
    float ut = inversesqrt(1.0 - dot(v, v) - f * lv * lv);
    float g = uDoppler != 0 ? -1.0 / (ut * (pt + dot(p, v))) : 1.0;

    // Temperature profile of a standard thin disk, peak normalised to 1.
    float x = rin / r;
    float temp = pow(x, 0.75) * pow(1.0 - sqrt(x), 0.25) / 0.488;

    // Blackbody: observed temperature scales with g, intensity with g^4.
    float tObs = g * temp;
    vec3 emission = blackbody(uDiskTemp * tObs) * pow(tObs, 4.0);

    // Two copies of the pattern half a cycle apart, cross-faded, so the
    // differential rotation can shear the gas forever without winding it up.
    const float PERIOD = 80.0;
    float phi = atan(hit.y, hit.x);
    float c0 = fract(uTime / PERIOD), c1 = fract(uTime / PERIOD + 0.5);
    float n = mix(diskPattern(r, phi + 2.0, c0 * PERIOD), diskPattern(r, phi, c1 * PERIOD),
                  abs(2.0 * c0 - 1.0));
    float density = 0.25 + 1.5 * n * n;

    float edge = smoothstep(uDiskOuter, uDiskOuter * 0.7, r) * smoothstep(rin, rin * 1.08, r);
    float alpha = clamp((0.55 + density) * edge, 0.0, 0.98);
    return vec4(emission * density * uDiskBrightness, alpha);
}
