"""Main entry point for the Flashcard Quizzer application."""

import sys
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from flashcard_quizzer.models import FlashcardLoader  # noqa: E402
from flashcard_quizzer.strategies import get_strategy  # noqa: E402
from flashcard_quizzer.quiz import QuizEngine, InteractiveQuiz  # noqa: E402


def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Flashcard Quizzer - Memorize flashcards interactively",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py -f data/python_basics.json
  python main.py -f data/python_basics.json -m random
  python main.py -f data/python_basics.json -m adaptive --stats
        """,
    )

    parser.add_argument(
        "-f",
        "--file",
        required=True,
        type=str,
        dest="file",
        help="Path to JSON file containing flashcards",
    )

    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        choices=["sequential", "random", "adaptive"],
        default="sequential",
        help="Quiz mode: sequential, random, or adaptive (default: sequential)",
    )

    parser.add_argument(
        "--stats", action="store_true", help="Show detailed statistics at the end"
    )

    return parser.parse_args()


def print_colored(text: str, color: str = "default"):
    """
    Print text with color.

    Args:
        text: Text to print
        color: Color name ('green', 'red', or 'default')
    """
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "default": "\033[0m",
        "reset": "\033[0m",
    }

    color_code = colors.get(color, colors["default"])
    reset_code = colors["reset"]
    print(f"{color_code}{text}{reset_code}")


def main():
    """
    Main entry point for the application.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        args = parse_arguments()

        # Load flashcards
        print(f"\nLoading flashcards from {args.file}...")
        try:
            flashcards = FlashcardLoader.load_from_json(args.file)
            print(f"Loaded {len(flashcards)} flashcards.\n")
        except FileNotFoundError as e:
            print_colored(f"Error: {e}", "red")
            return 1
        except ValueError as e:
            print_colored(f"Error: {e}", "red")
            return 1

        # Get quiz strategy
        print(f"Quiz mode: {args.mode}\n")
        strategy = get_strategy(args.mode)

        # Create quiz engine
        engine = QuizEngine(flashcards, strategy)

        # Custom output function with colors
        def colored_output(text: str):
            """Output function that adds colors to feedback."""
            if "✓" in text or "Correct" in text:
                print_colored(text, "green")
            elif "✗" in text or "Incorrect" in text:
                print_colored(text, "red")
            else:
                print(text)

        # Run interactive quiz
        quiz = InteractiveQuiz(engine, output_fn=colored_output)

        print("Type your answers or 'exit' to quit at any time.")
        print("Press Ctrl+C to exit gracefully.\n")

        # Override input to handle 'exit' command
        original_input = input

        def exit_aware_input(prompt):
            """Input function that handles 'exit' command."""
            user_input = original_input(prompt)
            if user_input.lower() == "exit":
                raise KeyboardInterrupt()
            return user_input

        quiz.input_fn = exit_aware_input

        # Run the quiz
        quiz.run()

        # Show stats if requested (always shown by InteractiveQuiz.run())
        if args.stats:
            print("\nDetailed statistics shown above.")

        return 0

    except KeyboardInterrupt:
        print_colored("\n\nExiting gracefully... Goodbye!", "default")
        return 0
    except Exception as e:
        print_colored(f"\nUnexpected error: {e}", "red")
        return 1


if __name__ == "__main__":
    sys.exit(main())
