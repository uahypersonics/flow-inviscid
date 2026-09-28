"""Tests for tangent-cone surface-condition calculations."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from flow_inviscid.config.schema import Config
from flow_inviscid.methods.tangent_cone import solve_tangent_cone


# --------------------------------------------------
# test helpers
# --------------------------------------------------
def _write_flow_conditions(path: Path) -> None:
    """Write the minimal flow-state JSON required by the solver."""

    values = {
        "mach": [5.3, "-"],
        "gamma": [1.4, "-"],
        "pres": [1827.6393385767838, "Pa"],
        "pres_stag": [1362806.4087942184, "Pa"],
    }
    path.write_text(json.dumps(values), encoding="utf-8")


def _build_config(tmp_path: Path, surface: str) -> Config:
    """Build a validated tangent-cone config for a temporary surface."""

    flow_path = tmp_path / "flow_conditions.json"
    body_path = tmp_path / "body.dat"
    _write_flow_conditions(flow_path)
    body_path.write_text(surface, encoding="utf-8")

    return Config.from_dict(
        {
            "method": {"name": "tangent_cone"},
            "flow_conditions": {"file": str(flow_path)},
            "body": {
                "geometry_file": str(body_path),
                "geometry_type": "axisymmetric",
            },
        }
    )


# --------------------------------------------------
# solver tests
# --------------------------------------------------
def test_tangent_cone_returns_attached_cone_solution(tmp_path: Path) -> None:
    """A constant ten-degree surface should use Taylor-Maccoll throughout."""

    surface = "\n".join(
        [
            "0.000000 0.000000",
            "0.010000 0.001763",
            "0.020000 0.003527",
            "0.030000 0.005290",
        ]
    )
    cfg = _build_config(tmp_path, surface)

    result = solve_tangent_cone(cfg)

    assert result.x.shape == (4,)
    assert result.p_p_inf.shape == (4,)
    assert result.mach.shape == (4,)
    assert np.all(result.p_p_inf > 1.0)
    assert np.all(result.mach > 0.0)
    assert result.newtonian_fallback_points == 0


def test_tangent_cone_falls_back_on_blunt_nose(tmp_path: Path) -> None:
    """A ninety-degree nose point should use Modified Newtonian fallback."""

    surface = "\n".join(
        [
            "0.000000 0.000000",
            "0.001000 0.010000",
            "0.010000 0.011582",
            "0.020000 0.013168",
        ]
    )
    cfg = _build_config(tmp_path, surface)

    result = solve_tangent_cone(cfg)

    assert result.newtonian_fallback_points >= 1
    assert np.all(np.isfinite(result.p_p_inf))
    assert np.all(np.isfinite(result.mach))
    assert result.mach[0] >= 0.0


@pytest.mark.parametrize("method_name", ["tangent_cone", "tangent-cone"])
def test_tangent_cone_method_name_normalizes(method_name: str) -> None:
    """Method config should accept underscore and hyphen spellings."""

    cfg = Config.from_dict({"method": {"name": method_name}})

    assert cfg.method.name == "tangent_cone"
