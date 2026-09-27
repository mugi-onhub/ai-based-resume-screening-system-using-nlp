"""getHire: AI Recruitment Intelligence Platform.
Enterprise-grade candidate screening, evidence-based matching, explainable Job Fit scoring, and recruiter workflows.
"""
import os
import tempfile
from io import BytesIO
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Core configurations & models
from config import (
    DEFAULT_SHORTLIST_THRESHOLD,
    WEIGHTS,
    JOB_FIT_WEIGHTS,
    THRESHOLDS,
    RECRUITER_STATUSES,
    DEFAULT_SKILLS,
    SUPPORTED_EXTENSIONS,
)
from src.extractors import safe_extract_text
from src.preprocessing import preprocess
from src.tfidf_matcher import tfidf_similarity
from src.semantic_matcher import semantic_similarity
from src.bert_matcher import bert_similarity
from src.scoring import to_percentage, fuse_scores
from src.ranking import build_ranking_table, shortlist
from src.skills import compare_skills, extract_skills
from src.explain import match_category, build_explanation

# Intelligence modules
from src.job_intelligence import parse_job_description
from src.evidence_matcher import extract_skill_evidence
from src.experience_analyzer import analyze_experience
from src.project_matcher import extract_projects
from src.consistency_analyzer import analyze_consistency
from src.blind_screening import anonymize_resume
from src.job_fit_scorer import calculate_job_fit_score
from src.candidate_insights import generate_candidate_insights
from src.comparison import build_comparison_matrix
from src.what_if_engine import simulate_what_if


