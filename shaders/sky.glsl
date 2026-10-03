// Background seen by rays that escape: a procedural starfield, or a
// latitude/longitude grid that makes the lensing distortion easy to read.

float hash13(vec3 p) {
    p = fract(p * 0.1031);
    p += dot(p, p.zyx + 31.32);
    return fract((p.x + p.y) * p.z);
}

vec3 hash33(vec3 p) {
    p = fract(p * vec3(0.1031, 0.1030, 0.0973));
    p += dot(p, p.yxz + 33.33);
    return fract((p.xxy + p.yxx) * p.zyx);
}

float valueNoise(vec3 p) {
    vec3 i = floor(p);
    vec3 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(mix(hash13(i), hash13(i + vec3(1, 0, 0)), f.x),
                   mix(hash13(i + vec3(0, 1, 0)), hash13(i + vec3(1, 1, 0)), f.x), f.y),
               mix(mix(hash13(i + vec3(0, 0, 1)), hash13(i + vec3(1, 0, 1)), f.x),
                   mix(hash13(i + vec3(0, 1, 1)), hash13(i + vec3(1, 1, 1)), f.x), f.y), f.z);
}

float fbm(vec3 p) {
    float sum = 0.0, amp = 0.5;
    for (int i = 0; i < 4; ++i) {
        sum += amp * valueNoise(p);
        p = p * 2.03 + 17.1;
        amp *= 0.5;
    }
    return sum;
}

vec3 starLayer(vec3 dir, float cells) {
    vec3 q = dir * cells;
    vec3 id = floor(q);
    vec3 rnd = hash33(id);
    // Keep the star away from the cell walls so it is never clipped.
    float d = length(q - (id + 0.2 + 0.6 * rnd));
    float brightness = pow(hash13(id + 7.0), 6.0) * 12.0 + 0.3;
    vec3 tint = mix(vec3(1.0, 0.75, 0.55), vec3(0.6, 0.75, 1.0), hash13(id + 3.0));
    return tint * brightness * smoothstep(0.12, 0.0, d);
}

vec3 skyStars(vec3 dir) {
    vec3 col = starLayer(dir, 70.0) + starLayer(dir, 130.0) * 0.6 + starLayer(dir, 220.0) * 0.35;
    // A faint galactic band, tilted against the disk plane.
    vec3 axis = normalize(vec3(0.3, 0.5, 0.8));
    float band = exp(-12.0 * pow(dot(dir, axis), 2.0));
    float clouds = fbm(dir * 4.0);
    col += band * clouds * clouds * vec3(0.35, 0.3, 0.45) * 0.5;
    return col;
}

vec3 skyGrid(vec3 dir) {
    const float PI = 3.14159265;
    float theta = acos(clamp(dir.z, -1.0, 1.0));
    float phi = atan(dir.y, dir.x);
    // Four colours by quadrant so you can tell which part of the sky a pixel shows.
    vec3 base = dir.z > 0.0
        ? (dir.y > 0.0 ? vec3(0.9, 0.25, 0.2) : vec3(0.95, 0.75, 0.15))
        : (dir.y > 0.0 ? vec3(0.15, 0.45, 0.9) : vec3(0.2, 0.75, 0.4));
    float spacing = PI / 12.0;  // 15 degrees
    float lt = abs(fract(theta / spacing + 0.5) - 0.5) * spacing;
    float lp = abs(fract(phi / spacing + 0.5) - 0.5) * spacing * max(sin(theta), 0.05);
    float line = smoothstep(0.012, 0.004, min(lt, lp));
    return mix(base * 0.22, vec3(1.0), line);
}

vec3 sky(vec3 dir) {
    return uGrid != 0 ? skyGrid(dir) : skyStars(dir);
}
