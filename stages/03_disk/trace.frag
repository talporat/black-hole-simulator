#version 410 core
// Stage 3: the ray tracer from stage 2, plus a glowing disk of gas that
// orbits the hole. New code is marked with "NEW".

uniform vec2 uResolution;   // size of the window in pixels
uniform vec3 uCamPos;       // where the camera is
uniform vec3 uCamRight;     // the camera's three axes
uniform vec3 uCamUp;
uniform vec3 uCamForward;
uniform int uGrid;          // 1 = draw a grid on the sky
uniform float uTime;        // NEW: seconds since the program started
uniform int uDoppler;       // NEW: 1 = apply the redshift factor g

out vec4 fragColor;

const float M = 1.0;

// ------------------------------------------------------------ physics
// Unchanged from stage 2.

void derivatives(vec3 x, vec3 p, float pt, out vec3 dx, out vec3 dp) {
    float r = length(x);
    vec3 L = x / r;
    float f = 2.0 * M / r;
    vec3 gradF = (-f / r) * L;
    vec3 gradLp = (p - dot(L, p) * L) / r;
    float A = dot(L, p) - pt;

    dx = p - f * A * L;                          // rule 1
    dp = 0.5 * A * A * gradF + f * A * gradLp;   // rule 2
}

float photonEnergy(vec3 x, vec3 p) {
    float r = length(x);
    float f = 2.0 * M / r;
    float Lp = dot(x, p) / r;
    float a = -(1.0 + f);
    float b = 2.0 * f * Lp;
    float c = dot(p, p) - f * Lp * Lp;
    return (-b + sqrt(b * b - 4.0 * a * c)) / (2.0 * a);
}

void rk4Step(inout vec3 x, inout vec3 p, float pt, float h) {
    vec3 k1x, k1p, k2x, k2p, k3x, k3p, k4x, k4p;
    derivatives(x, p, pt, k1x, k1p);
    derivatives(x + 0.5 * h * k1x, p + 0.5 * h * k1p, pt, k2x, k2p);
    derivatives(x + 0.5 * h * k2x, p + 0.5 * h * k2p, pt, k3x, k3p);
    derivatives(x + h * k3x, p + h * k3p, pt, k4x, k4p);
    x += (h / 6.0) * (k1x + 2.0 * k2x + 2.0 * k3x + k4x);
    p += (h / 6.0) * (k1p + 2.0 * k2p + 2.0 * k3p + k4p);
}

// ------------------------------------------------------------ the sky

float hash(vec3 p) {
    p = fract(p * 0.1031);
    p += dot(p, p.zyx + 31.32);
    return fract((p.x + p.y) * p.z);
}

// What you see looking out in direction dir: stars, or a grid.
vec3 sky(vec3 dir) {
    if (uGrid == 1) {
        float lat = asin(dir.z), lon = atan(dir.y, dir.x);
        vec2 cell = abs(fract(vec2(lat, lon) * 12.0 / 3.14159) - 0.5);
        float line = smoothstep(0.46, 0.49, max(cell.x, cell.y));
        vec3 base = dir.z > 0.0 ? vec3(0.07, 0.17, 0.36) : vec3(0.33, 0.11, 0.08);
        return mix(base, vec3(1.0), line);
    }
    vec3 cellId = floor(dir * 90.0);
    vec3 star = cellId + 0.2 + 0.6 * vec3(hash(cellId), hash(cellId + 1.0), hash(cellId + 2.0));
    float glow = smoothstep(0.14, 0.0, length(dir * 90.0 - star));
    return vec3(glow * (0.3 + 2.0 * pow(hash(cellId + 5.0), 6.0)));
}

// ------------------------------------------------------------ the disk (NEW)

const float DISK_INNER = 6.0 * M;    // the innermost stable orbit
const float DISK_OUTER = 20.0 * M;

float noise(vec3 p) {
    vec3 i = floor(p), t = fract(p);
    t = t * t * (3.0 - 2.0 * t);
    float a = mix(mix(hash(i), hash(i + vec3(1, 0, 0)), t.x),
                  mix(hash(i + vec3(0, 1, 0)), hash(i + vec3(1, 1, 0)), t.x), t.y);
    float b = mix(mix(hash(i + vec3(0, 0, 1)), hash(i + vec3(1, 0, 1)), t.x),
                  mix(hash(i + vec3(0, 1, 1)), hash(i + vec3(1, 1, 1)), t.x), t.y);
    return mix(a, b, t.z);
}