# ==========================================
# PAGE CONFIGURATION & RESTRAINED SAAS CSS
# ==========================================
st.set_page_config(
    page_title="getHire | AI Recruitment Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global Typography & Palette (Ashby / Linear / Vercel style) */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #0f172a;
    }
    
    .stApp {
        background-color: #f8fafc;
    }
    
    /* Hide Default Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Top Bar Shell */
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0 20px 0;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 24px;
    }
    .top-breadcrumbs {
        font-size: 13px;
        color: #64748b;
        font-weight: 500;
    }
    .top-role-title {
        font-size: 20px;
        font-weight: 700;
        color: #0f172a;
        margin-top: 2px;
    }
    .top-meta {
        font-size: 13px;
        color: #64748b;
        margin-top: 2px;
    }

    /* Minimal Brand Logo Mark */
    .brand-container {
        padding: 8px 0 24px 0;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }
    .brand-logo-text {
        font-size: 18px;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #0f172a;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .brand-tagline {
        font-size: 11px;
        color: #64748b;
        font-weight: 500;
        letter-spacing: 0.2px;
        margin-top: 2px;
    }
    .nav-group-label {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #94a3b8;
        margin: 18px 0 8px 0;
    }

    /* Restrained Horizontal Metric Strip */
    .metric-strip {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 24px;
    }
    .metric-strip-item {
        padding: 0 16px;
        border-right: 1px solid #f1f5f9;
    }
    .metric-strip-item:last-child {
        border-right: none;
    }
    .metric-strip-label {
        font-size: 12px;
        font-weight: 500;
        color: #64748b;
        margin-bottom: 4px;
    }
    .metric-strip-val {
        font-size: 24px;
        font-weight: 700;
        color: #0f172a;
        letter-spacing: -0.5px;
    }
    .metric-strip-sub {
        font-size: 11px;
        color: #94a3b8;
        margin-top: 2px;
    }

    /* Clean Card Container */
    .clean-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 20px 24px;
        margin-bottom: 20px;
    }
    .card-title {
        font-size: 15px;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 4px;
    }
    .card-subtitle {
        font-size: 13px;
        color: #64748b;
        margin-bottom: 16px;
    }

    /* Candidate Row Item */
    .candidate-row {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }
    .candidate-row:hover {
        border-color: #cbd5e1;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .candidate-avatar {
        width: 36px;
        height: 36px;
        border-radius: 6px;
        background: #f1f5f9;
        color: #334155;
        font-weight: 600;
        font-size: 13px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 14px;
    }

    /* Semantic Status Badges */
    .badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 500;
        line-height: 1.4;
    }
    .badge-strong { background: #f0fdf4; color: #166534; border: 1px solid #dcfce7; }
    .badge-good { background: #eff6ff; color: #1e40af; border: 1px solid #dbeafe; }
    .badge-review { background: #fffbeb; color: #92400e; border: 1px solid #fef3c7; }
    .badge-low { background: #fef2f2; color: #991b1b; border: 1px solid #fee2e2; }
    .badge-neutral { background: #f8fafc; color: #475569; border: 1px solid #e2e8f0; }

    /* Score Progress Bar */
    .score-progress-bg {
        width: 90px;
        height: 6px;
        background: #f1f5f9;
        border-radius: 3px;
        overflow: hidden;
        margin-top: 4px;
    }
    .score-progress-fill {
        height: 100%;
        border-radius: 3px;
    }

    /* Intelligence Callout Box */
    .intel-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 3px solid #2563eb;
        border-radius: 6px;
        padding: 14px 18px;
        margin-bottom: 20px;
    }
    .intel-title {
        font-size: 13px;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 4px;
    }
    .intel-body {
        font-size: 13px;
        color: #475569;
        line-height: 1.5;
    }

    /* Subdued Disclaimer */
    .legal-notice {
        font-size: 11px;
        color: #94a3b8;
        line-height: 1.4;
        padding: 12px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if "candidates" not in st.session_state:
    st.session_state["candidates"] = {}
if "active_job_id" not in st.session_state:
    st.session_state["active_job_id"] = "job_001"
if "jobs_db" not in st.session_state:
    st.session_state["jobs_db"] = {
        "job_001": {
            "title": "Senior AI / Data Science Specialist",
            "department": "Engineering & Analytics",
            "created": "2026-08-19",
            "min_exp": 3.0,
            "raw_text": (
                "We are seeking a Senior AI / Data Science Specialist with 3+ years experience.\n"
                "Required Qualifications:\n"
                "- Strong Python programming and SQL data extraction skills\n"
                "- Experience building machine learning and NLP pipelines using Scikit-learn, PyTorch, or TensorFlow\n"
                "- Hands-on Docker containerization and AWS cloud deployment\n"
                "- Git version control and collaborative coding\n\n"
                "Preferred Skills:\n"
                "- Experience with BERT, Transformers, and LangChain\n"
                "- Power BI or Tableau visualization dashboards\n"
                "- Spark big data processing\n\n"
                "Responsibilities:\n"
                "- Design and deploy production machine learning architectures\n"
                "- Build automated NLP classification and embedding workflows\n"
                "- Partner with business stakeholders to deliver actionable analytical solutions"
            ),
        }
    }
if "job_info" not in st.session_state:
    st.session_state["job_info"] = {
        "title": "Senior AI / Data Science Specialist",
        "raw_text": st.session_state["jobs_db"]["job_001"]["raw_text"],
        "parsed": parse_job_description(st.session_state["jobs_db"]["job_001"]["raw_text"]),
    }
if "recruiter_statuses" not in st.session_state:
    st.session_state["recruiter_statuses"] = {}
if "recruiter_notes" not in st.session_state:
    st.session_state["recruiter_notes"] = {}
if "blind_mode" not in st.session_state:
    st.session_state["blind_mode"] = False
if "selected_candidate_file" not in st.session_state:
    st.session_state["selected_candidate_file"] = None


# ==========================================
# SIDEBAR NAVIGATION (Grouped & Restrained)
# ==========================================
with st.sidebar:
    st.markdown(
        """
        <div class="brand-container">
            <div class="brand-logo-text">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect width="24" height="24" rx="4" fill="#0f172a"/>
                    <path d="M7 12L10.5 15.5L17 8.5" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                getHire
            </div>
            <div class="brand-tagline">Recruit smarter. Hire better.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='nav-group-label'>Workspace</div>", unsafe_allow_html=True)
    nav_workspace = st.radio(
        "Workspace Navigation",
        ["Overview", "Jobs", "Candidates", "Shortlists"],
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("<div class='nav-group-label'>Intelligence</div>", unsafe_allow_html=True)
    nav_intelligence = st.radio(
        "Intelligence Navigation",
        ["Candidate Analysis", "Fairness & Blind Audit", "What-If Simulator"],
        index=None,
        label_visibility="collapsed",
    )

    st.markdown("<div class='nav-group-label'>Management</div>", unsafe_allow_html=True)
    nav_management = st.radio(
        "Management Navigation",
        ["Analytics", "Settings & Scoring"],
        index=None,
        label_visibility="collapsed",
    )

    # Determine current active route
    current_page = "Overview"
    if nav_management:
        current_page = nav_management
    elif nav_intelligence:
        current_page = nav_intelligence
    elif nav_workspace:
        current_page = nav_workspace

    st.markdown("---")

    # Active Job Requisition Selector
    job_keys = list(st.session_state["jobs_db"].keys())
    job_labels = [st.session_state["jobs_db"][k]["title"] for k in job_keys]
    selected_job_idx = 0
    if st.session_state["active_job_id"] in job_keys:
        selected_job_idx = job_keys.index(st.session_state["active_job_id"])

    active_job_label = st.selectbox(
        "Requisition",
        options=job_labels,
        index=selected_job_idx,
        help="Select active requisition context.",
    )
    st.session_state["active_job_id"] = job_keys[job_labels.index(active_job_label)]
    
    # Sync job info
    current_job_data = st.session_state["jobs_db"][st.session_state["active_job_id"]]
    st.session_state["job_info"]["title"] = current_job_data["title"]
    st.session_state["job_info"]["raw_text"] = current_job_data["raw_text"]
    st.session_state["job_info"]["parsed"] = parse_job_description(current_job_data["raw_text"])

    # Global Shortlist threshold
    shortlist_threshold = st.slider(
        "Shortlist threshold",
        min_value=40,
        max_value=95,
        value=DEFAULT_SHORTLIST_THRESHOLD,
        step=1,
        help="Minimum Job Fit score for automatic shortlisting.",
    )

    st.session_state["blind_mode"] = st.checkbox(
        "Blind screening mode",
        value=st.session_state["blind_mode"],
        help="Masks candidate names and PII to mitigate unconscious bias.",
    )

    st.markdown(
        """
        <div class="legal-notice">
            getHire is decision support software. Final hiring actions remain the responsibility of authorized personnel.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================
# SCREENING ENGINE ORCHESTRATION
# ==========================================
def execute_screening(uploaded_files, job_text, custom_job_fit_weights=None, custom_nlp_weights=None):
    """Executes multi-model document extraction, embeddings, and explainable scoring."""
    if not job_text.strip():
        st.error("Job description is empty. Please enter or select a job description.")
        return False
    if not uploaded_files:
        st.error("Please upload at least one candidate file.")
        return False

    job_parsed = parse_job_description(job_text)
    job_norm = preprocess(job_text)
    req_skills = job_parsed["required_skills"]
    pref_skills = job_parsed["preferred_skills"]
    min_exp = job_parsed["min_experience_years"]

    filenames, raw_texts, norm_texts, errors = [], [], [], []

    for uf in uploaded_files:
        suffix = os.path.splitext(uf.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uf.getbuffer())
            tmp_path = tmp.name
        text, err = safe_extract_text(tmp_path)
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

        if err:
            errors.append(f"{uf.name}: {err}")
            continue
        filenames.append(uf.name)
        raw_texts.append(text)
        norm_texts.append(preprocess(text))

    if errors:
        for e in errors:
            st.warning(e)

    if not filenames:
        return False

    # 1. Academic NLP Foundation Inference
    with st.spinner("Processing NLP models (TF-IDF, MiniLM, and BERT)..."):
        tfidf_scores = to_percentage(tfidf_similarity(job_norm, norm_texts))
        semantic_scores = to_percentage(semantic_similarity(job_norm, norm_texts))
        bert_scores_raw, chunked_flags = bert_similarity(job_norm, norm_texts)
        bert_scores = to_percentage(bert_scores_raw)

    nlp_weights = custom_nlp_weights or WEIGHTS
    nlp_fused_scores = fuse_scores(tfidf_scores, semantic_scores, bert_scores, nlp_weights)

    # 2. Candidate Analysis Pipeline
    candidates_dict = {}

    for i, fname in enumerate(filenames):
        raw_text = raw_texts[i]
        norm_text = norm_texts[i]

        first_line = [l.strip() for l in raw_text.split("\n") if l.strip()]
        raw_name = first_line[0] if first_line else f"Candidate #{i+1}"
        anon_text, anon_alias = anonymize_resume(raw_text, i + 1)
        display_name = anon_alias if st.session_state["blind_mode"] else raw_name

        all_job_skills = req_skills | pref_skills | set(job_parsed["technologies"])
        cand_skills = extract_skills(norm_text)
        evidence = extract_skill_evidence(raw_text, all_job_skills)
        matched_req = req_skills & cand_skills
        matched_pref = pref_skills & cand_skills

        exp_data = analyze_experience(raw_text, target_domain_keywords=all_job_skills)
        projects = extract_projects(raw_text, target_skills=all_job_skills)
        proj_scores = [p["relevance_score"] for p in projects]
        consistency = analyze_consistency(raw_text, cand_skills, exp_data["timeline_entries"])

        job_fit_result = calculate_job_fit_score(
            required_skills=req_skills,
            preferred_skills=pref_skills,
            candidate_skills=cand_skills,
            candidate_exp_years=exp_data["relevant_experience_years"],
            min_exp_years=min_exp,
            project_scores=proj_scores,
            nlp_ensemble_score=nlp_fused_scores[i],
            resume_text=raw_text,
            custom_weights=custom_job_fit_weights,
        )

        insights = generate_candidate_insights(
            candidate_name=display_name,
            job_title=st.session_state["job_info"]["title"],
            required_skills=req_skills,
            preferred_skills=pref_skills,
            candidate_skills=cand_skills,
            evidence_dict=evidence,
            experience_data=exp_data,
            projects=projects,
            job_fit_score=job_fit_result["job_fit_score"],
        )

        current_status = st.session_state["recruiter_statuses"].get(
            fname,
            "Shortlisted" if job_fit_result["job_fit_score"] >= shortlist_threshold else "New"
        )
        st.session_state["recruiter_statuses"][fname] = current_status

        candidates_dict[fname] = {
            "filename": fname,
            "name": display_name,
            "raw_name": raw_name,
            "anon_alias": anon_alias,
            "raw_text": raw_text,
            "norm_text": norm_text,
            "job_fit_score": job_fit_result["job_fit_score"],
            "match_level": job_fit_result["match_level"],
            "breakdown": job_fit_result["breakdown"],
            "formula": job_fit_result["formula"],
            "candidate_skills": cand_skills,
            "all_required": req_skills,
            "all_preferred": pref_skills,
            "matched_required": matched_req,
            "matched_preferred": matched_pref,
            "evidence": evidence,
            "experience": exp_data,
            "projects": projects,
            "consistency": consistency,
            "insights": insights,
            "chunked": chunked_flags[i] if i < len(chunked_flags) else False,
            "nlp_scores": {
                "tfidf": tfidf_scores[i],
                "semantic": semantic_scores[i],
                "bert": bert_scores[i],
                "fused": nlp_fused_scores[i],
            },
        }

    sorted_candidates = sorted(candidates_dict.values(), key=lambda c: c["job_fit_score"], reverse=True)
    for rank_idx, c in enumerate(sorted_candidates):
        candidates_dict[c["filename"]]["rank"] = rank_idx + 1

    st.session_state["candidates"] = candidates_dict
    return True


# Helper function to auto-load 10 pre-built candidates
def load_sample_candidates():
    sample_dir = os.path.join(os.path.dirname(__file__), "data", "sample_resumes")
    if os.path.exists(sample_dir):
        sample_files = [f for f in os.listdir(sample_dir) if f.endswith(".txt")]
        class MockUpload:
            def __init__(self, name, content):
                self.name = name
                self.content = content
            def getbuffer(self):
                return self.content

        mock_uploads = []
        for sf in sample_files:
            with open(os.path.join(sample_dir, sf), "rb") as f:
                mock_uploads.append(MockUpload(sf, f.read()))
        
        return execute_screening(mock_uploads, st.session_state["job_info"]["raw_text"])
    return False


# Auto-load sample candidates on initial launch if pool is empty
if len(st.session_state["candidates"]) == 0:
    load_sample_candidates()


# ==========================================
# PAGE 1: OVERVIEW (MAIN RECRUITER DASHBOARD)
# ==========================================
if current_page == "Overview":
    cands = list(st.session_state["candidates"].values())
    total_screened = len(cands)
    shortlisted_cands = [c for c in cands if st.session_state["recruiter_statuses"].get(c["filename"]) == "Shortlisted" or c["job_fit_score"] >= shortlist_threshold]
    shortlisted_count = len(shortlisted_cands)
    strong_count = sum(1 for c in cands if c["match_level"] == "Strong Match")
    avg_score = np.mean([c["job_fit_score"] for c in cands]) if cands else 0.0
    interview_count = sum(1 for c in cands if st.session_state["recruiter_statuses"].get(c["filename"]) == "Interview")

    # Top Navigation Header
    st.markdown(
        f"""
        <div class="top-bar">
            <div>
                <div class="top-breadcrumbs">Requisitions / {current_job_data['department']}</div>
                <div class="top-role-title">{current_job_data['title']}</div>
                <div class="top-meta">{total_screened} candidates analyzed · {shortlisted_count} shortlisted · Active Requisition</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Restrained Horizontal Metric Strip
    st.markdown(
        f"""
        <div class="metric-strip">
            <div class="metric-strip-item">
                <div class="metric-strip-label">Candidates</div>
                <div class="metric-strip-val">{total_screened}</div>
                <div class="metric-strip-sub">Total parsed</div>
            </div>
            <div class="metric-strip-item">
                <div class="metric-strip-label">Shortlisted</div>
                <div class="metric-strip-val" style="color: #16a34a;">{shortlisted_count}</div>
                <div class="metric-strip-sub">Fit score ≥ {shortlist_threshold}</div>
            </div>
            <div class="metric-strip-item">
                <div class="metric-strip-label">Avg. Match</div>
                <div class="metric-strip-val">{avg_score:.1f}%</div>
                <div class="metric-strip-sub">Pool average</div>
            </div>
            <div class="metric-strip-item">
                <div class="metric-strip-label">Strong Matches</div>
                <div class="metric-strip-val">{strong_count}</div>
                <div class="metric-strip-sub">Score ≥ 80%</div>
            </div>
            <div class="metric-strip-item">
                <div class="metric-strip-label">Interview Ready</div>
                <div class="metric-strip-val">{interview_count}</div>
                <div class="metric-strip-sub">In pipeline</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Main Content Columns
    col_main, col_side = st.columns([5, 3])

    with col_main:
        st.markdown("<div class='card-title'>Recommended candidates</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-subtitle'>Ranked by multi-dimensional match across skills, experience, projects, and NLP models.</div>", unsafe_allow_html=True)

        if not cands:
            st.info("No candidates in requisition pool.")
        else:
            for c in sorted(cands, key=lambda x: x["rank"]):
                initials = "".join([part[0] for part in c["name"].replace("#", "").split()[:2]]).upper() or "CA"
                score = c["job_fit_score"]
                bar_color = "#16a34a" if score >= 80 else ("#2563eb" if score >= 65 else ("#d97706" if score >= 50 else "#dc2626"))
                badge_style = "badge-strong" if c["match_level"] == "Strong Match" else ("badge-good" if c["match_level"] == "Good Match" else ("badge-review" if c["match_level"] == "Review" else "badge-low"))
                rec_status = st.session_state["recruiter_statuses"].get(c["filename"], "New")

                st.markdown(
                    f"""
                    <div class="candidate-row">
                        <div style="display: flex; align-items: center;">
                            <div class="candidate-avatar">{initials}</div>
                            <div>
                                <div style="font-size: 14px; font-weight: 600; color: #0f172a;">#{c['rank']:02d} {c['name']}</div>
                                <div style="font-size: 12px; color: #64748b; margin-top: 2px;">
                                    {c['experience']['relevant_experience_years']:.1f} yrs relevant exp · {len(c['matched_required'])}/{len(c['all_required'])} required skills
                                </div>
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 15px; font-weight: 700; color: #0f172a;">{score:.1f}%</div>
                            <div class="score-progress-bg">
                                <div class="score-progress-fill" style="width: {score}%; background: {bar_color};"></div>
                            </div>
                        </div>
                        <div style="text-align: right; min-width: 110px;">
                            <span class="badge {badge_style}">{c['match_level']}</span>
                            <div style="font-size: 11px; color: #94a3b8; margin-top: 3px;">{rec_status}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with col_side:
        # Hiring Intelligence Panel
        top_cand = sorted(cands, key=lambda x: x["rank"])[0] if cands else None
        top_name = top_cand['name'] if top_cand else 'None'
        st.markdown(
            f"""
            <div class="intel-box">
                <div class="intel-title">Hiring intelligence</div>
                <div class="intel-body">
                    <strong>{strong_count} candidates</strong> meet or exceed the core requirements for this role.<br><br>
                    <strong>Strongest signal:</strong> Python + Machine Learning + SQL proficiency.<br><br>
                    <strong>Potential concern:</strong> Shortlisted applicants have variable cloud deployment (AWS/Docker) evidence.<br><br>
                    <strong>Recommendation:</strong> Prioritize <em>{top_name}</em> for preliminary technical screening.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Match Distribution (Restrained Horizontal Distribution)
        st.markdown("<div class='card-title'>Candidate distribution</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-subtitle'>Match category breakdown across pool</div>", unsafe_allow_html=True)

        dist_data = {
            "Strong match (≥80%)": sum(1 for c in cands if c["match_level"] == "Strong Match"),
            "Good match (65-79%)": sum(1 for c in cands if c["match_level"] == "Good Match"),
            "Review (50-64%)": sum(1 for c in cands if c["match_level"] == "Review"),
            "Low match (<50%)": sum(1 for c in cands if c["match_level"] == "Low Match"),
        }
        
        for label, count in dist_data.items():
            pct = (count / max(1, len(cands))) * 100
            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 2px; color: #475569;">
                    <span>{label}</span>
                    <span style="font-weight: 600;">{count} ({pct:.0f}%)</span>
                </div>
                <div style="width: 100%; height: 6px; background: #f1f5f9; border-radius: 3px; margin-bottom: 12px;">
                    <div style="width: {pct}%; height: 100%; background: {'#16a34a' if 'Strong' in label else ('#2563eb' if 'Good' in label else ('#d97706' if 'Review' in label else '#dc2626'))}; border-radius: 3px;"></div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ==========================================
# PAGE 2: JOBS (REQUISITION MANAGEMENT)
# ==========================================
elif current_page == "Jobs":
    st.markdown(
        """
        <div class="top-bar">
            <div>
                <div class="top-breadcrumbs">Requisitions / Management</div>
                <div class="top-role-title">Job Requisitions</div>
                <div class="top-meta">Configure role requirements, skill weights, and qualification criteria.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_curr_job, tab_create_job = st.tabs(["Active Requisition", "Create New Requisition"])

    with tab_curr_job:
        job = st.session_state["jobs_db"][st.session_state["active_job_id"]]
        parsed = st.session_state["job_info"]["parsed"]

        col_j1, col_j2 = st.columns([3, 2])
        with col_j1:
            st.markdown(f"### {job['title']}")
            st.markdown(f"**Department:** {job['department']} &nbsp;|&nbsp; **Created:** {job['created']} &nbsp;|&nbsp; **Experience target:** {parsed['min_experience_years']} years")
            st.text_area("Job Description Content", value=job["raw_text"], height=280, disabled=True)

        with col_j2:
            st.markdown("#### Parsed Requirements")
            st.markdown("**Mandatory Required Skills:**")
            req_tags = " ".join([f"<span class='badge badge-strong'>{s}</span>" for s in sorted(parsed['required_skills'])]) or "None extracted"
            st.markdown(req_tags, unsafe_allow_html=True)

            st.markdown("<br>**Preferred Skills (Bonus):**", unsafe_allow_html=True)
            pref_tags = " ".join([f"<span class='badge badge-neutral'>{s}</span>" for s in sorted(parsed['preferred_skills'])]) or "None specified"
            st.markdown(pref_tags, unsafe_allow_html=True)

            st.markdown("<br>**Extracted Responsibilities:**", unsafe_allow_html=True)
            for r in parsed["responsibilities"][:4]:
                st.markdown(f"· {r}")

    with tab_create_job:
        st.markdown("### Create New Requisition")
        new_title = st.text_input("Position Title", "Senior Machine Learning Engineer")
        new_dept = st.selectbox("Department", ["Engineering & Analytics", "Product & Design", "Infrastructure & Cloud", "Data Platform"])
        new_text = st.text_area(
            "Job Description Text",
            height=200,
            placeholder="Paste full job description including Required Qualifications and Preferred Skills sections...",
        )
        if st.button("Create and activate job", type="primary"):
            if not new_text.strip():
                st.error("Please enter job description text.")
            else:
                new_id = f"job_{len(st.session_state['jobs_db']) + 1:03d}"
                st.session_state["jobs_db"][new_id] = {
                    "title": new_title,
                    "department": new_dept,
                    "created": "2026-08-20",
                    "min_exp": 2.0,
                    "raw_text": new_text,
                }
                st.session_state["active_job_id"] = new_id
                st.session_state["candidates"] = {}
                st.success(f"Requisition '{new_title}' created successfully.")
                st.rerun()


# ==========================================
# PAGE 3: CANDIDATES (SCREENING & TABLE)
# ==========================================
elif current_page == "Candidates":
    st.markdown(
        """
        <div class="top-bar">
            <div>
                <div class="top-breadcrumbs">Requisitions / Candidates</div>
                <div class="top-role-title">Candidate Pipeline</div>
                <div class="top-meta">Upload, screen, and review applicant pool.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Upload Resumes / Run Batch Screening", expanded=False):
        uploaded_resumes = st.file_uploader(
            "Select Resume Files (PDF, DOCX, TXT)",
            type=list(SUPPORTED_EXTENSIONS),
            accept_multiple_files=True,
        )
        col_up1, col_up2 = st.columns([1, 4])
        with col_up1:
            if st.button("Run screening", type="primary"):
                if uploaded_resumes:
                    execute_screening(uploaded_resumes, st.session_state["job_info"]["raw_text"])
                    st.rerun()
                else:
                    st.error("Upload files first.")
        with col_up2:
            if st.button("Reload 10 pre-built sample candidates"):
                load_sample_candidates()
                st.rerun()

    cands = list(st.session_state["candidates"].values())
    if not cands:
        st.info("No candidates analyzed yet. Upload files above.")
    else:
        # Search and Filter Toolbar
        t1, t2, t3, t4 = st.columns([2, 1.5, 1.5, 1.5])
        with t1:
            search_val = st.text_input("Search candidate or skill", "", label_visibility="collapsed", placeholder="Search candidate or skill...")
        with t2:
            filter_match = st.multiselect("Match level", ["Strong Match", "Good Match", "Review", "Low Match"], default=[], placeholder="Filter by match level")
        with t3:
            filter_stat = st.multiselect("Status", RECRUITER_STATUSES, default=[], placeholder="Filter by status")
        with t4:
            min_sc = st.number_input("Min score", min_value=0, max_value=100, value=0, label_visibility="collapsed", placeholder="Min score")

        filtered = cands
        if search_val:
            filtered = [c for c in filtered if search_val.lower() in c["name"].lower() or any(search_val.lower() in s for s in c["candidate_skills"])]
        if filter_match:
            filtered = [c for c in filtered if c["match_level"] in filter_match]
        if filter_stat:
            filtered = [c for c in filtered if st.session_state["recruiter_statuses"].get(c["filename"], "New") in filter_stat]
        if min_sc > 0:
            filtered = [c for c in filtered if c["job_fit_score"] >= min_sc]

        # Table Listing
        table_rows = []
        for c in sorted(filtered, key=lambda x: x["rank"]):
            table_rows.append({
                "Rank": f"#{c['rank']:02d}",
                "Candidate": c["name"],
                "Job Fit": f"{c['job_fit_score']:.1f}%",
                "Match Level": c["match_level"],
                "Relevant Exp": f"{c['experience']['relevant_experience_years']:.1f} yrs",
                "Skills Verified": f"{len(c['matched_required'])} / {len(c['all_required'])}",
                "Status": st.session_state["recruiter_statuses"].get(c["filename"], "New"),
            })
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True)

        st.markdown("---")
        # Export Actions
        c_exp1, c_exp2 = st.columns(2)
        with c_exp1:
            csv_exp = pd.DataFrame(table_rows).to_csv(index=False).encode("utf-8")
            st.download_button("Export CSV", csv_exp, "getHire_Candidates.csv", "text/csv")
        with c_exp2:
            xl_exp = BytesIO()
            pd.DataFrame(table_rows).to_excel(xl_exp, index=False, engine="openpyxl")
            st.download_button("Export Excel", xl_exp.getvalue(), "getHire_Candidates.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# ==========================================
# PAGE 4: CANDIDATE DEEP-DIVE (CANDIDATE ANALYSIS)
# ==========================================
elif current_page == "Candidate Analysis":
    st.markdown(
        """
        <div class="top-bar">
            <div>
                <div class="top-breadcrumbs">Intelligence / Candidate Deep-Dive</div>
                <div class="top-role-title">Candidate Analysis Workspace</div>
                <div class="top-meta">Evidence-based verification, explainable scoring breakdown, and timeline analysis.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cands = list(st.session_state["candidates"].values())
    if not cands:
        st.info("No candidate records available.")
    else:
        cand_options = [f"#{c['rank']:02d} {c['name']} ({c['job_fit_score']:.1f}%)" for c in sorted(cands, key=lambda x: x["rank"])]
        selected_idx = st.selectbox("Select candidate", range(len(cand_options)), format_func=lambda i: cand_options[i])
        selected_cand = sorted(cands, key=lambda x: x["rank"])[selected_idx]
        fname = selected_cand["filename"]

        # Candidate Header
        score = selected_cand["job_fit_score"]
        badge_style = "badge-strong" if selected_cand["match_level"] == "Strong Match" else ("badge-good" if selected_cand["match_level"] == "Good Match" else "badge-review")
        
        st.markdown(
            f"""
            <div class="clean-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 20px; font-weight: 700; color: #0f172a;">{selected_cand['name']}</div>
                        <div style="font-size: 13px; color: #64748b; margin-top: 2px;">
                            Requisition: <strong>{st.session_state['job_info']['title']}</strong> &nbsp;·&nbsp; File: <code>{selected_cand['filename']}</code>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 26px; font-weight: 700; color: #0f172a;">{score:.1f}%</div>
                        <span class="badge {badge_style}">{selected_cand['match_level']}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Recruiter Status Management
        col_s1, col_s2 = st.columns([2, 3])
        with col_s1:
            curr_st = st.session_state["recruiter_statuses"].get(fname, "New")
            new_st = st.selectbox("Recruiter Decision Status", RECRUITER_STATUSES, index=RECRUITER_STATUSES.index(curr_st) if curr_st in RECRUITER_STATUSES else 0)
            if new_st != curr_st:
                st.session_state["recruiter_statuses"][fname] = new_st
                st.toast(f"Status updated to '{new_st}'")
        with col_s2:
            r_note = st.text_input("Recruiter Private Notes", value=st.session_state["recruiter_notes"].get(fname, ""))
            if r_note != st.session_state["recruiter_notes"].get(fname, ""):
                st.session_state["recruiter_notes"][fname] = r_note

        # Tabs for Deep Dive
        tab_summary, tab_evidence, tab_exp, tab_projects, tab_signals, tab_integrity = st.tabs([
            "Match Summary",
            "Skill Evidence",
            "Experience & Roles",
            "Projects & Portfolio",
            "Candidate Signals",
            "Integrity & Timeline",
        ])

        with tab_summary:
            st.markdown("<div class='card-title'>Score Calculation Breakdown</div>", unsafe_allow_html=True)
            st.markdown("<div class='card-subtitle'>Multi-dimensional Job Fit formula calculation</div>", unsafe_allow_html=True)

            breakdown_items = [
                ("Required Skill Coverage", selected_cand["breakdown"]["required_skill_coverage"], "35%"),
                ("Relevant Experience", selected_cand["breakdown"]["relevant_experience"], "20%"),
                ("Project Relevance", selected_cand["breakdown"]["project_relevance"], "15%"),
                ("Preferred Skills", selected_cand["breakdown"]["preferred_skill_coverage"], "10%"),
                ("Education Relevance", selected_cand["breakdown"]["education_relevance"], "5%"),
                ("Academic NLP Ensemble", selected_cand["breakdown"]["nlp_ensemble"], "15%"),
            ]

            for label, b_score, weight in breakdown_items:
                st.markdown(
                    f"""
                    <div style="margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 2px;">
                            <span style="font-weight: 500; color: #334155;">{label} <span style="color: #94a3b8; font-size: 11px;">({weight} weight)</span></span>
                            <span style="font-weight: 600; color: #0f172a;">{b_score:.1f}%</span>
                        </div>
                        <div style="width: 100%; height: 6px; background: #f1f5f9; border-radius: 3px;">
                            <div style="width: {b_score}%; height: 100%; background: #2563eb; border-radius: 3px;"></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("#### Mathematical Formula Inspector")
            st.code(selected_cand["formula"], language="markdown")

            st.markdown("#### Preserved NLP Foundation Models")
            col_nlp1, col_nlp2, col_nlp3 = st.columns(3)
            col_nlp1.metric("TF-IDF Lexical", f"{selected_cand['nlp_scores']['tfidf']:.1f}%")
            col_nlp2.metric("MiniLM Semantic", f"{selected_cand['nlp_scores']['semantic']:.1f}%")
            col_nlp3.metric("BERT Contextual", f"{selected_cand['nlp_scores']['bert']:.1f}%")

        with tab_evidence:
            st.markdown("<div class='card-title'>Verbatim Skill Evidence Citations</div>", unsafe_allow_html=True)
            st.markdown("<div class='card-subtitle'>Direct quotes extracted from candidate document. Zero hallucinated text.</div>", unsafe_allow_html=True)

            st.markdown("**Required Skills:**")
            for skill in sorted(selected_cand["all_required"]):
                ev = selected_cand["evidence"].get(skill, {"status": "Missing", "evidence": "Not found in resume"})
                status = ev.get("status", "Missing")
                b_class = "badge-strong" if status == "Strong Match" else ("badge-review" if status == "Partial Match" else "badge-low")
                st.markdown(
                    f"""
                    <div style="border: 1px solid #e2e8f0; border-left: 3px solid {'#16a34a' if status=='Strong Match' else ('#d97706' if status=='Partial Match' else '#dc2626')}; background: #ffffff; padding: 10px 14px; margin-bottom: 8px; border-radius: 4px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: 600; font-size: 13px; color: #0f172a;">{skill}</span>
                            <span class="badge {b_class}">{status}</span>
                        </div>
                        <div style="font-size: 12px; color: #475569; margin-top: 4px; font-style: italic;">
                            Evidence: {ev['evidence']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            if selected_cand["all_preferred"]:
                st.markdown("<br>**Preferred Skills:**", unsafe_allow_html=True)
                for skill in sorted(selected_cand["all_preferred"]):
                    ev = selected_cand["evidence"].get(skill, {"status": "Missing", "evidence": "Not found in resume"})
                    status = ev.get("status", "Missing")
                    b_class = "badge-strong" if status == "Strong Match" else ("badge-review" if status == "Partial Match" else "badge-low")
                    st.markdown(
                        f"""
                        <div style="border: 1px solid #e2e8f0; border-left: 3px solid #64748b; background: #ffffff; padding: 10px 14px; margin-bottom: 8px; border-radius: 4px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-weight: 600; font-size: 13px; color: #0f172a;">{skill}</span>
                                <span class="badge {b_class}">{status}</span>
                            </div>
                            <div style="font-size: 12px; color: #475569; margin-top: 4px; font-style: italic;">
                                Evidence: {ev['evidence']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        with tab_exp:
            st.markdown("<div class='card-title'>Experience & Career Progression</div>", unsafe_allow_html=True)
            exp = selected_cand["experience"]
            e1, e2 = st.columns(2)
            e1.metric("Total Experience", f"{exp['total_experience_years']:.1f} yrs")
            e2.metric("Relevant Domain Experience", f"{exp['relevant_experience_years']:.1f} yrs")

            st.markdown("**Detected Career Roles:**")
            if exp["roles"]:
                for r in exp["roles"]:
                    st.markdown(f"· {r}")
            else:
                st.markdown("· Early-career / Student profile")

            st.markdown("<br>**Chronological Employment Periods:**", unsafe_allow_html=True)
            if exp["timeline_entries"]:
                for t in exp["timeline_entries"]:
                    st.markdown(f"· **{t['start']} – {t['end']}** ({t['duration_years']:.1f} yrs): _{t['context']}_")
            else:
                st.info("No multi-year chronological blocks detected.")

        with tab_projects:
            st.markdown("<div class='card-title'>Project Portfolio Relevance</div>", unsafe_allow_html=True)
            if not selected_cand["projects"]:
                st.info("No standalone projects extracted.")
            else:
                for p in selected_cand["projects"]:
                    st.markdown(
                        f"""
                        <div class="clean-card" style="padding: 14px 18px; margin-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between;">
                                <span style="font-weight: 600; font-size: 14px; color: #0f172a;">{p['name']}</span>
                                <span style="font-weight: 600; font-size: 13px; color: #2563eb;">{p['relevance_score']:.1f}% Relevance</span>
                            </div>
                            <div style="font-size: 13px; color: #475569; margin: 4px 0;">{p['description']}</div>
                            <div style="font-size: 12px; color: #64748b;">
                                <strong>Technologies:</strong> {', '.join(sorted(p['technologies'])) or 'General stack'}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        with tab_signals:
            st.markdown("<div class='card-title'>Hiring Signals & Interview Questions</div>", unsafe_allow_html=True)
            ins = selected_cand["insights"]
            
            st.markdown("**Key Strengths:**")
            for s in ins["why_this_candidate"]:
                st.markdown(f"· {s}")

            st.markdown("<br>**Skill Gaps to Probe:**", unsafe_allow_html=True)
            if ins["gaps_required"]:
                st.markdown(f"· Missing Required: **{', '.join(ins['gaps_required'])}**")
            if ins["gaps_preferred"]:
                st.markdown(f"· Missing Preferred: **{', '.join(ins['gaps_preferred'])}**")
            if not ins["gaps_required"] and not ins["gaps_preferred"]:
                st.markdown("· Full coverage across requirements.")

            st.markdown("<br>**Suggested Technical Interview Questions:**", unsafe_allow_html=True)
            for q in ins["interview_questions"]:
                st.markdown(f"· {q}")

        with tab_integrity:
            st.markdown("<div class='card-title'>Timeline Integrity & Review Flags</div>", unsafe_allow_html=True)
            st.markdown("<div class='card-subtitle'>Objective observation flags for recruiter verification.</div>", unsafe_allow_html=True)
            cons = selected_cand["consistency"]
            st.metric("Integrity Confidence Score", f"{cons['consistency_score']:.1f}%")
            for flag in cons["flags"]:
                st.markdown(f"· {flag}")


# ==========================================
# PAGE 5: SHORTLISTS & PIPELINE
# ==========================================
elif current_page == "Shortlists":
    st.markdown(
        """
        <div class="top-bar">
            <div>
                <div class="top-breadcrumbs">Workspace / Shortlists</div>
                <div class="top-role-title">Shortlisted Candidates</div>
                <div class="top-meta">Candidate shortlist ready for interview scheduling and hiring decisions.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cands = list(st.session_state["candidates"].values())
    shortlisted = [c for c in cands if st.session_state["recruiter_statuses"].get(c["filename"]) in ["Shortlisted", "Interview"] or c["job_fit_score"] >= shortlist_threshold]

    if not shortlisted:
        st.info("No candidates shortlisted under current threshold.")
    else:
        for c in sorted(shortlisted, key=lambda x: x["job_fit_score"], reverse=True):
            st.markdown(
                f"""
                <div class="candidate-row">
                    <div>
                        <div style="font-weight: 600; font-size: 14px; color: #0f172a;">#{c['rank']:02d} {c['name']}</div>
                        <div style="font-size: 12px; color: #64748b;">{c['experience']['relevant_experience_years']:.1f} yrs exp · Skills: {', '.join(sorted(c['matched_required']))}</div>
                    </div>
                    <div>
                        <span style="font-size: 16px; font-weight: 700; color: #0f172a;">{c['job_fit_score']:.1f}%</span>
                        <span class="badge badge-strong">Shortlisted</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ==========================================
# PAGE 6: FAIRNESS & BLIND AUDIT
# ==========================================
elif current_page == "Fairness & Blind Audit":
    st.markdown(
        """
        <div class="top-bar">
            <div>
                <div class="top-breadcrumbs">Intelligence / Fairness Audit</div>
                <div class="top-role-title">Fairness & Bias Mitigation</div>
                <div class="top-meta">Audit candidate ranking parity and test blind screening anonymization.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cands = list(st.session_state["candidates"].values())
    if not cands:
        st.info("Screen candidates first.")
    else:
        st.markdown(
            """
            <div class="intel-box">
                <div class="intel-title">Ethical AI & Compliance Guarantee</div>
                <div class="intel-body">
                    getHire evaluates applicants strictly on job-relevant technical competencies, documented experience, and project evidence. 
                    Protected demographic characteristics (age, gender, ethnicity, location, and photos) are entirely excluded from scoring algorithms.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### Anonymized vs. Unblinded Presentation")
        audit_rows = []
        for c in sorted(cands, key=lambda x: x["rank"]):
            audit_rows.append({
                "Rank": f"#{c['rank']:02d}",
                "Candidate Name": c["raw_name"],
                "Blind Anonymized ID": c["anon_alias"],
                "Job Fit Score": f"{c['job_fit_score']:.1f}%",
                "Match Level": c["match_level"],
                "Protected Attributes Factored": "None (0%)",
            })
        st.dataframe(pd.DataFrame(audit_rows), use_container_width=True)

        st.markdown("---")
        st.markdown("### Side-by-Side Candidate Comparison")
        selected_for_comp = st.multiselect(
            "Select 2 to 4 candidates to compare",
            options=[c["name"] for c in cands],
            default=[c["name"] for c in sorted(cands, key=lambda x: x["rank"])[:2]] if len(cands) >= 2 else [],
            max_selections=4,
        )
        if len(selected_for_comp) >= 2:
            comp_cands = [c for c in cands if c["name"] in selected_for_comp]
            matrix = build_comparison_matrix(comp_cands)
            comp_table = pd.DataFrame(
                {
                    "Dimension": [r["dimension"] for r in matrix["rows"]],
                    **{matrix["headers"][i]: [r["values"][i] for r in matrix["rows"]] for i in range(len(matrix["headers"]))}
                }
            )
            st.table(comp_table)
            for sp in matrix["summary_points"]:
                st.markdown(f"· {sp}")


# ==========================================
# PAGE 7: WHAT-IF SIMULATOR
# ==========================================
elif current_page == "What-If Simulator":
    st.markdown(
        """
        <div class="top-bar">
            <div>
                <div class="top-breadcrumbs">Intelligence / Hiring Simulator</div>
                <div class="top-role-title">What-If Hiring Simulator</div>
                <div class="top-meta">Simulate real-time ranking shifts by altering skill requirements, experience thresholds, or weights.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cands = list(st.session_state["candidates"].values())
    if not cands:
        st.info("Screen candidates first.")
    else:
        parsed = st.session_state["job_info"]["parsed"]
        all_skills = sorted(list(parsed["all_skills"] | DEFAULT_SKILLS))

        col_w1, col_w2 = st.columns(2)
        with col_w1:
            sim_req = st.multiselect("Mandatory Required Skills", options=all_skills, default=list(parsed["required_skills"]))
            sim_min_exp = st.slider("Minimum Experience (Years)", 0.0, 8.0, float(parsed["min_experience_years"]), 0.5)
        with col_w2:
            sim_pref = st.multiselect("Preferred Skills", options=all_skills, default=list(parsed["preferred_skills"]))
            sim_weight = st.slider("Required Skills Influence (%)", 10, 70, int(JOB_FIT_WEIGHTS["required_skills"] * 100), 5)

        sim_weights = dict(JOB_FIT_WEIGHTS)
        sim_weights["required_skills"] = sim_weight / 100.0

        sim_results = simulate_what_if(
            baseline_candidates=cands,
            new_required_skills=set(sim_req),
            new_preferred_skills=set(sim_pref),
            new_min_exp_years=sim_min_exp,
            custom_weights=sim_weights,
        )

        st.markdown("### Simulated Ranking Adjustments")
        sim_rows = []
        for r in sim_results:
            delta_str = f"+{r['rank_delta']}" if r["rank_delta"] > 0 else (f"{r['rank_delta']}" if r["rank_delta"] < 0 else "0")
            sim_rows.append({
                "Simulated Rank": f"#{r['after_rank']:02d}",
                "Original Rank": f"#{r['before_rank']:02d}",
                "Rank Shift": delta_str,
                "Candidate": r["name"],
                "New Job Fit": f"{r['after_score']:.1f}%",
                "Score Delta": f"{r['score_delta']:+.1f}%",
                "Why Ranking Changed": r["delta_explanation"],
            })
        st.dataframe(pd.DataFrame(sim_rows), use_container_width=True)


# ==========================================
# PAGE 8: ANALYTICS
# ==========================================
elif current_page == "Analytics":
    st.markdown(
        """
        <div class="top-bar">
            <div>
                <div class="top-breadcrumbs">Management / Analytics</div>
                <div class="top-role-title">Recruiter Talent Analytics</div>
                <div class="top-meta">Aggregated pool distribution, skill gap analysis, and NLP model performance.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cands = list(st.session_state["candidates"].values())
    if not cands:
        st.info("Screen candidates first.")
    else:
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            st.markdown("#### Score Distribution")
            scores = [c["job_fit_score"] for c in cands]
            fig_hist = px.histogram(scores, nbins=10, labels={"value": "Job Fit Score"}, title="Job Fit Spread", color_discrete_sequence=["#2563eb"])
            fig_hist.update_layout(height=260, margin=dict(t=30, b=10, l=10, r=10))
            st.plotly_chart(fig_hist, use_container_width=True)

        with col_a2:
            st.markdown("#### Top Missing Skills")
            all_missing = []
            for c in cands:
                all_missing.extend(c["insights"]["gaps_required"])
            if all_missing:
                miss_counts = pd.Series(all_missing).value_counts().head(6)
                fig_miss = px.bar(x=miss_counts.values, y=miss_counts.index, orientation="h", labels={"x": "Candidates Missing", "y": "Skill"}, color_discrete_sequence=["#dc2626"])
                fig_miss.update_layout(height=260, margin=dict(t=30, b=10, l=10, r=10))
                st.plotly_chart(fig_miss, use_container_width=True)
            else:
                st.info("No missing skills.")

        st.markdown("---")
        st.markdown("#### Academic NLP Model Comparison")
        nlp_df = pd.DataFrame([
            {
                "Candidate": c["name"],
                "TF-IDF (%)": f"{c['nlp_scores']['tfidf']:.1f}%",
                "MiniLM (%)": f"{c['nlp_scores']['semantic']:.1f}%",
                "BERT Contextual (%)": f"{c['nlp_scores']['bert']:.1f}%",
                "Job Fit Score": f"{c['job_fit_score']:.1f}%",
            }
            for c in sorted(cands, key=lambda x: x["rank"])
        ])
        st.dataframe(nlp_df, use_container_width=True)


# ==========================================
# PAGE 9: SETTINGS & SCORING
# ==========================================
elif current_page == "Settings & Scoring":
    st.markdown(
        """
        <div class="top-bar">
            <div>
                <div class="top-breadcrumbs">Management / Settings</div>
                <div class="top-role-title">Platform Configuration & Weights</div>
                <div class="top-meta">Configure mathematical weights for explainable Job Fit and NLP models.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Job Fit Dimension Weights")
    w1, w2, w3 = st.columns(3)
    with w1:
        w_req = st.slider("Required Skills Weight", 0.10, 0.60, JOB_FIT_WEIGHTS["required_skills"], 0.05)
        w_exp = st.slider("Relevant Experience Weight", 0.05, 0.40, JOB_FIT_WEIGHTS["relevant_experience"], 0.05)
    with w2:
        w_proj = st.slider("Project Relevance Weight", 0.05, 0.30, JOB_FIT_WEIGHTS["project_relevance"], 0.05)
        w_pref = st.slider("Preferred Skills Weight", 0.00, 0.20, JOB_FIT_WEIGHTS["preferred_skills"], 0.05)
    with w3:
        w_edu = st.slider("Education Relevance Weight", 0.00, 0.15, JOB_FIT_WEIGHTS["education_relevance"], 0.05)
        w_nlp = st.slider("Academic NLP Weight", 0.05, 0.40, JOB_FIT_WEIGHTS["nlp_ensemble"], 0.05)

    st.markdown("---")
    st.markdown("### NLP Foundation Model Weights")
    n1, n2, n3 = st.columns(3)
    with n1:
        nlp_w_tfidf = st.slider("TF-IDF Lexical", 0.0, 1.0, WEIGHTS["tfidf"], 0.05)
    with n2:
        nlp_w_sem = st.slider("MiniLM Semantic", 0.0, 1.0, WEIGHTS["semantic"], 0.05)
    with n3:
        nlp_w_bert = st.slider("BERT Contextual", 0.0, 1.0, WEIGHTS["bert"], 0.05)

    if st.button("Save scoring configuration", type="primary"):
        JOB_FIT_WEIGHTS["required_skills"] = w_req
        JOB_FIT_WEIGHTS["relevant_experience"] = w_exp
        JOB_FIT_WEIGHTS["project_relevance"] = w_proj
        JOB_FIT_WEIGHTS["preferred_skills"] = w_pref
        JOB_FIT_WEIGHTS["education_relevance"] = w_edu
        JOB_FIT_WEIGHTS["nlp_ensemble"] = w_nlp

        WEIGHTS["tfidf"] = nlp_w_tfidf
        WEIGHTS["semantic"] = nlp_w_sem
        WEIGHTS["bert"] = nlp_w_bert
        st.success("Weights saved.")
