import pytest
from src.job_intelligence import parse_job_description


def test_parse_job_description_splits_required_and_preferred():
    jd_text = """
    Senior Python Engineer
    
    Required Qualifications:
    - 3+ years experience with Python and SQL
    - Hands-on machine learning experience with scikit-learn
    
    Preferred Skills:
    - Experience with Docker and AWS
    - Knowledge of PyTorch
    
    Responsibilities:
    - Build data pipelines and models
    """
    parsed = parse_job_description(jd_text)
    
    assert "python" in parsed["required_skills"]
    assert "sql" in parsed["required_skills"]
    assert "scikit-learn" in parsed["required_skills"]
    assert "docker" in parsed["preferred_skills"]
    assert "aws" in parsed["preferred_skills"]
    assert parsed["min_experience_years"] == 3.0
    assert len(parsed["responsibilities"]) >= 1


def test_parse_job_description_empty_input():
    parsed = parse_job_description("")
    assert parsed["required_skills"] == set()
    assert parsed["preferred_skills"] == set()
    assert parsed["min_experience_years"] == 0.0
