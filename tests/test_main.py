"""testing the main func"""

from thin_controller.__main__ import cli


def test_cli_help() -> None:
    """Test that the CLI help command works."""
    result = cli(["--help"], standalone_mode=False)
    assert result == 0
