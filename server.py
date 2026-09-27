"""CAREERPILOT Backend REST API Server powered by FastAPI.
Serves candidate screening, explainable job fit intelligence, what-if simulations, and recruiter workflow.
"""
import os
import tempfile
import numpy as np
import pandas as pd
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel


# Project configurations & models
from config import (
    DEFAULT_SHORTLIST_THRESHOLD,
    WEIGHTS,
    JOB_FIT_WEIGHTS,
    THRESHOLDS,
    RECRUITER_STATUSES,
    DEFAULT_SKILLS,
)
from src.extractors import safe_extract_text
from src.preprocessing import preprocess
from src.tfidf_matcher import tfidf_similarity
from src.semantic_matcher import semantic_similarity
from src.bert_matcher import bert_similarity
from src.scoring import to_percentage, fuse_scores
from src.skills import extract_skills

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


app = FastAPI(title="CAREERPILOT API", version="2.0.0")

# Enable CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session database
DB = {
    "active_job_id": "job_001",
    "jobs": {
        "job_001": {
            "id": "job_001",
            "title": "Senior AI / Data Science Specialist",
            "department": "Engineering & Analytics",
            "created": "2026-08-20",
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
    },
    "candidates": {},
    "recruiter_statuses": {},
    "recruiter_notes": {},
    "shortlist_threshold": DEFAULT_SHORTLIST_THRESHOLD,
    "blind_mode": False,
    "job_fit_weights": dict(JOB_FIT_WEIGHTS),
    "nlp_weights": dict(WEIGHTS),
}


def _process_candidates(raw_files_data: list[tuple[str, str]], job_text: str):
    """Core screening execution engine."""
    job_parsed = parse_job_description(job_text)
    job_norm = preprocess(job_text)
    req_skills = job_parsed["required_skills"]
    pref_skills = job_parsed["preferred_skills"]
    min_exp = job_parsed["min_experience_years"]

    filenames = [f[0] for f in raw_files_data]
    raw_texts = [f[1] for f in raw_files_data]
    norm_texts = [preprocess(t) for t in raw_texts]

    # Model inference
    tfidf_scores = to_percentage(tfidf_similarity(job_norm, norm_texts))
    semantic_scores = to_percentage(semantic_similarity(job_norm, norm_texts))
    bert_scores_raw, chunked_flags = bert_similarity(job_norm, norm_texts)
    bert_scores = to_percentage(bert_scores_raw)

    nlp_fused_scores = fuse_scores(tfidf_scores, semantic_scores, bert_scores, DB["nlp_weights"])

    candidates_dict = {}
    active_job = DB["jobs"][DB["active_job_id"]]

    for i, fname in enumerate(filenames):
        raw_text = raw_texts[i]
        norm_text = norm_texts[i]

        first_line = [l.strip() for l in raw_text.split("\n") if l.strip()]
        raw_name = first_line[0] if first_line else f"Candidate #{i+1}"
        anon_text, anon_alias = anonymize_resume(raw_text, i + 1)
        display_name = anon_alias if DB["blind_mode"] else raw_name

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
            custom_weights=DB["job_fit_weights"],
        )

        insights = generate_candidate_insights(
            candidate_name=display_name,
            job_title=active_job["title"],
            required_skills=req_skills,
            preferred_skills=pref_skills,
            candidate_skills=cand_skills,
            evidence_dict=evidence,
            experience_data=exp_data,
            projects=projects,
            job_fit_score=job_fit_result["job_fit_score"],
        )

        current_status = DB["recruiter_statuses"].get(
            fname,
            "Shortlisted" if job_fit_result["job_fit_score"] >= DB["shortlist_threshold"] else "New"
        )
        DB["recruiter_statuses"][fname] = current_status

        candidates_dict[fname] = {
            "filename": fname,
            "name": display_name,
            "raw_name": raw_name,
            "anon_alias": anon_alias,
            "raw_text": raw_text,
            "norm_text": norm_text,
            "job_fit_score": float(job_fit_result["job_fit_score"]),
            "match_level": job_fit_result["match_level"],
            "breakdown": job_fit_result["breakdown"],
            "formula": job_fit_result["formula"],
            "candidate_skills": sorted(list(cand_skills)),
            "all_required": sorted(list(req_skills)),
            "all_preferred": sorted(list(pref_skills)),
            "matched_required": sorted(list(matched_req)),
            "matched_preferred": sorted(list(matched_pref)),
            "evidence": evidence,
            "experience": exp_data,
            "projects": projects,
            "consistency": consistency,
            "insights": insights,
            "chunked": chunked_flags[i] if i < len(chunked_flags) else False,
            "nlp_scores": {
                "tfidf": float(tfidf_scores[i]),
                "semantic": float(semantic_scores[i]),
                "bert": float(bert_scores[i]),
                "fused": float(nlp_fused_scores[i]),
            },
        }

    # Sort & assign ranks
    sorted_candidates = sorted(candidates_dict.values(), key=lambda c: c["job_fit_score"], reverse=True)
    for rank_idx, c in enumerate(sorted_candidates):
        candidates_dict[c["filename"]]["rank"] = rank_idx + 1

    DB["candidates"] = candidates_dict
    return candidates_dict


