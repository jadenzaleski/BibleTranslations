from click.testing import CliRunner

from bible_translations.core import cli


def test_cli_help():
    """Test that the CLI help command runs."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Bible Translations CLI" in result.output
    assert "verse" in result.output
    assert "chapter" in result.output
    assert "book" in result.output
    assert "books" in result.output
    assert "selection" in result.output


def test_cli_verse_help():
    """Test that the verse command help shows the translation option."""
    runner = CliRunner()
    result = runner.invoke(cli, ["verse", "--help"])
    assert result.exit_code == 0
    assert "--translation" in result.output
    assert "-t" in result.output
