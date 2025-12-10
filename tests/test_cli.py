"""Tests for CLI interface."""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from flashcard_quizzer.cli import parse_args, main


class TestParseArgs:
    """Tests for argument parsing."""
    
    def test_parse_flashcard_file_only(self):
        """Test parsing with only flashcard file argument."""
        args = parse_args(["flashcards.json"])
        assert args.flashcard_file == "flashcards.json"
        assert args.mode == "sequential"
    
    def test_parse_with_sequential_mode(self):
        """Test parsing with sequential mode."""
        args = parse_args(["flashcards.json", "--mode", "sequential"])
        assert args.flashcard_file == "flashcards.json"
        assert args.mode == "sequential"
    
    def test_parse_with_random_mode(self):
        """Test parsing with random mode."""
        args = parse_args(["flashcards.json", "--mode", "random"])
        assert args.mode == "random"
    
    def test_parse_with_adaptive_mode(self):
        """Test parsing with adaptive mode."""
        args = parse_args(["flashcards.json", "--mode", "adaptive"])
        assert args.mode == "adaptive"
    
    def test_parse_with_short_mode_flag(self):
        """Test parsing with short mode flag."""
        args = parse_args(["flashcards.json", "-m", "random"])
        assert args.mode == "random"
    
    def test_parse_invalid_mode(self):
        """Test that invalid mode raises error."""
        with pytest.raises(SystemExit):
            parse_args(["flashcards.json", "--mode", "invalid"])
    
    def test_parse_no_arguments(self):
        """Test that no arguments raises error."""
        with pytest.raises(SystemExit):
            parse_args([])


class TestMain:
    """Tests for main CLI function."""
    
    def create_temp_flashcard_file(self):
        """Helper to create temporary flashcard file."""
        data = {
            "flashcards": [
                {"term": "DNS", "definition": "Domain Name System"},
                {"term": "HTTP", "definition": "Hypertext Transfer Protocol"},
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            return f.name
    
    def test_main_file_not_found(self):
        """Test main with non-existent file."""
        exit_code = main(["nonexistent.json"])
        assert exit_code == 1
    
    def test_main_invalid_json(self):
        """Test main with invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{invalid json")
            temp_path = f.name
        
        try:
            exit_code = main([temp_path])
            assert exit_code == 1
        finally:
            Path(temp_path).unlink()
    
    def test_main_empty_flashcards(self):
        """Test main with empty flashcards list."""
        data = {"flashcards": []}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = f.name
        
        try:
            exit_code = main([temp_path])
            assert exit_code == 1
        finally:
            Path(temp_path).unlink()
    
    def test_main_invalid_mode(self):
        """Test main with invalid quiz mode."""
        temp_path = self.create_temp_flashcard_file()
        
        try:
            # This will be caught at argument parsing level
            with pytest.raises(SystemExit):
                parse_args([temp_path, "--mode", "invalid"])
        finally:
            Path(temp_path).unlink()
    
    @patch('flashcard_quizzer.cli.InteractiveQuiz')
    def test_main_successful_run(self, mock_quiz_class):
        """Test successful main execution."""
        temp_path = self.create_temp_flashcard_file()
        
        try:
            # Mock the quiz run
            mock_quiz_instance = mock_quiz_class.return_value
            mock_quiz_instance.run.return_value = None
            
            exit_code = main([temp_path])
            
            assert exit_code == 0
            assert mock_quiz_class.called
        finally:
            Path(temp_path).unlink()
    
    @patch('flashcard_quizzer.cli.InteractiveQuiz')
    def test_main_with_different_modes(self, mock_quiz_class):
        """Test main with different quiz modes."""
        temp_path = self.create_temp_flashcard_file()
        
        try:
            mock_quiz_instance = mock_quiz_class.return_value
            mock_quiz_instance.run.return_value = None
            
            # Test sequential mode
            exit_code = main([temp_path, "--mode", "sequential"])
            assert exit_code == 0
            
            # Test random mode
            exit_code = main([temp_path, "--mode", "random"])
            assert exit_code == 0
            
            # Test adaptive mode
            exit_code = main([temp_path, "--mode", "adaptive"])
            assert exit_code == 0
        finally:
            Path(temp_path).unlink()
    
    @patch('flashcard_quizzer.cli.InteractiveQuiz')
    def test_main_keyboard_interrupt(self, mock_quiz_class):
        """Test main handles keyboard interrupt."""
        temp_path = self.create_temp_flashcard_file()
        
        try:
            # Mock the quiz to raise KeyboardInterrupt
            mock_quiz_instance = mock_quiz_class.return_value
            mock_quiz_instance.run.side_effect = KeyboardInterrupt()
            
            exit_code = main([temp_path])
            
            assert exit_code == 130
        finally:
            Path(temp_path).unlink()
