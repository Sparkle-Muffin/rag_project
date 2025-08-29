from tests.run_tests import run_tests
from tests.generate_test_report import generate_test_report


def main() -> None:
    """
    Execute the complete RAG testing and reporting pipeline.
    
    Runs the entire testing workflow by:
    1. Executing all test cases using the RAG system
    2. Generating comprehensive test reports with analysis and visualizations
    
    This function serves as the main entry point for the complete testing
    and evaluation process of the RAG system.
    """
    run_tests()
    generate_test_report()


if __name__ == "__main__":
    main()