# Usage Guide

## Basic Run

After installation and API key setup, ask a research question:

```bash
research-summarizer-agent "How does renewable energy affect grid reliability?"
```

The program prints each stage:

1. Planner output
2. Research answers
3. Summary generation
4. Evaluation scores
5. Final summary

## Interactive Mode

Run without arguments to enter a question when prompted:

```bash
research-summarizer-agent
```

## Model Settings

The application reads these optional environment variables:

```bash
set GEMINI_MODEL=gemini-2.5-flash
set GEMINI_TEMPERATURE=0.3
set GEMINI_MAX_OUTPUT_TOKENS=4096
```

## Troubleshooting

If you see `Missing API key`, set either `GOOGLE_API_KEY` or `GEMINI_API_KEY`.

If JSON parsing fails, rerun the request. The prompts ask the model for strict JSON, but
model output can occasionally include extra text.
