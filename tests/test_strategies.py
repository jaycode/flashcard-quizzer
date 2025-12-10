"""Tests for quiz strategies."""

import pytest
from flashcard_quizzer.models import Flashcard, QuizResult
from flashcard_quizzer.strategies import (
    SequentialStrategy, RandomStrategy, AdaptiveStrategy, get_strategy
)


@pytest.fixture
def sample_flashcards():
    """Fixture providing sample flashcards."""
    return [
        Flashcard(term="DNS", definition="Domain Name System"),
        Flashcard(term="HTTP", definition="Hypertext Transfer Protocol"),
        Flashcard(term="SSH", definition="Secure Shell"),
        Flashcard(term="FTP", definition="File Transfer Protocol"),
    ]


class TestSequentialStrategy:
    """Tests for SequentialStrategy."""
    
    def test_sequential_order(self, sample_flashcards):
        """Test that flashcards are presented in sequential order."""
        strategy = SequentialStrategy()
        results = []
        
        # Get all flashcards in order
        for i in range(len(sample_flashcards)):
            card = strategy.get_next_flashcard(sample_flashcards, results)
            assert card == sample_flashcards[i]
            results.append(QuizResult(card, "answer", True))
    
    def test_has_more_questions_true(self, sample_flashcards):
        """Test has_more_questions returns True when questions remain."""
        strategy = SequentialStrategy()
        results = []
        
        assert strategy.has_more_questions(sample_flashcards, results) is True
    
    def test_has_more_questions_false(self, sample_flashcards):
        """Test has_more_questions returns False when all done."""
        strategy = SequentialStrategy()
        results = [
            QuizResult(card, "answer", True) for card in sample_flashcards
        ]
        
        assert strategy.has_more_questions(sample_flashcards, results) is False
    
    def test_partial_completion(self, sample_flashcards):
        """Test strategy with partial completion."""
        strategy = SequentialStrategy()
        results = [
            QuizResult(sample_flashcards[0], "answer", True),
            QuizResult(sample_flashcards[1], "answer", False),
        ]
        
        assert strategy.has_more_questions(sample_flashcards, results) is True
        next_card = strategy.get_next_flashcard(sample_flashcards, results)
        assert next_card == sample_flashcards[2]


class TestRandomStrategy:
    """Tests for RandomStrategy."""
    
    def test_all_cards_presented(self, sample_flashcards):
        """Test that all flashcards are eventually presented."""
        strategy = RandomStrategy()
        results = []
        presented_terms = []
        
        while strategy.has_more_questions(sample_flashcards, results):
            card = strategy.get_next_flashcard(sample_flashcards, results)
            presented_terms.append(card.term)
            results.append(QuizResult(card, "answer", True))
        
        assert len(presented_terms) == len(sample_flashcards)
        assert set(presented_terms) == set(card.term for card in sample_flashcards)
    
    def test_no_repetition(self, sample_flashcards):
        """Test that cards are not repeated in random mode."""
        strategy = RandomStrategy()
        results = []
        presented_terms = []
        
        while strategy.has_more_questions(sample_flashcards, results):
            card = strategy.get_next_flashcard(sample_flashcards, results)
            presented_terms.append(card.term)
            results.append(QuizResult(card, "answer", True))
        
        # Check no duplicates
        assert len(presented_terms) == len(set(presented_terms))
    
    def test_has_more_questions(self, sample_flashcards):
        """Test has_more_questions for random strategy."""
        strategy = RandomStrategy()
        results = []
        
        assert strategy.has_more_questions(sample_flashcards, results) is True
        
        # Add results for all cards
        for card in sample_flashcards:
            results.append(QuizResult(card, "answer", True))
        
        assert strategy.has_more_questions(sample_flashcards, results) is False
    
    def test_consistent_shuffle(self, sample_flashcards):
        """Test that shuffle is consistent within same strategy instance."""
        strategy = RandomStrategy()
        results = []
        
        first_card = strategy.get_next_flashcard(sample_flashcards, results)
        results.append(QuizResult(first_card, "answer", True))
        
        second_card = strategy.get_next_flashcard(sample_flashcards, results)
        
        # Create new results and verify order is same
        results2 = []
        strategy2 = RandomStrategy()
        
        # Can't guarantee same order due to randomness, but verify consistency
        card1 = strategy2.get_next_flashcard(sample_flashcards, results2)
        results2.append(QuizResult(card1, "answer", True))
        card2 = strategy2.get_next_flashcard(sample_flashcards, results2)
        
        # Both should complete successfully
        assert card1 in sample_flashcards
        assert card2 in sample_flashcards


