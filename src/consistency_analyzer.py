"""Resume Consistency Analyzer: Identifies timeline gaps, date overlaps, and unsupported skills.
Flags items strictly as objective recruiter-review points, never making definitive fraud accusations.
"""
import re
from datetime import datetime


def analyze_consistency(resume_text: str, detected_skills: set[str], timeline_entries: list[dict]) -> dict:
    """
    Analyzes resume consistency:
    - flags: list of objective review observations
    - consistency_score: float (0 - 100)
    - has_warnings: bool
    """
    if not resume_text:
        return {
            "flags": ["Empty or unreadable document."],
            "consistency_score": 0.0,
            "has_warnings": True,
        }

    flags = []
    score = 100.0

    # 1. Timeline Overlap Check
    if len(timeline_entries) >= 2:
        sorted_entries = sorted(timeline_entries, key=lambda x: x["start"])
        for i in range(len(sorted_entries) - 1):
            curr_entry = sorted_entries[i]
            next_entry = sorted_entries[i + 1]
            # If current ends after next starts by > 1 year
            if curr_entry["end"] > next_entry["start"] + 1:
                flags.append(
                    f"Overlapping employment timeline detected: ({curr_entry['start']}–{curr_entry['end']}) "
                    f"overlaps with ({next_entry['start']}–{next_entry['end']})."
                )
                score -= 10.0

    # 2. Date Gap Check (> 1.5 years between roles)
    if len(timeline_entries) >= 2:
        sorted_entries = sorted(timeline_entries, key=lambda x: x["start"])
        for i in range(len(sorted_entries) - 1):
            curr_end = sorted_entries[i]["end"]
            next_start = sorted_entries[i + 1]["start"]
            if next_start - curr_end > 1.5:
                flags.append(
                    f"Employment timeline gap of ~{int(next_start - curr_end)} years detected between {curr_end} and {next_start}."
                )
                score -= 5.0

    # 3. Unsupported Skills Check (Skills listed in summary without any project/experience sentence context)
    unsupported = []
    text_lower = resume_text.lower()
    for skill in detected_skills:
        skill_lower = skill.lower()
        # Count occurrences
        matches = len(re.findall(rf"\b{re.escape(skill_lower)}\b", text_lower))
        if matches == 1:
            # Check if it only appears in a comma-separated list line
            for line in text_lower.split("\n"):
                if skill_lower in line and ("," in line or "/" in line) and len(line.split()) < 15:
                    if not any(v in line for v in ["developed", "built", "designed", "created", "led", "managed"]):
                        unsupported.append(skill)
                        break

    if len(unsupported) > 3:
        flags.append(
            f"Skills mentioned with limited supporting project/role context: {', '.join(unsupported[:4])}. (Recommended for phone-screen verification)."
        )
        score -= 5.0

    # 4. Check for completely missing dates when roles are listed
    has_roles_no_dates = bool(
        re.search(r"\b(software engineer|data scientist|analyst|developer)\b", text_lower)
        and not timeline_entries
        and not re.search(r"\b(20\d\d|19\d\d)\b", resume_text)
    )
    if has_roles_no_dates:
        flags.append("Employment titles mentioned without explicit dates or durations.")
        score -= 10.0

    if not flags:
        flags.append("No obvious timeline inconsistencies or unverified skill clusters detected.")

    return {
        "flags": flags,
        "consistency_score": max(50.0, round(score, 1)),
        "has_warnings": len(flags) > 1 or (len(flags) == 1 and "No obvious" not in flags[0]),
    }
