#!/usr/bin/env python3
"""
Check a Model Trust Record before it is signed or used to gate a deployment.

Two passes:
  1. Shape: the record validates against templates/model-trust-record.schema.json.
  2. Invariants: the rules in FRAMEWORK.md ("How the per-layer results become the overall
     verdict" and the policy-engine invariants) that a JSON Schema cannot express.

Like the policy in FRAMEWORK.md, this checks consistency, not truth: it cannot tell whether
a layer that says "conditional" should have said "stop".

Usage:
  python3 tools/validate_record.py templates/model-trust-record.bedrock-example.json
  python3 tools/validate_record.py --example templates/model-trust-record.fine-tuned-example.json

Needs: python3 -m pip install jsonschema
Exit codes: 0 valid, 1 invalid, 2 could not run.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys

SCHEMA = pathlib.Path(__file__).resolve().parent.parent / "templates" / "model-trust-record.schema.json"
LAYERS = ["L0", "L1", "L2", "L3", "L4", "L5"]
PLACEHOLDER = re.compile(r"<[^<>]+>")


def closed_layers(guardrails: list) -> set[str]:
    """Layers whose findings some guardrail says it closes (IDs like L4-F1 in `closes`)."""
    found = set()
    for g in guardrails:
        found.update(re.findall(r"\b(L[0-5])-F\d+\b", str(g.get("closes", ""))))
    return found


def check_invariants(r: dict, example: bool) -> list[str]:
    errs = []
    layers = r.get("layers", {})
    missing = [layer for layer in LAYERS if layer not in layers]
    if missing:
        errs.append(f"layers missing a result: {', '.join(missing)}")

    stops = [layer for layer in LAYERS if layers.get(layer) == "stop"]
    conds = [layer for layer in LAYERS if layers.get(layer) == "conditional"]
    gov_conds = [layer for layer in conds if layer in ("L0", "L1", "L2")]
    tech_conds = [layer for layer in conds if layer in ("L3", "L4")]
    closed = closed_layers(r.get("guardrails", []))
    unclosed = [layer for layer in tech_conds if layer not in closed]
    overall = r.get("overall")

    if gov_conds:
        errs.append(f"governance conditional(s) {', '.join(gov_conds)} must be resolved to pass "
                    "(fix landed) or stop before the record is signed")
    if layers.get("L5") == "conditional":
        errs.append("L5 cannot be conditional: it either contains the findings (pass) or not (stop)")

    if stops or unclosed:
        if overall != "deny":
            why = f"stop at {', '.join(stops)}" if stops else f"no guardrail closes a finding from {', '.join(unclosed)}"
            errs.append(f"overall must be 'deny' ({why}), found {overall!r}")
    elif tech_conds:
        if overall not in ("allow_with_controls", "restrict"):
            errs.append(f"conditional layer(s) {', '.join(tech_conds)} closed at L5 give "
                        f"'allow_with_controls' or 'restrict', found {overall!r}")
    elif overall not in ("allow", "restrict"):
        errs.append(f"every layer passed, so overall should be 'allow', found {overall!r}")

    if overall == "restrict" and not r.get("narrowed_use"):
        errs.append("overall 'restrict' needs the narrower use in narrowed_use")
    if overall != "restrict" and r.get("narrowed_use"):
        errs.append("narrowed_use is set but overall is not 'restrict'")

    if str(r.get("version", "")).strip().lower() in ("", "latest"):
        errs.append("version must pin an exact served version or file hash, not 'latest'")
    if not r.get("evidence"):
        errs.append("evidence is empty")
    for i, e in enumerate(r.get("evidence", [])):
        if e.get("layer") in ("L3", "L4") and not e.get("tier"):
            errs.append(f"evidence[{i}] is L3/L4 behavioural evidence and needs a tier (T1/T2/T3)")
        if r.get("modified") != "no" and e.get("source") == "vendor's" and e.get("layer") in ("L3", "L4") and e.get("valid"):
            errs.append(f"evidence[{i}]: the model was modified, so inherited vendor behavioural evidence must be marked invalid")

    try:
        expires = dt.date.fromisoformat(str(r.get("expires_date")))
        if expires < dt.date.today() and not example:
            errs.append(f"record expired on {expires.isoformat()}")
    except ValueError:
        errs.append(f"expires_date is not an ISO date: {r.get('expires_date')!r}")

    if r.get("risk_transfer_ref") and r.get("risk_transfer_accepted") is not True:
        errs.append("a risk was transferred but not accepted by the system-review owner")
    if not example:
        sig = str(r.get("record_signature") or "")
        if not sig or PLACEHOLDER.fullmatch(sig):
            errs.append("record_signature is empty: sign the record before using it to gate a deployment")
        placeholders = sorted({m for v in _strings(r) for m in PLACEHOLDER.findall(v)})
        if placeholders:
            errs.append(f"unfilled placeholders: {', '.join(placeholders[:5])}")
    if r.get("rigor") in ("R3", "R4"):
        print("  note: R3/R4 needs an approver independent of the requesting team; "
              "this tool cannot check independence, confirm it by hand")
    return errs


def _strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _strings(v)


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate a Model Trust Record")
    ap.add_argument("records", nargs="+", help="record JSON file(s)")
    ap.add_argument("--example", action="store_true",
                    help="for the shipped examples: skip the signature, placeholder and expiry checks")
    args = ap.parse_args()
    try:
        import jsonschema
    except ImportError:
        print("needs jsonschema: python3 -m pip install jsonschema", file=sys.stderr)
        return 2

    schema = json.loads(SCHEMA.read_text())
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    bad = 0
    for path in args.records:
        record = json.loads(pathlib.Path(path).read_text())
        print(path)
        shape = [f"schema: {'/'.join(map(str, e.path)) or '(root)'}: {e.message}" for e in validator.iter_errors(record)]
        errs = shape + check_invariants(record, args.example)
        for e in errs:
            print(f"  FAIL {e}")
        if errs:
            bad += 1
        else:
            print("  OK")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
