# Raport z testów RAG

**Data testu:** 2025-08-29 10:14:57

**Model LLM:** Bielik-11B-v2.6-Instruct.Q4_K_M.gguf

**Model do embeddingu:** mmlw-roberta-large

**Rodzaj wyszukiwania:** embedding, BM25

**Metody testowe:** keywords, LLM-as-a-judge

**Liczba przypadków testowych:** 1000<font color="red">*</font>


## Analiza jakości systemu

![Test results plots](tests/plots/test_results_plots.png)<font color="red">*</font>



- **Średnia ocena LLM-as-a-judge:** 9.17/10  
  • Zakres wyników: 7.0 – 10.0, odchylenie: 1.17  
  → Jakość oceniono jako **znakomita – model bardzo precyzyjnie odpowiada na pytania**.

- **Skuteczność testów keywordowych:** 83.3%  
  • Zakres wyników: 0.0 – 100.0, odchylenie: 40.82  
  → Trafność oceniono jako **dobra – często zawiera najważniejsze informacje**.

- **Średni czas generacji odpowiedzi:** 69.2 s (zakres: 11.0 – 114.0 s)  
  → Szybkość oceniono jako **przeciętnie**.

- **10 najgorszych odpowiedzi:**<font color="red">*</font>  
  • Numery 10. pytań, dla których model uzyskał najgorsze wyniki:  
  → 39, 53, 153, 330, 331, 613, 713, 815, 918, 929

### Rekomendacja
System działa stabilnie – można go rozwijać o dodatkowe funkcjonalności.


<font color="red">* W rzeczywistości przypadków testowych jest tylko 6, przez co nie byłoby możliwe stworzenie powyższych elementów raportu. Na potrzeby demonstracji, założono że jest 1000 przypadków testowych.</font>