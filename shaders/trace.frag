#version 410 core
// The ray tracer. Each pixel sends one light ray backwards in time from the
// camera and integrates its geodesic until it falls into the hole, escapes
// to the sky, or runs out of steps; disk crossings on the way add light.

#define OUT(T) out T
#define INOUT(T) inout T

uniform vec2 uResolution;
uniform vec3 uCamPos;
uniform vec4 uTetT;          // time components of the camera tetrad e0..e3
uniform vec3 uTetS0, uTetS1, uTetS2, uTetS3;  // spatial parts: e0, right, up, forward
uniform float uTanHalfFov;
uniform float uTime;
uniform float uEscapeR;
uniform float uQuality;      // step scale, smaller = finer
uniform int uMaxSteps;
uniform int uDisk, uGrid, uDoppler;
uniform float uDiskOuter, uDiskTemp, uDiskBrightness;

#include "metric_schwarzschild.glsl"
#include "geodesic.glsl"
#include "sky.glsl"
#include "disk.glsl"

out vec4 fragColor;

void main() {
    vec2 uv = gl_FragCoord.xy / uResolution * 2.0 - 1.0;
    uv.x *= uResolution.x / uResolution.y;
    vec3 d = normalize(vec3(uv * uTanHalfFov, 1.0));  // (right, up, forward)

    vec3 x = uCamPos;
    vec3 p;
    float pt;
    camera_ray(d, x, uTetT, uTetS0, uTetS1, uTetS2, uTetS3, pt, p);

    vec3 color = vec3(0.0);
    float transmittance = 1.0;
    float horizon = metric_horizon();

    for (int i = 0; i < uMaxSteps; ++i) {
        float r = length(x);
        if (r < horizon) { transmittance = 0.0; break; }
        if (r > uEscapeR || transmittance < 0.01) break;

        vec3 x0 = x, p0 = p;
        // Negative step: p is the physical momentum, followed back in time.
        geodesic_rk4(x, p, pt, -geodesic_step(x, uQuality));

        if (uDisk != 0 && x0.z * x.z < 0.0) {
            float s = x0.z / (x0.z - x.z);
            vec4 disk = diskShade(mix(x0, x, s), mix(p0, p, s), pt);
            color += transmittance * disk.a * disk.rgb;
            transmittance *= 1.0 - disk.a;
        }
    }

    if (transmittance >= 0.01) {
        vec3 dx, dp;
        geodesic_rhs(x, p, pt, dx, dp);
        color += transmittance * sky(normalize(-dx));
    }
    fragColor = vec4(color, 1.0);
}
