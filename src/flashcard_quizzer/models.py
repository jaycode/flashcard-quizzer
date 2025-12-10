"""Data models for flashcard quizzer."""

from dataclasses import dataclass
from typing import List, Dict, Any
import json


@dataclass
class Flashcard:
    """Represents a single flashcard with a term and definition."""
    
    term: str
    definition: str
    
    def __post_init__(self) -> None:
        """Validate flashcard data."""
        if not self.term or not isinstance(self.term, str):
            raise ValueError("Flashcard term must be a non-empty string")
        if not self.definition or not isinstance(self.definition, str):
            raise ValueError("Flashcard definition must be a non-empty string")


@dataclass
class QuizResult:
    """Represents the result of a single quiz question."""
    
    flashcard: Flashcard
    user_answer: str
    is_correct: bool
    
    
@dataclass
class SessionStats:
    """Tracks statistics for a quiz session."""
    
    total_questions: int = 0
    correct_answers: int = 0
    incorrect_answers: int = 0
    missed_terms: List[str] = None
    
    def __post_init__(self) -> None:
        """Initialize mutable default."""
        if self.missed_terms is None:
            self.missed_terms = []
    
    @property
    def accuracy(self) -> float:
        """Calculate accuracy percentage."""
        if self.total_questions == 0:
            return 0.0
        return (self.correct_answers / self.total_questions) * 100
    
    def record_answer(self, is_correct: bool, term: str = "") -> None:
        """
        Record a quiz answer.
        
        Args:
            is_correct: Whether the answer was correct
            term: The term that was being quizzed (for tracking missed terms)
        """
        self.total_questions += 1
        if is_correct:
            self.correct_answers += 1
        else:
            self.incorrect_answers += 1
            if term and term not in self.missed_terms:
                self.missed_terms.append(term)
            
    def __str__(self) -> str:
        """Return formatted statistics."""
        result = (
            f"\n{'='*50}\n"
            f"Session Statistics\n"
            f"{'='*50}\n"
            f"Total Questions: {self.total_questions}\n"
            f"Correct Answers: {self.correct_answers}\n"
            f"Incorrect Answers: {self.incorrect_answers}\n"
            f"Accuracy: {self.accuracy:.1f}%\n"
        )
        
        if self.missed_terms:
            result += f"\nTerms You Missed:\n"
            for term in self.missed_terms:
                result += f"  - {term}\n"
        
        result += f"{'='*50}\n"
        return result


class FlashcardLoader:
    """Loads and validates flashcards from JSON files."""
    
    @staticmethod
    def load_from_json(filepath: str) -> List[Flashcard]:
        """
        Load flashcards from a JSON file.
        
        Args:
            filepath: Path to the JSON file containing flashcards
            
        Returns:
            List of Flashcard objects
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If JSON is invalid or doesn't match expected format
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Flashcard file not found: {filepath}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        
        return FlashcardLoader._validate_and_parse(data)
    
    @staticmethod
    def _validate_and_parse(data: Any) -> List[Flashcard]:
        """
        Validate and parse JSON data into Flashcard objects.

        Supports three formats:
        1. Array format: [{"front": "...", "back": "..."}]
        2. Object with "cards": {"cards": [...]}
        3. Object with "flashcards": {"flashcards": [...]}

        Args:
            data: Parsed JSON data

        Returns:
            List of Flashcard objects

        Raises:
            ValueError: If data structure is invalid
        """
        # Format 1: Array format [{"front": "...", "back": "..."}]
        if isinstance(data, list):
            flashcards_data = data
        # Format 2 & 3: Object format
        elif isinstance(data, dict):
            # Try "cards" key first (new format)
            if "cards" in data:
                flashcards_data = data["cards"]
            # Fall back to "flashcards" key (existing format)
            elif "flashcards" in data:
                flashcards_data = data["flashcards"]
            else:
                raise ValueError(
                    "JSON object must contain 'cards' or 'flashcards' key"
                )
        else:
            raise ValueError(
                "JSON root must be an array or object"
            )

        if not isinstance(flashcards_data, list):
            raise ValueError("Flashcards data must be a list")

        if len(flashcards_data) == 0:
            raise ValueError("Flashcards list cannot be empty")

        flashcards: List[Flashcard] = []
        for idx, item in enumerate(flashcards_data):
            if not isinstance(item, dict):
                raise ValueError(
                    f"Flashcard at index {idx} must be an object"
                )

            # Support both "front"/"back" and "term"/"definition" keys
            if "front" in item and "back" in item:
                term = item["front"]
                definition = item["back"]
            elif "term" in item and "definition" in item:
                term = item["term"]
                definition = item["definition"]
            else:
                raise ValueError(
                    f"Flashcard at index {idx} must have either "
                    "'front'/'back' or 'term'/'definition' keys"
                )

            try:
                flashcard = Flashcard(term=term, definition=definition)
                flashcards.append(flashcard)
            except ValueError as e:
                raise ValueError(f"Invalid flashcard at index {idx}: {e}")

        return flashcards
