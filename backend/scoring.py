"""Fixed and documented SiteSentry grade calculation."""

from __future__ import annotations

from collections import Counter
from typing import Any


PENALTIES = {"critical": 30, "high": 15, "medium": 8, "low": 3, "info": 0}
GRADE_THRESHOLDS: tuple[tuple[int, str], ...] = ((90, "A"), (80, "B"), (70, "C"), (55, "D"), (40, "E"), (0, "F"))


def score_findings(findings: list[dict[str, Any]]) -> dict[str, Any]:
    """Start at 100, subtract the fixed severity weight for every open finding."""

    open_findings = [finding for finding in findings if finding.get("status") != "pass"]
    counts = Counter(finding.get("severity", "info") for finding in findings)
    penalty = sum(PENALTIES.get(finding.get("severity", "info"), 0) for finding in open_findings)
    score = max(0, 100 - penalty)
    grade = next(letter for threshold, letter in GRADE_THRESHOLDS if score >= threshold)
    return {
        "score": score,
        "grade": grade,
        "penalty": penalty,
        "summary": {severity: counts.get(severity, 0) for severity in PENALTIES},
        "open_findings": len(open_findings),
        "passed_checks": sum(1 for finding in findings if finding.get("status") == "pass"),
    }
