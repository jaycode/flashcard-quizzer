"""Quiz mode strategies implementing the Strategy pattern."""

from abc import ABC, abstractmethod
from typing import List
import random
from .models import Flashcard, QuizResult


class QuizStrategy(ABC):
    """Abstract base class for quiz mode strategies."""
    
    @abstractmethod
    def get_next_flashcard(
        self, 
        flashcards: List[Flashcard], 
        results: List[QuizResult]
    ) -> Flashcard:
        """
        Get the next flashcard to quiz.
        
        Args:
            flashcards: List of all available flashcards
            results: List of quiz results so far
            
        Returns:
            The next flashcard to present
        """
        pass
    
    @abstractmethod
    def has_more_questions(
        self, 
        flashcards: List[Flashcard], 
        results: List[QuizResult]
    ) -> bool:
        """
        Check if there are more questions to present.
        
        Args:
            flashcards: List of all available flashcards
            results: List of quiz results so far
            
        Returns:
            True if there are more questions, False otherwise
        """
        pass


class SequentialStrategy(QuizStrategy):
    """Present flashcards in sequential order."""
    
    def get_next_flashcard(
        self, 
        flashcards: List[Flashcard], 
        results: List[QuizResult]
    ) -> Flashcard:
        """Get the next flashcard in sequential order."""
        index = len(results)
        return flashcards[index]
    
    def has_more_questions(
        self, 
        flashcards: List[Flashcard], 
        results: List[QuizResult]
    ) -> bool:
        """Check if there are more flashcards in the sequence."""
        return len(results) < len(flashcards)


class RandomStrategy(QuizStrategy):
    """Present flashcards in random order without repetition."""
    
    def __init__(self) -> None:
        """Initialize the random strategy."""
        self._shuffled_indices: List[int] = []
        self._initialized = False
    
    def _initialize_shuffle(self, flashcards: List[Flashcard]) -> None:
        """Initialize the shuffled indices if not already done."""
        if not self._initialized:
            self._shuffled_indices = list(range(len(flashcards)))
            random.shuffle(self._shuffled_indices)
            self._initialized = True
    
    def get_next_flashcard(
        self, 
        flashcards: List[Flashcard], 
        results: List[QuizResult]
    ) -> Flashcard:
        """Get the next flashcard in random order."""
        self._initialize_shuffle(flashcards)
        index = self._shuffled_indices[len(results)]
        return flashcards[index]
    
    def has_more_questions(
        self, 
        flashcards: List[Flashcard], 
        results: List[QuizResult]
    ) -> bool:
        """Check if there are more flashcards to present."""
        self._initialize_shuffle(flashcards)
        return len(results) < len(flashcards)


class AdaptiveStrategy(QuizStrategy):
    """
    Present flashcards adaptively, repeating incorrectly answered cards.
    
    This strategy will continue until all flashcards have been answered correctly
    at least once, prioritizing cards that were answered incorrectly.
    """
    
    def __init__(self) -> None:
        """Initialize the adaptive strategy."""
        self._incorrect_terms: set[str] = set()
        self._correct_terms: set[str] = set()
        self._pending_cards: List[Flashcard] = []
        self._initialized = False
    
    def _initialize(self, flashcards: List[Flashcard]) -> None:
        """Initialize the pending cards list."""
        if not self._initialized:
            self._pending_cards = flashcards.copy()
            random.shuffle(self._pending_cards)
            self._initialized = True
    
    def get_next_flashcard(
        self, 
        flashcards: List[Flashcard], 
        results: List[QuizResult]
    ) -> Flashcard:
        """Get the next flashcard adaptively."""
        self._initialize(flashcards)
        
        # Update tracking based on previous result
        if results:
            last_result = results[-1]
            if last_result.is_correct:
                self._correct_terms.add(last_result.flashcard.term)
                self._incorrect_terms.discard(last_result.flashcard.term)
            else:
                self._incorrect_terms.add(last_result.flashcard.term)
        
        # Prioritize incorrect cards
        if self._incorrect_terms:
            # Find a flashcard from incorrect terms
            for card in self._pending_cards:
                if card.term in self._incorrect_terms:
                    return card
        
        # Otherwise, find a card that hasn't been answered correctly yet
        for card in self._pending_cards:
            if card.term not in self._correct_terms:
                return card
        
        # Fallback: return the first pending card
        return self._pending_cards[0]
    
    def has_more_questions(
        self, 
        flashcards: List[Flashcard], 
        results: List[QuizResult]
    ) -> bool:
        """Check if all flashcards have been answered correctly at least once."""
        self._initialize(flashcards)
        
        # Update tracking based on results
        for result in results:
            if result.is_correct:
                self._correct_terms.add(result.flashcard.term)
                self._incorrect_terms.discard(result.flashcard.term)
            else:
                self._incorrect_terms.add(result.flashcard.term)
        
        # Continue until all cards have been answered correctly
        return len(self._correct_terms) < len(flashcards)


def get_strategy(mode: str) -> QuizStrategy:
    """
    Factory function to get the appropriate quiz strategy.
    
    Args:
        mode: The quiz mode ('sequential', 'random', or 'adaptive')
        
    Returns:
        The appropriate QuizStrategy instance
        
    Raises:
        ValueError: If mode is not recognized
    """
    strategies = {
        "sequential": SequentialStrategy,
        "random": RandomStrategy,
        "adaptive": AdaptiveStrategy,
    }
    
    if mode not in strategies:
        raise ValueError(
            f"Invalid mode: {mode}. Must be one of: {', '.join(strategies.keys())}"
        )
    
    return strategies[mode]()
