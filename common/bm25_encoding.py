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


def generate_query_bm25_encoding(query, encodings_db_path):
    import bm25s

    retriever = bm25s.BM25.load(encodings_db_path, load_corpus=False)

    query = query.lower()
    query_tokens = bm25s.tokenize(query)

    # Get top-k results as a tuple of (doc ids, scores). Both are arrays of shape (n_queries, k).
    # To return docs instead of IDs, set the `corpus=corpus` parameter.
    results, scores = retriever.retrieve(query_tokens, k=10)

    for i in range(results.shape[1]):
        doc, score = results[0, i], scores[0, i]
        print(f"Rank {i+1} (score: {score:.2f}): {doc}")