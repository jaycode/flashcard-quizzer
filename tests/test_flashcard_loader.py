"""Tests for flashcard loader - specifically for new format requirements."""

import pytest
import json
import tempfile
from pathlib import Path

from flashcard_quizzer.models import FlashcardLoader


class TestFlashcardLoaderNewFormats:
    """Tests for FlashcardLoader with new format requirements."""

    def test_load_valid_flashcards_array(self):
        """Test loading array format: [{"front": "...", "back": "..."}]."""
        data = [
            {"front": "DNS", "back": "Domain Name System"},
            {"front": "HTTP", "back": "Hypertext Transfer Protocol"}
        ]

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            cards = FlashcardLoader.load_from_json(temp_path)
            assert len(cards) == 2
            assert cards[0].term == "DNS"
            assert cards[0].definition == "Domain Name System"
            assert cards[1].term == "HTTP"
            assert cards[1].definition == "Hypertext Transfer Protocol"
        finally:
            Path(temp_path).unlink()

    def test_load_valid_flashcards_object_with_cards(self):
        """Test loading object format: {"cards": [...]}."""
        data = {
            "cards": [
                {"front": "DNS", "back": "Domain Name System"},
                {"front": "HTTP", "back": "Hypertext Transfer Protocol"}
            ]
        }

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            cards = FlashcardLoader.load_from_json(temp_path)
            assert len(cards) == 2
            assert cards[0].term == "DNS"
            assert cards[0].definition == "Domain Name System"
        finally:
            Path(temp_path).unlink()

    def test_load_invalid_json(self):
        """Test that malformed JSON is handled gracefully."""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            f.write("{invalid json syntax")
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Invalid JSON format"):
                FlashcardLoader.load_from_json(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_load_missing_required_field(self):
        """Test that cards without required fields are rejected."""
        # Missing "back" field
        data = [
            {"front": "DNS"}
        ]

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            with pytest.raises(
                ValueError,
                match="must have either 'front'/'back' or 'term'/'definition'"
            ):
                FlashcardLoader.load_from_json(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_load_mixed_format_front_back(self):
        """Test loading with front/back format."""
        data = [
            {"front": "API", "back": "Application Programming Interface"},
            {"front": "REST", "back": "Representational State Transfer"}
        ]

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            cards = FlashcardLoader.load_from_json(temp_path)
            assert len(cards) == 2
            assert cards[0].term == "API"
            assert cards[0].definition == "Application Programming Interface"
        finally:
            Path(temp_path).unlink()

    def test_empty_back_field_rejected(self):
        """Test that empty back field is rejected."""
        data = [
            {"front": "DNS", "back": ""}
        ]

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Invalid flashcard"):
                FlashcardLoader.load_from_json(temp_path)
        finally:
            Path(temp_path).unlink()
