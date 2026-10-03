#version 410 core
// Halves the resolution with a 4-tap box filter. The first pass also keeps
// only the bright part of the image (soft threshold).
uniform sampler2D uSrc;
uniform vec2 uTexel;       // 1 / source size
uniform float uThreshold;  // 0 disables the threshold
in vec2 vUV;
out vec4 fragColor;

void main() {
    vec3 c = 0.25 * (texture(uSrc, vUV + uTexel * vec2(-1, -1)).rgb +
                     texture(uSrc, vUV + uTexel * vec2( 1, -1)).rgb +
                     texture(uSrc, vUV + uTexel * vec2(-1,  1)).rgb +
                     texture(uSrc, vUV + uTexel * vec2( 1,  1)).rgb);
    if (uThreshold > 0.0) {
        float lum = max(c.r, max(c.g, c.b));
        c *= max(lum - uThreshold, 0.0) / max(lum, 1e-4);
    }
    fragColor = vec4(c, 1.0);
}
