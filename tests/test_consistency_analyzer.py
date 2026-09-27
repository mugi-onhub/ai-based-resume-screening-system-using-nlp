import pytest
from src.consistency_analyzer import analyze_consistency


def test_analyze_consistency_detects_timeline_overlap():
    timeline_entries = [
        {"start": 2018, "end": 2022, "duration_years": 4.0, "context": "Company A"},
        {"start": 2019, "end": 2023, "duration_years": 4.0, "context": "Company B"},
    ]
    result = analyze_consistency("Sample text", {"python"}, timeline_entries)
    assert result["has_warnings"] is True
    assert any("Overlapping" in f for f in result["flags"])


def test_analyze_consistency_clean_timeline():
    timeline_entries = [
        {"start": 2018, "end": 2020, "duration_years": 2.0, "context": "Company A"},
        {"start": 2020, "end": 2023, "duration_years": 3.0, "context": "Company B"},
    ]
    result = analyze_consistency("Developed software in Python.", {"python"}, timeline_entries)
    assert result["consistency_score"] >= 90.0
