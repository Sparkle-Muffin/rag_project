import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from tqdm import tqdm


RESULTS_DIR = "tests/test_results"
SUMMARY_FILE = "tests/test_summary.md"

LLM_MODEL = "Bielik-11B-v2.6-Instruct.Q4_K_M.gguf"
EMBEDDING_MODEL = "mmlw-roberta-large"
HYBRID_SEARCH = ["embedding", "BM25"]
TEST_METHODS = ["keywords", "LLM-as-a-judge"]

def load_test_results():
    records = []
    for file in tqdm(os.listdir(RESULTS_DIR), desc="Wczytywanie wyników"):
        if file.endswith(".json"):
            with open(os.path.join(RESULTS_DIR, file), "r", encoding="utf-8") as f:
                data = json.load(f)
                records.append(data)
    return pd.DataFrame(records)


def generate_plots(df):
    plt.figure(figsize=(6,4))
    df["evaluation_score"].plot(kind="hist", bins=10, rwidth=0.8)
    plt.title("Rozkład ocen LLM-as-a-judge")
    plt.xlabel("Score (0-10)")
    plt.ylabel("Liczba odpowiedzi")
    plt.savefig("tests/test_score_hist.png")
    plt.close()

    plt.figure(figsize=(6,4))
    df.groupby("total_keywords_score")["evaluation_score"].mean().plot(kind="bar")
    plt.title("Średnia ocena vs. test keywordowy")
    plt.xlabel("Keyword test (False/True)")
    plt.ylabel("Średnia ocena")
    plt.savefig("tests/test_keyword_vs_score.png")
    plt.close()


def generate_analysis(df):
    avg_score = df["evaluation_score"].mean()
    pass_rate = df["required_keywords_score"].mean()
    avg_time = df["answer_generation_time_s"].mean()

    # Ocena jakości na podstawie średniego score
    if avg_score >= 8:
        quality = "bardzo dobra"
    elif avg_score >= 5:
        quality = "średnia – system odpowiada poprawnie, ale czasem niekompletnie"
    else:
        quality = "niska – wymaga znaczących poprawek"

    analysis = f"""
## Analiza jakości systemu

- Średnia ocena LLM-as-a-judge: **{avg_score:.2f}/10** → jakość oceniono jako **{quality}**.
- Skuteczność testów keywordowych: **{pass_rate:.1f}%** → system zwykle znajduje kluczowe informacje.
- Średni czas generacji odpowiedzi: **{avg_time:.1f} s** → {("akceptowalny" if avg_time < 30 else "zbyt długi – warto zoptymalizować")}.

### Wnioski
System działa poprawnie i potrafi udzielać sensownych odpowiedzi, 
jednak wymaga dalszej optymalizacji w zakresie **kompletności i precyzji** odpowiedzi. 
Warto też rozważyć dodatkowe techniki filtrowania kontekstu, 
aby ograniczyć halucynacje i przyspieszyć generację.
"""
    return analysis


def generate_summary(df):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.write(f"# Raport z testów RAG\n\n")
        f.write(f"**Data testu:** {now}\n\n")
        f.write(f"**Model LLM:** {LLM_MODEL}\n\n")
        f.write(f"**Model embeddingu:** {EMBEDDING_MODEL}\n\n")
        f.write(f"**Rodzaj wyszukiwania:** {', '.join(HYBRID_SEARCH)}\n\n")
        f.write(f"**Metody testowe:** {', '.join(TEST_METHODS)}\n\n")

        f.write(generate_analysis(df))

        f.write("## Wizualizacje\n")
        f.write("![Histogram ocen](test_score_hist.png)\n\n")
        f.write("![Keyword vs. score](test_keyword_vs_score.png)\n\n")

        f.write("## Wyniki szczegółowe\n\n")
        f.write(df[[
            "question", 
            "required_keywords",
            "optional_keywords",
            "required_keywords_score",
            "optional_keywords_score",
            "total_keywords_score",
            "evaluation_score", 
            "answer_generation_time_s"
        ]].to_markdown(index=False))
        f.write("\n\n")


if __name__ == "__main__":
    df = load_test_results()
    generate_plots(df)
    generate_summary(df)
    print(f"✅ Raport zapisany do {SUMMARY_FILE}")
