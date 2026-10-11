# prompt-regression-suite

Prompt edits ship with no regression check, so a wording tweak silently breaks output format, length limits or refusal behavior; this suite lints prompt templates and fails the build when a new version regresses a case that an older version passed.

## Run it in 60 seconds

```
python3 -m pip install pytest
python3 evaluate.py
python3 -m pytest -q
```

## Results

| bad caught | good passed |
|---|---|
| 1/1 | 1/1 |

## Honesty Statement

Synthetic data. Not production, not client data.

## Limitations

Small synthetic corpus. Replace before drawing conclusions.
