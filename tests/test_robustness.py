import pytest
from src.extractors import safe_extract_text
from src.job_intelligence import parse_job_description
from src.job_fit_scorer import calculate_job_fit_score
from src.comparison import build_comparison_matrix
from src.experience_analyzer import analyze_experience
from src.project_matcher import extract_projects


def test_safe_extract_nonexistent_file():
    text, err = safe_extract_text("nonexistent_path_to_file.pdf")
    assert text is None
    assert err is not None


def test_empty_job_and_resume_scoring():
    parsed = parse_job_description("")
    res = calculate_job_fit_score(
        required_skills=parsed["required_skills"],
        preferred_skills=parsed["preferred_skills"],
        candidate_skills=set(),
        candidate_exp_years=0.0,
        min_exp_years=0.0,
        project_scores=[],
        nlp_ensemble_score=0.0,
        resume_text="",
    )
    assert 0.0 <= res["job_fit_score"] <= 100.0
    assert res["match_level"] in ["Strong Match", "Good Match", "Review", "Low Match"]


def test_candidate_comparison_matrix_empty():
    matrix = build_comparison_matrix([])
    assert matrix["headers"] == []
    assert matrix["rows"] == []


def test_candidate_comparison_matrix_multiple():
    candidates = [
        {
            "name": "Candidate A",
            "job_fit_score": 88.0,
            "match_level": "Strong Match",
            "matched_required": {"python", "sql"},
            "all_required": {"python", "sql", "aws"},
            "breakdown": {"required_skill_coverage": 66.7, "nlp_ensemble": 85.0},
            "experience": {"relevant_experience_years": 4.0, "total_experience_years": 4.0},
            "projects": [{"name": "NLP Pipeline", "relevance_score": 90.0}],
            "insights": {"gaps_required": ["aws"]},
        },
        {
            "name": "Candidate B",
            "job_fit_score": 72.0,
            "match_level": "Good Match",
            "matched_required": {"python"},
            "all_required": {"python", "sql", "aws"},
            "breakdown": {"required_skill_coverage": 33.3, "nlp_ensemble": 70.0},
            "experience": {"relevant_experience_years": 2.0, "total_experience_years": 2.0},
            "projects": [{"name": "Data Dashboard", "relevance_score": 75.0}],
            "insights": {"gaps_required": ["sql", "aws"]},
        },
    ]
    matrix = build_comparison_matrix(candidates)
    assert matrix["headers"] == ["Candidate A", "Candidate B"]
    assert len(matrix["rows"]) >= 5
    assert len(matrix["summary_points"]) >= 1


def test_experience_and_project_robustness():
    exp = analyze_experience("", set())
    assert exp["total_experience_years"] == 0.0
    
    projs = extract_projects("", set())
    assert projs == []