// The colour something glows at temperature T (in kelvin): red-hot to white-hot.
vec3 glowColour(float T) {
    float t = clamp(T, 1000.0, 40000.0) / 100.0;
    float red = t <= 66.0 ? 1.0 : 1.29 * pow(t - 60.0, -0.133);
    float green = t <= 66.0 ? 0.39 * log(t) - 0.63 : 1.13 * pow(t - 60.0, -0.0755);
    float blue = t >= 66.0 ? 1.0 : (t <= 19.0 ? 0.0 : 0.543 * log(t - 10.0) - 1.196);
    return pow(clamp(vec3(red, green, blue), 0.0, 1.0), vec3(2.2));
}

// Light from the disk where a ray crosses it. rgb = colour, a = how opaque.
vec4 diskLight(vec3 hit, vec3 p, float pt) {
    float r = length(hit.xy);
    if (r < DISK_INNER || r > DISK_OUTER) return vec4(0.0);

    // The gas moves in a circle. Kepler: angular speed = sqrt(M / r^3).
    float omega = sqrt(M / (r * r * r));
    vec3 v = omega * vec3(-hit.y, hit.x, 0.0);

    // Energy of the light as the gas sends it out, and as the camera
    // receives it. Our ray runs camera -> gas, the real light ran the
    // other way, hence the minus in front of dot(p, v).
    float gasClock = inversesqrt(1.0 - 3.0 * M / r);
    float cameraClock = inversesqrt(1.0 - 2.0 * M / length(uCamPos));
    float emitted = gasClock * (pt - dot(p, v));
    float received = cameraClock * pt;
    float g = uDoppler == 1 ? received / emitted : 1.0;

    // Hot near the inner edge, cooler further out.
    float s = DISK_INNER / r;
    float temperature = pow(s, 0.75) * pow(1.0 - sqrt(s), 0.25) / 0.488;

    // What we see: temperature times g, brightness times g^4.
    float seen = g * temperature;
    vec3 light = glowColour(4800.0 * seen) * pow(seen, 4.0);

    // Streaks of gas that rotate with the disk.
    float angle = atan(hit.y, hit.x) - omega * uTime * 4.0;
    float streaks = noise(vec3(3.0 * cos(angle), 3.0 * sin(angle), 1.6 * r));
    float density = 0.3 + 1.4 * streaks * streaks;

    float edge = smoothstep(DISK_OUTER, 0.7 * DISK_OUTER, r) * smoothstep(DISK_INNER, 1.08 * DISK_INNER, r);
    return vec4(1.8 * density * light, clamp((0.55 + density) * edge, 0.0, 0.98));
}

// ------------------------------------------------------------ one pixel

void main() {
    vec2 uv = gl_FragCoord.xy / uResolution * 2.0 - 1.0;
    uv.x *= uResolution.x / uResolution.y;

    vec3 x = uCamPos;
    vec3 p = normalize(uCamForward + 0.5 * (uv.x * uCamRight + uv.y * uCamUp));
    float pt = photonEnergy(x, p);

    vec3 colour = vec3(0.0);
    float remaining = 1.0;   // NEW: how much light can still get through

    for (int i = 0; i < 400; ++i) {
        float r = length(x);
        if (r < 2.0 * M) { remaining = 0.0; break; }
        if (r > 70.0 || remaining < 0.01) break;

        vec3 before = x;
        rk4Step(x, p, pt, 0.05 * r);

        // NEW: the disk lies in the plane z = 0. If z changed sign
        // during this step, the ray went through that plane.
        if (before.z * x.z < 0.0) {
            float t = before.z / (before.z - x.z);
            vec4 disk = diskLight(mix(before, x, t), p, pt);
            colour += remaining * disk.a * disk.rgb;
            remaining *= 1.0 - disk.a;
        }
    }

    if (remaining >= 0.01) {
        vec3 dx, dp;
        derivatives(x, p, pt, dx, dp);
        colour += remaining * sky(normalize(dx));
    }
    fragColor = vec4(colour, 1.0);
}
