import json
import tarfile
import tempfile
import zipfile
from datetime import datetime
from os import mkdir
from os.path import exists
from pathlib import Path
from typing import List, Literal

from bible_translations.models.book import Book
from bible_translations.models.info import Info
from bible_translations.utils.logger import logger


class Exporter:
    """Export Bible translations to various formats."""

    def __init__(self, output_dir: str = "exports"):
        """
        Initialize the exporter.

        :param output_dir: Directory to save exported files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def export(
            self,
            books: List[Book],
            file_format: Literal["json"] = "json",
            compression: Literal[".tar.gz", ".tgz", ".zip"] = "zip",
            folder_name: str | None = None
    ) -> str:
        """
        Export books to the specified format.

        :param folder_name: Name of the exported folder
        :param compression: Type of compression to use (tar.gz, tgz, zip)
        :param books: List of Book objects to export
        :param file_format: Export format (json, txt, csv, xml)
        :return: Path to the exported file
        """

        # If the list is empty, return an error
        if not books or len(books) == 0:
            raise ValueError("No books to export")

        # first book info is always used
        book_info = books[0].info

        # Create a temp directory and do all the work in there
        with tempfile.TemporaryDirectory() as tempdir:
            logger.debug('Created temporary directory: %s', tempdir)
            # Grab today's date and time
            date = datetime.now().strftime("%Y%m%d_%H%M%S")
            logger.debug('Date: %s', date)
            # Create the parent folder if name is empty
            if not folder_name:
                abbreviation = book_info.abbreviation.lower() if book_info.abbreviation else "bt"
                abbreviation += "_"
                parent_folder = tempdir + "/" + abbreviation  + file_format + "_export_" + date
            else :
                parent_folder = folder_name

            Path(parent_folder).mkdir(exist_ok=False)

            # Create all the export files depending on parameters
            if file_format == "json":
                self._export_json(books, parent_folder, book_info)
            elif file_format == "sql":
                raise NotImplementedError("SQL export not implemented yet")

            # compress and zip to finale location
            if compression in [".tar.gz", ".tgz"]:
                output_path = str(self.output_dir / f"{Path(parent_folder).name}.tar.gz")
                with tarfile.open(output_path, "w:gz") as tar:
                    tar.add(parent_folder, arcname=Path(parent_folder).name)
                return output_path
            else:  # .zip
                output_path = str(self.output_dir / f"{Path(parent_folder).name}.zip")
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for file in Path(parent_folder).rglob('*'):
                        zip_file.write(file, file.relative_to(Path(parent_folder)))
                return output_path

    @staticmethod
    def _export_json(books: List[Book], output_dir: str, info: Info):
        logger.debug('Exporting JSON files...')
        # Generate the info first
        info_data = {
            "translation": info.translation or "",
            "abbreviation": info.abbreviation or "",
            "language": info.language or "",
            "copyright": info.copyright or "",
            "url": info.url or "",
            "fetch_date": info.fetch_date or ""
        }

        with open(output_dir + "/" + info.abbreviation.lower() + "_info.json", "w") as json_file:
            json.dump(info_data, json_file, indent=4)

        # Export each book as a separate JSON file
        for book in books:
            logger.debug('Exporting book: %s', book.name)

            # Create a book data structure
            book_data = {
                "name": book.name,
                "chapters": []
            }

            # Add chapters and verses
            for chapter in book.chapters:
                chapter_data = {
                    "number": chapter.number,
                    "verses": []
                }

                # Add verses to a chapter
                for verse in chapter.verses:
                    verse_data = {
                        "number": verse.number,
                        "text": verse.text
                    }
                    chapter_data["verses"].append(verse_data)

                book_data["chapters"].append(chapter_data)

            # Create filename (sanitize book name for filesystem)
            safe_book_name = "".join(c for c in book.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_book_name = safe_book_name.replace(' ', '_').lower()
            filename = f"{safe_book_name}.json"
            books_dir = Path(output_dir) / "books"
            if not exists(books_dir):
                mkdir(books_dir)

            # Write book data to JSON file
            file_path = Path(books_dir, filename)
            with open(file_path, "w", encoding="utf-8") as json_file:
                json.dump(book_data, json_file, indent=4, ensure_ascii=False)

        full_data = {
            "info": info_data,
            "books": [
                {
                    "name": book.name,
                    "chapters": [
                        {
                            "number": chapter.number,
                            "verses": [
                                {
                                    "number": verse.number,
                                    "text": verse.text
                                }
                                for verse in chapter.verses
                            ]
                        }
                        for chapter in book.chapters
                    ]
                }
                for book in books
            ]
        }

        full_file_path = Path(output_dir, info.abbreviation.lower() + ".json")
        with open(full_file_path, "w", encoding="utf-8") as json_file:
            json.dump(full_data, json_file, indent=4, ensure_ascii=False)

        logger.debug('JSON export completed for %d books', len(books))