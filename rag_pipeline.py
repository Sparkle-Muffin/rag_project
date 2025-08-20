import zipfile
from pathlib import Path

# Define paths
zip_file_path = Path("docs/Pliki_do_zadania_rekrutacyjnego.zip")
extract_dir = Path("docs/Pliki_do_zadania_rekrutacyjnego")


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


def main():
    # 1 Unzip db files
    unzip_db_files()


if __name__ == "__main__":
    main()