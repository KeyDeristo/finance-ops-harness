"""Check that rules/jurisdiction.yaml is complete and consistent.

The harness core is jurisdiction-agnostic; this check makes sure the declared
profile actually carries the information agents will rely on (control C-05).

Exposes run(root) -> list of problem strings (empty list = pass).
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

REQUIRED_STRING_FIELDS = [
    "country_name",
    "currency",
    "chart_of_accounts_standard",
    "statutory_export_format",
    "e_invoicing_standard",
]
VALID_CADENCES = {"monthly", "bimonthly", "quarterly", "annual", "none"}
VALID_DEADLINE_FREQUENCIES = VALID_CADENCES | {"on-demand"}


def run(root: Path) -> list[str]:
    path = root / "rules" / "jurisdiction.yaml"
    if not path.is_file():
        return ["rules/jurisdiction.yaml is missing"]

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [f"rules/jurisdiction.yaml is not valid YAML: {exc}"]

    if not isinstance(data, dict):
        return ["rules/jurisdiction.yaml must be a mapping"]

    problems: list[str] = []

    active = data.get("active_profile")
    profiles = data.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        return ["jurisdiction.yaml: 'profiles' must be a non-empty mapping"]
    if not active or not isinstance(active, str):
        return ["jurisdiction.yaml: 'active_profile' must be a non-empty string"]
    if active == "_TEMPLATE":
        return ["jurisdiction.yaml: active_profile is '_TEMPLATE' — select a "
                "real profile (the template block is a scaffold, not a profile)"]
    if active not in profiles:
        return [f"jurisdiction.yaml: active_profile {active!r} not found in "
                f"profiles ({', '.join(sorted(profiles))})"]

    profile = profiles[active]
    if not isinstance(profile, dict):
        return [f"jurisdiction.yaml: profile {active!r} must be a mapping"]
    label = f"profile {active!r}"

    for field in REQUIRED_STRING_FIELDS:
        value = profile.get(field)
        if not isinstance(value, str) or not value.strip():
            problems.append(f"{label}: {field!r} must be a non-empty string")

    vat = profile.get("vat")
    if not isinstance(vat, dict):
        problems.append(f"{label}: 'vat' section missing or not a mapping")
    else:
        cadence = vat.get("filing_cadence")
        if cadence not in VALID_CADENCES:
            problems.append(
                f"{label}: vat.filing_cadence {cadence!r} invalid "
                f"(expected one of: {', '.join(sorted(VALID_CADENCES))})")

    retention = profile.get("retention_years")
    if not isinstance(retention, int) or isinstance(retention, bool) or retention <= 0:
        problems.append(f"{label}: 'retention_years' must be a positive integer")

    deadlines = profile.get("statutory_reporting_deadlines")
    if not isinstance(deadlines, list) or not deadlines:
        problems.append(f"{label}: 'statutory_reporting_deadlines' must be a "
                        f"non-empty list")
    else:
        for i, entry in enumerate(deadlines):
            if not isinstance(entry, dict):
                problems.append(f"{label}: deadline[{i}] is not a mapping")
                continue
            for field in ("name", "frequency", "deadline_rule"):
                value = entry.get(field)
                if not isinstance(value, str) or not value.strip():
                    problems.append(
                        f"{label}: deadline[{i}] ({entry.get('name', '?')}): "
                        f"{field!r} must be a non-empty string")
            freq = entry.get("frequency")
            if isinstance(freq, str) and freq and freq not in VALID_DEADLINE_FREQUENCIES:
                problems.append(
                    f"{label}: deadline[{i}] frequency {freq!r} invalid "
                    f"(expected one of: "
                    f"{', '.join(sorted(VALID_DEADLINE_FREQUENCIES))})")

    return problems


def main() -> int:
    problems = run(Path(__file__).resolve().parent.parent)
    for p in problems:
        print(f"  FAIL {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
