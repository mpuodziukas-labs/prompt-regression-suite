# Prompt changelog

Why each version changed. Newest last.

## v1

Baseline. Classifies a support ticket into a category with a one-sentence summary. The ticket text is
interpolated only inside the untrusted block. Gap found in review: no refusal path, no length limit,
and the output format did not require a `refused` field.

## v2

Adds the `max_chars` variable to cap the summary, an explicit refusal rule with a `refused` field, and the
instruction to treat the block as data. Fixes the recorded failures where unsafe tickets were answered and
where the reply was wrapped in prose.

## v3

Shortened to cut prompt length. Drops the data-only instruction, the explicit refusal conditions and the
summary length cap. The template still lints clean, but the recorded outputs show two cases that passed
under v2 now fail (see `python3 regress.py v2 v3`). Kept in the repo as the planted regression the
suite must catch.
