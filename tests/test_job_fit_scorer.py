import pytest
from src.job_fit_scorer import calculate_job_fit_score, calculate_education_score


def test_calculate_job_fit_score_perfect_candidate():
    req_skills = {"python", "sql", "scikit-learn"}
    pref_skills = {"docker", "aws"}
    cand_skills = {"python", "sql", "scikit-learn", "docker", "aws", "git"}
    
    result = calculate_job_fit_score(
        required_skills=req_skills,
        preferred_skills=pref_skills,
        candidate_skills=cand_skills,
        candidate_exp_years=4.0,
        min_exp_years=3.0,
        project_scores=[90.0, 85.0],
        nlp_ensemble_score=88.0,
        resume_text="Master of Science in Computer Science with extensive background in Python.",
    )
    
    assert result["job_fit_score"] >= 80.0
    assert result["match_level"] == "Strong Match"
    assert result["breakdown"]["required_skill_coverage"] == 100.0
    assert result["breakdown"]["preferred_skill_coverage"] == 100.0
    assert "Job Fit" in result["formula"]


def test_calculate_job_fit_score_partial_candidate():
    req_skills = {"python", "sql", "scikit-learn", "pytorch"}
    pref_skills = {"docker", "aws"}
    cand_skills = {"python"}  # only 1 of 4 required
    
    result = calculate_job_fit_score(
        required_skills=req_skills,
        preferred_skills=pref_skills,
        candidate_skills=cand_skills,
        candidate_exp_years=0.5,
        min_exp_years=3.0,
        project_scores=[40.0],
        nlp_ensemble_score=45.0,
        resume_text="High school diploma.",
    )
    
    assert result["job_fit_score"] < 65.0
    assert result["breakdown"]["required_skill_coverage"] == 25.0


def test_education_scoring():
    assert calculate_education_score("Ph.D in AI") == 100.0
    assert calculate_education_score("Master of Science") == 90.0
    assert calculate_education_score("Bachelor of Technology") == 80.0
