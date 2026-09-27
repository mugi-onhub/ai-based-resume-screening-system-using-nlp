"""Evidence-Based Skill Matcher: Extracts verbatim sentence-level evidence from resumes.
Ensures zero hallucinations by quoting exact text snippets from candidate resumes.
"""
import re


def extract_skill_evidence(resume_text: str, skills: set[str]) -> dict[str, dict]:
    """
    For every skill in `skills`, finds exact verbatim evidence from `resume_text`.
    Returns:
      {
        "python": {
          "status": "Strong Match" | "Partial Match" | "Missing",
          "evidence": "Exact quote from resume...",
          "score": 100 | 70 | 0,
        }, ...
      }
    """
    if not resume_text:
        return {
            s: {"status": "Missing", "evidence": "No resume text available.", "score": 0}
            for s in skills
        }

    # Split text into clean sentences / bullet points
    raw_lines = resume_text.split("\n")
    sentences = []
    for line in raw_lines:
        line_clean = line.strip().lstrip("-*•– ")
        if not line_clean:
            continue
        # Split on sentence terminals if line is long
        parts = re.split(r"(?<=[.!?])\s+", line_clean)
        for p in parts:
            p_strip = p.strip()
            if len(p_strip) > 5:
                sentences.append(p_strip)

    action_verbs = {
        "developed", "built", "implemented", "designed", "engineered", "created",
        "trained", "deployed", "optimized", "analyzed", "architected", "managed",
        "lead", "spearheaded", "fine-tuned", "integrated", "automated", "scaled"
    }

    results = {}
    for skill in sorted(skills):
        skill_lower = skill.lower()
        escaped_skill = re.escape(skill_lower)
        pattern = re.compile(rf"(?<![a-z0-9]){escaped_skill}(?![a-z0-9])", re.IGNORECASE)

        matching_sentences = []
        for s in sentences:
            if pattern.search(s):
                matching_sentences.append(s)

        if not matching_sentences:
            results[skill] = {
                "status": "Missing",
                "evidence": f"No mention or evidence of '{skill}' found in resume.",
                "score": 0,
            }
        else:
            # Pick the most descriptive sentence (preferably one with action verbs and length)
            best_sentence = matching_sentences[0]
            is_strong = False
            
            for s in matching_sentences:
                words = set(re.findall(r"\b[a-z]+\b", s.lower()))
                if words & action_verbs:
                    best_sentence = s
                    is_strong = True
                    break
                elif len(s) > len(best_sentence):
                    best_sentence = s

            # If the sentence is just a comma list (e.g. "Skills: Python, SQL, Java") -> Partial Match
            if not is_strong and ("," in best_sentence or len(best_sentence.split()) <= 4):
                results[skill] = {
                    "status": "Partial Match",
                    "evidence": f'"{best_sentence}"',
                    "score": 70,
                }
            else:
                results[skill] = {
                    "status": "Strong Match",
                    "evidence": f'"{best_sentence}"',
                    "score": 100,
                }

    return results
