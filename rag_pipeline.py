import zipfile
from pathlib import Path
import os
import re

from common.file_utils import unzip_docs, preprocess_files, clean_and_unify_text, split_into_chunks, create_embedding_chunk_files
from common.embeddings import generate_embeddings_and_metadata
from common.qdrant import upload_to_qdrant


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


def main():
    # 1 Unzip docs files
    unzip_docs(docs_zip_path, docs_dir)
    # 2 Clean up and unify structure of docs files
    preprocess_files(input_dir=docs_dir, output_dir=docs_cleaned_up_dir, preprocess_func=clean_and_unify_text)
    # 3 Divide docs files into chunks
    preprocess_files(input_dir=docs_cleaned_up_dir, output_dir=docs_divided_into_chunks_dir, preprocess_func=split_into_chunks)
    # 4 Create chunk files for embedding
    create_embedding_chunk_files(input_dir=docs_divided_into_chunks_dir, output_dir=embedding_chunks_dir)
    # 5 Create embeddings using SentenceTransformer
    embeddings_and_metadata = generate_embeddings_and_metadata(input_dir=embedding_chunks_dir)
    # 6 Upload content to Qdrant
    upload_to_qdrant(collection_name="rag_project", embeddings_and_metadata=embeddings_and_metadata, vector_size=1024)


if __name__ == "__main__":
    main()