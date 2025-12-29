from click.testing import CliRunner

from bible_translations.cli import cli
from bible_translations.constants import VERSION


def test_bt():
    """Test that the CLI runs."""
    runner = CliRunner()
    result = runner.invoke(cli)  # type: ignore
    assert result.exit_code == 0
    assert VERSION in result.output


def test_bt_verse():
    """Test that the CLI verse runs."""
    runner = CliRunner()
    result = runner.invoke(cli, ["verse", "--help"])  # type: ignore
    assert result.exit_code == 0


def test_bt_chapter():
    """Test that the CLI chapter runs."""
    runner = CliRunner()
    result = runner.invoke(cli, ["chapter", "--help"])  # type: ignore
    assert result.exit_code == 0


def test_bt_book():
    """Test that the CLI book runs."""
    runner = CliRunner()
    result = runner.invoke(cli, ["book", "--help"])  # type: ignore
    assert result.exit_code == 0


def test_bt_books():
    """Test that the CLI books runs."""
    runner = CliRunner()
    result = runner.invoke(cli, ["books", "--help"])  # type: ignore


def test_bt_selection():
    """Test that the CLI selection runs."""
    runner = CliRunner()
    result = runner.invoke(cli, ["selection", "--help"])  # type: ignore
