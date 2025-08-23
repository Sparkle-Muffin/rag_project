from common.embeddings import generate_query_embedding
from common.qdrant import search_answer_in_qdrant


def create_prompt(user_prompt):
    system_prompt = "Jesteś pomocnym asystentem, który odpowiada na pytania na podstawie dostarczonego kontekstu. Oto konteskt:"
    query_embedding = generate_query_embedding(user_prompt)
    context = search_answer_in_qdrant(collection_name="rag_project", query_embedding=query_embedding)

    system_prompt = system_prompt + "\n\n" + context

    print(system_prompt)

    return system_prompt, user_prompt