"""Basic tests for generate-project."""

def test_version() -> None:
    """Test that version is defined."""
    from generate_project import __version__
    assert __version__ is not None
    assert isinstance(__version__, str)
