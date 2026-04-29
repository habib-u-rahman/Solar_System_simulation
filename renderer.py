import math
import random
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


# =============================================================================
#  Pre-generated static scene data  (fixed seeds = stable every frame)
# =============================================================================

# ---- Stars ------------------------------------------------------------------
_rng_s = random.Random(42)
_stars = []
for _ in range(650):
    x = _rng_s.uniform(-300, 300)
    y = _rng_s.uniform(-200, 200)
    z = _rng_s.uniform(-300, 300)
    roll = _rng_s.random()
    if roll > 0.95:
        size = 2.5;  brightness = _rng_s.uniform(0.88, 1.00)
    elif roll > 0.80:
        size = 1.8;  brightness = _rng_s.uniform(0.65, 1.00)
    else:
        size = 1.0;  brightness = _rng_s.uniform(0.28, 0.78)
    tint = _rng_s.random()
    if tint > 0.90:
        color = (brightness * 0.70, brightness * 0.80, brightness)      # blue-white
    elif tint > 0.80:
        color = (brightness, brightness * 0.85, brightness * 0.50)      # warm yellow
    else:
        color = (brightness, brightness, brightness)                     # white
    _stars.append((x, y, z, size, color))

_stars_small  = [(x, y, z, c) for x, y, z, s, c in _stars if s <= 1.0]
_stars_medium = [(x, y, z, c) for x, y, z, s, c in _stars if 1.0 < s <= 1.8]
_stars_bright = [(x, y, z, c) for x, y, z, s, c in _stars if s > 1.8]

# ---- Nebula clouds ----------------------------------------------------------
_rng_n = random.Random(99)
_nebula_defs = [
    ((-210,  65, -195), (0.55, 0.15, 0.85), 70),   # purple
    (( 185, -75,  215), (0.15, 0.45, 0.95), 65),   # blue
    ((-115,  95,  255), (0.95, 0.35, 0.15), 60),   # orange
    (( 265, -25, -140), (0.20, 0.80, 0.60), 55),   # teal
    ((  55, 155, -260), (0.80, 0.70, 0.20), 50),   # gold
]
_nebula = []
for (cx, cy, cz), (nr, ng, nb), count in _nebula_defs:
    for _ in range(count):
        dx = _rng_n.gauss(0, 22); dy = _rng_n.gauss(0, 14); dz = _rng_n.gauss(0, 22)
        br = _rng_n.uniform(0.18, 0.55)
        sz = _rng_n.choice([1.0, 1.0, 1.5, 2.0])
        _nebula.append((cx + dx, cy + dy, cz + dz, nr * br, ng * br, nb * br, sz))

_nebula_small  = [(x, y, z, r, g, b) for x, y, z, r, g, b, s in _nebula if s <= 1.0]
_nebula_medium = [(x, y, z, r, g, b) for x, y, z, r, g, b, s in _nebula if 1.0 < s <= 1.5]
_nebula_large  = [(x, y, z, r, g, b) for x, y, z, r, g, b, s in _nebula if s > 1.5]

# ---- Asteroid belt (between Mars r=17 and Jupiter r=24) --------------------
_rng_a = random.Random(7)
_ast_small = []
_ast_large = []
for _ in range(280):
    radius = _rng_a.uniform(19.5, 22.5)
    ang    = _rng_a.uniform(0, 2 * math.pi)
    height = _rng_a.uniform(-0.45, 0.45)
    br     = _rng_a.uniform(0.38, 0.68)
    col    = (br * 0.80, br * 0.72, br * 0.58)
    pt     = (radius * math.cos(ang), height, radius * math.sin(ang), col)
    if _rng_a.random() > 0.75:
        _ast_large.append(pt)
    else:
        _ast_small.append(pt)


# =============================================================================
#  Internal helpers
# =============================================================================

def _bon():
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

def _boff():
    glDisable(GL_BLEND)


# =============================================================================
#  Public drawing functions
# =============================================================================

