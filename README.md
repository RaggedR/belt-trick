# The Belt Trick

An interactive 3D visualization of the Dirac belt trick — why spinors need 720°.

**Live demo:** https://raggedr.github.io/belt-trick/

Two belts connect an inner sphere to an outer cage. Rotate the sphere and try to untwist:

- **360°** — the belts are twisted, and untwisting is impossible. Pressing *Untwist* makes an honest attempt: the twist axis swings over the pole and springs back. The twist survives.
- **720°** — the belts untwist completely, *without rotating the sphere back*.

This is π₁(SO(3)) = ℤ/2ℤ made tangible: a 360° rotation is a topologically non-trivial loop, but 720° is contractible. Spinors live in the double cover SU(2), which is why an electron's wavefunction picks up a factor of −1 under a full rotation.

## How the untwist works

The belt is parametrized as a path of rotations q(t) applied to the straight belt.
The 4π twist is a closed loop in SO(3) based at the identity. Its lift to
SU(2) = S³ is a great circle through the identity quaternion — and circles
through a fixed point of a sphere can be shrunk to that point by tilting the
cutting plane. That plane tilt (σ = πs/2) *is* the untwist animation.

Because every belt point is a pure rotation of the straight belt:

- both endpoints stay pinned exactly, for all time (by algebra, not patching),
- the belt can never pass through the ball (rotations preserve radius),
- the belt can never self-intersect (different parameters → different radii).

For an odd number of twists the lift runs from −1 to +1 — a path between
*different* endpoints, which no plane tilt can contract. The "stuck" animation
swings the twist axis n(s) instead: every intermediate configuration is still a
full 2π twist about some axis. The parity check in the code is literally the
class in ℤ/2ℤ.

## Files

- `index.html` — the interactive Three.js/WebGL version (self-contained, no build step)
- `manim/` — earlier [Manim Community](https://www.manim.community/) experiments (2D and 3D belt trick, cup trick, spinor vs vector)

Inspired by [Jason Hise's belt trick animations](https://www.youtube.com/watch?v=JaIR-cWk_-o).
