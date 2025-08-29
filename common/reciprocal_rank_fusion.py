import math
from typing import List, Dict, Any


def reciprocal_rank_fusion(
    qdrant_results: List[Dict[str, Any]],
    bm25_results: List[Dict[str, Any]],
    k: float = 60.0,
) -> List[Dict[str, Any]]:
    """
    Perform reciprocal rank fusion to combine results from Qdrant vector search and BM25 text search.

    Args:
        qdrant_results: List of dictionaries from search_answer_in_qdrant()
        bm25_results: List of dictionaries from get_top_k_bm25_encoding_results()
        k: Constant that controls the contribution of lower-ranked results (default: 60.0)

    Returns:
        List of dictionaries with combined scores, sorted by descending score
    """

    # Create a dictionary to store combined scores for each document
    combined_scores = {}

    # Process Qdrant results
    for rank, result in enumerate(qdrant_results):
        doc_id = result["id"]
        if doc_id not in combined_scores:
            combined_scores[doc_id] = {
                "id": doc_id,
                "text": result["text"],
                "qdrant_score": result["score"],
                "bm25_score": None,
                "combined_score": 0.0,
            }

        # Add reciprocal rank fusion score for Qdrant
        combined_scores[doc_id]["combined_score"] += 1.0 / (k + rank + 1)

    # Process BM25 results
    for rank, result in enumerate(bm25_results):
        doc_id = result["id"]
        if doc_id not in combined_scores:
            combined_scores[doc_id] = {
                "id": doc_id,
                "text": result["text"],
                "qdrant_score": None,
                "bm25_score": result["score"],
                "combined_score": 0.0,
            }
        else:
            combined_scores[doc_id]["bm25_score"] = result["score"]

        # Add reciprocal rank fusion score for BM25
        combined_scores[doc_id]["combined_score"] += 1.0 / (k + rank + 1)

    # Convert to list and sort by combined score
    final_results = list(combined_scores.values())
    final_results.sort(key=lambda x: x["combined_score"], reverse=True)

    # Return results in the expected format
    return [
        {"id": result["id"], "score": result["combined_score"], "text": result["text"]}
        for result in final_results
    ]


def hybrid_search(
    qdrant_results: List[Dict[str, Any]],
    bm25_results: List[Dict[str, Any]],
    k: float = 60.0,
    max_results: int = None,
) -> List[Dict[str, Any]]:
    """
    Convenience function that performs hybrid search using reciprocal rank fusion.

    Args:
        qdrant_results: List of dictionaries from search_answer_in_qdrant()
        bm25_results: List of dictionaries from get_top_k_bm25_encoding_results()
        k: Constant that controls the contribution of lower-ranked results (default: 60.0)
        max_results: Maximum number of results to return (default: None, returns all)

    Returns:
        List of dictionaries with combined scores, sorted by descending score
    """

    results = reciprocal_rank_fusion(qdrant_results, bm25_results, k)

    if max_results is not None:
        results = results[:max_results]

    answers = [result["text"] for result in results]

    return answers
