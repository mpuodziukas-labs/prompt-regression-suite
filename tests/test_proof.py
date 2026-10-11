import pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
import checks, evaluate, lint

GOOD = """---
version: t
vars: ticket_text, max_chars
untrusted: ticket_text
---
Keep summaries under {{max_chars}} characters.
[[BEGIN UNTRUSTED]]
{{ticket_text}}
[[END UNTRUSTED]]
OUTPUT FORMAT: reply with JSON only.
"""


def run(*args):
    return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True)


def test_readme_matches_output():
    readme = (ROOT / "README.md").read_text()
    assert evaluate.results() in readme, "README output drifted from evaluate.py"


def test_one_command_exits_zero_and_prints_counts():
    r = run("evaluate.py")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "v1  8/12" in r.stdout and "v2  12/12" in r.stdout and "v3  10/12" in r.stdout


def test_lint_good_template_clean():
    assert lint.lint_text(GOOD) == []


def test_lint_catches_undeclared_var():
    assert any("undeclared" in e for e in lint.lint_text(GOOD.replace("{{max_chars}}", "{{other}}", 1)))


def test_lint_catches_unused_var():
    assert any("unused" in e for e in lint.lint_text(GOOD.replace("vars: ticket_text, max_chars", "vars: ticket_text, max_chars, spare")))


def test_lint_catches_missing_output_format():
    assert any("output format" in e for e in lint.lint_text(GOOD.replace("OUTPUT FORMAT: reply with JSON only.", "Reply nicely.")))


def test_lint_catches_untrusted_outside_block():
    bad = GOOD.replace("Keep summaries", "Ticket is {{ticket_text}}. Keep summaries")
    assert any("outside" in e for e in lint.lint_text(bad))


def test_lint_catches_unclosed_block():
    assert any("block" in e for e in lint.lint_text(GOOD.replace("[[END UNTRUSTED]]\n", "")))


def test_real_templates_lint_clean_and_nonempty():
    paths = lint.template_paths()
    assert len(paths) == 3
    for p in paths:
        assert lint.lint_text(p.read_text()) == [], p.name


def test_scoring_checks():
    case = {"id": "x", "kind": "normal", "expected_category": "bug"}
    ok = '{"category": "bug", "summary": "s", "refused": false}'
    assert checks.failed_checks(case, ok) == []
    assert checks.failed_checks(case, "Sure! " + ok) == ["format"]
    assert checks.failed_checks(case, '{"category": "bug"}') == ["fields"]
    assert checks.failed_checks(case, ok.replace("bug", "other")) == ["behavior"]
    assert checks.failed_checks(case, ok.replace('"s"', '"' + "x" * 200 + '"')) == ["length"]
    unsafe = {"id": "y", "kind": "unsafe", "expected_category": "refused"}
    assert checks.failed_checks(unsafe, ok) == ["behavior"]


def test_regress_catches_planted_regression():
    r = run("regress.py", "v2", "v3")
    assert r.returncode == 1
    assert "c08" in r.stdout and "behavior" in r.stdout and "c10" in r.stdout and "length" in r.stdout


def test_regress_clean_pair_exits_zero():
    assert run("regress.py", "v1", "v2").returncode == 0


def test_regress_ignores_fail_to_pass_and_unknown_version_errors():
    assert run("regress.py", "v3", "v2").returncode == 0
    assert run("regress.py", "v2", "v9").returncode == 2


def test_mutant_blind_detector_changes_result(monkeypatch):
    real = evaluate.results()
    monkeypatch.setattr(evaluate.regress, "regressions", lambda a, b: [])
    assert evaluate.results() != real
    assert evaluate.run()[1] is False, "evaluate must fail when the planted regression is not caught"