# Auto-load sample candidates on startup
def _load_initial_samples():
    sample_dir = os.path.join(os.path.dirname(__file__), "data", "sample_resumes")
    if os.path.exists(sample_dir):
        sample_files = [f for f in os.listdir(sample_dir) if f.endswith(".txt")]
        files_data = []
        for sf in sample_files:
            with open(os.path.join(sample_dir, sf), "r", encoding="utf-8", errors="ignore") as f:
                files_data.append((sf, f.read()))
        if files_data:
            _process_candidates(files_data, DB["jobs"]["job_001"]["raw_text"])

_load_initial_samples()


# ==========================================
# API ENDPOINTS
# ==========================================

@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "CAREERPILOT API"}


@app.get("/api/overview")
def get_overview():
    active_job = DB["jobs"][DB["active_job_id"]]
    cands = list(DB["candidates"].values())
    total = len(cands)
    shortlisted = sum(1 for c in cands if DB["recruiter_statuses"].get(c["filename"]) == "Shortlisted" or c["job_fit_score"] >= DB["shortlist_threshold"])
    strong_count = sum(1 for c in cands if c["match_level"] == "Strong Match")
    good_count = sum(1 for c in cands if c["match_level"] == "Good Match")
    review_count = sum(1 for c in cands if c["match_level"] == "Review")
    low_count = sum(1 for c in cands if c["match_level"] == "Low Match")
    interview_count = sum(1 for c in cands if DB["recruiter_statuses"].get(c["filename"]) == "Interview")
    avg_score = float(np.mean([c["job_fit_score"] for c in cands])) if cands else 0.0

    return {
        "job": active_job,
        "metrics": {
            "total_candidates": total,
            "shortlisted_count": shortlisted,
            "avg_match": round(avg_score, 1),
            "strong_matches": strong_count,
            "interview_ready": interview_count,
        },
        "distribution": {
            "strong": strong_count,
            "good": good_count,
            "review": review_count,
            "low": low_count,
        },
        "blind_mode": DB["blind_mode"],
        "shortlist_threshold": DB["shortlist_threshold"],
    }


@app.get("/api/jobs")
def list_jobs():
    return {
        "jobs": list(DB["jobs"].values()),
        "active_job_id": DB["active_job_id"],
        "parsed_active": parse_job_description(DB["jobs"][DB["active_job_id"]]["raw_text"]),
    }


class JobCreateRequest(BaseModel):
    title: str
    department: str
    raw_text: str


