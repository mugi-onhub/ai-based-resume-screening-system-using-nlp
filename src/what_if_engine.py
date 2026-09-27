"""What-If Hiring Simulator Engine: Recalculates candidate rankings based on dynamic requirement shifts and explains rank deltas."""
from src.job_fit_scorer import calculate_job_fit_score


def simulate_what_if(
    baseline_candidates: list[dict],
    new_required_skills: set[str],
    new_preferred_skills: set[str],
    new_min_exp_years: float,
    custom_weights: dict | None = None,
) -> list[dict]:
    """
    Reruns the scoring pipeline on all candidates under modified job criteria.
    Returns:
      [
        {
          "name": str,
          "before_rank": int,
          "after_rank": int,
          "rank_delta": int (+1, -2, 0),
          "before_score": float,
          "after_score": float,
          "score_delta": float,
          "delta_explanation": str,
          "new_match_level": str,
          "new_breakdown": dict,
        }, ...
      ]
    """
    if not baseline_candidates:
        return []

    # Calculate new scores
    recalculated = []
    for c in baseline_candidates:
        new_result = calculate_job_fit_score(
            required_skills=new_required_skills,
            preferred_skills=new_preferred_skills,
            candidate_skills=c["candidate_skills"],
            candidate_exp_years=c["experience"]["relevant_experience_years"],
            min_exp_years=new_min_exp_years,
            project_scores=[p["relevance_score"] for p in c.get("projects", [])],
            nlp_ensemble_score=c["breakdown"]["nlp_ensemble"],
            resume_text=c.get("raw_text", ""),
            custom_weights=custom_weights,
        )
        recalculated.append({
            "name": c["name"],
            "candidate_skills": c["candidate_skills"],
            "before_rank": c.get("rank", 1),
            "before_score": c["job_fit_score"],
            "after_score": new_result["job_fit_score"],
            "new_match_level": new_result["match_level"],
            "new_breakdown": new_result["breakdown"],
            "raw_candidate": c,
        })

    # Sort by new after_score descending
    recalculated.sort(key=lambda x: x["after_score"], reverse=True)

    # Assign new ranks and compute deltas
    results = []
    for idx, item in enumerate(recalculated):
        after_rank = idx + 1
        before_rank = item["before_rank"]
        rank_delta = before_rank - after_rank  # positive means improved rank
        score_delta = round(item["after_score"] - item["before_score"], 1)

        # Generate reason for change
        reasons = []
        promoted_skills = new_required_skills - item["raw_candidate"]["all_required"]
        if promoted_skills:
            has_promoted = promoted_skills & item["candidate_skills"]
            missing_promoted = promoted_skills - item["candidate_skills"]
            if has_promoted:
                reasons.append(f"Possesses newly required skill(s): {', '.join(has_promoted)}")
            if missing_promoted:
                reasons.append(f"Lacks newly required skill(s): {', '.join(missing_promoted)}")

        if new_min_exp_years != item["raw_candidate"].get("min_exp_years", 0):
            cand_exp = item["raw_candidate"]["experience"]["relevant_experience_years"]
            if cand_exp >= new_min_exp_years:
                reasons.append(f"Meets adjusted experience bar ({cand_exp:.1f} >= {new_min_exp_years:.1f} yrs)")
            else:
                reasons.append(f"Below adjusted experience threshold ({cand_exp:.1f} < {new_min_exp_years:.1f} yrs)")

        explanation = "; ".join(reasons) if reasons else ("Score adjusted based on updated weight distribution." if score_delta != 0 else "Ranking and score remain stable.")

        results.append({
            "name": item["name"],
            "before_rank": before_rank,
            "after_rank": after_rank,
            "rank_delta": rank_delta,
            "before_score": item["before_score"],
            "after_score": item["after_score"],
            "score_delta": score_delta,
            "delta_explanation": explanation,
            "new_match_level": item["new_match_level"],
            "new_breakdown": item["new_breakdown"],
        })

    return results
