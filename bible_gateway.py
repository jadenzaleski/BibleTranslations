import json
import os
import re
import sys
import time
import signal
from datetime import datetime

import meaningless.utilities.common as common
from meaningless import JSONDownloader
from meaningless.utilities.common import BIBLE_TRANSLATIONS


# Replacing the function with a new version to allow for proper download of all verses in a chapter
def custom_get_capped_integer(number, min_value=1, max_value=200):
    return min(max(int(number), int(min_value)), int(max_value))


# Override the original function with the custom version
common.get_capped_integer = custom_get_capped_integer

# books of the bible in order
books = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges", "Ruth", "1 Samuel",
         "2 Samuel", "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Esther", "Job",
         "Psalm", "Proverbs", "Ecclesiastes", "Song Of Solomon", "Isaiah", "Jeremiah", "Lamentations", "Ezekiel",
         "Daniel", "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai",
         "Zechariah", "Malachi", "Matthew", "Mark", "Luke", "John", "Acts", "Romans", "1 Corinthians",
         "2 Corinthians", "Galatians", "Ephesians", "Philippians", "Colossians", "1 Thessalonians",
         "2 Thessalonians", "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "James", "1 Peter", "2 Peter",
         "1 John", "2 John", "3 John", "Jude", "Revelation"]

COUNT = 0
TOTAL = 0
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
TIMEOUT_SECONDS = 30  # timeout for each book download


class TimeoutError(Exception):
    """Custom exception for timeout errors"""
    pass


def timeout_handler(signum, frame):
    """Signal handler for timeout"""
    raise TimeoutError("Download timed out")


def is_valid_book_file(file_path):
    """Check if a book JSON file is valid and not empty"""
    if not os.path.exists(file_path):
        return False
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            # Check if the file has content
            if not data:
                return False
            # Check if it has at least one book with chapters
            for book_name, chapters in data.items():
                if chapters and len(chapters) > 0:
                    return True
            return False
    except (json.JSONDecodeError, IOError):
        return False


def is_valid_bible_json(file_path):
    """Check if the combined bible JSON file is valid and contains all 66 books"""
    if not os.path.exists(file_path):
        return False
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            # Check if we have all 66 books
            if len(data) == 66:
                # Verify all books are present
                return all(book in data for book in books)
            return False
    except (json.JSONDecodeError, IOError):
        return False


# download a single book with retry logic
def download_book_with_retry(book_name, folder, translation, max_retries=MAX_RETRIES):
    """Download a book with retry logic and timeout handling"""
    downloader = JSONDownloader(translation=translation, show_passage_numbers=False, strip_excess_whitespace=True)
    
    for attempt in range(max_retries):
        try:
            print(f"    Attempt {attempt + 1}/{max_retries} for {book_name}...", end="", flush=True)
            
            # Set up timeout
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(TIMEOUT_SECONDS)
            
            try:
                result = downloader.download_book(book_name, folder + "/" + book_name + ".json")
                signal.alarm(0)  # Cancel the alarm
                
                if result == 1:
                    print(f" ✓ Success")
                    return True
                else:
                    print(f" ✗ Failed (return code: {result})")
                    if attempt < max_retries - 1:
                        print(f"    Waiting {RETRY_DELAY} seconds before retry...")
                        time.sleep(RETRY_DELAY)
                    continue
                    
            except TimeoutError:
                print(f" ✗ Timeout after {TIMEOUT_SECONDS} seconds")
                if attempt < max_retries - 1:
                    print(f"    Waiting {RETRY_DELAY} seconds before retry...")
                    time.sleep(RETRY_DELAY)
                continue
                
            finally:
                signal.alarm(0)  # Cancel any pending alarm
                signal.signal(signal.SIGALRM, old_handler)  # Restore old handler
                
        except Exception as e:
            print(f" ✗ Error: {str(e)}")
            if attempt < max_retries - 1:
                print(f"    Waiting {RETRY_DELAY} seconds before retry...")
                time.sleep(RETRY_DELAY)
            continue
    
    print(f"    ✗ All {max_retries} attempts failed for {book_name}")
    return False


