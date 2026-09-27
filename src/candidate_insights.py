"""Candidate Insights Generator: Synthesizes 'Why this candidate?' rationales, skill gaps, and interview questions."""


def generate_candidate_insights(
    candidate_name: str,
    job_title: str,
    required_skills: set[str],
    preferred_skills: set[str],
    candidate_skills: set[str],
    evidence_dict: dict,
    experience_data: dict,
    projects: list[dict],
    job_fit_score: float,
) -> dict:
    """
    Produces actionable recruiter rationales:
    - why_this_candidate: list of top strengths with evidence
    - gaps_required: list of missing required skills
    - gaps_preferred: list of missing preferred skills
    - interview_questions: list of tailored interview probe questions
    - executive_summary: 2-sentence synthesis
    """
    matched_req = required_skills & candidate_skills
    missing_req = required_skills - candidate_skills
    matched_pref = preferred_skills & candidate_skills
    missing_pref = preferred_skills - candidate_skills

    # 1. Why this candidate points
    why_points = []
    
    # Top skills with strong evidence
    strong_skills = [
        s for s, ev in evidence_dict.items()
        if ev.get("status") == "Strong Match" and s in (required_skills | preferred_skills)
    ]
    if strong_skills:
        sample_s = strong_skills[:3]
        why_points.append(f"Strong verified experience in core requirements: {', '.join(sample_s)}.")

    # Experience strength
    rel_exp = experience_data.get("relevant_experience_years", 0.0)
    tot_exp = experience_data.get("total_experience_years", 0.0)
    roles = experience_data.get("roles", [])
    if roles:
        why_points.append(f"Demonstrated background in relevant role(s): {', '.join(roles[:2])} ({rel_exp:.1f} yrs domain experience).")
    elif tot_exp > 0:
        why_points.append(f"Professional track record with ~{tot_exp:.1f} years total industry experience.")

    # Projects strength
    if projects:
        best_proj = max(projects, key=lambda p: p.get("relevance_score", 0))
        if best_proj.get("relevance_score", 0) >= 60:
            why_points.append(f"Relevant project portfolio: '{best_proj['name']}' utilizing {', '.join(list(best_proj['technologies'])[:3])}.")

    if not why_points:
        why_points.append(f"Demonstrates foundational technical baseline with {len(candidate_skills)} detected competencies.")

    # 2. Gaps & Risk Points
    gaps_req_list = sorted(list(missing_req))
    gaps_pref_list = sorted(list(missing_pref))

    # 3. Dynamic Interview Questions based on Gaps
    questions = []
    if missing_req:
        top_missing_req = list(missing_req)[:2]
        for s in top_missing_req:
            questions.append(
                f"We noticed limited direct mention of {s.upper()}. Can you describe your familiarity or any practical exposure to {s.capitalize()} in previous work or coursework?"
            )
    
    if projects:
        proj_name = projects[0]["name"]
        questions.append(
            f"Could you walk us through the architecture and key challenges you encountered while building '{proj_name}'?"
        )
    else:
        questions.append("Can you walk us through a recent technical project you built from design to implementation?")

    # 4. Executive Summary
    summary = (
        f"{candidate_name} achieves a Job Fit score of {job_fit_score:.1f}/100 for {job_title or 'the role'}. "
        f"Shows solid coverage in {', '.join(list(matched_req)[:3]) if matched_req else 'general skills'}, "
        f"with potential growth opportunities in {', '.join(list(missing_req)[:2]) if missing_req else 'advanced requirements'}."
    )

    return {
        "why_this_candidate": why_points,
        "gaps_required": gaps_req_list,
        "gaps_preferred": gaps_pref_list,
        "interview_questions": questions[:3],
        "executive_summary": summary,
    }