@app.post("/api/jobs")
def create_job(req: JobCreateRequest):
    new_id = f"job_{len(DB['jobs']) + 1:03d}"
    DB["jobs"][new_id] = {
        "id": new_id,
        "title": req.title,
        "department": req.department,
        "created": "2026-08-26",
        "min_exp": 2.0,
        "raw_text": req.raw_text,
    }
    DB["active_job_id"] = new_id
    DB["candidates"] = {}
    return {"message": "Job created successfully", "job_id": new_id}


@app.post("/api/jobs/activate/{job_id}")
def activate_job(job_id: str):
    if job_id not in DB["jobs"]:
        raise HTTPException(status_code=404, detail="Job not found")
    DB["active_job_id"] = job_id
    # Re-screen candidates against new active job if candidates exist
    if DB["candidates"]:
        files_data = [(c["filename"], c["raw_text"]) for c in DB["candidates"].values()]
        _process_candidates(files_data, DB["jobs"][job_id]["raw_text"])
    return {"message": f"Activated job {job_id}"}


@app.get("/api/candidates")
def get_candidates():
    cands = list(DB["candidates"].values())
    sorted_cands = sorted(cands, key=lambda x: x["rank"])
    for c in sorted_cands:
        c["recruiter_status"] = DB["recruiter_statuses"].get(c["filename"], "New")
        c["recruiter_notes"] = DB["recruiter_notes"].get(c["filename"], "")
    return {"candidates": sorted_cands}


@app.get("/api/candidate/{filename}")
def get_candidate_detail(filename: str):
    if filename not in DB["candidates"]:
        raise HTTPException(status_code=404, detail="Candidate not found")
    cand = dict(DB["candidates"][filename])
    cand["recruiter_status"] = DB["recruiter_statuses"].get(filename, "New")
    cand["recruiter_notes"] = DB["recruiter_notes"].get(filename, "")
    return cand


