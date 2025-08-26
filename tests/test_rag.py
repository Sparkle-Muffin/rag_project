import re
import sys
import os

# Add the parent directory to Python path so we can import from common/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.prompt_generation import create_prompt
from common.bielik_api import call_model_non_stream


# === GOLDEN ANSWERS (do uzupełnienia na podstawie dokumentów w docs/) ===
golden_answers = {
    "Jakie modele LLaMa są dostępne?": [
        "llama 1", "llama 2", "llama 3"  # <-- wpisz dokładne modele z dokumentów
    ],
    "Kto stworzył PLLuM?": [
        "uniwersytet", "warszawski", "uw", "pllum"  # <-- dopasuj do treści w docs
    ],
    "Jaki model najlepiej działa na GPU z 24 GB VRAM?": [
        "13b", "24 gb", "gpu"  # <-- dopasuj do treści w docs
    ]
}

# === TWOJE WŁASNE PYTANIA (z uzupełnieniem expected_keywords) ===
extra_questions = {
    "Jaki model Bielik został zoptymalizowany do pracy na GPU z 8 GB VRAM?": [
        "7b", "q4", "8 gb"
    ],
    "Kto jest partnerem projektu PLLuM?": [
        "nask", "plgrid"  # przykłady, dostosuj do docs
    ],
    "Kiedy system powinien odpowiedzieć 'nie wiem'?": []  # tu test na brak info
}


# === MOCK / ADAPTER DO TWOJEGO SYSTEMU ===
def get_answer_from_system(question: str) -> str:
    db_chunks_number = 10
    model_context_chunks_number = 10
    
    system_prompt, user_prompt = create_prompt(user_prompt=question, 
                                               db_chunks_number=db_chunks_number, 
                                               model_context_chunks_number=model_context_chunks_number)

    model_response = call_model_non_stream(system_prompt, user_prompt)
    print(model_response)

    return model_response


# === SPRAWDZANIE POPRAWNOŚCI ===
def check_answer(question: str, answer: str, expected_keywords: list[str]) -> bool:
    if not expected_keywords:  # pytania typu "powinno powiedzieć 'nie wiem'"
        return "nie wiem" in answer.lower()
    return all(any(kw.lower() in answer.lower() for kw in expected_keywords) for kw in expected_keywords)


# === GŁÓWNA FUNKCJA TESTOWA ===
def run_tests():
    print("=== TESTY OBOWIĄZKOWE ===")
    for q, keywords in golden_answers.items():
        answer = get_answer_from_system(q)
        ok = check_answer(q, answer, keywords)
        print(f"Pytanie: {q}")
        print(f"Odpowiedź: {answer}")
        print(f"Wynik: {'✅ OK' if ok else '❌ BŁĄD'}")
        print("-" * 40)

    print("\n=== TESTY DODATKOWE ===")
    for q, keywords in extra_questions.items():
        answer = get_answer_from_system(q)
        ok = check_answer(q, answer, keywords)
        print(f"Pytanie: {q}")
        print(f"Odpowiedź: {answer}")
        print(f"Wynik: {'✅ OK' if ok else '❌ BŁĄD'}")
        print("-" * 40)


if __name__ == "__main__":
    run_tests()
