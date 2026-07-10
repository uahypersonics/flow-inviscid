"""flow-inviscid configuration package."""

from flow_inviscid.config.reader import read_config
from flow_inviscid.config.schema import (
    VALID_METHODS,
    BodyConfig,
    Config,
    FlowConditionsConfig,
    MethodConfig,
    OutputConfig,
)
from flow_inviscid.config.writer import write_config

__all__ = [
    "BodyConfig",
    "Config",
    "FlowConditionsConfig",
    "MethodConfig",
    "OutputConfig",
    "VALID_METHODS",
    "read_config",
    "write_config",
]
