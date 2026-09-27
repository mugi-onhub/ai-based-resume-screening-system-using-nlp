"""Phrase-boundary skill matching (avoids substring false positives)."""
import re
from config import DEFAULT_SKILLS


def _skill_pattern(skill: str) -> re.Pattern:
    """Builds a whole-word/phrase regex for a skill, escaping special chars."""
    escaped = re.escape(skill.lower())
    return re.compile(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])")


_SKILL_PATTERNS = {skill: _skill_pattern(skill) for skill in DEFAULT_SKILLS}


def extract_skills(text: str, skills: set[str] | None = None) -> set[str]:
    text_lower = text.lower()
    patterns = _SKILL_PATTERNS if skills is None else {s: _skill_pattern(s) for s in skills}
    return {skill for skill, pattern in patterns.items() if pattern.search(text_lower)}


def compare_skills(job_text: str, resume_text: str, skills: set[str] | None = None):
    job_skills = extract_skills(job_text, skills)
    resume_skills = extract_skills(resume_text, skills)
    matched = job_skills & resume_skills
    missing = job_skills - resume_skills
    return {
        "job_skills": job_skills,
        "resume_skills": resume_skills,
        "matched": matched,
        "missing": missing,
    }
