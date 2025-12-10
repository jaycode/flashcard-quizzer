"""Tests for quiz engine."""

import pytest
from flashcard_quizzer.models import Flashcard, QuizResult, SessionStats
from flashcard_quizzer.strategies import SequentialStrategy, RandomStrategy
from flashcard_quizzer.quiz import QuizEngine, InteractiveQuiz


@pytest.fixture
def sample_flashcards():
    """Fixture providing sample flashcards."""
    return [
        Flashcard(term="DNS", definition="Domain Name System"),
        Flashcard(term="HTTP", definition="Hypertext Transfer Protocol"),
        Flashcard(term="SSH", definition="Secure Shell"),
    ]


class TestQuizEngine:
    """Tests for QuizEngine class."""

    def test_initialization(self, sample_flashcards):
        """Test quiz engine initialization."""
        strategy = SequentialStrategy()
        engine = QuizEngine(sample_flashcards, strategy)

        assert engine.flashcards == sample_flashcards
        assert engine.strategy == strategy
        assert len(engine.results) == 0
        assert engine.stats.total_questions == 0

    def test_empty_flashcards_raises_error(self):
        """Test that empty flashcards list raises error."""
        strategy = SequentialStrategy()
        with pytest.raises(ValueError, match="Flashcards list cannot be empty"):
            QuizEngine([], strategy)

    def test_has_next_question(self, sample_flashcards):
        """Test has_next_question method."""
        strategy = SequentialStrategy()
        engine = QuizEngine(sample_flashcards, strategy)

        assert engine.has_next_question() is True

        # Answer all questions
        for card in sample_flashcards:
            engine.submit_answer(card, card.definition)

        assert engine.has_next_question() is False

    def test_get_next_question(self, sample_flashcards):
        """Test get_next_question method."""
        strategy = SequentialStrategy()
        engine = QuizEngine(sample_flashcards, strategy)

        first_question = engine.get_next_question()
        assert first_question == sample_flashcards[0]

    def test_get_next_question_no_more_raises_error(self, sample_flashcards):
        """Test that getting question when none left raises StopIteration."""
        strategy = SequentialStrategy()
        engine = QuizEngine(sample_flashcards, strategy)

        # Exhaust all questions
        for card in sample_flashcards:
            engine.submit_answer(card, card.definition)

        with pytest.raises(StopIteration, match="No more questions available"):
            engine.get_next_question()

    def test_check_answer_correct(self, sample_flashcards):
        """Test checking correct answer."""
        strategy = SequentialStrategy()
        engine = QuizEngine(sample_flashcards, strategy)

        card = sample_flashcards[0]
        assert engine.check_answer(card, "Domain Name System") is True

    def test_check_answer_incorrect(self, sample_flashcards):
        """Test checking incorrect answer."""
        strategy = SequentialStrategy()
        engine = QuizEngine(sample_flashcards, strategy)

        card = sample_flashcards[0]
        assert engine.check_answer(card, "Wrong Answer") is False

    def test_check_answer_case_insensitive(self, sample_flashcards):
        """Test that answer checking is case-insensitive."""
        strategy = SequentialStrategy()
        engine = QuizEngine(sample_flashcards, strategy)

        card = sample_flashcards[0]
        assert engine.check_answer(card, "domain name system") is True
        assert engine.check_answer(card, "DOMAIN NAME SYSTEM") is True
        assert engine.check_answer(card, "DoMaIn NaMe SyStEm") is True

    def test_check_answer_strips_whitespace(self, sample_flashcards):
        """Test that answer checking strips whitespace."""
        strategy = SequentialStrategy()
        engine = QuizEngine(sample_flashcards, strategy)

        card = sample_flashcards[0]
        assert engine.check_answer(card, "  Domain Name System  ") is True
        assert engine.check_answer(card, "\tDomain Name System\n") is True

    def test_submit_answer_correct(self, sample_flashcards):
        """Test submitting correct answer."""
        strategy = SequentialStrategy()
        engine = QuizEngine(sample_flashcards, strategy)

        card = sample_flashcards[0]
        result = engine.submit_answer(card, "Domain Name System")

        assert result.is_correct is True
        assert result.flashcard == card
        assert result.user_answer == "Domain Name System"
        assert len(engine.results) == 1
        assert engine.stats.correct_answers == 1
        assert engine.stats.total_questions == 1

    def test_submit_answer_incorrect(self, sample_flashcards):
        """Test submitting incorrect answer."""
        strategy = SequentialStrategy()
        engine = QuizEngine(sample_flashcards, strategy)

        card = sample_flashcards[0]
        result = engine.submit_answer(card, "Wrong Answer")

        assert result.is_correct is False
        assert len(engine.results) == 1
        assert engine.stats.incorrect_answers == 1
        assert engine.stats.total_questions == 1

    def test_get_feedback_correct(self, sample_flashcards):
        """Test feedback for correct answer."""
        strategy = SequentialStrategy()
        engine = QuizEngine(sample_flashcards, strategy)

        card = sample_flashcards[0]
        result = QuizResult(card, "Domain Name System", True)
        feedback = engine.get_feedback(result)

        assert "Correct" in feedback
        assert "✓" in feedback

    def test_get_feedback_incorrect(self, sample_flashcards):
        """Test feedback for incorrect answer."""
        strategy = SequentialStrategy()
        engine = QuizEngine(sample_flashcards, strategy)

        card = sample_flashcards[0]
        result = QuizResult(card, "Wrong", False)
        feedback = engine.get_feedback(result)

        assert "Incorrect" in feedback
        assert "✗" in feedback
        assert "Wrong" in feedback
        assert "Domain Name System" in feedback

    def test_get_stats(self, sample_flashcards):
        """Test getting session statistics."""
        strategy = SequentialStrategy()
        engine = QuizEngine(sample_flashcards, strategy)

        card1 = sample_flashcards[0]
        engine.submit_answer(card1, "Domain Name System")

        card2 = sample_flashcards[1]
        engine.submit_answer(card2, "Wrong")

        stats = engine.get_stats()
        assert stats.total_questions == 2
        assert stats.correct_answers == 1
        assert stats.incorrect_answers == 1
        assert stats.accuracy == 50.0


