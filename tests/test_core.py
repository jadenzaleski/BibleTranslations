from bible_translations.core import main


def test_main_runs():
    """Simple smoke test to ensure main() runs without error."""
    result = main()
    # If main() has no return, just ensure it doesn't raise an exception
    assert result is None or result is not None  # placeholder assert