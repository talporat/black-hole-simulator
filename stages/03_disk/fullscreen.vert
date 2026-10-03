#version 410 core
// One triangle big enough to cover the whole screen, built from the
// vertex number alone: corners at (-1,-1), (3,-1) and (-1,3).
void main() {
    vec2 corner = vec2((gl_VertexID << 1) & 2, gl_VertexID & 2);
    gl_Position = vec4(corner * 2.0 - 1.0, 0.0, 1.0);
}
