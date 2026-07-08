"""Tests for flow_inviscid.config.template."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from flow_inviscid.config.schema import VALID_METHODS
from flow_inviscid.config.template import TEMPLATES


# --------------------------------------------------
# template registry tests
# --------------------------------------------------

class TestTemplates:

    def test_all_methods_have_templates(self):
        # every valid method name must have a corresponding template
        assert set(TEMPLATES.keys()) == VALID_METHODS

    def test_each_template_has_method_section(self):
        # every template must contain the [method] header
        for key, content in TEMPLATES.items():
            assert "[method]" in content, f"template {key!r} missing [method] section"

    def test_each_template_has_correct_name(self):
        # the name field inside each template must match the registry key
        for key, content in TEMPLATES.items():
            assert f'name = "{key}"' in content, (
                f"template {key!r} missing or wrong name field"
            )

    def test_templates_are_strings(self):
        # templates must be non-empty strings
        for key, content in TEMPLATES.items():
            assert isinstance(content, str) and content.strip(), (
                f"template {key!r} is empty or not a string"
            )