def draw_starfield():
    """Size-varied, colour-tinted star background."""
    glDisable(GL_LIGHTING)
    glPointSize(1.0)
    glBegin(GL_POINTS)
    for x, y, z, (r, g, b) in _stars_small:
        glColor3f(r, g, b);  glVertex3f(x, y, z)
    glEnd()
    glPointSize(1.8)
    glBegin(GL_POINTS)
    for x, y, z, (r, g, b) in _stars_medium:
        glColor3f(r, g, b);  glVertex3f(x, y, z)
    glEnd()
    glPointSize(2.5)
    glBegin(GL_POINTS)
    for x, y, z, (r, g, b) in _stars_bright:
        glColor3f(r, g, b);  glVertex3f(x, y, z)
    glEnd()
    glPointSize(1.0)
    glEnable(GL_LIGHTING)


def draw_nebula():
    """Faint coloured point-cloud clusters simulating distant nebulae."""
    glDisable(GL_LIGHTING)
    glPointSize(1.0)
    glBegin(GL_POINTS)
    for x, y, z, r, g, b in _nebula_small:
        glColor3f(r, g, b);  glVertex3f(x, y, z)
    glEnd()
    glPointSize(1.5)
    glBegin(GL_POINTS)
    for x, y, z, r, g, b in _nebula_medium:
        glColor3f(r, g, b);  glVertex3f(x, y, z)
    glEnd()
    glPointSize(2.0)
    glBegin(GL_POINTS)
    for x, y, z, r, g, b in _nebula_large:
        glColor3f(r, g, b);  glVertex3f(x, y, z)
    glEnd()
    glPointSize(1.0)
    glEnable(GL_LIGHTING)


def draw_orbit_ring(radius, planet_color=(0.0, 0.0, 0.0), segments=120):
    """Dashed orbit circle on XZ plane, faintly tinted by the planet's colour."""
    glDisable(GL_LIGHTING)
    pr, pg, pb = planet_color
    # 18% planet tint blended onto a dim grey base
    glColor3f(pr * 0.18 + 0.20, pg * 0.18 + 0.20, pb * 0.18 + 0.24)
    glBegin(GL_LINES)
    for i in range(segments):
        if i % 2 != 0:
            continue
        a0 = (2 * math.pi * i)       / segments
        a1 = (2 * math.pi * (i + 1)) / segments
        glVertex3f(radius * math.cos(a0), 0.0, radius * math.sin(a0))
        glVertex3f(radius * math.cos(a1), 0.0, radius * math.sin(a1))
    glEnd()
    glEnable(GL_LIGHTING)


def draw_asteroid_belt():
    """Scattered brownish dots forming the asteroid belt."""
    glDisable(GL_LIGHTING)
    glPointSize(1.0)
    glBegin(GL_POINTS)
    for x, y, z, (r, g, b) in _ast_small:
        glColor3f(r, g, b);  glVertex3f(x, y, z)
    glEnd()
    glPointSize(1.8)
    glBegin(GL_POINTS)
    for x, y, z, (r, g, b) in _ast_large:
        glColor3f(r, g, b);  glVertex3f(x, y, z)
    glEnd()
    glPointSize(1.0)
    glEnable(GL_LIGHTING)


def draw_sun(sun_data):
    """Sun core plus four layered glow halos for a corona effect."""
    glDisable(GL_LIGHTING)
    _bon()
    glDepthMask(GL_FALSE)
    glPushMatrix()

    glColor4f(1.0, 0.38, 0.04, 0.035)          # wide outer corona
    glutSolidSphere(sun_data["size"] * 5.5, 28, 28)

    glColor4f(1.0, 0.50, 0.05, 0.070)          # outer glow
    glutSolidSphere(sun_data["size"] * 3.6, 30, 30)

    glColor4f(1.0, 0.80, 0.12, 0.150)          # mid golden halo
    glutSolidSphere(sun_data["size"] * 2.2, 32, 32)

    glColor4f(1.0, 0.95, 0.42, 0.300)          # inner bright halo
    glutSolidSphere(sun_data["size"] * 1.38, 36, 36)

    glColor4f(1.0, 0.80, 0.00, 0.150)          # close glow — warm golden (Step 7)
    glutSolidSphere(sun_data["size"] * 1.30, 36, 36)

    glDepthMask(GL_TRUE)
    _boff()

    glColor3f(1.0, 0.97, 0.32)                 # solid opaque core
    glutSolidSphere(sun_data["size"], 48, 48)

    glPopMatrix()
    glEnable(GL_LIGHTING)


