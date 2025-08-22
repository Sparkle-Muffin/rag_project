import zipfile
from pathlib import Path
import os
import re


# Define paths
docs_zip_path = Path("docs_zip/Pliki_do_zadania_rekrutacyjnego.zip")
docs_dir = Path("docs/")
docs_dir.mkdir(exist_ok=True)
docs_preprocessed_dir = Path("docs_preprocessed/")
docs_preprocessed_dir.mkdir(exist_ok=True)
docs_cleaned_up_dir = docs_preprocessed_dir / Path("docs_cleaned_up/")
docs_cleaned_up_dir.mkdir(exist_ok=True)
docs_divided_into_chunks_dir = docs_preprocessed_dir / Path("docs_divided_into_chunks/")
docs_divided_into_chunks_dir.mkdir(exist_ok=True)
embedding_chunks_dir = Path("embedding_chunks/")
embedding_chunks_dir.mkdir(exist_ok=True)


def unzip_docs():
    with zipfile.ZipFile(docs_zip_path, "r") as zf:
        for member in zf.namelist():
            # remove "Pliki_do_zadania_rekrutacyjnego/" prefix
            filename = member.split("/", 1)[-1]  # drops first directory
            if filename:  # skip empty names (like "files/")
                target_path = os.path.join(docs_dir, filename)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                with zf.open(member) as source, open(target_path, "wb") as target:
                    target.write(source.read())


def clean_and_unify_text(text):
    """
    Comprehensive text cleaning for optimal RAG embeddings.
    Preserves logical structure and section divisions while cleaning formatting.
    """
    # Remove URLs and file references (enhanced pattern)
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+|ftp://[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+|file:///.[^\s<>"{}|\\^`\[\]]+'
    text = re.sub(url_pattern, '', text)
    
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Remove markdown links
    
    text = re.sub(r'\*', '', text)  # Remove markdown bold
    text = re.sub(r'\|', '', text)  # Remove markdown tables
    
    # Remove excessive punctuation
    text = re.sub(r'\.{2,}', '.', text)  # Replace multiple dots with single
    text = re.sub(r'!{2,}', '!', text)  # Replace multiple exclamation marks
    text = re.sub(r'\?{2,}', '?', text)  # Replace multiple question marks
    
    text = re.sub(r'\n+', '\n\n', text)  # Replace multiple newlines with two newlines
    text = text.strip()  # Remove leading/trailing whitespace

    return text


def split_into_chunks(text):
    chunks = []
    headers_stack = []

    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue  # Skip empty lines

        # Check if line is a header
        header_match = re.match(r"^(#+)\s+(.*)", line)
        if header_match:
            level = len(header_match.group(1))  # number of '#'
            header_text = header_match.group(2).strip()

            # Cut headers stack to current level
            headers_stack = headers_stack[:level-1]
            headers_stack.append(header_text)
        else:
            # This is content -> create chunk
            context = " ".join(headers_stack)
            chunk = f"{context} {line}"
            chunks.append(chunk)

    text = "\n\n".join(chunks)

    return text


def preprocess_files(input_dir, output_dir, preprocess_func):
    # List docs files
    docs_files = os.listdir(input_dir)

    for file in docs_files:
        print(f"Processing: {file}")

        # Skip directories
        file_path = input_dir / file
        if file_path.is_dir():
            continue
            
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Apply comprehensive cleaning
            cleaned_content = preprocess_func(content)
            
            # Save the cleaned content to db_cleaned_up_dir
            output_path = output_dir / file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
                
            print(f"  ✓ Saved cleaned file to: {output_path}")
            print(f"  ✓ Original size: {len(content)} chars, Cleaned size: {len(cleaned_content)} chars")
            
        except Exception as e:
            print(f"  ✗ Error processing {file}: {e}")


def create_embedding_chunk_files(input_dir, output_dir):
    # List docs files
    docs_files = os.listdir(input_dir)

    index = 0
    for file in docs_files:
        file_path = input_dir / file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            index += 1
            # Create chunk file
            chunk_file_path = output_dir / f"{index}.txt"
            with open(chunk_file_path, 'w', encoding='utf-8') as f:
                f.write(line)
                
            print(f"  ✓ Saved chunk file to: {chunk_file_path}")
            print(f"  ✓ Original size: {len(line)} chars, Cleaned size: {len(line)} chars")


def main():
    # 1 Unzip docs files
    unzip_docs()
    # 2 Clean up and unify structure of docs files
    preprocess_files(input_dir=docs_dir, output_dir=docs_cleaned_up_dir, preprocess_func=clean_and_unify_text)
    # 3 Divide docs files into chunks
    preprocess_files(input_dir=docs_cleaned_up_dir, output_dir=docs_divided_into_chunks_dir, preprocess_func=split_into_chunks)
    # 4 Create chunk files for embedding
    create_embedding_chunk_files(input_dir=docs_divided_into_chunks_dir, output_dir=embedding_chunks_dir)


if __name__ == "__main__":
    main()