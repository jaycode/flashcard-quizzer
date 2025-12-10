---
Follow-up #1
---

Do a full-review of your code, and make sure it follows the following specficiations

# Overview

We need a lightweight internal tool to help new hires memorize our server acronyms. It needs to run in the terminal, load data from JSON, and have different quiz modes. The code needs to be clean so we can extend it later.

# The Specifications

You must produce an application that meets the following criteria.

1. Functional Requirements (What the app does)
  - Data Ingestion:
    - The app must load flashcards from a JSON file.
    - It must validate the JSON structure. If the file is missing or malformed, the app should crash gracefully with a helpful error message, not a stack trace.
  - The Quiz Loop:
    - Present the "Front" of the card to the user.
    - Accept text input for the answer.
    - Compare input to the "Back" of the card (case-insensitive).
    - Provide immediate feedback (Correct/Incorrect).
  - Quiz Modes:
    - Sequential: Go through cards from 1 to N.
    - Random: Shuffle the deck.
    - Adaptive: This is the challenge feature. The app should prioritize cards the user previously got wrong.
  - Session Stats:
    - At the end of a quiz, show a summary table: Total Questions, Accuracy %, and a list of terms the user missed.
2. Technical Requirements
  - Architecture:
    - The code must be modular. Do not submit a single main.py file. Separation of concerns is required (e.g., `data_loader.py`, `quiz_engine.py`, `ui.py`).
  - Design Patterns:
    - Use the Strategy Pattern for the Quiz Modes.
    - Why? Because Sequential, Random, and Adaptive are different algorithms for the same task (selecting the next card). This allows you to easily add a "Spaced Repetition" mode later without rewriting the whole app.
  - Type Safety:
    - All functions must have Python Type Hints.
  - Testing:
    - The project must include a test suite (using pytest).
    - You need at least 80% code coverage.

---
Follow-up #2
---

Update the project to meet the following requirements.

# 1. Project Structure

- `main.py`: Currently empty. This will be your entry point.
- `data/`: Place your sample JSON files here.
- `utils/`: For helper modules (you will generate file_handler.py here).
- `tests/`: Currently empty. You will direct the AI to fill this with pytest cases.
- `docs/`: Contains templates for your "AI Interaction Log." You must update this log as you work.
- `.env`: Configuration files for your AI tools.

# 2. Implementation Milestones

## Phase 1: Data Layer & Validation

Create a system to load and validate flashcard data.

- Requirement: The app must support JSON input in two formats:
  a. Array Format: A simple list of objects `[{"front": "...", "back": "..."}]`.
  b. Object Format: A wrapper object `{"cards": [...]}`.
- Error Handling: If the JSON is malformed or missing fields, the app must catch the error and print a friendly message (no raw Python tracebacks).

## Phase 2: Core Logic & Design Patterns

- The Logic: You need three distinct ways to serve questions:
  a. `SequentialMode`: Order 1, 2, 3...
  b. `RandomMode`: Shuffled order.
  c. `AdaptiveMode`: Prioritize cards the user gets wrong.
- Implement a `QuizMode` abstract base class. Then create three classes that inherit from it. Use a Factory Pattern to select the correct mode based on user input.

## Phase 3: The CLI & Interaction
Finally, build the user interface.

- Requirements:
  - Use argparse to handle flags like `-f` (file), `-m` (mode), and `--stats`.
  - Display text colors (Green for correct, Red for incorrect).
  - Allow the user to type "exit" or press Ctrl+C to quit gracefully without errors.

# 3. Testing Requirements

The code must pass the following test scenarios:

## A. Data Loader Tests (`test_flashcard_loader.py`)

- **`test_load_valid_flashcards_array`**: Does it load a list correctly?
- **`test_load_invalid_json`**: Does it gracefully handle bad syntax?
- **`test_load_missing_required_field`**: Does it reject cards without a "Back"?

## B. Quiz Logic Tests (`test_quiz_modes.py`)

- **`test_quiz_mode_factory`**: Does the factory return the correct class object?
- **`test_adaptive_mode_behavior`**: Does it actually repeat incorrect questions?

## C. Integration Tests (`test_integration.py`)

- **`test_full_session`**: Simulate a user answering 3 questions and checking the final stats calculation.

---

### How to verify
Run the full suite in your terminal:

```
pytest --cov=. --cov-report=html
```

Target: >80% code coverage.

# 4. Definition of Done

Your project is complete when:

1. You can run `python main.py -m adaptive -f data/python_basics.json` and play a full game.
2. The code uses the **Strategy** and **Factory** patterns (checked by inspecting `quiz_engine.py`).
3. All tests pass, and `flake8` reports no linting errors.