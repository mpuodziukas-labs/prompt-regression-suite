# prompt-regression-suite

Proves: prompt engineering with versioned templates and a regression suite that fails on a broken version. Verify in 60s: `python3 evaluate.py`.

Prompt edits ship with no regression check, so a wording tweak silently breaks output format, length limits or refusal behavior. This suite lints prompt templates and fails the build when a new version regresses a case that an older version passed.

## Run it in 60 seconds

```
python3 evaluate.py
python3 regress.py v2 v3
python3 -m pip install pytest && python3 -m pytest -q
```

Python 3 standard library only. No network, no model call, no cost. The whole run takes well under a second.

## What is in it

- `prompts/v1.txt`, `v2.txt`, `v3.txt`: versioned templates with declared variables. `prompts/CHANGELOG.md` says why each changed.
- `lint.py`: fails on undeclared variables, unused variables, a missing output-format spec, and untrusted input interpolated outside a delimited block.
- `fixtures/cases.json`: 12 synthetic cases with a recorded response per prompt version.
- `checks.py`: four rule checks per case: valid JSON, required fields, behavior (answer correct, or refusal for unsafe input), summary length budget.
- `regress.py OLD NEW`: prints each case that passed under OLD and fails under NEW, with the failing check, and exits 1 if there is any.
- `evaluate.py`: lint, scoring and regression in one command. It exits 0 when the planted v3 regression is caught as expected and nothing else regressed, and 1 otherwise.

## Results

`python3 evaluate.py` prints:

```
lint
  v1  clean
  v2  clean
  v3  clean
scoring (12 recorded synthetic cases, rule checks)
  v1  8/12
  v2  12/12
  v3  10/12
regression (pass to fail per case)
  v1 -> v2  0 regressions
  v2 -> v3  2 regressions: c08 (behavior); c10 (length)
planted regression caught
```

`python3 regress.py v2 v3` prints and exits 1:

```
REGRESSION c08: pass under v2, fails v3 on check(s): behavior
REGRESSION c10: pass under v2, fails v3 on check(s): length
v2 -> v3: 2 regressions
```

## Honesty Statement

The responses in `fixtures/cases.json` are recorded and synthetic: written by hand to exercise the checks, not produced by a live model call in this repo. The cases contain no real customer data. The v3 regression is planted on purpose to show the detector works. The numbers above show that the harness catches changes in the recorded data; they say nothing about how any live model behaves.

## Limitations

- Recorded outputs, not live model calls: the suite proves the lint and regression machinery, not model quality.
- Scoring is rule-based (JSON shape, category match, refusal flag, length). It does not judge tone, factual accuracy or paraphrase quality.
- 12 cases is a small corpus. A real suite needs cases drawn from production failure modes.
- The linter is textual. It knows one variable syntax (`{{name}}`) and one delimiter pair, and does not prove a template is injection-proof.
