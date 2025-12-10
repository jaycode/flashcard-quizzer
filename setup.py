"""Setup configuration for flashcard-quizzer package."""

from setuptools import setup, find_packages

setup(
    name="flashcard-quizzer",
    version="1.0.0",
    description="A lightweight terminal tool to help new hires memorize server acronyms",
    author="Flashcard Quizzer Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "flashcard-quiz=flashcard_quizzer.cli:main",
        ],
    },
)
