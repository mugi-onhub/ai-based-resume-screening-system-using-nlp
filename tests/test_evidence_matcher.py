import pytest
from src.evidence_matcher import extract_skill_evidence


def test_extract_skill_evidence_finds_verbatim_quote():
    resume_text = """
    Jane Doe
    Software Developer
    Experience:
    - Developed a real-time analytics dashboard in Python and SQL using FastAPI.
    - Deployed Docker containers to AWS EKS cluster.
    """
    evidence = extract_skill_evidence(resume_text, {"python", "docker", "kubernetes"})
    
    assert evidence["python"]["status"] == "Strong Match"
    assert "Developed a real-time analytics dashboard in Python and SQL" in evidence["python"]["evidence"]
    
    assert evidence["docker"]["status"] == "Strong Match"
    assert "Deployed Docker containers" in evidence["docker"]["evidence"]
    
    assert evidence["kubernetes"]["status"] == "Missing"
    assert "No mention" in evidence["kubernetes"]["evidence"]


def test_extract_skill_evidence_empty_resume():
    evidence = extract_skill_evidence("", {"python"})
    assert evidence["python"]["status"] == "Missing"
