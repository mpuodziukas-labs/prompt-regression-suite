"""Static linter for prompt templates in prompts/. Stdlib only."""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent
VAR = re.compile(r"\{\{\s*(\w+)\s*\}\}")
BEGIN, END = "[[BEGIN UNTRUSTED]]", "[[END UNTRUSTED]]"


def template_paths():
    return sorted((ROOT / "prompts").glob("v*.txt"))


def _split(text):
    m = re.match(r"---\n(.*?)\n---\n(.*)\Z", text, re.S)
    if not m:
        return None, text
    hdr = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        hdr[k.strip()] = v.strip()
    return hdr, m.group(2)


def _names(s):
    return {x.strip() for x in s.split(",") if x.strip()}


def lint_text(text):
    hdr, body = _split(text)
    if hdr is None:
        return ["missing header"]
    errs = []
    declared, untrusted = _names(hdr.get("vars", "")), _names(hdr.get("untrusted", ""))
    used = set(VAR.findall(body))
    errs += [f"undeclared variable: {v}" for v in sorted(used - declared)]
    errs += [f"unused variable: {v}" for v in sorted(declared - used)]
    errs += [f"untrusted variable not declared in vars: {v}" for v in sorted(untrusted - declared)]
    if not any(l.startswith("OUTPUT FORMAT:") and "JSON" in l for l in body.splitlines()):
        errs.append("missing output format spec (a line starting 'OUTPUT FORMAT:' that names JSON)")
    inside = False
    for n, line in enumerate(body.splitlines(), 1):
        s = line.strip()
        if s == BEGIN:
            errs += ["nested untrusted block"] if inside else []
            inside = True
        elif s == END:
            errs += [] if inside else ["end marker without begin"]
            inside = False
        elif not inside:
            errs += [f"untrusted variable outside delimited block, body line {n}: {v}"
                     for v in sorted(set(VAR.findall(line)) & untrusted)]
    if inside:
        errs.append("unclosed untrusted block")
    return errs


def lint_all():
    return {p.stem: lint_text(p.read_text()) for p in template_paths()}


if __name__ == "__main__":
    res = lint_all()
    for k, errs in res.items():
        print(k, "clean" if not errs else "; ".join(errs))
    sys.exit(1 if not res or any(res.values()) else 0)
