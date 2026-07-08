"""flow-inviscid configuration package."""

from flow_inviscid.config.reader import read_config
from flow_inviscid.config.schema import VALID_METHODS, Config, MethodConfig
from flow_inviscid.config.writer import write_config

__all__ = [
    "Config",
    "MethodConfig",
    "VALID_METHODS",
    "read_config",
    "write_config",
]
