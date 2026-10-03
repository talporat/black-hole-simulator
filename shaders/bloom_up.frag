#version 410 core
// 3x3 tent filter; drawn with additive blending onto the next larger level.
uniform sampler2D uSrc;
uniform vec2 uTexel;
in vec2 vUV;
out vec4 fragColor;

void main() {
    vec3 c = vec3(0.0);
    for (int y = -1; y <= 1; ++y)
        for (int x = -1; x <= 1; ++x)
            c += texture(uSrc, vUV + uTexel * vec2(x, y)).rgb * float((2 - abs(x)) * (2 - abs(y)));
    fragColor = vec4(c / 16.0, 1.0);
}
