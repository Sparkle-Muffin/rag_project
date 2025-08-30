from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
import os
import hashlib
from pathlib import Path
from typing import List
from tqdm import tqdm
from common.models import EmbeddingMetadata


# Global model instance to avoid loading it multiple times
_model_instance = None

def get_model() -> SentenceTransformer:
    """
    Get or create the SentenceTransformer model instance (singleton pattern).
    
    Returns:
        SentenceTransformer model instance for generating embeddings
    """
    global _model_instance
    if _model_instance is None:
        _model_instance = SentenceTransformer("sdadas/mmlw-roberta-large")
    return _model_instance

def generate_embeddings_and_metadata(input_dir: Path) -> List[EmbeddingMetadata]:
    """
    Generate embeddings and metadata for text files in the input directory.
    
    Reads text files, generates embeddings using the SentenceTransformer model,
    and returns a list of EmbeddingMetadata objects containing text, id, and vector for each file.
    
    Args:
        input_dir: Directory containing text files to embed
        
    Returns:
        List of EmbeddingMetadata objects with text, id, and vector for each document
    """
    # List embedding chunk files
    embedding_chunk_files = os.listdir(input_dir)

    embeddings_and_metadata = []
    texts = []
    ids = []
    i = 0
    for file in tqdm(embedding_chunk_files, desc="Generating embeddings and metadata"):
        with open(input_dir / file, 'r', encoding='utf-8') as f:
            text = f.read()
            texts.append(text)
            id = i
            i += 1
            ids.append(id)
                    
    model = get_model()
    vectors = model.encode(texts, convert_to_tensor=True, show_progress_bar=False)

    embeddings_and_metadata = [
        EmbeddingMetadata(
            text=text,
            id=id,
            vector=vector.tolist()
        ) for text, id, vector in zip(texts, ids, vectors)
    ]

    return embeddings_and_metadata


def generate_query_embedding(query: str) -> List[float]:
    """
    Generate embedding for a single query string.
    
    Adds a prefix to the query and generates an embedding vector using the
    SentenceTransformer model. Converts the PyTorch tensor to a Python list
    for compatibility with Qdrant.
    
    Args:
        query: Query string to embed
        
    Returns:
        List of floats representing the query embedding vector
    """
    query_prefix = "zapytanie: "
    query = [query_prefix + query]

    model = get_model()
    embeddings = model.encode(query, convert_to_tensor=True, show_progress_bar=False)

    embedding = embeddings[0]
    # Convert PyTorch tensor to Python list for Qdrant compatibility
    embedding_list = embedding.tolist()

    return embedding_list
