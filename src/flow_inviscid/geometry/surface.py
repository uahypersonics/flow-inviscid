"""Surface geometry computations for flow-inviscid.

Takes (x, y) body surface coordinates and returns derived geometric
quantities needed by the surface-pressure methods.
"""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


# --------------------------------------------------
# result dataclass
# --------------------------------------------------
@dataclass
class SurfaceGeometry:
    """Geometric quantities derived from body surface coordinates."""

    # streamwise coordinate [m]
    x: np.ndarray
    # wall-normal coordinate [m]
    y: np.ndarray
    # cumulative arc-length along the surface [m]
    s: np.ndarray
    # local surface inclination angle relative to freestream (x-axis) [rad]
    theta: np.ndarray


# --------------------------------------------------
# internal helpers
# --------------------------------------------------
def _arc_length(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Compute cumulative arc-length along the body surface.

    Args:
        x: streamwise coordinates [m]
        y: wall-normal coordinates [m]

    Returns:
        s [m], starting at 0 at the first point
    """
    # segment lengths between adjacent points
    ds = np.sqrt(np.diff(x) ** 2 + np.diff(y) ** 2)

    # cumulative sum, prepend 0 for the first point
    s = np.concatenate([[0.0], np.cumsum(ds)])
    return s


def _surface_inclination(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Compute local surface inclination angle from body coordinates.

    Uses numpy.gradient (central differences at interior points, one-sided
    at the endpoints).  The inclination angle is the angle between the
    surface tangent and the freestream (x-axis) direction.

    Args:
        x: streamwise coordinates [m]
        y: wall-normal coordinates [m]

    Returns:
        theta [rad], always in [0, pi/2]
    """
    # tangent vector components via central differences
    dx = np.gradient(x)
    dy = np.gradient(y)

    # angle between tangent and the freestream (x-axis)
    theta = np.arctan2(np.abs(dy), np.abs(dx))
    return theta


# --------------------------------------------------
# public API
# --------------------------------------------------
def compute_surface_geometry(x: np.ndarray, y: np.ndarray) -> SurfaceGeometry:
    """Compute geometric surface quantities from body coordinates.

    Args:
        x: streamwise surface coordinates [m]
        y: wall-normal surface coordinates [m]

    Returns:
        SurfaceGeometry with arc-length and inclination angle
    """
    # arc-length from nose to each surface point
    s = _arc_length(x, y)

    # local inclination angle relative to freestream direction
    theta = _surface_inclination(x, y)

    return SurfaceGeometry(x=x, y=y, s=s, theta=theta)