@app.post("/api/screen")
async def screen_resumes(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    active_job = DB["jobs"][DB["active_job_id"]]
    files_data = []

    for uf in files:
        suffix = os.path.splitext(uf.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await uf.read())
            tmp_path = tmp.name
        text, err = safe_extract_text(tmp_path)
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
        if not err and text:
            files_data.append((uf.filename, text))

    if not files_data:
        raise HTTPException(status_code=400, detail="No valid text could be extracted from uploaded files")

    _process_candidates(files_data, active_job["raw_text"])
    return {"message": f"Successfully screened {len(files_data)} resumes", "count": len(files_data)}


@app.post("/api/load-sample")
def load_sample_candidates():
    sample_dir = os.path.join(os.path.dirname(__file__), "data", "sample_resumes")
    if not os.path.exists(sample_dir):
        raise HTTPException(status_code=404, detail="Sample directory not found")
    sample_files = [f for f in os.listdir(sample_dir) if f.endswith(".txt")]
    files_data = []
    for sf in sample_files:
        with open(os.path.join(sample_dir, sf), "r", encoding="utf-8", errors="ignore") as f:
            files_data.append((sf, f.read()))
    _process_candidates(files_data, DB["jobs"][DB["active_job_id"]]["raw_text"])
    return {"message": f"Loaded and screened {len(files_data)} sample candidates", "count": len(files_data)}


class StatusUpdateRequest(BaseModel):
    filename: str
    status: str
    notes: Optional[str] = None


@app.post("/api/status")
def update_status(req: StatusUpdateRequest):
    if req.status in RECRUITER_STATUSES:
        DB["recruiter_statuses"][req.filename] = req.status
    if req.notes is not None:
        DB["recruiter_notes"][req.filename] = req.notes
    return {"message": "Status updated successfully"}


class WhatIfRequest(BaseModel):
    required_skills: List[str]
    preferred_skills: List[str]
    min_exp_years: float
    required_skills_weight: Optional[float] = None


@app.post("/api/what-if")
def run_what_if(req: WhatIfRequest):
    cands = list(DB["candidates"].values())
    if not cands:
        return {"results": []}

    # Format baseline candidates for simulation engine
    formatted_cands = []
    for c in cands:
        formatted_cands.append({
            "name": c["name"],
            "rank": c["rank"],
            "job_fit_score": c["job_fit_score"],
            "candidate_skills": set(c["candidate_skills"]),
            "all_required": set(c["all_required"]),
            "experience": c["experience"],
            "projects": c["projects"],
            "breakdown": c["breakdown"],
            "raw_text": c["raw_text"],
        })

    weights = dict(DB["job_fit_weights"])
    if req.required_skills_weight is not None:
        weights["required_skills"] = req.required_skills_weight

    results = simulate_what_if(
        baseline_candidates=formatted_cands,
        new_required_skills=set(req.required_skills),
        new_preferred_skills=set(req.preferred_skills),
        new_min_exp_years=req.min_exp_years,
        custom_weights=weights,
    )
    return {"results": results}


@app.get("/api/analytics")
def get_analytics():
    cands = list(DB["candidates"].values())
    if not cands:
        return {"scores": [], "missing_skills": [], "nlp_comparison": []}

    scores = [c["job_fit_score"] for c in cands]
    all_missing = []
    for c in cands:
        all_missing.extend(c["insights"]["gaps_required"])

    missing_counts = []
    if all_missing:
        counts = pd.Series(all_missing).value_counts().head(8)
        missing_counts = [{"skill": k, "count": int(v)} for k, v in counts.items()]

    nlp_comp = [
        {
            "name": c["name"],
            "tfidf": c["nlp_scores"]["tfidf"],
            "semantic": c["nlp_scores"]["semantic"],
            "bert": c["nlp_scores"]["bert"],
            "job_fit": c["job_fit_score"],
        }
        for c in sorted(cands, key=lambda x: x["rank"])
    ]

    return {
        "scores": scores,
        "missing_skills": missing_counts,
        "nlp_comparison": nlp_comp,
    }


class SettingsUpdateRequest(BaseModel):
    job_fit_weights: dict
    nlp_weights: dict
    shortlist_threshold: int
    blind_mode: bool


@app.get("/api/settings")
def get_settings():
    return {
        "job_fit_weights": DB["job_fit_weights"],
        "nlp_weights": DB["nlp_weights"],
        "shortlist_threshold": DB["shortlist_threshold"],
        "blind_mode": DB["blind_mode"],
        "statuses": RECRUITER_STATUSES,
        "default_skills": sorted(list(DEFAULT_SKILLS)),
    }


@app.post("/api/settings")
def update_settings(req: SettingsUpdateRequest):
    DB["job_fit_weights"] = req.job_fit_weights
    DB["nlp_weights"] = req.nlp_weights
    DB["shortlist_threshold"] = req.shortlist_threshold
    DB["blind_mode"] = req.blind_mode

    # Recalculate candidates if present
    if DB["candidates"]:
        files_data = [(c["filename"], c["raw_text"]) for c in DB["candidates"].values()]
        _process_candidates(files_data, DB["jobs"][DB["active_job_id"]]["raw_text"])

    return {"message": "Settings updated and applied successfully"}


# ==========================================
# STATIC FRONTEND SERVING (For Unified Production Deployments)
# ==========================================
_frontend_dist = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.exists(_frontend_dist):
    _assets_dir = os.path.join(_frontend_dist, "assets")
    if os.path.exists(_assets_dir):
        app.mount("/assets", StaticFiles(directory=_assets_dir), name="assets")

    @app.get("/", include_in_schema=False)
    async def serve_root():
        index_file = os.path.join(_frontend_dist, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "CAREERPILOT API is running"}

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):

        target = os.path.join(_frontend_dist, full_path)
        if full_path and os.path.exists(target) and os.path.isfile(target):
            return FileResponse(target)
        index_file = os.path.join(_frontend_dist, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "Frontend not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

