"""Text normalization that preserves technical tokens."""
import re

# Tokens that must never be mangled by cleanup (case-sensitive fragments)
PROTECTED_PATTERNS = [
    r"C\+\+", r"C#", r"\.NET", r"Node\.js", r"ASP\.NET", r"F#",
]

_WHITESPACE_RE = re.compile(r"[ \t]+")
_BLANK_LINES_RE = re.compile(r"\n{3,}")


def clean_whitespace(text: str) -> str:
    text = _WHITESPACE_RE.sub(" ", text)
    text = _BLANK_LINES_RE.sub("\n\n", text)
    return text.strip()


def normalize_for_matching(text: str) -> str:
    """
    Produces a lowercase, whitespace-cleaned copy for similarity/skill matching.
    The ORIGINAL text should still be kept separately for on-screen display.
    """
    text = clean_whitespace(text)
    # Lowercase everything except protected technical tokens, which we
    # temporarily mask so casing/punctuation survives lowercasing.
    placeholders = {}
    for i, pattern in enumerate(PROTECTED_PATTERNS):
        for match in re.finditer(pattern, text):
            key = f"__PROTECTED_{i}_{match.start()}__"
            placeholders[key] = match.group(0)
            text = text.replace(match.group(0), key, 1)

    text = text.lower()
    for key, original in placeholders.items():
        text = text.replace(key.lower(), original)
    return text


def remove_duplicate_lines(text: str) -> str:
    """Removes exact duplicate lines (common with repeated headers/footers)."""
    seen = set()
    out_lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped and stripped in seen:
            continue
        if stripped:
            seen.add(stripped)
        out_lines.append(line)
    return "\n".join(out_lines)


def preprocess(text: str) -> str:
    """Full pipeline: clean whitespace, dedupe lines, normalize for matching."""
    text = clean_whitespace(text)
    text = remove_duplicate_lines(text)
    return normalize_for_matching(text)
