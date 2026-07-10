"""Modified Newtonian method for inviscid surface pressures.

Theory
------
The Modified Newtonian method approximates the local surface pressure
coefficient using the maximum stagnation-point value scaled by the
square of the sine of the local surface inclination angle:

    Cp(theta) = Cp_max * sin^2(theta)

where theta is the angle between the freestream direction and the
local surface tangent, and Cp_max is computed from the Rayleigh
Pitot formula (stagnation pressure behind a normal shock):

    p02/p_inf = [(gamma+1)^2 * M^2 / (4*gamma*M^2 - 2*(gamma-1))]^(gamma/(gamma-1))
                * (1 - gamma + 2*gamma*M^2) / (gamma+1)

    q_inf = 0.5 * gamma * p_inf * M^2

    Cp_max = (p02 - p_inf) / q_inf

Surface pressure and Mach number follow from isentropic relations
referenced to p02.

References
----------
Anderson, J.D. (2006). Hypersonic and High Temperature Gas Dynamics, AIAA Education Series..
"""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from flow_inviscid.config.schema import Config


# --------------------------------------------------
# result dataclass
# --------------------------------------------------
@dataclass
class NewtonianResult:
    """Surface-condition results from the Modified Newtonian method."""

    # body geometry

    # streamwise coordinate [m]
    x: np.ndarray
    # wall-normal coordinate [m]
    y: np.ndarray
    # arc-length along surface [m]
    s: np.ndarray
    # local surface inclination angle [rad]
    theta: np.ndarray

    # surface conditions

    # pressure coefficient [-]
    cp: np.ndarray
    # surface pressure ratio p/p_inf [-]
    p_p_inf: np.ndarray
    # local surface Mach number [-]
    mach: np.ndarray

    # freestream scalars (stored for output header)

    # freestream Mach number [-]
    mach_inf: float
    # ratio of specific heats [-]
    gamma: float
    # stagnation pressure coefficient [-]
    cp_max: float


# --------------------------------------------------
# compute ratio of stagnation pressure p02 to freestream static pressure p_inf
# --------------------------------------------------
def _p02_over_pinf(mach: float, gamma: float) -> float:
    """Compute p02/p_inf from the Rayleigh Pitot formula.

    p02 is the stagnation (total) pressure behind a normal shock.
    Used to compute cp_max for Modified Newtonian theory.

    Args:
        mach:  freestream Mach number
        gamma: ratio of specific heats

    Returns:
        Pressure ratio p02 / p_inf
    """
    # Rayleigh Pitot tube formula
    #
    # p02/p_inf = [(gamma+1)^2 * M^2 / (4*gamma*M^2 - 2*(gamma-1))]^(gamma/(gamma-1)) * (1 - gamma + 2*gamma*M^2) / (gamma + 1)

    # term 1: [(gamma+1)^2 * M^2 / (4*gamma*M^2 - 2*(gamma-1))]^(gamma/(gamma-1))

    # numerator
    num = (gamma + 1) ** 2 * mach**2
    # denominator
    den = 4 * gamma * mach**2 - 2 * (gamma - 1)
    # exponent
    exponent = gamma / (gamma - 1)

    term_1 = (num / den) ** exponent

    # term 2: (1 - gamma + 2*gamma*M^2) / (gamma + 1)

    # numerator
    num = 1 - gamma + 2 * gamma * mach**2
    # denominator
    den = gamma + 1

    term_2 = num / den

    # compute ratio
    p02_p_inf = term_1 * term_2

    # return value to calling routine
    return float(p02_p_inf)

# --------------------------------------------------
# compute cp_max for the Modified Newtonian method
# --------------------------------------------------
def _cp_max(mach: float, gamma: float, pres_inf: float) -> tuple[float, float]:
    """Compute cp_max and p02 for the Modified Newtonian method.

    Args:
        mach:     freestream Mach number
        gamma:    ratio of specific heats
        pres_inf: freestream static pressure [Pa]

    Returns:
        Tuple (cp_max, p02) where p02 is total pressure behind normal shock [Pa]
    """

    # compute p02/p_inf via Rayleigh Pitot formula
    ratio = _p02_over_pinf(mach, gamma)

    # dimensional stagnation pressure behind normal shock
    p02 = ratio * pres_inf

    # dynamic pressure: q_inf = 0.5 * gamma * p_inf * M^2
    q_inf = 0.5 * gamma * pres_inf * mach**2

    # cp_max = (p02 - p_inf) / q_inf
    cp_max = (p02 - pres_inf) / q_inf

    # return cp_max and p02 to calling routine
    return float(cp_max), float(p02)

