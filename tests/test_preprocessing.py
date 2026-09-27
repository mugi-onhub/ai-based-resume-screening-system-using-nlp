from src.preprocessing import clean_whitespace, normalize_for_matching, preprocess


def test_clean_whitespace_collapses_spaces():
    assert clean_whitespace("a b\t\tc") == "a b c"


def test_normalize_preserves_protected_tokens():
    text = "Experienced in C++ and .NET development."
    normalized = normalize_for_matching(text)
    assert "C++" in normalized
    assert ".NET" in normalized
    assert "experienced in" in normalized  # rest is lowercased


def test_preprocess_removes_duplicate_lines():
    text = "Header\nHeader\nReal content line."
    result = preprocess(text)
    assert result.count("header") == 1
