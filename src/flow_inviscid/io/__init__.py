"""flow-inviscid I/O package."""

from flow_inviscid.io.read_ascii import AsciiData, read_ascii
from flow_inviscid.io.read_body import read_surface_coordinates
from flow_inviscid.io.write_tecplot import write_tecplot

__all__ = ["AsciiData", "read_ascii", "read_surface_coordinates", "write_tecplot"]