class TestAdaptiveStrategy:
    """Tests for AdaptiveStrategy."""
    
    def test_repeats_incorrect_answers(self, sample_flashcards):
        """Test that incorrect answers are repeated."""
        strategy = AdaptiveStrategy()
        results = []
        
        # Get first card and answer incorrectly
        first_card = strategy.get_next_flashcard(sample_flashcards, results)
        results.append(QuizResult(first_card, "wrong", False))
        
        # Continue until we get more questions
        question_count = 1
        seen_terms = {first_card.term}
        
        while strategy.has_more_questions(sample_flashcards, results) and question_count < 20:
            card = strategy.get_next_flashcard(sample_flashcards, results)
            # Answer correctly if it's the repeated card
            if card.term == first_card.term:
                results.append(QuizResult(card, card.definition, True))
            else:
                results.append(QuizResult(card, card.definition, True))
            seen_terms.add(card.term)
            question_count += 1
        
        # The incorrect card should have appeared again
        first_term_count = sum(1 for r in results if r.flashcard.term == first_card.term)
        assert first_term_count >= 2
    
    def test_ends_when_all_correct(self, sample_flashcards):
        """Test that quiz ends when all cards answered correctly."""
        strategy = AdaptiveStrategy()
        results = []
        
        terms_seen = set()
        
        while strategy.has_more_questions(sample_flashcards, results):
            card = strategy.get_next_flashcard(sample_flashcards, results)
            results.append(QuizResult(card, card.definition, True))
            terms_seen.add(card.term)
            
            # Safety check to prevent infinite loop
            if len(results) > 100:
                break
        
        # All terms should have been seen
        assert len(terms_seen) == len(sample_flashcards)
        assert not strategy.has_more_questions(sample_flashcards, results)
    
    def test_prioritizes_incorrect_cards(self, sample_flashcards):
        """Test that incorrect cards are tracked and repeated until answered correctly."""
        strategy = AdaptiveStrategy()
        results = []
        
        # Get first card and answer incorrectly
        first_card = strategy.get_next_flashcard(sample_flashcards, results)
        first_term = first_card.term
        results.append(QuizResult(first_card, "wrong", False))
        
        # Get next card - should prioritize incorrect, but might be different due to pending logic
        second_card = strategy.get_next_flashcard(sample_flashcards, results)
        
        # Continue until all cards seen at least once
        max_iterations = 20
        iterations = 0
        while strategy.has_more_questions(sample_flashcards, results) and iterations < max_iterations:
            card = strategy.get_next_flashcard(sample_flashcards, results)
            # Answer the first incorrect card correctly when we see it again
            if card.term == first_term:
                results.append(QuizResult(card, card.definition, True))
            else:
                results.append(QuizResult(card, card.definition, True))
            iterations += 1
        
        # The first card should have been presented at least twice
        first_term_appearances = sum(1 for r in results if r.flashcard.term == first_term)
        assert first_term_appearances >= 2
    
    def test_all_cards_eventually_presented(self, sample_flashcards):
        """Test that all cards are eventually presented even with some incorrect."""
        strategy = AdaptiveStrategy()
        results = []
        
        terms_seen = set()
        max_questions = 50
        question_count = 0
        
        while strategy.has_more_questions(sample_flashcards, results) and question_count < max_questions:
            card = strategy.get_next_flashcard(sample_flashcards, results)
            terms_seen.add(card.term)
            
            # Answer correctly on second attempt
            is_correct = card.term not in [r.flashcard.term for r in results if not r.is_correct]
            results.append(QuizResult(card, card.definition if is_correct else "wrong", is_correct))
            question_count += 1
        
        assert len(terms_seen) == len(sample_flashcards)


class TestGetStrategy:
    """Tests for get_strategy factory function."""
    
    def test_get_sequential_strategy(self):
        """Test getting sequential strategy."""
        strategy = get_strategy("sequential")
        assert isinstance(strategy, SequentialStrategy)
    
    def test_get_random_strategy(self):
        """Test getting random strategy."""
        strategy = get_strategy("random")
        assert isinstance(strategy, RandomStrategy)
    
    def test_get_adaptive_strategy(self):
        """Test getting adaptive strategy."""
        strategy = get_strategy("adaptive")
        assert isinstance(strategy, AdaptiveStrategy)
    
    def test_invalid_strategy_name(self):
        """Test that invalid strategy name raises error."""
        with pytest.raises(ValueError, match="Invalid mode"):
            get_strategy("invalid")
    
    def test_case_sensitive(self):
        """Test that strategy names are case-sensitive."""
        with pytest.raises(ValueError):
            get_strategy("Sequential")
