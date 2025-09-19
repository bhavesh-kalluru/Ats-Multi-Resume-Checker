from typing import Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .text_utils import normalize, keyword_set

def tfidf_cosine(a: str, b: str) -> float:
    a = normalize(a); b = normalize(b)
    if not a or not b:
        return 0.0
    vect = TfidfVectorizer(stop_words="english", ngram_range=(1,2), min_df=1)
    try:
        X = vect.fit_transform([a, b])
        cs = cosine_similarity(X[0], X[1]).ravel()[0]
        return float(cs * 100.0)
    except Exception:
        return 0.0

def keyword_overlap(a: str, b: str) -> float:
    sa = keyword_set(a); sb = keyword_set(b)
    if not sa or not sb:
        return 0.0
    inter = len(sa & sb)
    score = inter / len(sb) * 100.0
    return float(min(score, 100.0))

def hard_requirements_coverage(resume_text: str, hard_reqs: list) -> float:
    if not hard_reqs:
        return 0.0
    rset = keyword_set(resume_text)
    hits = 0
    for req in hard_reqs:
        tokens = set(req.lower().split())
        if tokens & rset:
            hits += 1
    return float(hits / len(hard_reqs) * 100.0)

def compute_ats_components(resume_text: str, jd_text: str, hard_reqs: list) -> Dict[str, float]:
    return {
        "semantic_score": tfidf_cosine(resume_text, jd_text),               # 0..100
        "keyword_score": keyword_overlap(resume_text, jd_text),              # 0..100
        "hard_requirements_score": hard_requirements_coverage(resume_text, hard_reqs), # 0..100
    }

def combine_components(components: Dict[str, float]) -> float:
    # Weighted sum; tweak as needed
    w_sem, w_kw, w_hr = 0.45, 0.35, 0.20
    score = (components.get("semantic_score", 0) * w_sem +
             components.get("keyword_score", 0) * w_kw +
             components.get("hard_requirements_score", 0) * w_hr)
    return float(max(0.0, min(score, 100.0)))

def rank_candidates(results: list) -> list:
    return sorted(results, key=lambda r: r["ats_score"], reverse=True)