# combine all the books into one json file
def combine(folder, n):
    combined_data = {}

    # Iterate through all files in the folder
    for file_name in os.listdir(folder):
        if file_name.endswith('.json'):
            fp = os.path.join(folder, file_name)

            try:
                with open(fp, 'r') as f:
                    data = json.load(f)
                    # Exclude the "Info" section if present
                    if "Info" in data:
                        del data["Info"]
                    # Remove extra whitespace characters from verse content
                    for book, chapters in data.items():
                        for chapter, verses in chapters.items():
                            for verse_num, verse_content in verses.items():
                                # Replace newline characters and excess spaces with a single space
                                data[book][chapter][verse_num] = verse_content.strip()

                    combined_data.update(data)
            except json.JSONDecodeError as e:
                print(f"[!] Error parsing {file_name}: {e}")
                continue

    # Write the combined data to the output file in order
    ordered_data = {book: combined_data[book] for book in books if book in combined_data}

    with open(n, 'w') as out_file:
        json.dump(ordered_data, out_file, indent=4)


# a text progress bar
def generate_progress_bar(progress, total, length=20):
    progress_ratio = min(progress / total, 1) if total > 0 else 0
    progress_bar_length = int(progress_ratio * length)
    progress_bar = "#" * progress_bar_length + "-" * (length - progress_bar_length)
    return f"[{progress_bar}] {progress:2d}/{total}"


def extract_books_from_bible_json(bible_json_path, books_folder):
    """Extract individual books from the combined bible JSON file"""
    try:
        with open(bible_json_path, 'r') as f:
            bible_data = json.load(f)
        
        extracted_count = 0
        for book_name, chapters in bible_data.items():
            book_file_path = os.path.join(books_folder, f"{book_name}.json")
            
            # Skip if book file already exists and is valid
            if is_valid_book_file(book_file_path):
                print(f"[+] Skipping {book_name} - already exists and valid")
                continue
            
            # Write the book to its own file
            book_data = {book_name: chapters}
            with open(book_file_path, 'w') as f:
                json.dump(book_data, f, indent=4)
            extracted_count += 1
            print(f"[+] Extracted {book_name} from combined JSON")
        
        return extracted_count
    except (json.JSONDecodeError, IOError) as e:
        print(f"[!] Error extracting books from {bible_json_path}: {e}")
        return 0


