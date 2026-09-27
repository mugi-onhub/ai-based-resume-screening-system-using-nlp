import pytest
from src.blind_screening import anonymize_resume


def test_anonymize_resume_redacts_pii():
    text = """
    Johnathan Smith
    Email: john.smith@example.com
    Phone: (555) 123-4567
    LinkedIn: linkedin.com/in/johnsmith
    Summary: He has 4 years experience in Python and SQL.
    """
    anon_text, alias = anonymize_resume(text, 1)
    
    assert "john.smith@example.com" not in anon_text
    assert "[REDACTED EMAIL]" in anon_text
    assert "(555) 123-4567" not in anon_text
    assert "[REDACTED PHONE]" in anon_text
    assert "linkedin.com/in/johnsmith" not in anon_text
    assert "Candidate #1" in alias


def test_anonymize_resume_empty_input():
    anon_text, alias = anonymize_resume("", 5)
    assert anon_text == ""
    assert alias == "Candidate #5"
