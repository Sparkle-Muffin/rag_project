import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from tqdm import tqdm
from scipy import stats
import seaborn as sns


RESULTS_DIR = "tests/test_results"
SUMMARY_FILE_PATH = "tests/test_summary.md"
PLOTS_FILE_PATH = "tests/test_results_plots.png"

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


def create_plots(df):
    """
    If we have data from hundreds of tests, we can use this function to create histograms.
    For the demo purposes, we will use fake, mockup data.
    """

    # Prepare fake, mockup data
    LLM_as_a_judge_scores = np.array([1, 2, 4, 3, 2, 1, 4, 10, 15, 32, 42, 51, 57, 70, 85, 69, 53, 26, 12, 2])
    LLM_as_a_judge_positions = np.linspace(0, 10, len(LLM_as_a_judge_scores))
    keyword_scores = np.array([2, 2, 4, 4, 3, 5, 8, 11, 12, 19, 29, 42, 51, 63, 80, 83, 67, 48, 39, 22])
    keyword_positions = np.linspace(0, 100, len(keyword_scores))
    response_times = np.array([1, 9, 39, 65, 92, 108, 88, 57, 42, 16, 11, 7, 3, 2, 1, 2, 1, 2, 1, 1])
    response_times_positions = np.linspace(0, 250, len(response_times))

    # Set style
    plt.style.use('default')
    sns.set_palette("husl")
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Wyniki testów RAG', fontsize=16, fontweight='bold')
    
    axes[0].bar(LLM_as_a_judge_positions, LLM_as_a_judge_scores, width=0.4)
    axes[0].set_title('Oceny LLM-as-a-judge', fontweight='bold')
    axes[0].set_xlabel('Ocena (1-10)')
    axes[0].set_ylabel('Liczba próbek')
    axes[0].grid(True, alpha=0.3)
    
    axes[1].bar(keyword_positions, keyword_scores, width=4)
    axes[1].set_title('Skuteczność testów keywordowych', fontweight='bold')
    axes[1].set_xlabel('Skuteczność (%)')
    axes[1].set_ylabel('Liczba próbek')
    axes[1].grid(True, alpha=0.3)

    axes[2].bar(response_times_positions, response_times, width=10)
    axes[2].set_title('Czas generacji odpowiedzi', fontweight='bold')
    axes[2].set_xlabel('Czas (s)')
    axes[2].set_ylabel('Liczba próbek')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(PLOTS_FILE_PATH, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Plots saved to: {PLOTS_FILE_PATH}")
    

def generate_analysis(df):
    avg_score = df["evaluation_score"].mean()
    std_score = df["evaluation_score"].std()
    min_score = df["evaluation_score"].min()
    max_score = df["evaluation_score"].max()

    avg_keywords = df["required_keywords_score"].mean()
    std_keywords = df["required_keywords_score"].std()
    min_keywords = df["required_keywords_score"].min()
    max_keywords = df["required_keywords_score"].max()

    avg_time = df["answer_generation_time_s"].mean()
    min_time = df["answer_generation_time_s"].min()
    max_time = df["answer_generation_time_s"].max()

    # Model answer quality evaluation
    if avg_score >= 9:
        quality = "znakomita – model bardzo precyzyjnie odpowiada na pytania"
    elif avg_score >= 8:
        quality = "bardzo dobra – odpowiedzi pełne, drobne niedociągnięcia"
    elif avg_score >= 6:
        quality = "średnia – odpowiedzi częściowe lub niepełne"
    elif avg_score >= 4:
        quality = "słaba – model często się myli lub pomija kluczowe informacje"
    else:
        quality = "bardzo niska – odpowiedzi w większości nietrafne"

    # Keywords evaluation
    if avg_keywords >= 90:
        keywords_quality = "znakomita – prawie zawsze zawiera kluczowe informacje"
    elif avg_keywords >= 70:
        keywords_quality = "dobra – często zawiera najważniejsze informacje"
    elif avg_keywords >= 50:
        keywords_quality = "przeciętna – tylko część kluczowych informacji jest obecna"
    else:
        keywords_quality = "niska – system gubi większość kluczowych informacji"

    # Answer generation time evaluation
    if avg_time < 30:
        speed = "super (bardzo szybkie odpowiedzi)"
    elif avg_time <= 60:
        speed = "dość szybko"
    elif avg_time <= 100:
        speed = "przeciętnie"
    elif avg_time <= 150:
        speed = "wolno"
    else:
        speed = "bardzo wolno"

    # General recommendation
    if avg_score < 6 or avg_keywords < 60:
        recommendation = "System wymaga wyraźnych poprawek – warto skupić się na lepszym retrievalu lub dopasowaniu promptów."
    elif avg_time > 100:
        recommendation = "Jakość odpowiedzi jest akceptowalna, ale warto zoptymalizować czas generacji."
    else:
        recommendation = "System działa stabilnie – można go rozwijać o dodatkowe funkcjonalności."

    analysis = f"""
## Analiza jakości systemu

- **Średnia ocena LLM-as-a-judge:** {avg_score:.2f}/10  
  • Zakres wyników: {min_score:.1f} – {max_score:.1f}, odchylenie: {std_score:.2f}  
  → Jakość oceniono jako **{quality}**.

- **Skuteczność testów keywordowych:** {avg_keywords:.1f}%  
  • Zakres wyników: {min_keywords:.1f} – {max_keywords:.1f}, odchylenie: {std_keywords:.2f}  
  → Trafność oceniono jako **{keywords_quality}**.

- **Średni czas generacji odpowiedzi:** {avg_time:.1f} s (zakres: {min_time:.1f} – {max_time:.1f} s)  
  → Szybkość oceniono jako **{speed}**.

### Rekomendacja
{recommendation}
"""
    return analysis



def generate_summary(df):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(SUMMARY_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(f"# Raport z testów RAG\n\n")
        f.write(f"**Data testu:** {now}\n\n")
        f.write(f"**Model LLM:** {LLM_MODEL}\n\n")
        f.write(f"**Model do embeddingu:** {EMBEDDING_MODEL}\n\n")
        f.write(f"**Rodzaj wyszukiwania:** {', '.join(HYBRID_SEARCH)}\n\n")
        f.write(f"**Metody testowe:** {', '.join(TEST_METHODS)}\n\n")

        f.write(generate_analysis(df))

        f.write(f"![Test results plots]({PLOTS_FILE_PATH})\n\n")


def main():
    df = load_test_results()
    create_plots(df)
    generate_summary(df)


if __name__ == "__main__":
    main()

