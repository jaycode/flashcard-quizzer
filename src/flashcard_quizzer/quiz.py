"""Quiz engine for running flashcard quizzes."""

from typing import List, Optional, Callable
from .models import Flashcard, QuizResult, SessionStats
from .strategies import QuizStrategy


class QuizEngine:
    """Engine for running flashcard quizzes with different strategies."""

    def __init__(self, flashcards: List[Flashcard], strategy: QuizStrategy) -> None:
        """
        Initialize the quiz engine.

        Args:
            flashcards: List of flashcards to quiz
            strategy: Quiz strategy to use

        Raises:
            ValueError: If flashcards list is empty
        """
        if not flashcards:
            raise ValueError("Flashcards list cannot be empty")

        self.flashcards = flashcards
        self.strategy = strategy
        self.results: List[QuizResult] = []
        self.stats = SessionStats()

    def has_next_question(self) -> bool:
        """
        Check if there are more questions to present.

        Returns:
            True if there are more questions, False otherwise
        """
        return self.strategy.has_more_questions(self.flashcards, self.results)

    def get_next_question(self) -> Flashcard:
        """
        Get the next flashcard to quiz.

        Returns:
            The next flashcard

        Raises:
            StopIteration: If there are no more questions
        """
        if not self.has_next_question():
            raise StopIteration("No more questions available")

        return self.strategy.get_next_flashcard(self.flashcards, self.results)

    def check_answer(self, flashcard: Flashcard, user_answer: str) -> bool:
        """
        Check if the user's answer is correct.

        Args:
            flashcard: The flashcard being answered
            user_answer: The user's answer

        Returns:
            True if correct, False otherwise
        """
        # Case-insensitive comparison, strip whitespace
        correct_answer = flashcard.definition.strip().lower()
        user_answer_normalized = user_answer.strip().lower()

        return correct_answer == user_answer_normalized

    def submit_answer(self, flashcard: Flashcard, user_answer: str) -> QuizResult:
        """
        Submit an answer and record the result.

        Args:
            flashcard: The flashcard being answered
            user_answer: The user's answer

        Returns:
            The quiz result
        """
        is_correct = self.check_answer(flashcard, user_answer)

        result = QuizResult(
            flashcard=flashcard, user_answer=user_answer, is_correct=is_correct
        )

        self.results.append(result)
        self.stats.record_answer(is_correct, flashcard.term)

        return result

    def get_feedback(self, result: QuizResult) -> str:
        """
        Generate feedback message for a quiz result.

        Args:
            result: The quiz result

        Returns:
            Formatted feedback string
        """
        if result.is_correct:
            return "✓ Correct!"
        else:
            return (
                f"✗ Incorrect.\n"
                f"Your answer: {result.user_answer}\n"
                f"Correct answer: {result.flashcard.definition}"
            )

    def get_stats(self) -> SessionStats:
        """
        Get current session statistics.

        Returns:
            SessionStats object
        """
        return self.stats


class InteractiveQuiz:
    """Interactive quiz runner for terminal interface."""

    def __init__(
        self,
        engine: QuizEngine,
        input_fn: Optional[Callable[[str], str]] = None,
        output_fn: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Initialize the interactive quiz.

        Args:
            engine: The quiz engine to use
            input_fn: Optional custom input function (for testing)
            output_fn: Optional custom output function (for testing)
        """
        self.engine = engine
        self.input_fn = input_fn or input
        self.output_fn = output_fn or print

    def _is_acronym(self, term: str) -> bool:
        """
        Determine if a term is likely an acronym or abbreviation.

        Args:
            term: The term to check

        Returns:
            True if the term appears to be an acronym, False otherwise
        """
        # Remove common punctuation that might appear in acronyms
        cleaned = term.replace(".", "").replace("-", "").replace("_", "")
        # Consider it an acronym if it's all uppercase and has at least 2 characters
        return len(cleaned) >= 2 and cleaned.isupper() and cleaned.isalpha()

    def run(self) -> SessionStats:
        """
        Run the interactive quiz.

        Returns:
            Final session statistics
        """
        self.output_fn("\n" + "=" * 50)
        self.output_fn("Starting Quiz!")
        self.output_fn("=" * 50 + "\n")

        question_num = 1

        while self.engine.has_next_question():
            try:
                flashcard = self.engine.get_next_question()

                self.output_fn(f"\nQuestion {question_num}:")
                # Use appropriate question format based on whether term is an acronym
                if self._is_acronym(flashcard.term):
                    self.output_fn(f"What does '{flashcard.term}' stand for?")
                else:
                    self.output_fn(f"What is '{flashcard.term}'?")

                user_answer = self.input_fn("Your answer: ")

                result = self.engine.submit_answer(flashcard, user_answer)
                feedback = self.engine.get_feedback(result)

                self.output_fn(feedback)

                question_num += 1

            except KeyboardInterrupt:
                self.output_fn("\n\nQuiz interrupted by user.")
                break

        # Show final statistics
        stats = self.engine.get_stats()
        self.output_fn(str(stats))

        return stats
