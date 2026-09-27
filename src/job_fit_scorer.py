"""Explainable Job Fit Scorer: Combines multi-dimensional candidate evaluation with Academic NLP ensemble.
Provides transparent, mathematically documented scoring breakdowns.
"""
import re
import numpy as np
from config import JOB_FIT_WEIGHTS, THRESHOLDS


def calculate_education_score(resume_text: str) -> float:
    """Evaluates degree level and STEM alignment."""
    if not resume_text:
        return 50.0
    
    text_lower = resume_text.lower()
    if re.search(r"\b(ph\.?d|doctorate|doctor of philosophy)\b", text_lower):
        return 100.0
    if re.search(r"\b(master|m\.s|m\.tech|msc|mba)\b", text_lower):
        return 90.0
    if re.search(r"\b(bachelor|b\.s|b\.tech|b\.e|bsc|bca)\b", text_lower):
        return 80.0
    if re.search(r"\b(diploma|associate|bootcamp|certificate)\b", text_lower):
        return 70.0
    return 60.0


def calculate_job_fit_score(
    required_skills: set[str],
    preferred_skills: set[str],
    candidate_skills: set[str],
    candidate_exp_years: float,
    min_exp_years: float,
    project_scores: list[float],
    nlp_ensemble_score: float,
    resume_text: str,
    custom_weights: dict | None = None,
) -> dict:
    """
    Computes a comprehensive, explainable Job Fit Score.
    Returns:
      {
        "job_fit_score": float (0-100),
        "match_level": "Strong Match" | "Good Match" | "Review" | "Low Match",
        "breakdown": {
          "required_skill_coverage": float,
          "relevant_experience": float,
          "project_relevance": float,
          "preferred_skill_coverage": float,
          "education_relevance": float,
          "nlp_ensemble": float,
        },
        "formula": str,
      }
    """
    weights = custom_weights or JOB_FIT_WEIGHTS

    # 1. Required Skill Coverage (0-100)
    if not required_skills:
        req_coverage = 85.0
    else:
        matched_req = required_skills & candidate_skills
        req_coverage = round((len(matched_req) / len(required_skills)) * 100.0, 1)

    # 2. Preferred Skill Coverage (0-100)
    if not preferred_skills:
        pref_coverage = 80.0  # neutral default if no preferred skills specified
    else:
        matched_pref = preferred_skills & candidate_skills
        pref_coverage = round((len(matched_pref) / len(preferred_skills)) * 100.0, 1)

    # 3. Relevant Experience Score (0-100)
    if min_exp_years <= 0.0:
        exp_score = 90.0 if candidate_exp_years > 0 else 80.0
    else:
        exp_ratio = candidate_exp_years / min_exp_years
        if exp_ratio >= 1.0:
            # Bonus for exceeding up to 100
            exp_score = min(100.0, 85.0 + (exp_ratio - 1.0) * 15.0)
        else:
            exp_score = max(30.0, exp_ratio * 85.0)
    exp_score = round(exp_score, 1)

    # 4. Project Relevance Score (0-100)
    if project_scores:
        proj_score = round(float(np.mean(project_scores)), 1)
    else:
        proj_score = 65.0

    # 5. Education Relevance Score (0-100)
    edu_score = calculate_education_score(resume_text)

    # 6. Academic NLP Ensemble (0-100)
    nlp_score = round(float(np.clip(nlp_ensemble_score, 0.0, 100.0)), 1)

    # Weighted Sum
    total_w = sum(weights.values())
    w_norm = {k: v / total_w for k, v in weights.items()}

    final_score = (
        w_norm.get("required_skills", 0.35) * req_coverage
        + w_norm.get("relevant_experience", 0.20) * exp_score
        + w_norm.get("project_relevance", 0.15) * proj_score
        + w_norm.get("preferred_skills", 0.10) * pref_coverage
        + w_norm.get("education_relevance", 0.05) * edu_score
        + w_norm.get("nlp_ensemble", 0.15) * nlp_score
    )
    final_score = round(float(np.clip(final_score, 0.0, 100.0)), 1)

    # Determine Match Level
    if final_score >= THRESHOLDS.get("strong", 80):
        match_level = "Strong Match"
    elif final_score >= THRESHOLDS.get("good", 65):
        match_level = "Good Match"
    elif final_score >= THRESHOLDS.get("review", 50):
        match_level = "Review"
    else:
        match_level = "Low Match"

    formula_str = (
        f"Job Fit ({final_score:.1f}) = "
        f"({w_norm.get('required_skills', 0.35):.2f} × {req_coverage:.1f} Req Skills) + "
        f"({w_norm.get('relevant_experience', 0.20):.2f} × {exp_score:.1f} Experience) + "
        f"({w_norm.get('project_relevance', 0.15):.2f} × {proj_score:.1f} Projects) + "
        f"({w_norm.get('preferred_skills', 0.10):.2f} × {pref_coverage:.1f} Preferred) + "
        f"({w_norm.get('education_relevance', 0.05):.2f} × {edu_score:.1f} Education) + "
        f"({w_norm.get('nlp_ensemble', 0.15):.2f} × {nlp_score:.1f} NLP Ensemble)"
    )

    return {
        "job_fit_score": final_score,
        "match_level": match_level,
        "breakdown": {
            "required_skill_coverage": req_coverage,
            "relevant_experience": exp_score,
            "project_relevance": proj_score,
            "preferred_skill_coverage": pref_coverage,
            "education_relevance": edu_score,
            "nlp_ensemble": nlp_score,
        },
        "formula": formula_str,
    }
