# CAREERPILOT: AI-Based Resume Screening System Using NLP

<div align="center">

[![Live App](https://img.shields.io/badge/Live_App-Vercel-black?style=for-the-badge&logo=vercel)](https://careerpilot-ai-nlp.vercel.app)
[![Backend API](https://img.shields.io/badge/Backend_API-Render-46E3B7?style=for-the-badge&logo=render)](https://careerpilot-api-n37s.onrender.com)
[![API Docs](https://img.shields.io/badge/API_Docs-Swagger-85EA2D?style=for-the-badge&logo=swagger)](https://careerpilot-api-n37s.onrender.com/docs)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://python.org)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)

**Next-Generation AI Candidate Screening & Explainable Job Fit Platform**

[🌐 Open Live Web App](https://careerpilot-ai-nlp.vercel.app) • [📖 Interactive Swagger API Docs](https://careerpilot-api-n37s.onrender.com/docs)

</div>

---

## 📌 Overview

**CAREERPILOT** is an enterprise-grade recruitment intelligence platform that replaces opaque, keyword-stuffed "black box" ATS screening with an explainable **Tri-Model NLP Ensemble** (TF-IDF + Sentence-Transformers + BERT) and a transparent **100-point multi-criteria Job Fit scoring formula**.


- **Multi-Format Ingestion**: Robust text extraction from PDF (`PyMuPDF`), Word (`python-docx`), and plain text (`TXT`) files.
- **NLP Matching Engines**:
  - **TF-IDF Vectorizer**: Lexical keyword and bi-gram matching baseline.
  - **Sentence Transformers (`all-MiniLM-L6-v2`)**: Dense semantic embedding similarity with `@st.cache_resource` caching.
  - **BERT (`bert-base-uncased`)**: Contextual representation with token chunking and aggregation for long documents.
- **Phrase-Boundary Skill Extraction**: Regex matching with whole-word boundaries to avoid false positives (e.g., distinguishing `Java` from `JavaScript`).
- **Weighted Score Fusion**: Configurable score combination with real-time UI sliders.
- **Interactive Streamlit Dashboard**: Top metrics, candidate ranking table, skill comparison breakdown, Plotly comparison charts, and CSV/Excel export.
- **Non-Decisional Explainability**: Provides human-readable match categories (`Strong match`, `Moderate match`, `Low match`) with clear decision-support disclaimers.

---

## 📂 Project Structure

```text
resume-screening-nlp/
|-- app.py
|-- requirements.txt
|-- README.md
|-- config.py
|-- .gitignore
|-- .streamlit/
|   `-- config.toml
|-- data/
|   |-- sample_resumes/
|   |   |-- resume_strong_match.txt
|   |   |-- resume_partial_match.txt
|   |   `-- resume_weak_match.txt
|   `-- sample_job_descriptions/
|       `-- data_scientist_jd.txt
|-- src/
|   |-- __init__.py
|   |-- extractors.py
|   |-- preprocessing.py
|   |-- skills.py
|   |-- tfidf_matcher.py
|   |-- semantic_matcher.py
|   |-- bert_matcher.py
|   |-- scoring.py
|   |-- ranking.py
|   `-- explain.py
|-- tests/
|   |-- test_extractors.py
|   |-- test_preprocessing.py
|   |-- test_scoring.py
|   `-- test_ranking.py
`-- outputs/
```

---

## 🚀 Installation & Setup

1. **Create and Activate Virtual Environment**:
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Unit Tests**:
   ```bash
   pytest -v
   ```

4. **Launch Streamlit App**:
   ```bash
   streamlit run app.py
   ```

---

## 🧪 Running the Demo

1. Open the Streamlit web dashboard in your browser.
2. Copy the sample job description from `data/sample_job_descriptions/data_scientist_jd.txt` into the **Job Description** field.
3. Upload the sample resumes located in `data/sample_resumes/` (`resume_strong_match.txt`, `resume_partial_match.txt`, `resume_weak_match.txt`).
4. Click **Screen Resumes** to view live rankings, metrics, skill comparisons, score charts, and export options.
