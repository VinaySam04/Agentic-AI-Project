# Research Summarizer Agent

A command-line multi-agent research summarizer powered by Gemini and LangChain.

The workflow breaks a research question into sub-questions, generates factual answers,
synthesizes a final summary, evaluates the result, and performs a refinement pass when
the evaluation finds gaps.

## Features

- Planner agent creates three focused research sub-questions.
- Researcher agent answers each sub-question.
- Synthesizer agent turns the answers into a coherent summary.
- Evaluator agent scores coverage, accuracy, clarity, and depth.
- Refinement step incorporates evaluator feedback when needed.

## Requirements

- Python 3.10 or newer
- A Google Gemini API key

## Installation

```bash
git clone https://github.com/VinaySam04/Agentic-AI-Project.git
cd Agentic-AI-Project
python -m venv .venv
```

On Windows, activate the virtual environment with:

```bash
.venv\Scripts\activate
```

On macOS or Linux, activate with:

```bash
source .venv/bin/activate
```

Then install the package with development dependencies:

```bash
pip install -e ".[dev]"
```

## Configuration

Create an environment variable with your Gemini API key:

On Windows:
```bash
set GOOGLE_API_KEY=your_api_key_here
```

On macOS or Linux:
```bash
export GOOGLE_API_KEY=your_api_key_here
```

Optional environment variables:

- `GEMINI_MODEL`: defaults to `gemini-2.5-flash`
- `GEMINI_TEMPERATURE`: defaults to `0.3`
- `GEMINI_MAX_OUTPUT_TOKENS`: defaults to `4096`

## Usage

Run the research summarizer:

```bash
research-summarizer-agent
```

The script will prompt you to enter a research question interactively.

Example:
```
Enter research question: What are the main impacts of AI on healthcare?
```

Alternatively, run directly with Python:

```bash
python src/research_summarizer_agent.py
```

## Development

Run tests:

```bash
pytest
```

Run linting:

```bash
ruff check .
```

## Project Structure

```
Agentic-AI-Project/
  src/
    research_summarizer_agent.py
  tests/
    test_parse_json.py
    test_research_summarizer_agent.py
  requirements.txt
  pyproject.toml
  README.md
```

## Notes

The agent relies on the language model for research-style answers. For high-stakes
topics, independently verify the output with trusted sources.

## License

This project is shared for portfolio review only. All rights reserved.
You may view the code, but you may not copy, modify, distribute, or reuse it
without written permission.
