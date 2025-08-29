import zipfile
from pathlib import Path
import os
import re

from common.constants import QDRANT_COLLECTION_NAME, VECTOR_SIZE, BM25_ENCODINGS_DB_PATH
from common.file_utils import unzip_docs, preprocess_files, clean_and_unify_text, split_into_chunks, create_chunk_files
from common.embeddings import generate_embeddings_and_metadata
from common.qdrant_api import upload_to_qdrant
from common.bm25_encoding import generate_bm25_encodings


def main() -> None:
    """
    Main pipeline for setting up the RAG system.
    
    Executes the complete pipeline to prepare documents for retrieval:
    1. Creates necessary directories
    2. Extracts documents from zip file
    3. Cleans and preprocesses text files
    4. Splits documents into logical chunks
    5. Creates individual chunk files for embedding
    6. Generates embeddings using SentenceTransformer
    7. Uploads embeddings to Qdrant vector database
    8. Creates BM25 encodings for text-based search
    
    This function sets up the complete infrastructure needed for the RAG system
    to function, including both vector and keyword-based retrieval capabilities.
    """
    # 0 Create directories
    docs_zip_path = Path("docs_zip/Pliki_do_zadania_rekrutacyjnego.zip")
    docs_dir = Path("docs/")
    docs_dir.mkdir(exist_ok=True)
    docs_preprocessed_dir = Path("docs_preprocessed/")
    docs_preprocessed_dir.mkdir(exist_ok=True)
    docs_cleaned_up_dir = docs_preprocessed_dir / Path("docs_cleaned_up/")
    docs_cleaned_up_dir.mkdir(exist_ok=True)
    docs_divided_into_chunks_dir = docs_preprocessed_dir / Path("docs_divided_into_chunks/")
    docs_divided_into_chunks_dir.mkdir(exist_ok=True)
    text_chunks_dir = Path("text_chunks/")
    text_chunks_dir.mkdir(exist_ok=True)

    # 1 Unzip docs files
    unzip_docs(docs_zip_path, docs_dir)

    # 2 Clean up and unify structure of docs files
    preprocess_files(input_dir=docs_dir, output_dir=docs_cleaned_up_dir, preprocess_func=clean_and_unify_text)

    # 3 Divide docs files into chunks
    preprocess_files(input_dir=docs_cleaned_up_dir, output_dir=docs_divided_into_chunks_dir, preprocess_func=split_into_chunks)

    # 4 Create chunk files for embedding
    create_chunk_files(input_dir=docs_divided_into_chunks_dir, output_dir=text_chunks_dir)

    # 5 Create embeddings using SentenceTransformer
    embeddings_and_metadata = generate_embeddings_and_metadata(input_dir=text_chunks_dir)

    # 6 Upload content to Qdrant
    upload_to_qdrant(collection_name=QDRANT_COLLECTION_NAME, embeddings_and_metadata=embeddings_and_metadata, vector_size=VECTOR_SIZE)

    # 7 Create BM25 encodings
    generate_bm25_encodings(input_dir=text_chunks_dir, encodings_db_path=BM25_ENCODINGS_DB_PATH)


if __name__ == "__main__":
    main()