---
Copilot jumpstart prompt
---

A lightweight terminal tool to help new hires memorize server acronyms. It must load and validate JSON flashcards, run quizzes with sequential, random, or adaptive modes, give instant feedback, and show session stats. Code must be modular, use the Strategy pattern for modes, include full type hints, and ship with a pytest suite achieving at least 80% coverage.

---
Full prompt after the project's created
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