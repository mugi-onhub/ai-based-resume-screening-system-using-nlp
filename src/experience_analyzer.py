"""Experience Analyzer: Extracts and distinguishes Total Experience vs Relevant Experience.
Analyzes job titles, roles, career progression, and duration.
"""
import re
from datetime import datetime


def analyze_experience(resume_text: str, target_domain_keywords: set[str] | None = None) -> dict:
    """
    Extracts experience metrics from resume text:
    - total_experience_years: float
    - relevant_experience_years: float
    - roles: list of detected job titles / positions
    - timeline_entries: list of detected employment periods
    """
    if not resume_text:
        return {
            "total_experience_years": 0.0,
            "relevant_experience_years": 0.0,
            "roles": [],
            "timeline_entries": [],
        }

    current_year = datetime.now().year

    # 1. Look for explicit mentions like "4 years of experience", "2+ yrs experience"
    explicit_exp_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:\+|-\s*\d+)?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp)?", resume_text, re.IGNORECASE)
    explicit_exp = float(explicit_exp_match.group(1)) if explicit_exp_match else None

    # 2. Extract Date Ranges (e.g. "2019 - 2022", "2021 - Present", "Jun 2020 - Dec 2022")
    year_range_pattern = re.compile(
        r"(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*)?(20\d\d|19\d\d)\s*(?:-|–|to)\s*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*)?(20\d\d|19\d\d|Present|Current|Now)",
        re.IGNORECASE,
    )

    timeline_entries = []
    total_calculated_years = 0.0
    detected_roles = []

    # Common tech/data role patterns
    role_titles = [
        "Data Scientist", "Senior Data Scientist", "Lead Data Scientist", "Junior Data Scientist",
        "Machine Learning Engineer", "ML Engineer", "AI Engineer", "AI Researcher",
        "Data Analyst", "Senior Data Analyst", "Business Intelligence Analyst", "BI Developer",
        "Software Engineer", "Senior Software Engineer", "Backend Engineer", "Full Stack Developer",
        "Frontend Developer", "DevOps Engineer", "Cloud Architect", "MLOps Engineer",
        "Data Engineer", "Big Data Engineer", "Intern", "Data Science Intern", "Research Assistant",
    ]

    for line in resume_text.split("\n"):
        line_clean = line.strip()
        if not line_clean:
            continue
        
        # Check for role titles
        for title in role_titles:
            if re.search(rf"\b{re.escape(title)}\b", line_clean, re.IGNORECASE):
                if title not in detected_roles:
                    detected_roles.append(title)

        # Check for date ranges
        for match in year_range_pattern.finditer(line_clean):
            start_yr = int(match.group(1))
            end_str = match.group(2)
            end_yr = current_year if end_str.lower() in ["present", "current", "now"] else int(end_str)
            
            duration = max(0.5, round(end_yr - start_yr + 0.5, 1))
            if start_yr <= end_yr and duration <= 40:
                timeline_entries.append({
                    "start": start_yr,
                    "end": end_yr,
                    "duration_years": duration,
                    "context": line_clean[:80],
                })
                total_calculated_years += duration

    # Resolve Total Experience
    if timeline_entries:
        # Avoid simple double counting if overlapping years occur
        min_start = min(e["start"] for e in timeline_entries)
        max_end = max(e["end"] for e in timeline_entries)
        total_span = max(0.0, float(max_end - min_start))
        total_exp = min(total_span, total_calculated_years)
    elif explicit_exp is not None:
        total_exp = explicit_exp
    else:
        # Check if fresh graduate / intern
        if re.search(r"\b(student|intern|graduate|fresher|internship)\b", resume_text, re.IGNORECASE):
            total_exp = 0.5
        else:
            total_exp = 0.0

    # Calculate Relevant Experience (ratio based on domain keywords and role titles)
    domain_kw = target_domain_keywords or {"data", "machine learning", "ml", "ai", "python", "analytics", "software", "developer"}
    relevant_exp = total_exp

    # If candidate worked in unrelated roles or is a fresher with projects, weight relevance accordingly
    text_lower = resume_text.lower()
    kw_hits = sum(1 for kw in domain_kw if re.search(rf"\b{re.escape(kw)}\b", text_lower))
    relevance_factor = min(1.0, max(0.4, kw_hits / max(1, len(domain_kw))))
    
    if detected_roles:
        has_direct_role = any("data" in r.lower() or "machine learning" in r.lower() or "ai" in r.lower() or "software" in r.lower() for r in detected_roles)
        if has_direct_role:
            relevance_factor = max(relevance_factor, 0.85)

    relevant_exp = round(total_exp * relevance_factor, 1)

    return {
        "total_experience_years": round(total_exp, 1),
        "relevant_experience_years": relevant_exp,
        "roles": detected_roles[:5],
        "timeline_entries": timeline_entries,
    }
