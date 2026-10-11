"""Compare two prompt versions per case. Exit 1 if any case passed under OLD and fails under NEW.
usage: python3 regress.py OLD NEW   (example: python3 regress.py v2 v3)"""
import sys

import checks


def regressions(old, new):
    a, b = checks.score(old), checks.score(new)
    return [(cid, b[cid]) for cid in a if not a[cid] and b[cid]]


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    versions = set(checks.load()["cases"][0]["recorded"])
    if not set(argv) <= versions:
        print(f"unknown version in {argv}; known: {sorted(versions)}")
        return 2
    reg = regressions(*argv)
    for cid, bad in reg:
        print(f"REGRESSION {cid}: pass under {argv[0]}, fails {argv[1]} on check(s): {', '.join(bad)}")
    print(f"{argv[0]} -> {argv[1]}: {len(reg)} regressions")
    return 1 if reg else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
