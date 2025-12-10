# Final Project Report: Using AI in Development

## Overview

This report explains how AI was used throughout the development of the flashcard-quizzer project, reflects on what I learned about working with AI tools, and highlights practical takeaways that shaped the codebase and workflow. The content is grounded in the project's commit history, tests, and the documented AI prompts and reviews in `docs/ai_edit_logs.md`.

## How AI Was Used Across the Project

AI played three roles throughout development: requirements clarification and planning, code generation and refactoring, and quality assurance/tooling.

1) Requirements Clarification and Planning
- Early on, AI helped transform a high-level idea into a detailed specification. The first review (Follow-up #1) articulated functional requirements (data ingestion, quiz loop, modes, session stats) and technical requirements (modular architecture, Strategy Pattern, type hints, tests and coverage). This clarified deliverables and provided a clear definition of done.
- The prompt guidance ensured the app was not a monolithic script but divided by responsibility. This led to the module layout under `src/flashcard_quizzer/` and a CLI entry in `main.py`.

2) Architecture and Design Decisions
- Strategy Pattern: AI emphasized using Strategy for quiz modes (Sequential, Random, Adaptive). This decoupled selection logic from the quiz engine and made adding new modes straightforward. It influenced the `strategies.py` design and the factory that resolves a user's `--mode` selection.
- Factory Pattern: From Follow-up #2, AI guided the introduction of a QuizMode factory to choose the implementation based on flags, improving extensibility and discoverability.
- Modular Structure: AI reinforced separation of concerns, prompting the split into `cli.py`, `quiz.py`, `models.py`, `strategies.py`, and a `utils/file_handler.py`. This made testing easier and improved cohesion.

3) Implementation and Code Generation
- Data loading and validation: AI recommended supporting both array and object JSON formats and producing human-friendly errors instead of raw tracebacks. The code in `utils/file_handler.py` and the data loader path respects these constraints, gracefully handling malformed input.
- CLI: AI's guidance ensured `argparse`-based flags (`--mode`, `--file`, `--stats`, `--help`) are implemented. It also called out colored output and graceful exits (e.g., processing ctrl+c or "exit"), improving usability.
- Adaptive Mode: AI repeatedly nudged that Adaptive should prioritize previously incorrect answers. This required tracking per-card correctness and revisiting missed cards more often within a session. Tests were aligned to verify that behavior.

4) Testing and Coverage
- AI helped define test scenarios matching real usage: loader tests for valid/invalid formats, factory and mode behavior tests, and an integration test simulating a full quiz session. The target of >80% coverage prevented codepaths from being left untested.
- Importantly, AI advised not only unit tests but also integration tests, catching configuration and wiring mistakes between CLI, strategies, and loader.

5) Tooling and Quality Assurance
- Follow-up #3 stressed installing and running `pytest`, `black`, and `mypy`. This improved code quality on multiple axes: correctness, formatting consistency, and type safety. AI also nudged a quick verification path: `python main.py --help` and `python main.py --mode sequential --file data/glossary.json`.
- The addition of static typing allowed AI to reason more precisely during code suggestions and reduced runtime surprises.

6) Content and Domain Feedback
- Follow-up #4 surfaced a domain nuance: some glossary items (like "Algorithm") are not acronyms, so asking "What does 'Algorithm' stand for?" is semantically incorrect. AI flagged the issue and recommended making questions literate and meaningful. That feedback loop made the dataset more coherent and the quiz experience more credible.

## What I Learned About Working With AI Tools

1) Provide Context, Get Better Outcomes
- Detailed prompts produce stronger results. The early prompt in Follow-up #1 included functional/technical requirements, design patterns, and testing goals. With that context, AI proposed modular architecture and precise implementation choices that aligned well with future extensibility.
- Referencing actual files and paths (e.g., `src/flashcard_quizzer/strategies.py`) helped AI provide changes that fit the structure instead of generic snippets.

2) Iterate with Concrete Checks
- Each follow-up was anchored by tangible checks: running `pytest`, invoking CLI help, and trying real commands with real data files. These checks prevented drifting into theoretical solutions. AI responded better to specific failures (e.g., file not found) than to vague issues.

3) Use AI for Architecture Patterns, Not Just Code Blocks
- AI shines when shaping system-level decisions (Strategy/Factory patterns, module boundaries, separation of concerns). These choices have long-term leverage and are areas where AI's pattern knowledge amplifies productivity.
- When asking AI to write code, I learned to request abstractions with clear contracts and types, then iterate on implementations with tests. This kept AI's output aligned with the architecture.

