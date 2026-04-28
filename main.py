import time
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from renderer import (draw_starfield, draw_nebula, draw_orbit_ring,
                      draw_asteroid_belt, draw_sun, draw_planet)
from planets import PLANETS, SUN, update_planets
import camera
from camera import apply_camera, keyboard_handler, special_keys_handler
from ui import draw_hud, draw_planet_labels, build_menu
import ui

_last_time = None
_window_w  = 800
_window_h  = 600


def setup_lighting():
    """Configure OpenGL fixed-function lighting to simulate sunlight.

    Light model
    -----------
    GL_LIGHT0 is a point light placed at the Sun's world-space origin (0,0,0).
    It casts warm-white diffuse light so the illuminated side of each planet
    is bright and the shadowed side fades to near-black.

    NOTE: glLightfv(GL_LIGHT0, GL_POSITION, ...) must be called every frame
    *after* gluLookAt() so OpenGL can transform the world-space position into
    eye space correctly.  That call lives in display() for this reason.
    """

    # --- Enable the lighting engine and light source 0 ---
    glEnable(GL_LIGHTING)   # switch on the lighting calculation
    glEnable(GL_LIGHT0)     # activate the first (sun) light

    # --- LIGHT0 colour channels ---
    # Ambient: very faint fill so completely shadowed faces are still barely
    # visible — simulates indirect light bouncing around the solar system.
    glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.08, 0.08, 0.08, 1.0])

    # Diffuse: near-white with a very slight warm tint — the dominant
    # channel that gives planets their lit/shadow contrast.
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [1.0,  1.0,  0.9,  1.0])

    # Specular: medium-intensity white for subtle shiny highlights.
    glLightfv(GL_LIGHT0, GL_SPECULAR, [0.5,  0.5,  0.5,  1.0])

    # --- Color material: let glColor3f control the diffuse/ambient material
    # so each planet's colour tuple is respected under lighting.
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)

    # Specular material + shininess applied to every surface
    glMaterialfv(GL_FRONT, GL_SPECULAR,  [0.22, 0.22, 0.22, 1.0])
    glMaterialf (GL_FRONT, GL_SHININESS, 20.0)

    # GL_NORMALIZE re-normalises surface normals after scale transforms so
    # lighting calculations remain correct when planets are scaled/tilted.
    glEnable(GL_NORMALIZE)

    # Smooth (Gouraud) shading interpolates colour across each polygon face.
    glShadeModel(GL_SMOOTH)


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Delegate camera placement to camera.py (supports orbit, tilt, zoom)
    apply_camera()

    # Sun point-light at origin (must be set after gluLookAt to transform correctly)
    glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 0.0, 0.0, 1.0])

    # ── Background ─────────────────────────────────────────────────────────
    draw_starfield()
    draw_nebula()

    # ── Orbit guide rings (tinted by each planet's colour) ─────────────────
    for planet in PLANETS:
        draw_orbit_ring(planet["distance"], planet["color"])

    # ── Asteroid belt ───────────────────────────────────────────────────────
    draw_asteroid_belt()

    # ── Sun ─────────────────────────────────────────────────────────────────
    draw_sun(SUN)

    # ── Planets (lit by LIGHT0, each with atmosphere / rings / moon) ────────
    for planet in PLANETS:
        draw_planet(planet)

    # ── Planet labels (ui.py, respects ui.labels_visible toggle) ───────────
    draw_planet_labels(PLANETS)

    # ── HUD overlay: title, controls, PAUSED banner (ui.py) ─────────────────
    draw_hud(PLANETS, camera)

    glutSwapBuffers()


def timer(_value):
    """Fires every ~16 ms — advances the simulation then requests a redraw."""
    global _last_time
    now   = time.time()
    delta = 0.0 if _last_time is None else (now - _last_time)
    _last_time = now
    # Only move planets when the simulation is not paused (camera.paused flag)
    if not camera.paused:
        update_planets(delta)
    glutPostRedisplay()
    glutTimerFunc(16, timer, 0)


def reshape(width, height):
    global _window_w, _window_h
    _window_w = width
    _window_h = max(height, 1)
    glViewport(0, 0, _window_w, _window_h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, _window_w / _window_h, 0.1, 1200.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowSize(900, 650)
    glutInitWindowPosition(150, 60)
    glutCreateWindow(b"Solar System Simulation | CG Lab Project")

    glClearColor(0.00, 0.00, 0.02, 1.0)   # very slightly blue-black sky
    glEnable(GL_DEPTH_TEST)
    setup_lighting()

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard_handler)       # ASCII keys  (ESC, P, R, +, -)
    glutSpecialFunc(special_keys_handler)    # Arrow keys  (orbit + tilt)
    build_menu(PLANETS)                      # right-click context menu
    glutTimerFunc(16, timer, 0)

    glutMainLoop()


if __name__ == "__main__":
    main()
