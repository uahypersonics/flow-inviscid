"""Configuration schema for flow-inviscid.

Uses Pydantic v2 BaseModel for validation and rich error messages.
Mirrors the pattern used in similarity-bl.

Current sections:
    [method]  -- which surface-condition method to use (always required)

Future sections will be added here as the tool develops:
    [body]       -- body geometry (type, dimensions)
    [freestream] -- freestream conditions (Mach, temperature, etc.)
    [output]     -- output format and station locations
"""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

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
# Config class
#
# based on the Pydantic BaseModel, which provides validation and rich error messages
# --------------------------------------------------
class Config(BaseModel):
    """Top-level configuration for a flow-inviscid solve."""

    method: MethodConfig

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Config:
        """Build from a raw dict parsed from a TOML file."""
        return cls.model_validate(d)