4) Keep Human Judgment on Domain Semantics
- AI can write logical code but might miss domain subtleties (the acronym vs. non-acronym distinction). Human review is essential to validate not only correctness but also whether the product makes sense to users. Combining AI's speed with domain judgment yields better outcomes.

5) Make Tests the Source of Truth
- The test suite acted as a constant guardrail. When AI proposed changes, tests caught regressions, and coverage targets forced thought about edge cases (invalid JSON, missing fields, adaptive weighting). AI was more reliable when guided by tests that define expected behaviors.

6) Embrace Tooling for Consistency and Safety
- Adding `black` and `mypy` made AI-assisted code easier to maintain. Formatting reduces cognitive load and diff noise; typing prevents category errors and clarifies APIs. AI responds well to typed code, proposing more accurate completions and refactors.

7) Be Explicit About Error Handling and UX
- Requiring friendly error messages (instead of tracebacks) helped AI generate code that treats the user respectfully. Likewise, CLI help and colored feedback increased usability. AI was effective when asked to include these UX touches early instead of as afterthoughts.

8) Close the Loop With Data Quality
- The Follow-up #4 experience showed that technical quality is not sufficient; data drives user experience. Updating content to ask meaningful questions required revisiting the dataset and adjusting prompt/response phrasing. AI can assist in finding inconsistencies, but curating the content requires ownership.

## Specific Examples of AI's Impact

- Strategy Mode Implementation: AI guided setting up `QuizMode` as an abstract base class and creating `SequentialMode`, `RandomMode`, and `AdaptiveMode`, then a factory to instantiate them based on CLI inputs. That design choice decoupled the selection algorithm from the quiz loop, and tests assert correct factory behavior.
- Robust Data Loader: AI recommended supporting both `[ { front, back } ]` and `{ cards: [...] }` JSON structures, plus validating fields and catching errors. Tests cover valid loads and error cases without raw tracebacks. This improved real-world reliability when swapping datasets.
- CLI Surface: AI ensured `argparse` exposed descriptive flags with `--help` printing usage, and made outputs more readable with color and graceful exits. These touches made the tool feel professional and approachable for new hires.
- Adaptive Prioritization: AI emphasized re-asking missed cards, which improved learning efficiency. Tests verify that missed items are more likely to be presented again, and session stats report accuracy and missed terms.
- Quality Gates: AI's insistence on `pytest`, `black`, and `mypy` added friction in the right places: code formatting consistency, type correctness, and stable behavior. This created a pipeline that supported rapid iteration without degrading code health.
- Content Corrections: By flagging ill-posed questions (non-acronyms), AI helped steer content revisions that make quiz prompts semantically sound. This was an important reminder that AI can spot patterns in prompts that humans might gloss over during implementation.

## Challenges and How They Were Addressed

- File Not Found Errors: As noted in Follow-up #3, `python main.py --mode sequential --file data/glossary.json` initially failed. AI helped identify path handling and ensured that `main.py` acts as the canonical entry point with sensible defaults and clear errors.
- Balancing Flexibility with Simplicity: Strategy + Factory patterns provide extensibility but require discipline in passing state and keeping interfaces tight. Tests and type hints kept implementations aligned.
- Dataset Semantics: Ensuring acronyms vs. general terms were treated appropriately required manual content curation. AI flagged the issue; human review corrected and standardized wording.

## Key Takeaways for Future Projects

- Start with a strong spec prompt. Include architecture patterns, testing requirements, and quality tools up front. AI operates best with constraints and goals.
- Treat AI as a partner in design and scaffolding. Let tests arbitrate correctness, and iteratively refine implementations.
- Maintain developer ergonomics. Formatting and typing make AI suggestions cleaner and more reliable; friendly CLI and error messages improve user trust.
- Keep domain sense in the loop. Use AI to detect inconsistencies, but retain ownership of content and product semantics.
- Close the loop with continuous verification. Regularly run `pytest`, `mypy`, and the CLI with real data files to validate end-to-end behavior.

## Conclusion

AI significantly accelerated the development of flashcard-quizzer by clarifying requirements, informing architectural choices, scaffolding implementations, and reinforcing quality gates. The iterative loop—prompt, implement, test, refine—kept progress steady while controlling for regressions. The project demonstrates how AI can be leveraged not only to write code but also to shape the structure and standards of a maintainable tool. Perhaps most importantly, I learned to integrate AI-driven speed with human judgment about domain semantics and user experience. That pairing produced a terminal-based quizzer that's modular, testable, and ready to evolve—whether adding spaced repetition or expanding datasets for new onboarding contexts.
