import pytest
from src.what_if_engine import simulate_what_if


def test_what_if_reranks_candidates_when_requirement_added():
    cand_a = {
        "name": "Candidate A (Has Python only)",
        "rank": 1,
        "job_fit_score": 80.0,
        "candidate_skills": {"python"},
        "all_required": {"python"},
        "experience": {"relevant_experience_years": 3.0},
        "projects": [{"relevance_score": 80.0}],
        "breakdown": {"nlp_ensemble": 80.0},
        "raw_text": "Python engineer with 3 years experience.",
    }
    cand_b = {
        "name": "Candidate B (Has Python and AWS)",
        "rank": 2,
        "job_fit_score": 75.0,
        "candidate_skills": {"python", "aws"},
        "all_required": {"python"},
        "experience": {"relevant_experience_years": 3.0},
        "projects": [{"relevance_score": 80.0}],
        "breakdown": {"nlp_ensemble": 75.0},
        "raw_text": "Python and AWS engineer.",
    }

    # Now make AWS mandatory
    results = simulate_what_if(
        baseline_candidates=[cand_a, cand_b],
        new_required_skills={"python", "aws"},
        new_preferred_skills=set(),
        new_min_exp_years=3.0,
    )

    # Candidate B should now be #1 because they have AWS
    top_cand = results[0]
    assert top_cand["name"] == cand_b["name"]
    assert top_cand["after_rank"] == 1
    assert "Possesses newly required skill(s): aws" in top_cand["delta_explanation"]
