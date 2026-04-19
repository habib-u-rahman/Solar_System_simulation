import os
import math
from OpenGL.GLU import *
from OpenGL.GLUT import *

# =============================================================================
#  Camera state — module-level so every function shares the same values
# =============================================================================

cam_distance = 65.0   # distance from origin (zoom level)
cam_angle_x  = 20.0   # vertical tilt in degrees  (elevation above XZ plane)
cam_angle_y  = 0.0    # horizontal orbit in degrees (rotation around Y axis)
paused       = False   # when True, planet movement is frozen


# =============================================================================
#  Public functions
# =============================================================================

def apply_camera():
    """Compute eye position from spherical coordinates and call gluLookAt.

    Spherical → Cartesian conversion:
        x = distance * cos(angle_x) * sin(angle_y)
        y = distance * sin(angle_x)          ← vertical component
        z = distance * cos(angle_x) * cos(angle_y)

    This allows the user to freely orbit and tilt around the solar system
    while always looking at the origin (where the Sun sits).
    """
    ax = math.radians(cam_angle_x)
    ay = math.radians(cam_angle_y)

    eye_x = cam_distance * math.cos(ax) * math.sin(ay)
    eye_y = cam_distance * math.sin(ax)
    eye_z = cam_distance * math.cos(ax) * math.cos(ay)

    gluLookAt(eye_x, eye_y, eye_z,   # eye position (computed above)
              0.0,   0.0,   0.0,     # always look at the Sun / origin
              0.0,   1.0,   0.0)     # world up vector


def keyboard_handler(key, _x, _y):
    """Handle regular (ASCII) key presses.

    ESC     — quit the application
    P / p   — toggle pause (freeze / resume planet orbits)
    R / r   — reset camera to its default position and orientation
    + or =  — zoom in  (decrease cam_distance, clamped to 10)
    - or _  — zoom out (increase cam_distance, clamped to 150)
    """
    global cam_distance, cam_angle_x, cam_angle_y, paused

    if key == b'\x1b':          # ESC — force-kill the process
        os._exit(0)             # sys.exit() is caught by GLUT's C loop; os._exit() is not

    elif key in (b'p', b'P'):   # pause / resume
        paused = not paused

    elif key in (b'r', b'R'):   # reset camera to defaults
        cam_distance = 60.0
        cam_angle_x  = 20.0
        cam_angle_y  = 0.0

    elif key in (b'+', b'='):   # zoom in — move camera closer
        cam_distance = max(10.0, cam_distance - 3.0)

    elif key in (b'-', b'_'):   # zoom out — move camera farther
        cam_distance = min(150.0, cam_distance + 3.0)

    # Request a redraw so the new camera position takes effect immediately
    glutPostRedisplay()


def special_keys_handler(key, _x, _y):
    """Handle GLUT special keys (arrow keys) to orbit and tilt the camera.

    UP    — tilt camera upward   (decrease cam_angle_x, min −89°)
    DOWN  — tilt camera downward (increase cam_angle_x, max  +89°)
    LEFT  — orbit left           (decrease cam_angle_y)
    RIGHT — orbit right          (increase cam_angle_y)

    Each press moves 3 degrees.  cam_angle_y wraps freely;
    cam_angle_x is clamped so the camera never flips past the poles.
    """
    global cam_angle_x, cam_angle_y

    STEP = 3.0   # degrees per key press

    if key == GLUT_KEY_UP:
        cam_angle_x = max(-89.0, cam_angle_x - STEP)   # tilt up

    elif key == GLUT_KEY_DOWN:
        cam_angle_x = min( 89.0, cam_angle_x + STEP)   # tilt down

    elif key == GLUT_KEY_LEFT:
        cam_angle_y -= STEP                             # orbit left

    elif key == GLUT_KEY_RIGHT:
        cam_angle_y += STEP                             # orbit right

    glutPostRedisplay()
