"""Tangent-cone surface conditions for axisymmetric blunt bodies."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from gasdyn import solve_taylor_maccoll

from flow_inviscid.config.schema import Config
from flow_inviscid.geometry import compute_surface_geometry
from flow_inviscid.methods.newtonian import solve_newtonian


# --------------------------------------------------
# result dataclass
# --------------------------------------------------
@dataclass
class TangentConeResult:
    """Surface-condition results from the tangent-cone method."""

    # body geometry
    x: np.ndarray
    y: np.ndarray
    s: np.ndarray
    theta: np.ndarray

    # surface conditions
    cp: np.ndarray
    p_p_inf: np.ndarray
    mach: np.ndarray

    # freestream scalars
    mach_inf: float
    gamma: float

    # count of points using the Modified Newtonian nose fallback
    newtonian_fallback_points: int


# --------------------------------------------------
# internal helpers
# --------------------------------------------------
def _load_flow_conditions(json_path: Path) -> dict[str, float]:
    """Read scalar flow-state values from a flow-state JSON file."""

    # read the JSON file
    raw: dict[str, object] = json.loads(json_path.read_text())

    # extract values from flow-state [value, unit] pairs
    values: dict[str, float] = {}
    for key, value in raw.items():
        if isinstance(value, list) and len(value) == 2:
            values[key] = float(value[0])
        elif isinstance(value, (int, float)):
            values[key] = float(value)

    return values


def _surface_mach_from_temperature_ratio(
    temperature_ratio: float,
    mach_inf: float,
    gamma: float,
) -> float:
    """Recover surface Mach from Taylor-Maccoll static-temperature ratio."""

    # total temperature remains constant through the adiabatic inviscid flow
    total_temperature_ratio = 1.0 + 0.5 * (gamma - 1.0) * mach_inf**2
    surface_total_temperature_ratio = total_temperature_ratio / temperature_ratio

    # invert the isentropic total-to-static temperature relation
    mach_squared = 2.0 / (gamma - 1.0) * (surface_total_temperature_ratio - 1.0)
    return float(np.sqrt(max(mach_squared, 0.0)))


def _tangent_cone_point(
    theta_rad: float,
    mach_inf: float,
    gamma: float,
    pressure_fallback: float,
    mach_fallback: float,
) -> tuple[float, float, bool]:
    """Compute one tangent-cone point, falling back when no attached cone exists."""

    # zero-angle surface is the freestream limit
    theta_deg = float(np.degrees(theta_rad))
    if theta_deg <= 1.0e-8:
        return 1.0, mach_inf, False

    try:
        # solve Taylor-Maccoll for the local tangent cone
        result = solve_taylor_maccoll(
            mach=mach_inf,
            cone_angle=theta_deg,
            gamma=gamma,
        )
    except ValueError:
        # detached or otherwise invalid local cone: retain Modified Newtonian value
        return pressure_fallback, mach_fallback, True

    # use Taylor-Maccoll pressure ratio directly
    pressure_ratio = float(result.surface_pressure_ratio)
    mach_surface = _surface_mach_from_temperature_ratio(
        temperature_ratio=float(result.surface_temp_ratio),
        mach_inf=mach_inf,
        gamma=gamma,
    )

    return pressure_ratio, mach_surface, False


# --------------------------------------------------
# public API
# --------------------------------------------------
def solve_tangent_cone(cfg: Config) -> TangentConeResult:
    """Run tangent-cone theory over a body surface.

    Taylor-Maccoll is applied at local surface angles where an attached conical
    solution exists. The existing Modified Newtonian result supplies the blunt
    nose fallback, where a detached shock makes tangent-cone theory invalid.

    Args:
        cfg: Validated flow-inviscid configuration.

    Returns:
        TangentConeResult with pressure and Mach distributions.

    Raises:
        ValueError: If required configuration sections or flow values are missing.
    """

    # validate required sections
    if cfg.flow_conditions is None:
        raise ValueError("solve_tangent_cone requires [flow_conditions] in config")
    if cfg.body is None:
        raise ValueError("solve_tangent_cone requires [body] in config")

    # load freestream conditions
    flow_values = _load_flow_conditions(cfg.flow_conditions.file)
    mach_inf = flow_values["mach"]
    gamma = flow_values["gamma"]
    pres_inf = flow_values["pres"]

    # reuse Modified Newtonian for the blunt-nose fallback and common geometry load
    newtonian_result = solve_newtonian(cfg)
    geometry = compute_surface_geometry(newtonian_result.x, newtonian_result.y)

    # initialize outputs from the fallback model
    pressure_ratio = np.asarray(newtonian_result.p_p_inf, dtype=float).copy()
    mach_surface = np.asarray(newtonian_result.mach, dtype=float).copy()
    fallback_points = 0

    # replace valid local points with Taylor-Maccoll predictions
    for index, theta_rad in enumerate(geometry.theta):
        pressure_ratio[index], mach_surface[index], used_fallback = _tangent_cone_point(
            theta_rad=float(theta_rad),
            mach_inf=mach_inf,
            gamma=gamma,
            pressure_fallback=float(pressure_ratio[index]),
            mach_fallback=float(mach_surface[index]),
        )
        if used_fallback:
            fallback_points += 1

    # convert pressure ratio to pressure coefficient using freestream dynamic pressure
    dynamic_pressure = 0.5 * gamma * pres_inf * mach_inf**2
    pressure = pressure_ratio * pres_inf
    cp = (pressure - pres_inf) / dynamic_pressure

    return TangentConeResult(
        x=geometry.x,
        y=geometry.y,
        s=geometry.s,
        theta=geometry.theta,
        cp=cp,
        p_p_inf=pressure_ratio,
        mach=mach_surface,
        mach_inf=mach_inf,
        gamma=gamma,
        newtonian_fallback_points=fallback_points,
    )