# --------------------------------------------------
# compute local surface Mach number from isentropic relations
# --------------------------------------------------
def _surface_mach(p_s: np.ndarray, p02: float, pres_inf: float, gamma: float) -> np.ndarray:
    """Compute local surface Mach number from isentropic relations.

    Uses the stagnation pressure p02 (behind normal shock at nose)
    and the local surface pressure p_s to invert:

        p02 / p_s = (1 + (gamma-1)/2 * Ms^2)^(gamma/(gamma-1))

    Returns zero for any point where p_s >= p02 (degenerate).

    Args:
        p_s:      local surface static pressure [Pa]
        p02:      total pressure behind normal shock [Pa]
        pres_inf: freestream static pressure [Pa]
        gamma:    ratio of specific heats

    Returns:
        Local surface Mach number array
    """
    # isentropic inversion: Ms = sqrt(2/(gamma-1) * ((p02/p_s)^((gamma-1)/gamma) - 1))
    ratio = np.where(p_s < p02, p02 / np.maximum(p_s, 1e-30), 1.0)
    exponent = (gamma - 1.0) / gamma
    inner = np.maximum(ratio**exponent - 1.0, 0.0)
    mach_s = np.sqrt(2.0 / (gamma - 1.0) * inner)
    return mach_s


def _load_flow_conditions(json_path: Path) -> dict:
    """Read a flow-state JSON file and extract values from [value, unit] pairs.

    flow-state serialises every scalar as [value, "unit"].  This function
    reads the JSON and returns a plain dict of floats.

    Args:
        json_path: path to the flow-state JSON file

    Returns:
        Dict of floats with keys matching flow-state field names
    """
    # read the JSON file
    raw: dict = json.loads(json_path.read_text())

    # extract scalar values — entries are either [value, "unit"] or None
    out: dict = {}
    for key, val in raw.items():
        if isinstance(val, list) and len(val) == 2:
            # [value, "unit"] pair — take the numeric value
            out[key] = val[0]
        elif isinstance(val, (int, float)):
            # plain number (hand-written files)
            out[key] = float(val)
        # skip None entries and nested dicts (kolmogorov, taylor)

    return out


def _load_body(geometry_file: Path) -> tuple[np.ndarray, np.ndarray]:
    """Load x, y body coordinates from an ASCII or Tecplot geometry file.

    Delegates to read_surface_coordinates in flow_inviscid.io.

    Args:
        geometry_file: path to the geometry file

    Returns:
        Tuple (x, y) of numpy arrays [m]
    """
    from flow_inviscid.io import read_surface_coordinates
    return read_surface_coordinates(geometry_file)


# --------------------------------------------------
# public solver entry point
# --------------------------------------------------
def solve_newtonian(cfg: Config) -> NewtonianResult:
    """Run the Modified Newtonian method for the given configuration.

    Args:
        cfg: validated Config object (must have flow_conditions, body, output)

    Returns:
        NewtonianResult with surface cp, p/p_inf, and Mach arrays

    Raises:
        ValueError: if required config sections are missing
    """
    from flow_inviscid.geometry import compute_surface_geometry

    # validate required sections
    if cfg.flow_conditions is None:
        raise ValueError("solve_newtonian requires [flow_conditions] in config")
    if cfg.body is None:
        raise ValueError("solve_newtonian requires [body] in config")

    # load freestream conditions
    fc = _load_flow_conditions(cfg.flow_conditions.file)

    # extract required scalars
    mach_inf: float = fc["mach"]
    gamma: float    = fc["gamma"]
    pres_inf: float = fc["pres"]

    # compute cp_max and p02 from freestream conditions
    cp_max, p02 = _cp_max(mach_inf, gamma, pres_inf)

    # load body coordinates and compute surface geometry
    x, y = _load_body(cfg.body.geometry_file)
    geom = compute_surface_geometry(x, y)

    # Modified Newtonian cp = cp_max * sin^2(theta), clamped to 0 on leeward surfaces
    cp = np.maximum(cp_max * np.sin(geom.theta) ** 2, 0.0)

    # surface pressure ratio: p_s / p_inf = 1 + (gamma * M_inf^2 / 2) * cp
    p_p_inf = 1.0 + 0.5 * gamma * mach_inf**2 * cp

    # surface Mach from isentropic inversion using p_s [Pa]
    p_s = p_p_inf * pres_inf
    mach_surface = _surface_mach(p_s, p02, pres_inf, gamma)

    return NewtonianResult(
        x=geom.x,
        y=geom.y,
        s=geom.s,
        theta=geom.theta,
        cp=cp,
        p_p_inf=p_p_inf,
        mach=mach_surface,
        mach_inf=mach_inf,
        gamma=gamma,
        cp_max=cp_max,
    )