def _draw_saturn_rings(planet_size):
    """Multi-band Saturn ring system with a Cassini-division gap."""
    # (inner_mult, outer_mult, r, g, b, alpha)
    bands = [
        (1.45, 1.72, 0.75, 0.68, 0.48, 0.50),   # C ring — dark inner
        (1.72, 2.12, 0.92, 0.84, 0.62, 0.80),   # B ring — brightest
        (2.12, 2.28, 0.30, 0.28, 0.20, 0.20),   # Cassini division — gap
        (2.25, 2.58, 0.88, 0.80, 0.58, 0.68),   # A ring — outer
    ]
    segs = 96
    glDisable(GL_LIGHTING)
    _bon()
    glDepthMask(GL_FALSE)

    for im, om, r, g, b, a in bands:
        ir = planet_size * im
        or_ = planet_size * om
        glBegin(GL_TRIANGLE_STRIP)
        for i in range(segs + 1):
            ang = (2 * math.pi * i) / segs
            c = math.cos(ang);  s = math.sin(ang)
            glColor4f(r * 1.10, g * 1.10, b * 1.10, a)
            glVertex3f(or_ * c, 0.0, or_ * s)
            glColor4f(r * 0.72, g * 0.72, b * 0.72, a * 0.50)
            glVertex3f(ir  * c, 0.0, ir  * s)
        glEnd()

    glDepthMask(GL_TRUE)
    _boff()
    glEnable(GL_LIGHTING)



def _draw_atmosphere(planet):
    """Translucent glow shell around atmospherically active planets."""
    atm = {
        "Venus":   (1.00, 0.88, 0.38, 0.13),
        "Earth":   (0.22, 0.52, 1.00, 0.14),
        "Neptune": (0.18, 0.38, 1.00, 0.12),
        "Uranus":  (0.48, 0.90, 0.96, 0.11),
    }
    if planet["name"] not in atm:
        return
    r, g, b, a = atm[planet["name"]]
    glDisable(GL_LIGHTING)
    _bon()
    glDepthMask(GL_FALSE)
    glColor4f(r, g, b, a)
    glutSolidSphere(planet["size"] * 1.30, 32, 32)
    glDepthMask(GL_TRUE)
    _boff()
    glEnable(GL_LIGHTING)


def _draw_moon(moon):
    """Moon orbiting in the parent planet's local (tilted) frame."""
    glPushMatrix()
    glRotatef(moon["angle"], 0.0, 1.0, 0.0)
    glTranslatef(moon["distance"], 0.0, 0.0)
    r, g, b = moon["color"]
    glColor3f(r, g, b)
    glutSolidSphere(moon["size"], 16, 16)
    glPopMatrix()


def draw_planet(planet):
    """Draw one planet: orbital position → tilt → rings/moon/atm → spin → sphere."""
    glPushMatrix()

    glRotatef(planet["angle"], 0.0, 1.0, 0.0)   # orbit around sun
    glTranslatef(planet["distance"], 0.0, 0.0)   # move to orbital radius
    glRotatef(planet["tilt"], 0.0, 0.0, 1.0)     # axial tilt

    # All of these share the tilted frame but are independent of self-spin
    if planet["name"] == "Saturn":
        _draw_saturn_rings(planet["size"])
    if "moon" in planet:
        _draw_moon(planet["moon"])
    _draw_atmosphere(planet)

    # Spin only applies to the planet body
    glPushMatrix()
    glRotatef(planet["spin_angle"], 0.0, 1.0, 0.0)
    r, g, b = planet["color"]
    glColor3f(r, g, b)
    glutSolidSphere(planet["size"], 38, 38)
    glPopMatrix()

    glPopMatrix()


