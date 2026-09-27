"""Human-readable, non-decisional explanations for each candidate."""
from config import THRESHOLDS


def match_category(final_score: float) -> str:
    if final_score >= THRESHOLDS["strong"]:
        return "Strong match"
    if final_score >= THRESHOLDS["moderate"]:
        return "Moderate match"
    return "Low match"


def build_explanation(final_score: float, matched_skills: set, missing_skills: set) -> str:
    category = match_category(final_score)
    matched_str = ", ".join(sorted(matched_skills)) if matched_skills else "none identified"
    missing_str = ", ".join(sorted(missing_skills)) if missing_skills else "none"
    return (
        f"{category} (score: {final_score:.1f}/100). "
        f"Matched skills: {matched_str}. Missing skills: {missing_str}. "
        f"This is a relevance signal for human review, not a hiring recommendation."
    )
