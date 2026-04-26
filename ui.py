import os
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import camera

# Whether planet name labels are drawn (toggled from the right-click menu)
labels_visible = True

# Populated by build_menu(); used to restore "Normal" speeds
_original_speeds = {}


# =============================================================================
#  Internal helpers
# =============================================================================

def _write12(text):
    """Render a string at the current raster position using 12-pt Helvetica."""
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))


def _begin_2d():
    """Switch OpenGL into 2-D ortho mode for HUD/label drawing.

    Pushes both the projection and modelview matrices so they can be restored
    cleanly by _end_2d().  Returns (viewport_width, viewport_height).
    """
    vp = glGetIntegerv(GL_VIEWPORT)
    w, h = int(vp[2]), int(vp[3])

    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, w, 0, h)     # screen space: (0,0) bottom-left, (w,h) top-right

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    return w, h


def _end_2d():
    """Restore the 3-D projection/modelview matrices saved by _begin_2d()."""
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)


# =============================================================================
#  Public drawing functions
# =============================================================================

def draw_hud(planets, cam):
    """Draw the 2-D on-screen HUD: title, controls, and optional PAUSED banner.

    Temporarily switches to an orthographic projection so text coordinates
    map directly to pixel positions, then restores the 3-D perspective.

    Parameters
    ----------
    planets : list  — the PLANETS list (used for future per-planet stats)
    cam     : module — the camera module, read for cam.paused state
    """
    w, h = _begin_2d()

    # ── Title ────────────────────────────────────────────────────────────────
    glColor3f(1.0, 0.85, 0.18)
    glRasterPos2f(14, h - 24)
    for ch in "Solar System Simulation":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    # ── Info line 1 ──────────────────────────────────────────────────────────
    glColor3f(0.78, 0.78, 0.88)
    glRasterPos2f(14, h - 46)
    _write12("Planets: 8  |  P: Pause/Resume  |  R: Reset Camera")

    # ── Info line 2 ──────────────────────────────────────────────────────────
    glColor3f(0.52, 0.52, 0.62)
    glRasterPos2f(14, h - 64)
    _write12("Zoom: +/-   Orbit: Arrow Keys   Right-click: Menu   ESC: Exit")

    # ── Bottom-left hint ─────────────────────────────────────────────────────
    glColor3f(0.38, 0.38, 0.45)
    glRasterPos2f(14, 14)
    _write12("Right-click for menu options")

    # ── PAUSED banner — centred, red ─────────────────────────────────────────
    if cam.paused:
        banner = "[ PAUSED ]"
        # Approximate pixel width: HELVETICA_18 chars are ~11 px wide on average
        bx = (w - len(banner) * 11) / 2
        by = h / 2
        glColor3f(1.0, 0.10, 0.10)
        glRasterPos2f(bx, by)
        for ch in banner:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    _end_2d()


def draw_planet_labels(planets):
    """Draw each planet's name near its current screen position.

    Uses gluProject to convert the 3-D world position (just above the planet)
    into 2-D window coordinates, then renders the text in ortho mode.
    Skips planets that are behind the camera or outside the viewport.
    """
    if not labels_visible:
        return

    # Read the live 3-D matrices BEFORE switching to ortho — once we call
    # _begin_2d() the matrices change and gluProject would give wrong results.
    modelview  = glGetDoublev(GL_MODELVIEW_MATRIX)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)
    viewport   = glGetIntegerv(GL_VIEWPORT)

    w, h = _begin_2d()

    glColor3f(0.88, 0.88, 0.96)

    for planet in planets:
        # Compute world-space position above the planet's surface
        a  = math.radians(planet["angle"])
        wx =  planet["distance"] * math.cos(a)   # matches OpenGL Y-rotation math
        wy =  planet["size"] + 1.2               # hover above the sphere
        wz = -planet["distance"] * math.sin(a)

        try:
            # gluProject: world → window (screen) coordinates
            sx, sy, sz = gluProject(wx, wy, wz, modelview, projection, viewport)
            # sz < 1.0 means the point is in front of the far plane;
            # the sx/sy bounds check keeps labels inside the window
            if 0 < sx < w and 0 < sy < h and sz < 1.0:
                glRasterPos2f(float(sx), float(sy))
                _write12(planet["name"])
        except Exception:
            pass    # planet is off-screen or behind camera — silently skip

    _end_2d()


