"""AI-Based Resume Screening System & Recruitment Intelligence Platform package."""
from src.extractors import extract_text, safe_extract_text
from src.preprocessing import preprocess, clean_whitespace, normalize_for_matching
from src.skills import extract_skills, compare_skills
from src.tfidf_matcher import tfidf_similarity
from src.semantic_matcher import semantic_similarity
from src.bert_matcher import bert_similarity
from src.scoring import to_percentage, fuse_scores
from src.ranking import build_ranking_table, shortlist
from src.explain import match_category, build_explanation
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
