"""CLI integration tests using typer's CliRunner."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import pytest
from typer.testing import CliRunner

from flow_inviscid.cli.app import cli

# -- shared runner ---
runner = CliRunner()


# --------------------------------------------------
# help / smoke tests
# --------------------------------------------------
class TestHelp:
    def test_root_help(self):
        # top-level --help must exit 0
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "init" in result.output
        assert "solve" in result.output

    def test_init_help(self):
        result = runner.invoke(cli, ["init", "--help"])
        assert result.exit_code == 0

    def test_solve_help(self):
        result = runner.invoke(cli, ["solve", "--help"])
        assert result.exit_code == 0


# --------------------------------------------------
# init subcommands
# --------------------------------------------------
class TestInitCommands:
    @pytest.mark.parametrize(
        "subcmd, default_stem",
        [
            ("tangent-cone", "tangent_cone"),
            ("newtonian", "newtonian"),
            ("shock-expansion", "shock_expansion"),
        ],
    )
    def test_init_writes_file(self, tmp_path, subcmd, default_stem):
        # write config to a temp path and confirm the file appears
        out = tmp_path / f"{default_stem}.toml"
        result = runner.invoke(cli, ["init", subcmd, "--output", str(out)])
        assert result.exit_code == 0
        assert out.exists()
        assert "Written:" in result.output

    @pytest.mark.parametrize("subcmd", ["tangent-cone", "newtonian", "shock-expansion"])
    def test_init_refuses_overwrite_without_force(self, tmp_path, subcmd):
        # second write without --force must exit 1 with an error message
        out = tmp_path / "cfg.toml"
        runner.invoke(cli, ["init", subcmd, "--output", str(out)])
        result = runner.invoke(cli, ["init", subcmd, "--output", str(out)])
        assert result.exit_code == 1
        assert "already exists" in result.output

    @pytest.mark.parametrize("subcmd", ["tangent-cone", "newtonian", "shock-expansion"])
    def test_init_force_overwrites(self, tmp_path, subcmd):
        # --force must allow overwrite and exit 0
        out = tmp_path / "cfg.toml"
        runner.invoke(cli, ["init", subcmd, "--output", str(out)])
        result = runner.invoke(cli, ["init", subcmd, "--output", str(out), "--force"])
        assert result.exit_code == 0


# --------------------------------------------------
# solve subcommand
# --------------------------------------------------
class TestSolveCommand:
    def test_solve_method_not_implemented(self, tmp_path):
        # tangent-cone is not yet implemented — solve must exit 1 with a clear message
        out = tmp_path / "tc.toml"
        runner.invoke(cli, ["init", "tangent-cone", "--output", str(out)])
        result = runner.invoke(cli, ["solve", str(out)])
        assert result.exit_code == 1
        assert "not yet implemented" in result.output.lower()

    def test_solve_missing_file(self, tmp_path):
        # solve on a non-existent file must exit non-zero
        result = runner.invoke(cli, ["solve", str(tmp_path / "ghost.toml")])
        assert result.exit_code != 0
