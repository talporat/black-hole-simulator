"""NumPy port of shaders/metric_schwarzschild.glsl and shaders/geodesic.glsl.

Used by the Manim scenes to draw real light paths. Same equations, same
conventions: outgoing Kerr-Schild coordinates, physical momentum p, and a
negative affine step to follow the ray backwards in time.
"""
import numpy as np

M = 1.0
HORIZON = 2.0 * M
B_CRIT = 3.0 * np.sqrt(3.0) * M


def metric(x, p):
    r = np.linalg.norm(x)
    n = x / r
    f = 2.0 * M / r
    L = -n
    gradf = -(2.0 * M / r**2) * n
    gradLp = -(p - n * np.dot(n, p)) / r
    return f, L, gradf, gradLp


def rhs(x, p, pt):
    f, L, gradf, gradLp = metric(x, p)
    A = np.dot(L, p) - pt
    return p - f * A * L, 0.5 * A * A * gradf + f * A * gradLp


def rk4(x, p, pt, h):
    k1x, k1p = rhs(x, p, pt)
    k2x, k2p = rhs(x + 0.5 * h * k1x, p + 0.5 * h * k1p, pt)
    k3x, k3p = rhs(x + 0.5 * h * k2x, p + 0.5 * h * k2p, pt)
    k4x, k4p = rhs(x + h * k3x, p + h * k3p, pt)
    return (x + h / 6.0 * (k1x + 2 * k2x + 2 * k3x + k4x),
            p + h / 6.0 * (k1p + 2 * k2p + 2 * k3p + k4p))


def euler(x, p, pt, h):
    dx, dp = rhs(x, p, pt)
    return x + h * dx, p + h * dp


def photon(x0, d):
    """Momentum (pt, p), with energy 1, of the photon whose backward path leaves x0 along d."""
    x0 = np.asarray(x0, float)
    k = -np.asarray(d, float) / np.linalg.norm(d)
    f, L, _, _ = metric(x0, k)
    lk = np.dot(L, k)
    # Null condition g(k, k) = 0 for the time component:
    # (f - 1) kt^2 + 2 f (L.k) kt + |k|^2 + f (L.k)^2 = 0, future-directed root.
    a, b, c = f - 1.0, 2.0 * f * lk, 1.0 + f * lk * lk
    kt = (-b - np.sqrt(b * b - 4 * a * c)) / (2 * a)
    pt = -kt + f * (kt + lk)
    p = k + f * (kt + lk) * L
    return -1.0, p / -pt


def trace(x0, d, r_escape=60.0, quality=0.3, fixed_h=None, stepper=rk4, max_steps=20000):
    """Follow a ray from x0 along d. Returns (points [N,3], fate) with fate
    'captured', 'escaped' or 'undecided'."""
    x = np.asarray(x0, float)
    pt, p = photon(x, d)
    pts = [x.copy()]
    for _ in range(max_steps):
        r = np.linalg.norm(x)
        if r < HORIZON:
            return np.array(pts), "captured"
        if r > r_escape:
            return np.array(pts), "escaped"
        h = fixed_h if fixed_h is not None else quality * max(0.02, 0.06 * r)
        x, p = stepper(x, p, pt, -h)
        pts.append(x.copy())
    return np.array(pts), "undecided"


def impact_parameter(x0, d):
    _, p = photon(x0, d)
    return np.linalg.norm(np.cross(np.asarray(x0, float), p))
