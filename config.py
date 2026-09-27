"""Central configuration for the AI-Powered Recruitment Intelligence Platform."""
import os as _os

# ==========================================
# 1. ACADEMIC NLP MODEL FUSION WEIGHTS (Preserved)
# ==========================================
WEIGHTS = {
    "tfidf": 0.25,
    "semantic": 0.50,
    "bert": 0.25,
}

# ==========================================
# 2. EXPLAINABLE JOB FIT SCORING WEIGHTS
# ==========================================
JOB_FIT_WEIGHTS = {
    "required_skills": 0.35,      # Core mandatory technical skills
    "relevant_experience": 0.20,  # Relevant domain experience
    "project_relevance": 0.15,    # Project portfolio match
    "preferred_skills": 0.10,     # Bonus / nice-to-have skills
    "education_relevance": 0.05,  # Academic background alignment
    "nlp_ensemble": 0.15,         # TF-IDF + MiniLM + BERT deep semantic foundation
}

# ==========================================
# 3. MATCH CATEGORY & FIT LEVEL THRESHOLDS (0-100)
# ==========================================
THRESHOLDS = {
    "strong": 80,    # Strong Match: Excellent fit across required dimensions
    "good": 65,      # Good Match: Meets core criteria with minor gaps
    "review": 50,    # Review / Moderate: Partial match, requires recruiter review
    "moderate": 50,  # Backward compatibility with existing tests
    # Below 50 is Low Match
}

# ==========================================
# 4. RECRUITER WORKFLOW STATUSES
# ==========================================
RECRUITER_STATUSES = [
    "New",
    "Under Review",
    "Shortlisted",
    "Interview",
    "On Hold",
    "Rejected",
]

# Shortlist threshold default
DEFAULT_SHORTLIST_THRESHOLD = 65

# ==========================================
# 5. MODEL PATHS & CHUNKING (Local cache first)
# ==========================================
_BASE_DIR = _os.path.dirname(_os.path.abspath(__file__))
_LOCAL_SEMANTIC = _os.path.join(_BASE_DIR, "models", "all-MiniLM-L6-v2")
_LOCAL_BERT = _os.path.join(_BASE_DIR, "models", "bert-base-uncased")

SEMANTIC_MODEL_NAME = _LOCAL_SEMANTIC if _os.path.exists(_LOCAL_SEMANTIC) else "all-MiniLM-L6-v2"
BERT_MODEL_NAME = _LOCAL_BERT if _os.path.exists(_LOCAL_BERT) else "bert-base-uncased"

BERT_MAX_TOKENS = 512
BERT_CHUNK_OVERLAP = 50

# Supported file types
SUPPORTED_EXTENSIONS = {"pdf", "docx", "txt"}

# ==========================================
# 6. EXTENSIVE TECHNICAL SKILL TAXONOMY
# ==========================================
DEFAULT_SKILLS = {
    # Programming & Scripting
    "python", "r", "java", "c++", "c", "c#", ".net", "node.js", "javascript", "typescript",
    "go", "golang", "rust", "scala", "kotlin", "ruby", "php", "sql", "nosql", "bash", "shell",
    
    # Machine Learning & AI
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "reinforcement learning", "genai", "generative ai", "llms", "large language models",
    "transformers", "bert", "gpt", "rag", "retrieval augmented generation", "fine-tuning",
    "predictive modeling", "feature engineering", "time series", "classification", "clustering",
    
    # Frameworks & Libraries
    "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn", "pandas", "numpy", "scipy",
    "xgboost", "lightgbm", "catboost", "spacy", "nltk", "huggingface", "opencv", "langchain", "llamaindex",
    
    # Data Engineering & Databases
    "spark", "pyspark", "hadoop", "kafka", "airflow", "databricks", "snowflake", "bigquery",
    "postgresql", "mysql", "mongodb", "cassandra", "redis", "elasticsearch", "sqlite",
    
    # Cloud & DevOps
    "aws", "amazon web services", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s",
    "ci/cd", "git", "github", "gitlab", "linux", "terraform", "ansible", "mlops", "kubeflow", "mlflow",
    
    # Web & API Frameworks
    "fastapi", "flask", "django", "streamlit", "react", "vue", "angular", "html", "css", "rest api", "graphql",
    
    # Business Intelligence & Visualization
    "tableau", "power bi", "matplotlib", "seaborn", "plotly", "excel", "d3.js", "looker",
}

