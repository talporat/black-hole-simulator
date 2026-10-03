#version 410 core
// Second pass: squeeze the huge range of brightness in the traced image
// into the 0..1 range a monitor can show.
uniform sampler2D uImage;
uniform vec2 uResolution;
out vec4 fragColor;

void main() {
    vec3 c = texture(uImage, gl_FragCoord.xy / uResolution).rgb;
    c = (c * (2.51 * c + 0.03)) / (c * (2.43 * c + 0.59) + 0.14);  // filmic curve
    fragColor = vec4(pow(clamp(c, 0.0, 1.0), vec3(1.0 / 2.2)), 1.0);
}
