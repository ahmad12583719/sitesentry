from backend.scoring import score_findings


def test_scoring_applies_only_open_findings():
    result = score_findings([
        {"severity": "critical", "status": "finding"},
        {"severity": "medium", "status": "finding"},
        {"severity": "high", "status": "pass"},
    ])
    assert result["score"] == 62
    assert result["grade"] == "D"
    assert result["open_findings"] == 2
    assert result["passed_checks"] == 1


def test_scoring_never_drops_below_zero():
    result = score_findings([{"severity": "critical", "status": "finding"}] * 4)
    assert result["score"] == 0
    assert result["grade"] == "F"
