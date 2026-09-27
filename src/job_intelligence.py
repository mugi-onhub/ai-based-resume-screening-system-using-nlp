"""Job Intelligence Module: Parses Job Descriptions into structured requirements.
Extracts: Required Skills, Preferred Skills, Minimum Experience, Responsibilities, and Technologies.
"""
import re
from src.skills import extract_skills
from config import DEFAULT_SKILLS


def parse_job_description(job_text: str, custom_skills: set[str] | None = None) -> dict:
    """
    Parses a raw job description into structured criteria:
    - required_skills: set of skills in mandatory/required sections
    - preferred_skills: set of skills in preferred/nice-to-have sections
    - min_experience_years: float minimum years of experience detected
    - responsibilities: list of extracted responsibility bullet points
    - technologies: set of all detected technologies/tools
    - all_skills: set of all skills found across the JD
    """
    if not job_text or not job_text.strip():
        return {
            "required_skills": set(),
            "preferred_skills": set(),
            "min_experience_years": 0.0,
            "responsibilities": [],
            "technologies": set(),
            "all_skills": set(),
        }

    lines = [line.strip() for line in job_text.split("\n") if line.strip()]
    skills_pool = custom_skills or DEFAULT_SKILLS
    
    # Section classifiers
    required_keywords = ["required", "requirement", "must have", "minimum qualification", "qualifications", "what you need", "essential", "mandatory"]
    preferred_keywords = ["preferred", "nice to have", "plus", "bonus", "good to have", "desired", "advantageous", "optional"]
    resp_keywords = ["responsibilities", "duties", "what you will do", "role", "key responsibilities", "tasks", "what you'll do"]

    current_section = "general"
    required_text_blocks = []
    preferred_text_blocks = []
    resp_blocks = []

    for line in lines:
        lower_line = line.lower()
        
        # Check if line is a section header
        is_header = False
        if any(kw in lower_line for kw in preferred_keywords) and len(line) < 60:
            current_section = "preferred"
            is_header = True
        elif any(kw in lower_line for kw in required_keywords) and len(line) < 60:
            current_section = "required"
            is_header = True
        elif any(kw in lower_line for kw in resp_keywords) and len(line) < 60:
            current_section = "responsibilities"
            is_header = True

        if not is_header:
            if current_section == "required":
                required_text_blocks.append(line)
            elif current_section == "preferred":
                preferred_text_blocks.append(line)
            elif current_section == "responsibilities":
                if line.startswith(("-", "*", "•", "–")) or len(line) > 20:
                    resp_blocks.append(line.lstrip("-*•– "))
            else:
                # Default general text can contribute to required if not specified
                required_text_blocks.append(line)

    req_text = " \n ".join(required_text_blocks)
    pref_text = " \n ".join(preferred_text_blocks)
    all_text = job_text

    all_skills = extract_skills(all_text, skills_pool)
    pref_skills = extract_skills(pref_text, skills_pool) if pref_text else set()
    
    # Required skills are all skills in required section or remaining skills if sections weren't clearly demarcated
    req_skills = extract_skills(req_text, skills_pool) if req_text else (all_skills - pref_skills)
    
    # Ensure no overlap: required takes precedence unless strictly in preferred block
    req_skills = req_skills - pref_skills
    if not req_skills and all_skills:
        # If no strict split was found, treat all found skills as required
        req_skills = set(all_skills)
        pref_skills = set()

    # Extract Minimum Experience (e.g. "3+ years", "2-5 years", "min 1 year", "0-12 months")
    min_exp = 0.0
    exp_matches = re.findall(r"(\d+(?:\.\d+)?)\s*(?:\+|-\s*\d+)?\s*(?:years?|yrs?|months?)\s*(?:of)?\s*(?:experience|exp)?", job_text, re.IGNORECASE)
    month_matches = re.findall(r"(\d+)\s*(?:-\s*(\d+))?\s*months?", job_text, re.IGNORECASE)
    
    if month_matches:
        months = float(month_matches[0][0])
        min_exp = round(months / 12.0, 1)
    elif exp_matches:
        try:
            min_exp = float(exp_matches[0])
        except ValueError:
            min_exp = 0.0

    return {
        "required_skills": req_skills,
        "preferred_skills": pref_skills,
        "min_experience_years": min_exp,
        "responsibilities": resp_blocks[:6],
        "technologies": all_skills,
        "all_skills": all_skills,
    }
