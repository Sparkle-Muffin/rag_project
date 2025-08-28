# Raport z testów RAG

**Data testu:** 2025-08-28 16:36:04

**Model LLM:** Bielik-11B-v2.6-Instruct.Q4_K_M.gguf

**Model do embeddingu:** mmlw-roberta-large

**Rodzaj wyszukiwania:** embedding, BM25

**Metody testowe:** keywords, LLM-as-a-judge

**Liczba przypadków testowych:** 1000<font color="red">*</font>


## Analiza jakości systemu

![Test results plots](tests/plots/test_results_plots.png)<font color="red">*</font>



- **Średnia ocena LLM-as-a-judge:** 8.75/10  
  • Zakres wyników: 7.0 – 10.0, odchylenie: 1.26  
  → Jakość oceniono jako **bardzo dobra – odpowiedzi pełne, drobne niedociągnięcia**.

- **Skuteczność testów keywordowych:** 100.0%  
  • Zakres wyników: 100.0 – 100.0, odchylenie: 0.00  
  → Trafność oceniono jako **znakomita – prawie zawsze zawiera kluczowe informacje**.

- **Średni czas generacji odpowiedzi:** 72.8 s (zakres: 9.0 – 137.0 s)  
  → Szybkość oceniono jako **przeciętnie**.

- **10 najgorszych odpowiedzi:**<font color="red">*</font>  
  • Numery 10. pytań, dla których model uzyskał najgorsze wyniki:  
  → 98, 278, 286, 322, 532, 570, 796, 817, 946, 988

### Rekomendacja
System działa stabilnie – można go rozwijać o dodatkowe funkcjonalności.


<font color="red">* W rzeczywistości przypadków testowych jest tylko 6, przez co nie byłoby możliwe stworzenie powyższych elementów raportu. Na potrzeby demonstracji, założono że jest 1000 przypadków testowych.</font>