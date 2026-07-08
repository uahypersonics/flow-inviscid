"""Tests for flow_inviscid.config.reader and writer (round-trip)."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
import pytest
from click.exceptions import Exit as ClickExit

from flow_inviscid.config.reader import read_config
from flow_inviscid.config.writer import write_config


# --------------------------------------------------
# round-trip tests
# --------------------------------------------------

class TestReaderWriter:

    def test_round_trip_tangent_cone(self, tmp_path):
        # write a tangent-cone config then read it back
        path = tmp_path / "tangent_cone.toml"
        write_config("tangent_cone", path)
        cfg = read_config(path)
        assert cfg.method.name == "tangent_cone"

    def test_round_trip_newtonian(self, tmp_path):
        # write a newtonian config then read it back
        path = tmp_path / "newtonian.toml"
        write_config("newtonian", path)
        cfg = read_config(path)
        assert cfg.method.name == "newtonian"

    def test_round_trip_shock_expansion(self, tmp_path):
        # write a shock-expansion config then read it back
        path = tmp_path / "shock_expansion.toml"
        write_config("shock_expansion", path)
        cfg = read_config(path)
        assert cfg.method.name == "shock_expansion"

    def test_write_creates_file(self, tmp_path):
        # write_config must create the output file
        path = tmp_path / "test.toml"
        assert not path.exists()
        write_config("newtonian", path)
        assert path.exists()

    def test_force_false_blocks_overwrite(self, tmp_path):
        # without --force, writing to an existing file should raise SystemExit
        path = tmp_path / "existing.toml"
        write_config("newtonian", path)
        with pytest.raises(ClickExit):
            write_config("newtonian", path, force=False)

    def test_force_true_allows_overwrite(self, tmp_path):
        # with force=True, overwriting should succeed
        path = tmp_path / "existing.toml"
        write_config("newtonian", path)
        write_config("tangent_cone", path, force=True)
        cfg = read_config(path)
        assert cfg.method.name == "tangent_cone"

    def test_read_missing_file_raises(self, tmp_path):
        # reading a non-existent file should raise FileNotFoundError
        with pytest.raises(FileNotFoundError):
            read_config(tmp_path / "does_not_exist.toml")
