SUN = {
    "name":  "Sun",
    "size":  2.5,
    "color": (1.0, 0.92, 0.10),
}

# speed / spin_speed = degrees per second  (frame-rate independent)
# tilt               = axial tilt in degrees on the Z axis
# moon               = optional dict for a natural satellite
PLANETS = [
    {
        "name": "Mercury", "distance": 6.0,  "size": 0.35,
        "color": (0.72, 0.60, 0.50),
        "speed": 47.0,  "angle": 0.0, "tilt": 0.03,
        "spin_speed": 10.0,  "spin_angle": 0.0,
    },
    {
        "name": "Venus",   "distance": 9.0,  "size": 0.60,
        "color": (0.95, 0.78, 0.42),
        "speed": 35.0,  "angle": 0.0, "tilt": 177.4,  # retrograde
        "spin_speed": -4.0,  "spin_angle": 0.0,
    },
    {
        "name": "Earth",   "distance": 13.0, "size": 0.65,
        "color": (0.18, 0.48, 0.90),
        "speed": 29.0,  "angle": 0.0, "tilt": 23.4,
        "spin_speed": 120.0, "spin_angle": 0.0,
        "moon": {
            "name": "Moon", "distance": 1.8, "size": 0.18,
            "color": (0.75, 0.73, 0.70),
            "speed": 200.0, "angle": 45.0,
        },
    },
    {
        "name": "Mars",    "distance": 17.0, "size": 0.45,
        "color": (0.85, 0.33, 0.18),
        "speed": 24.0,  "angle": 0.0, "tilt": 25.2,
        "spin_speed": 115.0, "spin_angle": 0.0,
    },
    {
        "name": "Jupiter", "distance": 24.0, "size": 1.55,
        "color": (0.85, 0.68, 0.48),
        "speed": 13.0,  "angle": 0.0, "tilt": 3.1,
        "spin_speed": 500.0, "spin_angle": 0.0,  # fastest spinner
    },
    {
        "name": "Saturn",  "distance": 32.0, "size": 1.30,
        "color": (0.92, 0.82, 0.58),
        "speed": 9.7,   "angle": 0.0, "tilt": 26.7,
        "spin_speed": 450.0, "spin_angle": 0.0,
    },
    {
        "name": "Uranus",  "distance": 40.0, "size": 0.95,
        "color": (0.55, 0.88, 0.93),
        "speed": 6.8,   "angle": 0.0, "tilt": 97.8,   # nearly on its side
        "spin_speed": -180.0, "spin_angle": 0.0,       # retrograde
    },
    {
        "name": "Neptune", "distance": 48.0, "size": 0.90,
        "color": (0.20, 0.38, 0.98),
        "speed": 5.4,   "angle": 0.0, "tilt": 28.3,
        "spin_speed": 165.0, "spin_angle": 0.0,
    },
]


def update_planets(delta_time):
    """Advance every planet's orbit angle, spin angle, and moon angle."""
    for planet in PLANETS:
        planet["angle"]      = (planet["angle"]      + planet["speed"]      * delta_time) % 360.0
        planet["spin_angle"] = (planet["spin_angle"] + planet["spin_speed"] * delta_time) % 360.0
        if "moon" in planet:
            moon = planet["moon"]
            moon["angle"] = (moon["angle"] + moon["speed"] * delta_time) % 360.0
