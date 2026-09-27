"""Project-to-Job Matcher: Extracts projects and scores their relevance to job requirements."""
import re
from src.skills import extract_skills
from config import DEFAULT_SKILLS


def extract_projects(resume_text: str, target_skills: set[str] | None = None) -> list[dict]:
    """
    Identifies and parses distinct project entries from resume text.
    Returns:
      [
        {
          "name": "E-Commerce Recommendation System",
          "technologies": {"python", "scikit-learn", "sql"},
          "description": "Built collaborative filtering model...",
          "matched_requirements": {"python", "scikit-learn"},
          "relevance_score": 88.0,
        }, ...
      ]
    """
    if not resume_text:
        return []

    lines = [line.strip() for line in resume_text.split("\n") if line.strip()]
    skills_pool = target_skills or DEFAULT_SKILLS
    target_set = {s.lower() for s in (target_skills or set())}

    # Find project section
    project_headers = ["projects", "academic projects", "key projects", "personal projects", "selected projects", "technical projects"]
    in_project_section = False
    project_lines = []
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(line_lower.startswith(h) or line_lower == h for h in project_headers) and len(line) < 40:
            in_project_section = True
            continue
        elif in_project_section:
            # Check if next major section started
            if any(line_lower.startswith(h) for h in ["experience", "employment", "education", "skills", "certifications", "interests"]) and len(line) < 40:
                in_project_section = False
                break
            project_lines.append(line)

    # If no explicit projects section header was found, scan entire text for project-like blocks
    if not project_lines:
        for line in lines:
            if re.search(r"\b(project|system|platform|application|pipeline|engine|app|classifier|model)\b", line, re.IGNORECASE) and len(line) < 80:
                project_lines.append(line)

    # Group into individual project blocks
    projects = []
    current_proj_name = ""
    current_proj_desc = []

    for line in project_lines:
        is_title = (
            (len(line) < 65 and not line.startswith(("-", "*", "•", "–")) and any(c.isupper() for c in line))
            or "|" in line or ":" in line
        )
        if is_title and current_proj_name and current_proj_desc:
            # Flush previous project
            desc_text = " ".join(current_proj_desc)
            techs = extract_skills(f"{current_proj_name} {desc_text}", skills_pool)
            matched = techs & target_set if target_set else techs
            
            relevance = 0.0
            if target_set:
                relevance = round(min(100.0, (len(matched) / max(1, min(4, len(target_set)))) * 100.0), 1)
            else:
                relevance = round(min(100.0, len(techs) * 25.0), 1)

            projects.append({
                "name": current_proj_name.split("|")[0].split(":")[0].strip(),
                "technologies": techs,
                "description": desc_text[:200] + ("..." if len(desc_text) > 200 else ""),
                "matched_requirements": matched,
                "relevance_score": max(50.0 if techs else 30.0, relevance),
            })
            current_proj_name = line
            current_proj_desc = []
        elif is_title and not current_proj_name:
            current_proj_name = line
        else:
            current_proj_desc.append(line)

    # Flush final project
    if current_proj_name:
        desc_text = " ".join(current_proj_desc) if current_proj_desc else current_proj_name
        techs = extract_skills(f"{current_proj_name} {desc_text}", skills_pool)
        matched = techs & target_set if target_set else techs
        relevance = round(min(100.0, (len(matched) / max(1, min(4, len(target_set)))) * 100.0), 1) if target_set else round(min(100.0, len(techs) * 25.0), 1)
        projects.append({
            "name": current_proj_name.split("|")[0].split(":")[0].strip(),
            "technologies": techs,
            "description": desc_text[:200] + ("..." if len(desc_text) > 200 else ""),
            "matched_requirements": matched,
            "relevance_score": max(50.0 if techs else 30.0, relevance),
        })

    # If no structured projects could be parsed, synthesize top project context from technical descriptions
    if not projects:
        techs = extract_skills(resume_text, skills_pool)
        matched = techs & target_set if target_set else techs
        if techs:
            projects.append({
                "name": "Applied Technical Portfolio & Implementations",
                "technologies": techs,
                "description": "Applied hands-on projects and implementations documented across the candidate resume.",
                "matched_requirements": matched,
                "relevance_score": round(min(100.0, len(matched) * 20.0), 1) if target_set else 75.0,
            })

    return projects[:4]
