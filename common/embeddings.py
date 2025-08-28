from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
import os
import hashlib
from tqdm import tqdm

# Global model instance to avoid loading it multiple times
_model_instance = None

def get_model():
    """Get or create the SentenceTransformer model instance (singleton pattern)"""
    global _model_instance
    if _model_instance is None:
        _model_instance = SentenceTransformer("sdadas/mmlw-roberta-large")
    return _model_instance

def generate_embeddings_and_metadata(input_dir):
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

    embeddings_and_metadata = [{"text": text,
                                "id": id,
                                "vector": vector} for text, id, vector in zip(texts, ids, vectors)]

    return embeddings_and_metadata


def generate_query_embedding(query):
    query_prefix = "zapytanie: "
    query = [query_prefix + query]

    model = get_model()
    embeddings = model.encode(query, convert_to_tensor=True, show_progress_bar=False)

    embedding = embeddings[0]
    # Convert PyTorch tensor to Python list for Qdrant compatibility
    embedding_list = embedding.tolist()

    return embedding_list
