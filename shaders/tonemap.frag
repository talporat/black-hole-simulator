#version 410 core
// HDR scene + bloom -> display: exposure, ACES filmic curve, gamma.
uniform sampler2D uScene;
uniform sampler2D uBloom;
uniform float uBloomStrength;
uniform float uExposure;
in vec2 vUV;
out vec4 fragColor;

vec3 aces(vec3 x) {
    return clamp((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), 0.0, 1.0);
}

void main() {
    vec3 c = texture(uScene, vUV).rgb;
    // With bloom off its texture is never written, so do not sample it at all.
    if (uBloomStrength > 0.0) c += uBloomStrength * texture(uBloom, vUV).rgb;
    fragColor = vec4(pow(aces(c * uExposure), vec3(1.0 / 2.2)), 1.0);
}
