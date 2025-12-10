# Flashcard Quizzer

A lightweight terminal tool to help new hires memorize server acronyms through interactive quizzes.

## Features

- 📚 **JSON-based flashcard management** - Load and validate flashcards from JSON files
- 🎯 **Three quiz modes**:
  - **Sequential**: Present flashcards in order
  - **Random**: Shuffle flashcards for varied practice
  - **Adaptive**: Repeat incorrectly answered cards until mastered
- ✅ **Instant feedback** - See correct/incorrect results immediately
- 📊 **Session statistics** - Track your progress with accuracy metrics
- 🏗️ **Modular architecture** - Built with the Strategy pattern for extensibility
- 🔍 **Full type hints** - Complete Python type annotations for better code clarity
- ✨ **Comprehensive testing** - 96% test coverage with pytest

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/jaycode/flashcard-quizzer.git
cd flashcard-quizzer

# Install the package
pip install -e .

# Install development dependencies (for testing)
pip install -r requirements-dev.txt
```

## Usage

### Basic Usage

Run a quiz with the default sequential mode:

```bash
flashcard-quiz data/server_acronyms.json
```

### Quiz Modes

**Sequential Mode** (default):
```bash
flashcard-quiz data/server_acronyms.json --mode sequential
```

**Random Mode**:
```bash
flashcard-quiz data/server_acronyms.json --mode random
```

**Adaptive Mode** (repeats incorrect answers):
```bash
flashcard-quiz data/server_acronyms.json --mode adaptive
```

### Command Line Options

```
usage: flashcard-quiz [-h] [-m {sequential,random,adaptive}] flashcard_file

positional arguments:
  flashcard_file        Path to JSON file containing flashcards

optional arguments:
  -h, --help            show this help message and exit
  -m, --mode {sequential,random,adaptive}
                        Quiz mode (default: sequential)
```

## Flashcard JSON Format

Create your own flashcard files using this JSON structure:

```json
{
  "flashcards": [
    {
      "term": "DNS",
      "definition": "Domain Name System"
    },
    {
      "term": "HTTP",
      "definition": "Hypertext Transfer Protocol"
    }
  ]
}
```

### Validation Rules

- Root must be a JSON object with a `flashcards` key
- `flashcards` must be a non-empty array
- Each flashcard must have `term` and `definition` fields
- Both fields must be non-empty strings

## Example Session

```
$ flashcard-quiz data/server_acronyms.json --mode sequential

Loading flashcards from data/server_acronyms.json...
Loaded 15 flashcards.

Quiz mode: sequential

==================================================
Starting Quiz!
==================================================

Question 1:
What does 'DNS' stand for?
Your answer: Domain Name System
✓ Correct!

Question 2:
What does 'HTTP' stand for?
Your answer: HyperText Protocol
✗ Incorrect.
Your answer: HyperText Protocol
Correct answer: Hypertext Transfer Protocol

...

==================================================
Session Statistics
==================================================
Total Questions: 15
Correct Answers: 13
Incorrect Answers: 2
Accuracy: 86.7%
==================================================
```

## Development

### Running Tests

Run the full test suite:

```bash
pytest tests/
```

Run tests with coverage report:

```bash
pytest tests/ --cov=src/flashcard_quizzer --cov-report=term-missing
```

Run specific test files:

```bash
pytest tests/test_models.py -v
pytest tests/test_strategies.py -v
pytest tests/test_quiz.py -v
pytest tests/test_cli.py -v
```

### Project Structure

```
flashcard-quizzer/
├── src/
│   └── flashcard_quizzer/
│       ├── __init__.py         # Package initialization
│       ├── models.py           # Data models and JSON loader
│       ├── strategies.py       # Quiz mode strategies (Strategy pattern)
│       ├── quiz.py             # Quiz engine and interactive runner
│       └── cli.py              # Command-line interface
├── tests/
│   ├── test_models.py          # Tests for data models
│   ├── test_strategies.py      # Tests for quiz strategies
│   ├── test_quiz.py            # Tests for quiz engine
│   └── test_cli.py             # Tests for CLI
├── data/
│   └── server_acronyms.json    # Sample flashcard data
├── setup.py                    # Package setup configuration
├── requirements.txt            # Runtime dependencies
├── requirements-dev.txt        # Development dependencies
└── README.md                   # This file
```

## Architecture

The application follows a clean, modular architecture:

- **Strategy Pattern**: Quiz modes (Sequential, Random, Adaptive) implement a common interface, making it easy to add new quiz modes
- **Separation of Concerns**: Models, strategies, quiz engine, and CLI are separate modules
- **Type Safety**: Full type hints throughout the codebase
- **Testability**: All components are designed for easy unit testing with dependency injection

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure everything passes
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is open source and available under the MIT License.

## Sample Flashcards

The repository includes a sample set of 15 common server acronyms in `data/server_acronyms.json`:

- DNS, HTTP, HTTPS, SSH, FTP
- SMTP, API, REST, TCP, UDP
- IP, VPN, CDN, SQL, CORS

Feel free to create your own flashcard files for different topics!