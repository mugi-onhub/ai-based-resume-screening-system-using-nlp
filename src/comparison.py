"""Candidate Comparison Module: Builds multi-candidate side-by-side matrices and objective contrast summaries."""


def build_comparison_matrix(candidates_data: list[dict]) -> dict:
    """
    Takes 2-4 candidate detail dictionaries and returns a structured comparison payload.
    """
    if not candidates_data:
        return {"headers": [], "rows": [], "summary_points": []}

    headers = [c["name"] for c in candidates_data]
    
    rows = [
        {
            "dimension": "Job Fit Score",
            "values": [f"{c['job_fit_score']:.1f}/100" for c in candidates_data],
        },
        {
            "dimension": "Match Level",
            "values": [c["match_level"] for c in candidates_data],
        },
        {
            "dimension": "Required Skills Match",
            "values": [
                f"{len(c['matched_required'])} / {len(c['all_required'])} ({c['breakdown']['required_skill_coverage']:.0f}%)"
                for c in candidates_data
            ],
        },
        {
            "dimension": "Relevant Experience",
            "values": [
                f"{c['experience']['relevant_experience_years']:.1f} yrs ({c['experience']['total_experience_years']:.1f} yrs total)"
                for c in candidates_data
            ],
        },
        {
            "dimension": "Top Project",
            "values": [
                f"{c['projects'][0]['name']} ({c['projects'][0]['relevance_score']:.0f}%)"
                if c.get("projects") else "N/A"
                for c in candidates_data
            ],
        },
        {
            "dimension": "Critical Gaps",
            "values": [
                ", ".join(c["insights"]["gaps_required"][:3]) or "None"
                for c in candidates_data
            ],
        },
        {
            "dimension": "Academic NLP Ensemble",
            "values": [
                f"{c['breakdown']['nlp_ensemble']:.1f}/100"
                for c in candidates_data
            ],
        },
    ]

    # Generate objective contrast summary
    summary_points = []
    if len(candidates_data) >= 2:
        top_c = max(candidates_data, key=lambda x: x["job_fit_score"])
        summary_points.append(
            f"**{top_c['name']}** leads in overall Job Fit ({top_c['job_fit_score']:.1f}) with {len(top_c['matched_required'])} required skills matched."
        )
        
        # Experience comparison
        exp_sorted = sorted(candidates_data, key=lambda x: x["experience"]["relevant_experience_years"], reverse=True)
        if exp_sorted[0]["experience"]["relevant_experience_years"] > exp_sorted[-1]["experience"]["relevant_experience_years"]:
            summary_points.append(
                f"**{exp_sorted[0]['name']}** offers the highest relevant domain experience ({exp_sorted[0]['experience']['relevant_experience_years']:.1f} years)."
            )

    return {
        "headers": headers,
        "rows": rows,
        "summary_points": summary_points,
    }
