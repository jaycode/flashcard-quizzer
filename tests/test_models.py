"""Tests for data models."""

import pytest
import json
import tempfile
from pathlib import Path

from flashcard_quizzer.models import (
    Flashcard, QuizResult, SessionStats, FlashcardLoader
)


class TestFlashcard:
    """Tests for Flashcard class."""
    
    def test_valid_flashcard(self):
        """Test creating a valid flashcard."""
        card = Flashcard(term="DNS", definition="Domain Name System")
        assert card.term == "DNS"
        assert card.definition == "Domain Name System"
    
    def test_empty_term_raises_error(self):
        """Test that empty term raises ValueError."""
        with pytest.raises(ValueError, match="term must be a non-empty string"):
            Flashcard(term="", definition="Definition")
    
    def test_empty_definition_raises_error(self):
        """Test that empty definition raises ValueError."""
        with pytest.raises(ValueError, match="definition must be a non-empty string"):
            Flashcard(term="Term", definition="")
    
    def test_non_string_term_raises_error(self):
        """Test that non-string term raises ValueError."""
        with pytest.raises(ValueError, match="term must be a non-empty string"):
            Flashcard(term=123, definition="Definition")
    
    def test_non_string_definition_raises_error(self):
        """Test that non-string definition raises ValueError."""
        with pytest.raises(ValueError, match="definition must be a non-empty string"):
            Flashcard(term="Term", definition=456)


class TestQuizResult:
    """Tests for QuizResult class."""
    
    def test_correct_result(self):
        """Test creating a correct quiz result."""
        card = Flashcard(term="DNS", definition="Domain Name System")
        result = QuizResult(
            flashcard=card,
            user_answer="Domain Name System",
            is_correct=True
        )
        assert result.flashcard == card
        assert result.user_answer == "Domain Name System"
        assert result.is_correct is True
    
    def test_incorrect_result(self):
        """Test creating an incorrect quiz result."""
        card = Flashcard(term="HTTP", definition="Hypertext Transfer Protocol")
        result = QuizResult(
            flashcard=card,
            user_answer="Wrong Answer",
            is_correct=False
        )
        assert result.is_correct is False


class TestSessionStats:
    """Tests for SessionStats class."""
    
    def test_initial_stats(self):
        """Test initial session statistics."""
        stats = SessionStats()
        assert stats.total_questions == 0
        assert stats.correct_answers == 0
        assert stats.incorrect_answers == 0
        assert stats.accuracy == 0.0
    
    def test_record_correct_answer(self):
        """Test recording a correct answer."""
        stats = SessionStats()
        stats.record_answer(True)
        assert stats.total_questions == 1
        assert stats.correct_answers == 1
        assert stats.incorrect_answers == 0
        assert stats.accuracy == 100.0
    
    def test_record_incorrect_answer(self):
        """Test recording an incorrect answer."""
        stats = SessionStats()
        stats.record_answer(False)
        assert stats.total_questions == 1
        assert stats.correct_answers == 0
        assert stats.incorrect_answers == 1
        assert stats.accuracy == 0.0
    
    def test_multiple_answers(self):
        """Test recording multiple answers."""
        stats = SessionStats()
        stats.record_answer(True)
        stats.record_answer(True)
        stats.record_answer(False)
        stats.record_answer(True)
        
        assert stats.total_questions == 4
        assert stats.correct_answers == 3
        assert stats.incorrect_answers == 1
        assert stats.accuracy == 75.0
    
    def test_stats_string_representation(self):
        """Test string representation of stats."""
        stats = SessionStats()
        stats.record_answer(True)
        stats.record_answer(False)
        
        stats_str = str(stats)
        assert "Session Statistics" in stats_str
        assert "Total Questions: 2" in stats_str
        assert "Correct Answers: 1" in stats_str
        assert "Incorrect Answers: 1" in stats_str
        assert "Accuracy: 50.0%" in stats_str


class TestFlashcardLoader:
    """Tests for FlashcardLoader class."""
    
    def test_load_valid_json(self):
        """Test loading valid JSON file."""
        data = {
            "flashcards": [
                {"term": "DNS", "definition": "Domain Name System"},
                {"term": "HTTP", "definition": "Hypertext Transfer Protocol"}
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = f.name
        
        try:
            cards = FlashcardLoader.load_from_json(temp_path)
            assert len(cards) == 2
            assert cards[0].term == "DNS"
            assert cards[0].definition == "Domain Name System"
            assert cards[1].term == "HTTP"
        finally:
            Path(temp_path).unlink()
    
    def test_file_not_found(self):
        """Test loading non-existent file."""
        with pytest.raises(FileNotFoundError, match="Flashcard file not found"):
            FlashcardLoader.load_from_json("nonexistent.json")
    
    def test_invalid_json_format(self):
        """Test loading file with invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{invalid json")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Invalid JSON format"):
                FlashcardLoader.load_from_json(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_json_not_object(self):
        """Test JSON that is not an object."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(["array"], f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="JSON root must be an object"):
                FlashcardLoader.load_from_json(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_missing_flashcards_key(self):
        """Test JSON missing 'flashcards' key."""
        data = {"other_key": []}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="must contain 'flashcards' key"):
                FlashcardLoader.load_from_json(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_flashcards_not_list(self):
        """Test 'flashcards' value is not a list."""
        data = {"flashcards": "not a list"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="'flashcards' must be a list"):
                FlashcardLoader.load_from_json(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_empty_flashcards_list(self):
        """Test empty flashcards list."""
        data = {"flashcards": []}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Flashcards list cannot be empty"):
                FlashcardLoader.load_from_json(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_flashcard_not_object(self):
        """Test flashcard item that is not an object."""
        data = {"flashcards": ["string instead of object"]}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Flashcard at index 0 must be an object"):
                FlashcardLoader.load_from_json(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_missing_term_or_definition(self):
        """Test flashcard missing term or definition."""
        data = {"flashcards": [{"term": "DNS"}]}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="must have 'term' and 'definition' keys"):
                FlashcardLoader.load_from_json(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_invalid_flashcard_data(self):
        """Test flashcard with invalid data."""
        data = {"flashcards": [{"term": "", "definition": "Definition"}]}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Invalid flashcard at index 0"):
                FlashcardLoader.load_from_json(temp_path)
        finally:
            Path(temp_path).unlink()
