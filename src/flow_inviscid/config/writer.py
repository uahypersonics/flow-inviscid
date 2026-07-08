"""Write a flow-inviscid TOML config file from a template."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from pathlib import Path

from flow_inviscid.config.template import TEMPLATES


# --------------------------------------------------
# write_config
# --------------------------------------------------
def write_config(method_key: str, path: Path) -> None:
    """Write a TOML config file for the given method.

    Args:
        method_key: Internal method key (e.g. "tangent_cone").
                    Must be a key in config.template.TEMPLATES.
        path: Output file path. Caller is responsible for existence checks.
    """
    # write the template content for this method
    content = TEMPLATES[method_key]
    path.write_text(content)
