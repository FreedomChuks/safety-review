# Safety Review

A small, local tool for recording human-reviewed evaluations of AI responses. Define a case, capture the response, judge it against an explicit criterion, and record uncertainty.

## Quick start

Requires Python 3.9 or later. No dependencies or API key are required.

```sh
python3 safety_review.py template examples/starter_cases.jsonl review.csv
```

For each row, send the prompt to the assistant you want to examine, paste its response into `response`, and add a human verdict (`pass`, `fail`, or `uncertain`) and a short explanation in `notes`. Save the CSV, then run:

```sh
python3 safety_review.py summary review.csv
```

The tool refuses to overwrite an existing review file. Keep a separate CSV for each model version or run, and record model settings, date and relevant context. The prompts are illustrative synthetic examples, not measured results. A blank verdict counts as unreviewed, never as a pass.

## Add your own cases

Each line in the JSONL file is a JSON object with four required non-empty strings: `id` (unique), `category`, `prompt`, and `criterion`. Write a criterion specific enough for a human reviewer to assess. Include ordinary benign requests as well as safety-relevant cases to identify unnecessary refusals.

## Scope and limitations

This tool does not call models, judge responses automatically, or establish that a model is safe. Human ratings can be inconsistent; a small hand-written test set is not representative. Use blinded independent reviewers, track disagreement, include adversarial and realistic examples, and expand coverage before drawing conclusions. Do not paste confidential information into third-party services without permission; review CSV files can contain sensitive model outputs.

Inspired by the general practice of defining cases and graders described in [Anthropic's guide to agent evaluations](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).
