"""One command: lint all templates, score recorded responses, check regressions between versions."""
import sys

import checks
import lint
import regress

VERSIONS = ["v1", "v2", "v3"]


def run():
    data = checks.load()
    n = len(data["cases"])
    ok = True
    out = ["lint"]
    lres = lint.lint_all()
    ok &= sorted(lres) == VERSIONS and not any(lres.values())
    out += [f"  {v}  {'clean' if not lres.get(v) else 'RED'}" for v in VERSIONS]
    out.append(f"scoring ({n} recorded synthetic cases, rule checks)")
    for v in VERSIONS:
        s = checks.score(v)
        out.append(f"  {v}  {sum(1 for f in s.values() if not f)}/{n}")
    out.append("regression (pass to fail per case)")
    for old, new in zip(VERSIONS, VERSIONS[1:]):
        reg = regress.regressions(old, new)
        want = data["planted_regressions"].get(f"{old}->{new}", [])
        found = [c for c, _ in reg]
        ok &= found == want
        detail = "; ".join(f"{c} ({', '.join(b)})" for c, b in reg)
        out.append(f"  {old} -> {new}  {len(reg)} regressions" + (f": {detail}" if reg else ""))
    out.append("planted regression caught" if ok else "RED: detector or lint did not match expectations")
    return "\n".join(out), bool(ok)


def results():
    return run()[0]


if __name__ == "__main__":
    text, ok = run()
    print(text)
    sys.exit(0 if ok else 1)
