import re
import sys
import os
import json
from pathlib import Path
import time

# Add the parent directory to Python path so we can import from common/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.prompt_generation import create_prompt
from common.bielik_api import call_model_non_stream


def get_answer_from_system(question: str) -> str:
    db_chunks_number = 50
    model_context_chunks_number = 10
    
    system_prompt, user_prompt = create_prompt(user_prompt=question, 
                                               db_chunks_number=db_chunks_number, 
                                               model_context_chunks_number=model_context_chunks_number)

    model_response = call_model_non_stream(system_prompt, user_prompt)
    print(model_response)

    return model_response



def run_keyword_test(question: str, answer: str, expected_keywords: list[str]) -> bool:
    if not expected_keywords:  # pytania typu "powinno powiedzieć 'nie wiem'"
        return "nie wiem" in answer.lower()
    return all(any(kw.lower() in answer.lower() for kw in expected_keywords) for kw in expected_keywords)



def run_tests():
    test_cases_dir = "tests/test_cases"
    test_cases = sorted(os.listdir(test_cases_dir))

    test_results_dir = Path("tests/test_results/")
    test_results_dir.mkdir(exist_ok=True)

    for test_case in test_cases:
        with open(test_cases_dir + "/" + test_case, "r") as f:
            test_case_content = json.load(f)

        start_time = time.time()
        model_answer = get_answer_from_system(test_case_content["question"])
        end_time = time.time()
        answer_generation_time_s = end_time - start_time
        answer_generation_time_s = int(answer_generation_time_s)
        keyword_test_passed = run_keyword_test(test_case_content["question"], model_answer, test_case_content["keywords"])
        print(f"Pytanie: {test_case_content['question']}")
        print(f"Odpowiedź: {model_answer}")
        print(f"Wynik: {'✅ OK' if keyword_test_passed else '❌ BŁĄD'}")
        print("-" * 40)


        test_results_file = test_results_dir / test_case
        with open(test_results_file, "w") as f:
            json.dump({"question": test_case_content["question"], 
                       "keywords": test_case_content["keywords"],                      
                       "expected_answer": test_case_content["expected_answer"],
                       "model_answer": model_answer,
                       "keyword_test_passed": keyword_test_passed,
                       "answer_generation_time_s": answer_generation_time_s}, f, indent=4, ensure_ascii=False)



if __name__ == "__main__":
    run_tests()
