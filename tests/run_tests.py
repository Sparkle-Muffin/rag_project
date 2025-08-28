import re
import sys
import os
import json
from pathlib import Path
import time
from typing import List, Dict
from tqdm import tqdm


# Add the parent directory to Python path so we can import from common/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.prompt_generation import create_prompt
from common.bielik_api import call_model_non_stream


def get_answer_from_model(question: str) -> str:
    db_chunks_number = 20
    model_context_chunks_number = 10

    with open("common/prompts/rag_system_prompt.txt", "r") as f:
        system_prompt = f.read()
    
    system_prompt, user_prompt = create_prompt(system_prompt=system_prompt, 
                                               user_prompt=question, 
                                               db_chunks_number=db_chunks_number, 
                                               model_context_chunks_number=model_context_chunks_number)

    model_response = call_model_non_stream(system_prompt, user_prompt)
    print(model_response)

    return model_response


def run_keyword_coverage_test(answer: str, required: List[str], optional: List[str] = None) -> Dict[str, float]:
    """
    Checks keyword coverage.
    - Each keyword can have variants separated by "/" e.g. "politechnika/politechniki/politechnikę".
    - Matching is case-insensitive.
    """
    ans = answer.casefold()
    optional = optional or []

    def contains_any_variant(text, kw_group: str) -> bool:
        variants = [v.strip().casefold() for v in kw_group.split("/")]
        return any(re.search(rf"\b{re.escape(v)}\b", text) for v in variants)

    required_hits = sum(1 for kw in required if contains_any_variant(ans, kw))
    optional_hits = sum(1 for kw in optional if contains_any_variant(ans, kw))

    return {
        "required_score": required_hits / len(required) * 100 if required else None,
        "optional_score": optional_hits / len(optional) * 100 if optional else None,
        "total_score": (
            (required_hits + optional_hits) / (len(required) + len(optional)) * 100
            if required or optional else None
        )
    }



def run_LLM_as_a_judge_test(question: str, expected_answer: str, model_answer: str):
    
    with open("tests/prompts/test_system_prompt.txt", "r") as f:
        system_prompt = f.read()

    with open("tests/prompts/structured_output.json", "r") as f:
        structured_output = json.load(f)

    user_prompt = "Pytanie: " + question + "\n" + \
                  "Prawidłowa odpowiedź: " + expected_answer + "\n" + \
                  "Odpowiedź modelu: " + model_answer
    
    model_evaluation_answer = call_model_non_stream(system_prompt, user_prompt, structured_output)
    # Parse the JSON string response into a dictionary
    model_evaluation_dict = json.loads(model_evaluation_answer)
    evaluation_score = model_evaluation_dict["evaluation_score"]
    descriptive_evaluation = model_evaluation_dict["descriptive_evaluation"]

    return evaluation_score, descriptive_evaluation


def run_tests():
    test_cases_dir = "tests/test_cases"
    test_cases = sorted(os.listdir(test_cases_dir))

    test_results_dir = Path("tests/test_results/")
    test_results_dir.mkdir(exist_ok=True)

    for test_case in tqdm(test_cases, desc="Running tests"):
        with open(test_cases_dir + "/" + test_case, "r") as f:
            test_case_content = json.load(f)

        # Run model
        start_time = time.time()
        model_answer = get_answer_from_model(test_case_content["question"])
        end_time = time.time()
        answer_generation_time_s = end_time - start_time
        answer_generation_time_s = int(answer_generation_time_s)

        # Run keyword test
        keyword_scores = run_keyword_coverage_test(model_answer, 
                                                   test_case_content["required_keywords"],
                                                   test_case_content["optional_keywords"])

        # Run LLM-as-a-judge test
        evaluation_score, descriptive_evaluation = run_LLM_as_a_judge_test(test_case_content["question"], 
                                                                           test_case_content["expected_answer"],
                                                                           model_answer)

        test_results_file = test_results_dir / test_case
        with open(test_results_file, "w") as f:
            json.dump({"question": test_case_content["question"], 
                       "required_keywords": test_case_content["required_keywords"],
                       "optional_keywords": test_case_content["optional_keywords"],
                       "expected_answer": test_case_content["expected_answer"],
                       "model_answer": model_answer,
                       "required_keywords_score": keyword_scores["required_score"],
                       "optional_keywords_score": keyword_scores["optional_score"],
                       "total_keywords_score": keyword_scores["total_score"],
                       "evaluation_score": evaluation_score,
                       "descriptive_evaluation": descriptive_evaluation,                       
                       "answer_generation_time_s": answer_generation_time_s}, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    run_tests()
