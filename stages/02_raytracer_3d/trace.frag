#version 410 core
// Stage 2: the ray tracer. This program runs once for every pixel.
// It shoots one ray from the camera and follows it around the hole.

uniform vec2 uResolution;   // size of the window in pixels
uniform vec3 uCamPos;       // where the camera is
uniform vec3 uCamRight;     // the camera's three axes
uniform vec3 uCamUp;
uniform vec3 uCamForward;
uniform int uGrid;          // 1 = draw a grid on the sky

out vec4 fragColor;

const float M = 1.0;

// ------------------------------------------------------------ physics
// The same three functions as stage 1, with vec2 replaced by vec3.

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

// ------------------------------------------------------------ one pixel

void main() {
    // Where is this pixel on the screen? -1..1 in both directions.
    vec2 uv = gl_FragCoord.xy / uResolution * 2.0 - 1.0;
    uv.x *= uResolution.x / uResolution.y;

    // The ray through this pixel: starts at the camera, heads into the scene.
    vec3 x = uCamPos;
    vec3 p = normalize(uCamForward + 0.5 * (uv.x * uCamRight + uv.y * uCamUp));
    float pt = photonEnergy(x, p);

    for (int i = 0; i < 400; ++i) {
        float r = length(x);
        if (r < 2.0 * M) {                 // fell through the horizon
            fragColor = vec4(0.0, 0.0, 0.0, 1.0);
            return;
        }
        if (r > 70.0) break;               // escaped
        rk4Step(x, p, pt, 0.05 * r);
    }

    // Escaped: which way is it heading now? That part of the sky is the colour.
    vec3 dx, dp;
    derivatives(x, p, pt, dx, dp);
    fragColor = vec4(sky(normalize(dx)), 1.0);
}
