from common.constants import QDRANT_COLLECTION_NAME, BM25_ENCODINGS_DB_PATH
from common.embeddings import generate_query_embedding
from common.qdrant_api import search_answer_in_qdrant
from common.bm25_encoding import get_top_k_bm25_encoding_results
from common.reciprocal_rank_fusion import hybrid_search
from typing import Tuple


def create_prompt(
    system_prompt: str,
    user_prompt: str,
    db_chunks_number: int,
    model_context_chunks_number: int,
) -> Tuple[str, str]:
    """
    Create a complete prompt by combining system prompt with retrieved context.

    Generates embeddings for the user query, retrieves relevant documents using both
    vector search (Qdrant) and text search (BM25), combines results using hybrid search,
    and appends the context to the system prompt.

    Args:
        system_prompt: Base system prompt for the model
        user_prompt: User's question or query
        db_chunks_number: Number of chunks to retrieve from the database
        model_context_chunks_number: Maximum number of chunks to include in the final context

    Returns:
        Tuple of (enhanced_system_prompt, user_prompt) where the system prompt
        contains the retrieved context
    """
    query_embedding = generate_query_embedding(user_prompt)
    qdrant_results = search_answer_in_qdrant(
        collection_name=QDRANT_COLLECTION_NAME,
        query_embedding=query_embedding,
        db_chunks_number=db_chunks_number,
    )

    bm25_results = get_top_k_bm25_encoding_results(
        user_prompt, BM25_ENCODINGS_DB_PATH, db_chunks_number=db_chunks_number
    )

    hybrid_search_answers = hybrid_search(
        qdrant_results=qdrant_results,
        bm25_results=bm25_results,
        max_results=model_context_chunks_number,
    )

    context = "\n\n".join(hybrid_search_answers)
    system_prompt = system_prompt + "\n\n" + context

    return system_prompt, user_prompt
