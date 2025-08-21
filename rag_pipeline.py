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


def clean_text_for_rag(text):
    """
    Comprehensive text cleaning for optimal RAG embeddings.
    Preserves logical structure and section divisions while cleaning formatting.
    """
    # Remove URLs and file references (enhanced pattern)
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+|ftp://[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+|file:///.[^\s<>"{}|\\^`\[\]]+'
    text = re.sub(url_pattern, '', text)
    
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Remove markdown links
    
    text = re.sub(r'\*', '', text)  # Remove markdown bold
    
    # Remove excessive punctuation
    text = re.sub(r'\.{2,}', '.', text)  # Replace multiple dots with single
    text = re.sub(r'!{2,}', '!', text)  # Replace multiple exclamation marks
    text = re.sub(r'\?{2,}', '?', text)  # Replace multiple question marks
    
    text = re.sub(r'\n+', '\n\n', text)  # Replace multiple newlines with two newlines
    text = text.strip()  # Remove leading/trailing whitespace

    return text


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
            
            # Apply comprehensive cleaning
            cleaned_content = clean_text_for_rag(content)
            
            # Save the cleaned content to db_cleaned_up_dir
            output_path = db_cleaned_up_dir / file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
                
            print(f"  ✓ Saved cleaned file to: {output_path}")
            print(f"  ✓ Original size: {len(content)} chars, Cleaned size: {len(cleaned_content)} chars")
            
        except Exception as e:
            print(f"  ✗ Error processing {file}: {e}")


def main():
    # 1 Unzip db files
    unzip_db_files()
    # 2 Clean up db files
    clean_up_db_files()


if __name__ == "__main__":
    main()