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
    def test_solve_tangent_cone(self, tmp_path):
        # write the required tangent-cone inputs
        out = tmp_path / "tc.toml"
        flow = tmp_path / "freestream.json"
        body = tmp_path / "body.dat"
        result_path = tmp_path / "result.dat"
        flow.write_text(
            '{"mach": [5.3, "-"], "gamma": [1.4, "-"], '
            '"pres": [1827.6393385767838, "Pa"], '
            '"pres_stag": [1362806.4087942184, "Pa"]}',
            encoding="utf-8",
        )
        body.write_text("0.0 0.0\n0.01 0.001763\n0.02 0.003527\n", encoding="utf-8")
        out.write_text(
            "\n".join(
                [
                    '[method]\nname = "tangent_cone"',
                    "[flow_conditions]",
                    f'file = "{flow}"',
                    "[body]",
                    f'geometry_file = "{body}"',
                    'geometry_type = "axisymmetric"',
                    "[output]",
                    f'file = "{result_path}"',
                    'format = "tecplot"',
                ]
            ),
            encoding="utf-8",
        )

        # run tangent-cone through the public solve command
        result = runner.invoke(cli, ["solve", str(out)])

        assert result.exit_code == 0
        assert result_path.exists()
        assert "Tangent Cone" in result.output

    def test_solve_unknown_method_reports_error(self, tmp_path):
        # tangent-cone is no longer the unimplemented-method case
        out = tmp_path / "unknown.toml"
        out.write_text('[method]\nname = "shock_expansion"\n', encoding="utf-8")

        result = runner.invoke(cli, ["solve", str(out)])
        assert result.exit_code == 1
        assert "not yet implemented" in result.output.lower()

    def test_solve_missing_file(self, tmp_path):
        # solve on a non-existent file must exit non-zero
        result = runner.invoke(cli, ["solve", str(tmp_path / "ghost.toml")])
        assert result.exit_code != 0
