# 📚 RAG QA Chat z Bielikiem i Qdrant

## 🎯 Cel projektu
Celem projektu jest stworzenie kompletnego systemu **RAG (Retrieval-Augmented Generation)**.
System pozwala użytkownikowi zadawać pytania dotyczące treści dokumentów, które wcześniej zostały:

- oczyszczone i ujednolicone,
- podzielone na **chunki**,
- zamienione na **embeddingi** (model *mmlw-roberta-large*),
- zapisane w bazie wektorowej **Qdrant**.

Na tej podstawie system wyszukuje najbardziej adekwatne fragmenty dokumentów i przekazuje je do dużego modelu językowego **Bielik-11B-v2.6-Instruct**, który generuje odpowiedź prezentowaną użytkownikowi w formie czatu.

---

## 🚀 Jak uruchomić projekt

### 1. Przygotowanie środowiska
Zainstaluj Minicondę i utwórz środowisko z pliku `.yml`:

```bash
conda env create -f environment.yml
conda activate rag_env
```

### 2. Uruchomienie Ollama
Kontener Ollama służy jako runtime dla modelu Bielik:

```bash
# Pobierz i uruchom kontener Ollama z obsługą GPU
docker run -d --gpus=all -v ${PWD}/ollama_volumes:/root/.ollama -p 11434:11434 --name ollama ollama/ollama

# Wznów kontener (przy kolejnych uruchomieniach)
docker start ollama
```

### 3. Konfiguracja i uruchomienie Bielika
```bash
# 1. Pobierz model z Hugging Face:
#    https://huggingface.co/speakleash/Bielik-11B-v2.6-Instruct-GGUF/blob/main/Bielik-11B-v2.6-Instruct.Q4_K_M.gguf

# 2. Pobierz plik Modelfile z repozytorium HF i zapisz jako "Modelfile"

# 3. Skopiuj model i Modelfile do kontenera Ollama:
docker cp . ollama:/root/.ollama/Bielik-11B-v2_6-Instruct_Q4_K_M

# 4. Utwórz model w Ollama:
docker exec -it ollama ollama create Bielik-11B-v2_6-Instruct_Q4_K_M -f /root/.ollama/Bielik-11B-v2_6-Instruct_Q4_K_M/Modelfile

# 5. Uruchom model:
docker exec -it ollama ollama run Bielik-11B-v2_6-Instruct_Q4_K_M
```

> ℹ️ Jeśli chcesz zmodyfikować `Modelfile`, skopiuj go ponownie do kontenera i powtórz kroki 4–5.

### 4. Uruchomienie Qdrant
```bash
# Pobierz najnowszy obraz Qdrant:
docker pull qdrant/qdrant

# Uruchom Qdrant na porcie domyślnym (6333)
docker run -d -p 6333:6333 qdrant/qdrant
```

### 5. Uruchomienie pipeline i aplikacji użytkownika
- **Przetwarzanie dokumentów i przygotowanie embeddingów**:
  ```bash
  python rag_pipeline.py
  ```
- **Aplikacja użytkownika (czat w Streamlit)**:
  ```bash
  streamlit run rag_user_app.py
  ```

---

## 🛠️ Opis działania

### `rag_pipeline.py`
- czyści dane wejściowe,  
- dzieli je na chunki,  
- generuje embeddingi modelem **mmlw-roberta-large**,  
- zapisuje embeddingi i metadane w bazie **Qdrant**.

### `rag_user_app.py` (Streamlit)
- udostępnia prosty interfejs czatu na `localhost`,  
- pobiera pytanie użytkownika, zamienia je na embedding,  
- wysyła zapytanie do **Qdrant**, aby odnaleźć najbardziej pasujące fragmenty,  
- dokleja znalezione chunki jako kontekst do promptu,  
- wysyła pytanie i kontekst do modelu **Bielik**,  
- wyświetla odpowiedź w formie strumieniowanego czatu.

---

## 📂 Struktura projektu

```
rag_pipeline.py                     # logika przetwarzania i przygotowania danych
rag_user_app.py                     # interfejs użytkownika (czat w Streamlit)
common/                             # biblioteki wspólne: obsługa plików, Qdrant, Bielik, embeddingi
docs_zip/                           # folder z oryginalnymi spakowanymi plikami
docs/                               # folder z rozpakowanymi plikami
docs_preprocessed/
    ├─ docs_cleaned_up/             # oczyszczone i ujednolicone pliki
    └─ docs_divided_into_chunks/    # pliki podzielone na chunki
embedding_chunks/                   # każdy plik = chunk do embeddingu
```

---

## 🤖 Użyte modele

- **Bielik-11B-v2.6-Instruct.Q4_K_M.gguf**  
  [Hugging Face link](https://huggingface.co/speakleash/Bielik-11B-v2.6-Instruct-GGUF)

- **mmlw-roberta-large**  
  [Hugging Face link](https://huggingface.co/sdadas/mmlw-roberta-large)

---

## 📦 Użyte kontenery

- **Ollama** – runtime do uruchamiania modelu Bielik,  
- **Qdrant** – wektorowa baza danych do przechowywania embeddingów i metadanych.