def generate_bible(bible_translation, show_progress=True):
    # root
    if not os.path.exists(bible_translation):
        os.makedirs(bible_translation)

    root = bible_translation + "/"
    path = root + bible_translation + "_books"
    if not os.path.exists(path):
        os.makedirs(path)
    
    bible_json_path = root + bible_translation + "_bible.json"
    bible_sql_path = root + bible_translation + "_bible.sql"
    
    # Check if the combined bible JSON already exists and is valid
    if is_valid_bible_json(bible_json_path):
        print(f"[✓] {bible_translation} is already complete (all 66 books found in {bible_json_path})")
        
        # Extract books from the existing JSON if needed
        extracted = extract_books_from_bible_json(bible_json_path, path)
        if extracted > 0:
            print(f"[+] Extracted {extracted} books from existing combined JSON")
        
        # Check if SQL file needs to be generated
        if not os.path.exists(bible_sql_path):
            print(f"[+] Generating SQL file for {bible_translation}...")
            generate_sql(bible_json_path, bible_sql_path, bible_translation)
            print(f"[✓] SQL file created: {bible_sql_path}")
        else:
            print(f"[✓] SQL file already exists: {bible_sql_path}")
        
        print(f"[✓] {bible_translation} is ready, skipping...")
        return
    
    print(f"[+] Starting download for {bible_translation}")
    start_time = datetime.now()
    
    # Download missing books
    downloaded_count = 0
    skipped_count = 0
    failed_books = []
    
    for i, book in enumerate(books):
        global COUNT, TOTAL
        COUNT += 1
        
        book_file_path = os.path.join(path, f"{book}.json")
        
        # Check if book already exists and is valid
        if is_valid_book_file(book_file_path):
            skipped_count += 1
            if show_progress:
                print(f"[✓] Skipping {book} - already exists and valid ({i+1}/{len(books)})")
            continue
        
        # Download the book with retry logic
        print(f"[+] Downloading {book} ({i+1}/{len(books)})...")
        
        if not download_book_with_retry(book, path, bible_translation):
            failed_books.append(book)
            print(f"[!] ERROR: {book} failed to download after {MAX_RETRIES} attempts")
            # Continue with next book instead of stopping
            continue
        else:
            downloaded_count += 1
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    if show_progress:
        print(f"\n[+] Download summary for {bible_translation}:")
        print(f"    - Time taken: {duration}")
        print(f"    - Downloaded: {downloaded_count} books")
        print(f"    - Skipped (already existed): {skipped_count} books")
        if failed_books:
            print(f"    - Failed: {len(failed_books)} books")
            for failed_book in failed_books:
                print(f"      • {failed_book}")
    
    # Check if we have all books before combining
    existing_books = []
    for book in books:
        if is_valid_book_file(os.path.join(path, f"{book}.json")):
            existing_books.append(book)
    
    print(f"[+] Progress: {len(existing_books)}/66 books available for {bible_translation}")
    
    if len(existing_books) == 66:
        # Combine all books
        print(f"[+] Combining all books for {bible_translation}...")
        combine(path, bible_json_path)
        print(f"[✓] All books combined into: {bible_json_path}")
        
        # Generate SQL
        generate_sql(bible_json_path, bible_sql_path, bible_translation)
        print(f"[✓] SQL file created: {bible_sql_path}")
    else:
        print(f"[!] Cannot combine books for {bible_translation} - only {len(existing_books)}/66 books available")
        missing_books = [book for book in books if book not in existing_books]
        if missing_books:
            print(f"[!] Missing books: {', '.join(missing_books[:10])}{'...' if len(missing_books) > 10 else ''}")


def generate_sql(json_path, sql_path, translation):
    """Generate SQL file from the combined bible JSON"""
    with open(sql_path, 'w') as output_file:
        with open(json_path, 'r') as input_file:
            output_file.write(
                "create table " + translation.lower() + "(book_id int not null, book varchar(255) not null, "
                                                       "chapter int not null, verse int not null, text varchar(1000) not "
                                                       "null, primary key (book_id, chapter, verse));\n\n")

            cd = json.load(input_file)

            for book, chapters in cd.items():
                for chapter, verses in chapters.items():
                    output_file.write(
                        "INSERT INTO " + translation.lower() + "(book_id, book, chapter, verse, text) VALUES\n")
                    for verse_num, verse_content in verses.items():
                        book_id = books.index(book) + 1
                        verse_content = re.sub(r'\s+', ' ', verse_content)
                        verse_content = verse_content.replace("'", "''")
                        output_file.write("(" + str(
                            book_id) + ",'" + book + "'," + chapter + "," + verse_num + ",'" + verse_content + "')")
                        # Check if it's the last line
                        if verse_num == list(verses.keys())[-1]:
                            output_file.write(";\n")
                        else:
                            output_file.write(",\n")


if __name__ == '__main__':
    print("[+] Available Translations: ")
    for bt in BIBLE_TRANSLATIONS.keys():
        sys.stdout.write(bt + " ")
        TOTAL += 66

    download_all = input("\n[+] Download all translations (Y/N): ").upper()
    if download_all == "Y":
        bibles_trans = list(BIBLE_TRANSLATIONS.keys())
        # remove NMB since it's not complete
        # bibles_trans.remove("NMB")
        bibles_trans.remove("RVA")
        bibles_trans.sort()
        TOTAL -= 66 * 2
        for t in bibles_trans:
            print(f"\n{'='*60}")
            print(f"Processing translation: {t}")
            print(f"{'='*60}")
            generate_bible(t, show_progress=False)
        print("\n[+] All translations downloaded!")

    else:
        translation = input("[+] Translation: ").upper()
        generate_bible(translation)