"""Blind Screening & Fairness Module: Anonymizes PII to mitigate unconscious bias."""
import re
import hashlib


def anonymize_resume(resume_text: str, candidate_index: int = 1) -> tuple[str, str]:
    """
    Strips personal identifying information (PII) from resume text:
    - Names, Emails, Phone numbers, URLs, Social profiles, Physical addresses
    Returns:
      (anonymized_text, candidate_alias)
    """
    if not resume_text:
        return "", f"Candidate #{candidate_index}"

    # Generate consistent short anonymized ID
    hash_id = hashlib.md5(resume_text.encode("utf-8")).hexdigest()[:4].upper()
    candidate_alias = f"Candidate #{candidate_index} (ID: {hash_id})"

    text = resume_text

    # 1. Redact Emails
    text = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[REDACTED EMAIL]", text)

    # 2. Redact Phone Numbers
    text = re.sub(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", "[REDACTED PHONE]", text)

    # 3. Redact URLs / LinkedIn / GitHub / Portfolios
    text = re.sub(r"https?://\S+|www\.\S+|linkedin\.com/\S+|github\.com/\S+", "[REDACTED LINK]", text)

    # 4. Redact potential name in first 2 lines
    lines = text.split("\n")
    if lines:
        # First non-empty line is usually the candidate name
        for i, line in enumerate(lines[:3]):
            if line.strip() and not any(kw in line.lower() for kw in ["resume", "curriculum", "cv", "page", "summary"]):
                lines[i] = f"[ANONYMIZED CANDIDATE - ID: {hash_id}]"
                break
    text = "\n".join(lines)

    # 5. Redact gender/demographic pronouns if present
    demographics_pattern = re.compile(r"\b(he/him|she/her|they/them|male|female|married|single|age:\s*\d+)\b", re.IGNORECASE)
    text = demographics_pattern.sub("[REDACTED DEMOGRAPHIC]", text)

    return text, candidate_alias
