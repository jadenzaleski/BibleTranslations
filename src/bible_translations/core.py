from datetime import datetime
from zoneinfo import ZoneInfo

import click
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn

from bible_translations.constants import SUPPORTED_FORMATS, VERSION
from bible_translations.models.book import Book
from bible_translations.models.chapter import Chapter
from bible_translations.models.info import Info
from bible_translations.translations import TRANSLATIONS, get_translation
from bible_translations.utils.exporter import Exporter

console = Console()

customSpinner = SpinnerColumn(spinner_name="dots10", finished_text="[green]✓[/green]")


@click.group()
@click.version_option(version=VERSION)
def cli():
    """Bible Translations CLI - A tool to fetch and export Bible translations."""
    pass


def run_export(book_list, output_file, file_format):
    exporter = Exporter()
    return exporter.export(book_list, file_format=file_format, folder_name=output_file)


def get_translation_instance(name):
    try:
        return get_translation(name)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        console.print_exception()
        raise click.Abort()


@cli.command()
@click.argument("reference", metavar="VERSE")
@click.option(
    "--output",
    "-o",
    "output_file",
    type=click.Path(writable=True),
    help="Output file path. Default is generated with date.",
)
@click.option(
    "--format",
    "-f",
    "file_format",
    default="json",
    type=click.Choice(SUPPORTED_FORMATS, case_sensitive=False),
    show_default=True,
    help="Output format.",
)
@click.option(
    "--translation",
    "-t",
    default="KJV",
    type=click.Choice(list(TRANSLATIONS.keys()), case_sensitive=False),
    show_default=True,
    help="Bible translation to use.",
)
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output.")
def verse(reference, output_file, file_format, translation, verbose):
    """Fetch and export a specific verse (e.g., 'John 3:16')."""
    translation_obj = get_translation_instance(translation)
    try:
        if " " not in reference or ":" not in reference:
            raise ValueError(f"Invalid verse reference: {reference}. Expected format: 'Book Chapter:Verse'")

        book_name, chapter_num, verse_num = translation_obj.parse_ref(reference)

        with Progress(
            customSpinner, TextColumn("[progress.description]{task.description}"), console=console
        ) as progress:
            fetch_task = progress.add_task(description=f"Fetching {reference}...", total=1)
            verse_obj = translation_obj.get_verse(book_name, chapter_num, verse_num)

            info = Info(
                translation=translation_obj.name,
                abbreviation=translation_obj.abbreviation,
                language=translation_obj.language,
                copyright=translation_obj.copyright,
                url=translation_obj.url,
                fetch_date=datetime.now(tz=ZoneInfo("UTC")).isoformat(),
            )
            chapter_obj = Chapter(number=chapter_num, verses=[verse_obj])
            book_obj = Book(name=book_name, chapters=[chapter_obj], info=info)
            progress.update(fetch_task, advance=1, description=f"Fetched {book_name} {chapter_num}:{verse_num}")

            export_task = progress.add_task(description="Exporting...", total=1)
            output_path = run_export([book_obj], output_file, file_format)
            progress.update(export_task, advance=1, description=f"Exported {book_name} {chapter_num}:{verse_num}")

        console.print(
            f"[green]Successfully exported [bold]{book_name} {chapter_num}:{verse_num}[/bold] to {output_path}[/green]"
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        if verbose:
            console.print_exception()
        raise click.Abort()


@cli.command()
@click.argument("reference", metavar="CHAPTER")
@click.option(
    "--output",
    "-o",
    "output_file",
    type=click.Path(writable=True),
    help="Output file path. Default is generated with date.",
)
@click.option(
    "--format",
    "-f",
    "file_format",
    default="json",
    type=click.Choice(SUPPORTED_FORMATS, case_sensitive=False),
    show_default=True,
    help="Output format.",
)
@click.option(
    "--translation",
    "-t",
    default="KJV",
    type=click.Choice(list(TRANSLATIONS.keys()), case_sensitive=False),
    show_default=True,
    help="Bible translation to use.",
)
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output.")
def chapter(reference, output_file, file_format, translation, verbose):
    """Fetch and export a specific chapter (e.g., 'John 3')."""
    translation_obj = get_translation_instance(translation)
    try:
        if " " not in reference:
            raise ValueError(f"Invalid chapter reference: {reference}. Expected format: 'Book Chapter'")

        book_name, chapter_num, verse_num = translation_obj.parse_ref(reference)

        with Progress(
            customSpinner, TextColumn("[progress.description]{task.description}"), console=console
        ) as progress:
            fetch_task = progress.add_task(description=f"Fetching {reference}...", total=1)
            chapter_obj = translation_obj.get_chapter(book_name, chapter_num)

            info = Info(
                translation=translation_obj.name,
                abbreviation=translation_obj.abbreviation,
                language=translation_obj.language,
                copyright=translation_obj.copyright,
                url=translation_obj.url,
                fetch_date=datetime.now(tz=ZoneInfo("UTC")).isoformat(),
            )
            book_obj = Book(name=book_name, chapters=[chapter_obj], info=info)
            progress.update(fetch_task, advance=1, description=f"Fetched {book_name} {chapter_num}")

            export_task = progress.add_task(description="Exporting...", total=1)
            output_path = run_export([book_obj], output_file, file_format)
            progress.update(export_task, advance=1, description=f"Exported {book_name} {chapter_num}")

        console.print(f"[green]Successfully exported [bold]{book_name} {chapter_num}[/bold] to {output_path}[/green]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        if verbose:
            console.print_exception()
        raise click.Abort()


@cli.command()
@click.argument("book_name", metavar="BOOK")
@click.option(
    "--output",
    "-o",
    "output_file",
    type=click.Path(writable=True),
    help="Output file path. Default is generated with date.",
)
@click.option(
    "--format",
    "-f",
    "file_format",
    default="json",
    type=click.Choice(SUPPORTED_FORMATS, case_sensitive=False),
    show_default=True,
    help="Output format.",
)
@click.option(
    "--translation",
    "-t",
    default="KJV",
    type=click.Choice(list(TRANSLATIONS.keys()), case_sensitive=False),
    show_default=True,
    help="Bible translation to use.",
)
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output.")
def book(book_name, output_file, file_format, translation, verbose):
    """Fetch and export a specific book (e.g., 'John')."""
    translation_obj = get_translation_instance(translation)
    try:
        with Progress(
            customSpinner,
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            normalized_book_name, chapter_num, verse_num = translation_obj.parse_ref(book_name)
            chapter_count = translation_obj.book_chapter_counts[normalized_book_name]

            fetch_task = progress.add_task(f"Fetching {normalized_book_name}", total=chapter_count)
            book_obj = translation_obj.get_book(
                name=book_name, on_chapter_complete=lambda: progress.update(fetch_task, advance=1)
            )
            progress.update(fetch_task, completed=chapter_count, description=f"Fetched {normalized_book_name}")

            export_task = progress.add_task(description="Exporting...", total=None)
            output_path = run_export([book_obj], output_file, file_format)
            progress.update(export_task, total=1, completed=1, description=f"Exported {normalized_book_name}")

        console.print(f"[green]Successfully exported [bold]{normalized_book_name}[/bold] to {output_path}[/green]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        if verbose:
            console.print_exception()
        raise click.Abort()


@cli.command(name="books")
@click.option(
    "--output",
    "-o",
    "output_file",
    type=click.Path(writable=True),
    help="Output file path. Default is generated with date.",
)
@click.option(
    "--format",
    "-f",
    "file_format",
    default="json",
    type=click.Choice(SUPPORTED_FORMATS, case_sensitive=False),
    show_default=True,
    help="Output format.",
)
@click.option(
    "--translation",
    "-t",
    default="KJV",
    type=click.Choice(list(TRANSLATIONS.keys()), case_sensitive=False),
    show_default=True,
    help="Bible translation to use.",
)
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output.")
def books(output_file, file_format, translation, verbose):
    """Fetch and export all books."""
    translation_obj = get_translation_instance(translation)
    try:
        with Progress(
            customSpinner,
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            book_count = len(translation_obj.books)
            fetch_task = progress.add_task(f"Fetching {book_count} books", total=book_count)

            books_obj = translation_obj.get_books(on_book_complete=lambda: progress.update(fetch_task, advance=1))

            progress.update(fetch_task, completed=book_count, description=f"Fetched {book_count} books")

            export_task = progress.add_task(description="Exporting...", total=None)
            output_path = run_export(books_obj, output_file, file_format)
            progress.update(export_task, total=1, completed=1, description=f"Exported {book_count} books")

        console.print(
            f"[green]Successfully exported {book_count} {translation_obj.abbreviation} books to {output_path}[/green]"
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        if verbose:
            console.print_exception()
        raise click.Abort()


@cli.command()
@click.argument("start_ref")
@click.argument("end_ref")
@click.option(
    "--output",
    "-o",
    "output_file",
    type=click.Path(writable=True),
    help="Output file path. Default is generated with date.",
)
@click.option(
    "--format",
    "-f",
    "file_format",
    default="json",
    type=click.Choice(SUPPORTED_FORMATS, case_sensitive=False),
    show_default=True,
    help="Output format.",
)
@click.option(
    "--translation",
    "-t",
    default="KJV",
    type=click.Choice(list(TRANSLATIONS.keys()), case_sensitive=False),
    show_default=True,
    help="Bible translation to use.",
)
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output.")
def selection(start_ref, end_ref, output_file, file_format, translation, verbose):
    """Fetch and export a selection (e.g., 'John 3:16' 'John 3:17')."""
    translation_obj = get_translation_instance(translation)
    try:
        with Progress(
            customSpinner, TextColumn("[progress.description]{task.description}"), console=console
        ) as progress:
            fetch_task = progress.add_task(f"Fetching {start_ref} - {end_ref} ", total=None)

            selection_obj = translation_obj.get_selection(start_ref, end_ref)

            progress.update(fetch_task, completed=1, total=1, description=f"Fetched {start_ref} - {end_ref}")

            export_task = progress.add_task(description="Exporting...", total=None)
            output_path = run_export(selection_obj, output_file, file_format)
            progress.update(export_task, total=1, completed=1, description=f"Exported {start_ref} - {end_ref}")

        console.print(f"[green]Successfully exported selection to {output_path}[/green]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        if verbose:
            console.print_exception()
        raise click.Abort()


def main():
    cli()


if __name__ == "__main__":
    main()
