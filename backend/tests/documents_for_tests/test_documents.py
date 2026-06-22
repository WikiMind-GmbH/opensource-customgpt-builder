from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import ClassVar


class AvailableFiles(StrEnum):
    northstar = "northstar"
    aurelian = "aurelian"


@dataclass(frozen=True)
class IndexedQuestionsWithCorrectAnswerIndices:
    indexed_questions: str
    correct_answer_indices: list[int]


class TestDocuments:
    @staticmethod
    def get_paths_for_test_files(file: AvailableFiles) -> Path:
        match file:
            case AvailableFiles.northstar:
                return Path("./tests/documents_for_tests/synthetic_doc_northstar.txt")
            case AvailableFiles.aurelian:
                return Path("./tests/documents_for_tests/synthetic_doc_aurelian.txt")

    @staticmethod
    def get_yes_no_questions_for_documents(
        file: AvailableFiles,
    ) -> list[tuple[str, bool]]:
        match file:
            case AvailableFiles.northstar:
                return [
                    ("Does Northstar Linen Logistics operate in Hamburg?", True),
                    ("Does the Hamburg facility process laundry?", True),
                    ("Are electric vans used only within Hamburg city limits?", True),
                    ("Does Northstar process laundry at the Bremen depot?", False),
                    (
                        "Are Sunday emergency deliveries available for hotel customers?",
                        False,
                    ),
                ]
            case AvailableFiles.aurelian:
                return []

    @staticmethod
    def get_indexed_questions_and_indices_of_correct_answers(
        file: AvailableFiles,
        max_number_of_questions: int,
    ) -> IndexedQuestionsWithCorrectAnswerIndices:
        if max_number_of_questions < 1:
            raise ValueError("max_number_of_questions must be at least 1")

        question_tuples = TestDocuments.get_yes_no_questions_for_documents(file=file)
        selected_question_tuples = question_tuples[:max_number_of_questions]

        indexed_questions = "\n".join(
            [
                f"{index}) {question}"
                for index, (question, _) in enumerate(
                    selected_question_tuples,
                    start=1,
                )
            ]
        )

        correct_answer_indices = [
            index
            for index, (_, is_correct_answer) in enumerate(
                selected_question_tuples,
                start=1,
            )
            if is_correct_answer
        ]

        return IndexedQuestionsWithCorrectAnswerIndices(
            indexed_questions=indexed_questions,
            correct_answer_indices=correct_answer_indices,
        )

    yes_no_questions_prompt: ClassVar[str] = """\
    Please answer the list of questions.

    Answer exactly in the following format:
    a comma-separated list without spaces consisting only of the numbers of the correct answers.

    Example:

    Questions:
    1) 2 + 2 = 5
    2) 5 + 2 = 7
    3) 5 + 12 = 17

    Your answer:
    2,3
    """
