"""Command-line interface for flashcard quizzer."""

import argparse
import sys
from typing import Optional, List

from .models import FlashcardLoader
from .strategies import get_strategy
from .quiz import QuizEngine, InteractiveQuiz


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.

    Args:
        args: Optional list of arguments (for testing)

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Flashcard Quizzer - A terminal tool for memorizing server acronyms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  flashcard-quiz flashcards.json                    # Sequential mode (default)
  flashcard-quiz flashcards.json --mode random      # Random mode
  flashcard-quiz flashcards.json --mode adaptive    # Adaptive mode
        """,
    )

    parser.add_argument(
        "flashcard_file", type=str, help="Path to JSON file containing flashcards"
    )

    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        choices=["sequential", "random", "adaptive"],
        default="sequential",
        help="Quiz mode (default: sequential)",
    )

    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI application.

    Args:
        args: Optional list of arguments (for testing)

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        parsed_args = parse_args(args)

        # Load flashcards
        print(f"Loading flashcards from {parsed_args.flashcard_file}...")
        flashcards = FlashcardLoader.load_from_json(parsed_args.flashcard_file)
        print(f"Loaded {len(flashcards)} flashcards.\n")

        # Get quiz strategy
        strategy = get_strategy(parsed_args.mode)
        print(f"Quiz mode: {parsed_args.mode}")

        # Create quiz engine
        engine = QuizEngine(flashcards, strategy)

        # Run interactive quiz
        quiz = InteractiveQuiz(engine)
        quiz.run()

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n\nExiting...", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
