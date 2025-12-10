"""Integration tests for full quiz sessions."""

import pytest
from flashcard_quizzer.models import Flashcard
from flashcard_quizzer.strategies import SequentialStrategy
from flashcard_quizzer.quiz import QuizEngine


@pytest.fixture
def sample_flashcards():
    """Fixture providing sample flashcards for integration tests."""
    return [
        Flashcard(term="DNS", definition="Domain Name System"),
        Flashcard(term="HTTP", definition="Hypertext Transfer Protocol"),
        Flashcard(term="SSH", definition="Secure Shell"),
    ]


class TestIntegration:
    """Integration tests for complete quiz sessions."""

    def test_full_session(self, sample_flashcards):
        """
        Test a full quiz session with 3 questions.

        Simulates a user answering questions and verifies
        that final stats are calculated correctly.
        """
        # Setup quiz engine with sequential strategy
        strategy = SequentialStrategy()
        engine = QuizEngine(sample_flashcards, strategy)

        # Simulate user answering 3 questions
        # Question 1: Correct
        question1 = engine.get_next_question()
        assert question1.term == "DNS"
        result1 = engine.submit_answer(question1, "Domain Name System")
        assert result1.is_correct is True

        # Question 2: Incorrect
        question2 = engine.get_next_question()
        assert question2.term == "HTTP"
        result2 = engine.submit_answer(question2, "Wrong Answer")
        assert result2.is_correct is False

        # Question 3: Correct
        question3 = engine.get_next_question()
        assert question3.term == "SSH"
        result3 = engine.submit_answer(question3, "Secure Shell")
        assert result3.is_correct is True

        # Verify final stats calculation
        stats = engine.get_stats()
        assert stats.total_questions == 3
        assert stats.correct_answers == 2
        assert stats.incorrect_answers == 1
        assert stats.accuracy == pytest.approx(66.67, rel=0.1)

        # Verify missed terms tracking
        assert "HTTP" in stats.missed_terms
        assert "DNS" not in stats.missed_terms
        assert "SSH" not in stats.missed_terms

    def test_full_session_all_correct(self, sample_flashcards):
        """Test a session where user answers all questions correctly."""
        strategy = SequentialStrategy()
        engine = QuizEngine(sample_flashcards, strategy)

        # Answer all questions correctly
        for card in sample_flashcards:
            question = engine.get_next_question()
            engine.submit_answer(question, question.definition)

        # Verify stats
        stats = engine.get_stats()
        assert stats.total_questions == 3
        assert stats.correct_answers == 3
        assert stats.incorrect_answers == 0
        assert stats.accuracy == 100.0
        assert len(stats.missed_terms) == 0

    def test_full_session_all_incorrect(self, sample_flashcards):
        """Test a session where user answers all questions incorrectly."""
        strategy = SequentialStrategy()
        engine = QuizEngine(sample_flashcards, strategy)

        # Answer all questions incorrectly
        for card in sample_flashcards:
            question = engine.get_next_question()
            engine.submit_answer(question, "Wrong Answer")

        # Verify stats
        stats = engine.get_stats()
        assert stats.total_questions == 3
        assert stats.correct_answers == 0
        assert stats.incorrect_answers == 3
        assert stats.accuracy == 0.0
        assert len(stats.missed_terms) == 3

    def test_session_with_case_insensitive_answers(self, sample_flashcards):
        """Test that answers are case-insensitive in a full session."""
        strategy = SequentialStrategy()
        engine = QuizEngine(sample_flashcards, strategy)

        # Answer with different cases
        q1 = engine.get_next_question()
        r1 = engine.submit_answer(q1, "domain name system")  # lowercase
        assert r1.is_correct

        q2 = engine.get_next_question()
        r2 = engine.submit_answer(q2, "HYPERTEXT TRANSFER PROTOCOL")  # upper
        assert r2.is_correct

        q3 = engine.get_next_question()
        r3 = engine.submit_answer(q3, "SeCuRe ShElL")  # mixed case
        assert r3.is_correct

        stats = engine.get_stats()
        assert stats.accuracy == 100.0