# =============================================================================
#  Right-click context menu
# =============================================================================

def _menu_callback(value):
    """Dispatch right-click menu selections to the appropriate action.

    ID ranges
    ---------
    1 – 8   : Focus camera on that planet (Mercury=1 … Neptune=8)
    10      : Set speed to Slow  (0.3×)
    11      : Set speed to Normal (1×)
    12      : Set speed to Fast  (3×)
    20      : Toggle planet labels on / off
    21      : Reset camera to default view
    22      : Exit the application
    """
    global labels_visible
    from planets import PLANETS   # imported here to avoid a circular import

    # ── Focus planet ─────────────────────────────────────────────────────────
    if 1 <= value <= 8:
        planet = PLANETS[value - 1]
        camera.cam_distance = planet["distance"] + 15.0
        camera.cam_angle_x  = 20.0
        camera.cam_angle_y  = -planet["angle"]   # face toward the planet

    # ── Speed presets ─────────────────────────────────────────────────────────
    elif value == 10:   # Slow
        for p in PLANETS:
            p["speed"] = _original_speeds.get(p["name"], p["speed"]) * 0.3

    elif value == 11:   # Normal — restore saved original speeds
        for p in PLANETS:
            p["speed"] = _original_speeds.get(p["name"], p["speed"])

    elif value == 12:   # Fast
        for p in PLANETS:
            p["speed"] = _original_speeds.get(p["name"], p["speed"]) * 3.0

    # ── UI toggles / actions ─────────────────────────────────────────────────
    elif value == 20:   # Toggle labels
        labels_visible = not labels_visible

    elif value == 21:   # Reset view
        camera.cam_distance = 60.0
        camera.cam_angle_x  = 20.0
        camera.cam_angle_y  = 0.0

    elif value == 22:   # Exit
        os._exit(0)

    glutPostRedisplay()


def build_menu(planets):
    """Create the GLUT right-click context menu with two submenus.

    Must be called after glutCreateWindow() and before glutMainLoop().

    Submenus
    --------
    Focus Planet — one entry per planet; zooms the camera toward it
    Speed        — Slow / Normal / Fast presets

    Main entries
    ------------
    Focus Planet ▶ | Speed ▶ | Toggle Labels | Reset View | Exit
    """
    global _original_speeds
    # Snapshot speeds now so "Normal" can restore them even after Slow/Fast
    _original_speeds = {p["name"]: p["speed"] for p in planets}

    # ── Focus Planet submenu ─────────────────────────────────────────────────
    focus_menu = glutCreateMenu(_menu_callback)
    for i, planet in enumerate(planets):
        glutAddMenuEntry(planet["name"].encode(), i + 1)   # IDs 1-8

    # ── Speed submenu ────────────────────────────────────────────────────────
    speed_menu = glutCreateMenu(_menu_callback)
    glutAddMenuEntry(b"Slow  (0.3x)", 10)
    glutAddMenuEntry(b"Normal  (1x)", 11)
    glutAddMenuEntry(b"Fast  (3x)",   12)

    # ── Main menu ────────────────────────────────────────────────────────────
    glutCreateMenu(_menu_callback)
    glutAddSubMenu(b"Focus Planet",    focus_menu)
    glutAddSubMenu(b"Speed",           speed_menu)
    glutAddMenuEntry(b"Toggle Labels", 20)
    glutAddMenuEntry(b"Reset View",    21)
    glutAddMenuEntry(b"Exit",          22)
    glutAttachMenu(GLUT_RIGHT_BUTTON)  # right mouse button opens the menu
