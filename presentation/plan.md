# Ray Tracing a Black Hole: a four-part series

## Overview
- **Topic**: How a real-time black hole renderer works, built up in three runnable stages.
- **Target audience**: High-school physics level (Newton's gravity, vectors, Pythagoras, the quadratic
  formula, circular motion, the Doppler effect). No programming with OpenGL assumed.
- **Key idea**: Every equation on screen turns into a line of code, and every stage ends with a
  program the viewer can run. University-level ideas are introduced through a high-school counterpart.
- **Format**: 1080p30, narrated (Kokoro), soft music bed, subtitles.

## Episode 1: Why light bends  (no program)
| Scene | Content |
|---|---|
| Hook | Simulator footage; the three stages we will build |
| Why light bends | Newton's formula and massless light; curved space; Pythagoras to the metric; units; 2M, 3M, 6M |
| The two rules | A thrown ball's two rules next to light's two rules (Hamilton's equations) |
| A formula the computer can use | Division by zero at 2M; flat space plus one correction; the two rules term by term |
| Where we are | The two rules, what they will produce, teaser for the code |

## Episode 2: Bending light in 2D  (program: `stages/01_rays_2d`)
| Scene | Content |
|---|---|
| Recap | The two rules; promise of ~200 lines that bend light |
| The plan | Processor traces, graphics card draws; what OpenGL is |
| Code: physics | `Vec2`; `derivatives` with a line drawn from each code line to its equation; H = 0 as a quadratic; Euler vs RK4; `traceRay` with rays stepping alongside |
| Code: OpenGL | Window and context; vertex and fragment shader; compiling and linking; vertex buffer and array; `draw`; the main loop |
| Result | The program running; the critical ray and the shadow |

## Episode 3: A ray tracer in 3D  (program: `stages/02_raytracer_3d`)
| Scene | Content |
|---|---|
| Recap | From diagram to picture |
| Ray tracing | Camera, pixels, straight rays; swap the sphere for a hole |
| Why the graphics card | Billions of steps per second; one small program per pixel |
| Covering the screen | The fullscreen triangle from the vertex number |
| The physics moves | Stage-1 C++ and stage-2 GLSL `derivatives` side by side |
| The camera | Two angles and a distance; forward, right, up with cross products; uniforms; pixel to ray |
| The loop | Horizon, escape, step; looking up the sky |
| Result | Shadow at 5.2 M, the lensed grid explained |

## Episode 4: The spinning disk  (program: `stages/03_disk`)
| Scene | Content |
|---|---|
| Recap | Why a disk |
| One disk, three images | Side-view rays: direct, over the top, from underneath |
| Did the ray hit the disk? | The sign change in z, interpolation, blending and carrying on |
| Making it spin | Centripetal force = gravity gives the orbital speed; velocity in the shader; the clock uniform |
| Colour and brightness | Doppler and gravitational redshift; the factor g in code; glow colour; with and without g |
| Too bright for the screen | Floating-point texture, framebuffer, two passes, the tone-mapping curve |
| Result | The final image explained; recap of the three stages; the full simulator and its tests |

## Shared elements
- Narration is inline as `self.voice("...")`; each block lasts as long as its sentence.
- Code is read from the real source files at render time and shown in a panel with a file tab;
  a highlight bar moves to the lines being discussed.
- Every light path drawn is a real geodesic from `geodesics.py`.
- Palette: background `#0c0f16`; orange accent for the hole and f; blue for escaping rays and L;
  red for captured rays and errors; gold for the thing being discussed; green for correct results.
