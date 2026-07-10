"""Tests for flow_inviscid.config.schema."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
import pytest
from pydantic import ValidationError

from flow_inviscid.config.schema import VALID_METHODS, Config, MethodConfig

# --------------------------------------------------
# MethodConfig tests
# --------------------------------------------------

class TestMethodConfig:

    def test_valid_method_names(self):
        # each registered method name should construct without error
        for name in VALID_METHODS:
            cfg = MethodConfig(name=name)
            assert cfg.name == name

    def test_case_normalization_upper(self):
        # uppercase should be folded to lowercase
        cfg = MethodConfig(name="TANGENT_CONE")
        assert cfg.name == "tangent_cone"

    def test_case_normalization_mixed(self):
        # mixed case should also normalize
        cfg = MethodConfig(name="Newtonian")
        assert cfg.name == "newtonian"

    def test_hyphen_normalization(self):
        # hyphens should be converted to underscores
        cfg = MethodConfig(name="shock-expansion")
        assert cfg.name == "shock_expansion"

    def test_hyphen_and_upper(self):
        # combined: uppercase + hyphens
        cfg = MethodConfig(name="SHOCK-EXPANSION")
        assert cfg.name == "shock_expansion"

    def test_invalid_method_name_raises(self):
        # an unrecognized name should raise a Pydantic ValidationError
        with pytest.raises(ValidationError):
            MethodConfig(name="bad_method")

    def test_empty_string_raises(self):
        # an empty string is not a valid method name
        with pytest.raises(ValidationError):
            MethodConfig(name="")


# --------------------------------------------------
# Config tests
# --------------------------------------------------

class TestConfig:

    def test_from_dict_valid(self):
        # a well-formed dict should produce a Config with the correct method name
        cfg = Config.from_dict({"method": {"name": "tangent_cone"}})
        assert cfg.method.name == "tangent_cone"

    def test_from_dict_normalizes_name(self):
        # normalization applies through from_dict as well
        cfg = Config.from_dict({"method": {"name": "shock-expansion"}})
        assert cfg.method.name == "shock_expansion"

    def test_from_dict_missing_method_section_raises(self):
        # [method] is required -- missing it should raise
        with pytest.raises(ValidationError):
            Config.from_dict({})

    def test_from_dict_invalid_method_name_raises(self):
        # invalid method name inside a valid structure should raise
        with pytest.raises(ValidationError):
            Config.from_dict({"method": {"name": "not_a_method"}})

    def test_from_dict_missing_name_key_raises(self):
        # [method] section present but no "name" field
        with pytest.raises(ValidationError):
            Config.from_dict({"method": {}})
