import os
import pytest
from src.extractors import extract_text, safe_extract_text, ExtractionError


def test_extract_txt(tmp_path):
    p = tmp_path / "sample.txt"
    p.write_text("Python developer with SQL experience.")
    assert "Python" in extract_text(str(p))


def test_extract_txt_empty_raises(tmp_path):
    p = tmp_path / "empty.txt"
    p.write_text("")
    with pytest.raises(ExtractionError):
        extract_text(str(p))


def test_unsupported_extension_raises(tmp_path):
    p = tmp_path / "resume.xyz"
    p.write_text("some content")
    with pytest.raises(ExtractionError):
        extract_text(str(p))


def test_missing_file_raises():
    with pytest.raises(ExtractionError):
        extract_text("/no/such/file.pdf")


def test_safe_extract_never_raises(tmp_path):
    p = tmp_path / "empty.txt"
    p.write_text("")
    text, err = safe_extract_text(str(p))
    assert text is None
    assert err is not None
