from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
import os
import hashlib


def generate_embeddings_and_metadata(input_dir):
    # List embedding chunk files
    embedding_chunk_files = os.listdir(input_dir)

    embeddings_and_metadata = []
    texts = []
    ids = []
    i = 0
    for file in embedding_chunk_files:
        with open(input_dir / file, 'r', encoding='utf-8') as f:
            text = f.read()
            texts.append(text)
            id = i
            i += 1
            ids.append(id)
                    
    model = SentenceTransformer("sdadas/mmlw-roberta-large")
    vectors = model.encode(texts, convert_to_tensor=True, show_progress_bar=False)

    embeddings_and_metadata = [{"text": text,
                                "id": id,
                                "vector": vector} for text, id, vector in zip(texts, ids, vectors)]

    return embeddings_and_metadata


def generate_query_embedding(query):
    query_prefix = "zapytanie: "
    query = [query_prefix + query]

    model = SentenceTransformer("sdadas/mmlw-roberta-large")
    embeddings = model.encode(query, convert_to_tensor=True, show_progress_bar=False)

    embedding = embeddings[0]
    # Convert PyTorch tensor to Python list for Qdrant compatibility
    embedding_list = embedding.tolist()

    return embedding_list
