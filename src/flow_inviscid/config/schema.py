"""Configuration schema for flow-inviscid.

Uses Pydantic v2 BaseModel for validation and rich error messages.
Mirrors the pattern used in similarity-bl.

Sections:
    [method]          -- which surface-condition method to use (always required)
    [flow_conditions] -- path to a flow-state JSON file
    [body]            -- body geometry file and type
    [output]          -- output file and format
"""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, field_validator

# --------------------------------------------------
# define valid method names (add as required)
# --------------------------------------------------
VALID_METHODS = {"tangent_cone", "newtonian", "shock_expansion"}

# --------------------------------------------------
# MethodConfig
# --------------------------------------------------
class MethodConfig(BaseModel):
    """[method] section: selects the surface-condition calculation method."""

    # method name (must be a string and one of VALID_METHODS defined above -> see validator below)
    name: str

    # @field_validator is the pydantic decorator for field validation logic.
    # it runs after pydantic has already confirmed the field is the right type.
    @field_validator("name")
    # required by pydantic v2
    @classmethod
    # validator logic for the method name field
    # cls is the class MethodConfig
    # v is the value of the field "name" of MethodConfig that pydantic extracted from the input dict
    def validate_method_name(cls, v: str) -> str:
        # normalize: lowercase and replace hyphens with underscores so that
        # "shock-expansion", "SHOCK_EXPANSION", and "shock_expansion" all match
        normalized = v.strip().lower().replace("-", "_")

        # check that the normalized name is one of the registered options
        if normalized not in VALID_METHODS:
            raise ValueError(
                f"must be one of {sorted(VALID_METHODS)}: got {v!r}"
            )

        # return the normalized form so the stored value is always consistent
        return normalized


# --------------------------------------------------
# FlowConditionsConfig
# --------------------------------------------------
class FlowConditionsConfig(BaseModel):
    """[flow_conditions] section: path to a flow-state JSON file."""

    # path to a flow-state JSON file produced by `flow-state`
    file: Path

    # create validator for the file extension
    @field_validator("file")
    @classmethod
    def validate_extension(cls, v: Path) -> Path:
        # validate that the file has a .json or .dat extension
        if v.suffix.lower() not in {".json", ".dat"}:
            raise ValueError(
                f"flow_conditions.file must be a .json or .dat file: got {v.name!r}"
            )
        return v

# --------------------------------------------------
# BodyConfig
# --------------------------------------------------

# valid geometry types
VALID_GEOMETRY_TYPES = {"axisymmetric", "2d"}

class BodyConfig(BaseModel):
    """[body] section: body geometry file and coordinate system."""

    # path to a two-column (x  y) geometry file
    geometry_file: Path
    # coordinate system: axisymmetric (cone, ogive) or 2d (wedge, airfoil)
    geometry_type: str = "axisymmetric"

    @field_validator("geometry_type")
    @classmethod
    def validate_geometry_type(cls, v: str) -> str:
        # normalize and validate geometry type
        normalized = v.strip().lower()
        if normalized not in VALID_GEOMETRY_TYPES:
            raise ValueError(
                f"body.geometry_type must be one of {sorted(VALID_GEOMETRY_TYPES)}: got {v!r}"
            )
        return normalized

# --------------------------------------------------
# OutputConfig
# --------------------------------------------------

# valid output formats
VALID_OUTPUT_FORMATS = {"tecplot"}

class OutputConfig(BaseModel):
    """[output] section: output file path and format."""

    # output file path
    file: Path
    # output format (tecplot ASCII is the only supported format for now)
    format: str = "tecplot"

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        # normalize and validate output format
        normalized = v.strip().lower()
        if normalized not in VALID_OUTPUT_FORMATS:
            raise ValueError(
                f"output.format must be one of {sorted(VALID_OUTPUT_FORMATS)}: got {v!r}"
            )
        return normalized

# --------------------------------------------------
# Config class
# --------------------------------------------------
class Config(BaseModel):
    """Top-level configuration for a flow-inviscid solve."""

    method: MethodConfig
    # optional sections — present only for full solve configs
    flow_conditions: FlowConditionsConfig | None = None
    body: BodyConfig | None = None
    output: OutputConfig | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Config:
        """Build from a raw dict parsed from a TOML file."""
        return cls.model_validate(d)

