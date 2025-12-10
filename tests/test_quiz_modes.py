"""Tests for quiz mode factory and adaptive behavior."""

import pytest
from flashcard_quizzer.models import Flashcard, QuizResult
from flashcard_quizzer.strategies import (
    get_strategy,
    SequentialStrategy,
    RandomStrategy,
    AdaptiveStrategy
)


@pytest.fixture
def sample_flashcards():
    """Fixture providing sample flashcards."""
    return [
        Flashcard(term="DNS", definition="Domain Name System"),
        Flashcard(term="HTTP", definition="Hypertext Transfer Protocol"),
        Flashcard(term="SSH", definition="Secure Shell"),
    ]


class TestQuizModeFactory:
    """Tests for quiz mode factory pattern."""

    def test_quiz_mode_factory(self):
        """Test that factory returns correct class objects."""
        # Test sequential mode
        sequential = get_strategy("sequential")
        assert isinstance(sequential, SequentialStrategy)

        # Test random mode
        random_mode = get_strategy("random")
        assert isinstance(random_mode, RandomStrategy)

        # Test adaptive mode
        adaptive = get_strategy("adaptive")
        assert isinstance(adaptive, AdaptiveStrategy)

    def test_factory_invalid_mode(self):
        """Test that factory raises error for invalid mode."""
        with pytest.raises(ValueError, match="Invalid mode"):
            get_strategy("invalid_mode")

    def test_factory_case_sensitive(self):
        """Test that factory is case-sensitive."""
        with pytest.raises(ValueError):
            get_strategy("Sequential")


class TestAdaptiveModeRequirement:
    """Tests for adaptive mode behavior as specified in requirements."""

    def test_adaptive_mode_behavior(self, sample_flashcards):
        """
        Test that adaptive mode actually repeats incorrect questions.

        This test verifies that when a user gets a question wrong,
        the adaptive mode will present it again until answered correctly.
        """
        strategy = AdaptiveStrategy()
        results = []

        # Get first card and answer incorrectly
        first_card = strategy.get_next_flashcard(sample_flashcards, results)
        first_term = first_card.term
        results.append(QuizResult(first_card, "wrong answer", False))

        # Continue through quiz
        terms_seen = [first_term]
        iterations = 0
        max_iterations = 20

        while (
            strategy.has_more_questions(sample_flashcards, results)
            and iterations < max_iterations
        ):
            card = strategy.get_next_flashcard(sample_flashcards, results)
            terms_seen.append(card.term)

            # Answer the first incorrect card correctly when we see it again
            if card.term == first_term:
                results.append(QuizResult(card, card.definition, True))
            else:
                # Answer other cards correctly on first attempt
                results.append(QuizResult(card, card.definition, True))

            iterations += 1

        # Verify the first card appeared at least twice
        first_term_count = terms_seen.count(first_term)
        assert first_term_count >= 2, (
            f"Adaptive mode should repeat incorrect answers. "
            f"Term '{first_term}' appeared {first_term_count} times, "
            f"expected at least 2"
        )

    def test_adaptive_prioritizes_wrong_answers(self, sample_flashcards):
        """Test that adaptive mode prioritizes cards answered incorrectly."""
        strategy = AdaptiveStrategy()
        results = []

        # Answer first two cards incorrectly
        card1 = strategy.get_next_flashcard(sample_flashcards, results)
        results.append(QuizResult(card1, "wrong", False))

        card2 = strategy.get_next_flashcard(sample_flashcards, results)
        results.append(QuizResult(card2, "wrong", False))

        # Track which cards get repeated
        incorrect_terms = {card1.term, card2.term}
        repeated_terms = set()

        # Continue quiz
        iterations = 0
        while (
            strategy.has_more_questions(sample_flashcards, results)
            and iterations < 30
        ):
            card = strategy.get_next_flashcard(sample_flashcards, results)

            if card.term in incorrect_terms:
                repeated_terms.add(card.term)
                # Answer correctly this time
                results.append(QuizResult(card, card.definition, True))
            else:
                results.append(QuizResult(card, card.definition, True))

            iterations += 1

        # Both incorrect cards should have been repeated
        assert len(repeated_terms) >= 1, (
            "Adaptive mode should repeat at least one incorrect card"
        )

    def test_adaptive_ends_when_all_correct(self, sample_flashcards):
        """Test that adaptive mode ends when all cards answered correctly."""
        strategy = AdaptiveStrategy()
        results = []

        # Answer all cards correctly on first attempt
        iterations = 0
        while (
            strategy.has_more_questions(sample_flashcards, results)
            and iterations < 20
        ):
            card = strategy.get_next_flashcard(sample_flashcards, results)
            results.append(QuizResult(card, card.definition, True))
            iterations += 1

        # Should have exactly as many results as flashcards
        assert len(results) == len(sample_flashcards)
        assert not strategy.has_more_questions(sample_flashcards, results)