class TestInteractiveQuiz:
    """Tests for InteractiveQuiz class."""

    def test_initialization(self, sample_flashcards):
        """Test interactive quiz initialization."""
        strategy = SequentialStrategy()
        engine = QuizEngine(sample_flashcards, strategy)

        # Create mock functions
        inputs = ["Domain Name System", "HTTP Protocol", "SSH"]
        outputs = []

        def mock_input(prompt):
            return inputs.pop(0)

        def mock_output(text):
            outputs.append(text)

        quiz = InteractiveQuiz(engine, mock_input, mock_output)
        assert quiz.engine == engine

    def test_run_all_correct(self, sample_flashcards):
        """Test running quiz with all correct answers."""
        strategy = SequentialStrategy()
        engine = QuizEngine(sample_flashcards, strategy)

        # Prepare correct answers
        inputs = [card.definition for card in sample_flashcards]
        outputs = []

        def mock_input(prompt):
            return inputs.pop(0)

        def mock_output(text):
            outputs.append(text)

        quiz = InteractiveQuiz(engine, mock_input, mock_output)
        stats = quiz.run()

        assert stats.total_questions == 3
        assert stats.correct_answers == 3
        assert stats.incorrect_answers == 0
        assert stats.accuracy == 100.0

    def test_run_mixed_answers(self, sample_flashcards):
        """Test running quiz with mixed correct and incorrect answers."""
        strategy = SequentialStrategy()
        engine = QuizEngine(sample_flashcards, strategy)

        # Prepare mixed answers
        inputs = ["Domain Name System", "Wrong Answer", "Secure Shell"]
        outputs = []

        def mock_input(prompt):
            return inputs.pop(0)

        def mock_output(text):
            outputs.append(text)

        quiz = InteractiveQuiz(engine, mock_input, mock_output)
        stats = quiz.run()

        assert stats.total_questions == 3
        assert stats.correct_answers == 2
        assert stats.incorrect_answers == 1

    def test_run_displays_questions(self, sample_flashcards):
        """Test that questions are displayed during quiz."""
        strategy = SequentialStrategy()
        engine = QuizEngine(sample_flashcards, strategy)

        inputs = [card.definition for card in sample_flashcards]
        outputs = []

        def mock_input(prompt):
            return inputs.pop(0)

        def mock_output(text):
            outputs.append(text)

        quiz = InteractiveQuiz(engine, mock_input, mock_output)
        quiz.run()

        # Check that questions were displayed
        output_text = " ".join(outputs)
        assert "DNS" in output_text
        assert "HTTP" in output_text
        assert "SSH" in output_text

    def test_run_displays_feedback(self, sample_flashcards):
        """Test that feedback is displayed during quiz."""
        strategy = SequentialStrategy()
        engine = QuizEngine(sample_flashcards, strategy)

        inputs = ["Domain Name System", "Wrong", "Secure Shell"]
        outputs = []

        def mock_input(prompt):
            return inputs.pop(0)

        def mock_output(text):
            outputs.append(text)

        quiz = InteractiveQuiz(engine, mock_input, mock_output)
        quiz.run()

        output_text = " ".join(outputs)
        assert "Correct" in output_text or "✓" in output_text
        assert "Incorrect" in output_text or "✗" in output_text

    def test_run_displays_stats(self, sample_flashcards):
        """Test that final statistics are displayed."""
        strategy = SequentialStrategy()
        engine = QuizEngine(sample_flashcards, strategy)

        inputs = [card.definition for card in sample_flashcards]
        outputs = []

        def mock_input(prompt):
            return inputs.pop(0)

        def mock_output(text):
            outputs.append(text)

        quiz = InteractiveQuiz(engine, mock_input, mock_output)
        quiz.run()

        output_text = " ".join(outputs)
        assert "Session Statistics" in output_text
        assert "Total Questions" in output_text
        assert "Accuracy" in output_text
