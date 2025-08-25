import os


def generate_bm25_encodings(input_dir, encodings_db_path):
    import bm25s

    # Create your corpus here
    corpus = []
    for file in os.listdir(input_dir):
        with open(input_dir / file, 'r', encoding='utf-8') as f:
            text = f.read()
            corpus.append(text)

    # Tokenize the corpus and only keep the ids (faster and saves memory)
    corpus_tokens = bm25s.tokenize(corpus, stopwords="en")

    # Create the BM25 model and index the corpus
    retriever = bm25s.BM25()
    retriever.index(corpus_tokens)

    # You can save the arrays to a directory...
    retriever.save(encodings_db_path)

    # You can save the corpus along with the model
    retriever.save(encodings_db_path, corpus=corpus)


def get_top_k_bm25_encoding_results(query, encodings_db_path, db_chunks_number):
    import bm25s

    retriever = bm25s.BM25.load(encodings_db_path, load_corpus=True)

    query = query.lower()
    query_tokens = bm25s.tokenize(query, return_ids=False)

    answers = []
    results, scores = retriever.retrieve(query_tokens, k=db_chunks_number)

    for i in range(results.shape[1]):
        doc, score = results[0, i], scores[0, i]
        answers.append({
            "id": doc["id"],
            "score": score,
            "text": doc["text"]
        })

    return answers