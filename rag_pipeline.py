import zipfile
from pathlib import Path
import os
import re


# Define paths
zip_file_path = Path("docs/Pliki_do_zadania_rekrutacyjnego.zip")
extract_dir = Path("docs/Pliki_do_zadania_rekrutacyjnego")
db_cleaned_up_dir = Path("db_cleaned_up")


def unzip_db_files():
    # Create extraction directory if it doesn't exist
    extract_dir.mkdir(exist_ok=True)

    # Open and extract the zip file
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        print(f"Unzipping {zip_file_path} to {extract_dir}...")
        
        # Extract all contents
        zip_ref.extractall("docs/")

        # List extracted files
        extracted_files = zip_ref.namelist()


def clean_up_db_files():
    # Create extraction directory if it doesn't exist
    db_cleaned_up_dir.mkdir(exist_ok=True)

    # List extracted files
    extracted_files = os.listdir(extract_dir)

    for file in extracted_files:
        print(f"Processing: {file}")
        
        # Skip directories
        file_path = extract_dir / file
        if file_path.is_dir():
            continue
            
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove URLs using regex pattern
            # This pattern matches http/https URLs, ftp URLs, and other common URL formats
            url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+|ftp://[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+|file:///.[^\s<>"{}|\\^`\[\]]+'
            cleaned_content = re.sub(url_pattern, '', content)
            
            # Save the cleaned content to db_cleaned_up_dir
            output_path = db_cleaned_up_dir / file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
                
            print(f"  ✓ Saved cleaned file to: {output_path}")
            
        except Exception as e:
            print(f"  ✗ Error processing {file}: {e}")


def main():
    # 1 Unzip db files
    unzip_db_files()
    # 2 Clean up db files
    clean_up_db_files()


if __name__ == "__main__":
    main()