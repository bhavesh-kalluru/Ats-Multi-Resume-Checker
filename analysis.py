from typing import Dict, List, Any
from .text_utils import normalize, keyword_set, extract_hard_requirements
from .scoring import compute_ats_components, combine_components
from .llm import llm_resume_analysis

def rule_based_improvements(resume_text: str, jd_text: str, missing_keywords: List[str]) -> List[str]:
    tips = []
    if len(resume_text) < 500:
        tips.append("Expand experience details with measurable results (add metrics and scope).")
    if any(k in jd_text.lower() for k in ["sql", "python", "java", "cloud", "aws", "gcp", "azure"]):
        for kw in ["sql", "python", "java", "aws", "gcp", "azure"]:
            if kw in jd_text.lower() and kw not in resume_text.lower():
                tips.append(f"Add evidence of {kw.upper()} (projects, certifications, or achievements).")
    for mk in missing_keywords[:10]:
        tips.append(f"Address missing keyword: '{mk}'. Add relevant experience or training.")
    return list(dict.fromkeys(tips))

def missing_keywords(resume_text: str, jd_text: str) -> List[str]:
    rset = keyword_set(resume_text)
    jset = keyword_set(jd_text)
    missing = [w for w in sorted(jset) if w not in rset and len(w) > 3]
    # keep top 25 unique-looking tokens
    return missing[:25]

def analyze_single_resume(filename: str, resume_text: str, jd_text: str, llm_model: str, llm_temperature: float, use_llm: bool) -> Dict[str, Any]:
    jd_norm = normalize(jd_text)
    r_norm = normalize(resume_text)
    hard_reqs = extract_hard_requirements(jd_norm)
    components = compute_ats_components(r_norm, jd_norm, hard_reqs)
    ats = combine_components(components)

    llm_out = None
    if use_llm:
        llm_out = llm_resume_analysis(r_norm, jd_norm, model=llm_model, temperature=llm_temperature)

    miss = missing_keywords(r_norm, jd_norm)

    strengths = []
    improvements = []
    if llm_out:
        strengths = llm_out.get("strengths", [])[:10]
        improvements = llm_out.get("improvements", [])[:10]
        # Prefer LLM missing keywords when available
        mk = llm_out.get("missing_keywords", [])
        if mk:
            miss = mk[:25]
    else:
        improvements = rule_based_improvements(r_norm, jd_norm, miss)

    return {
        "filename": filename,
        "ats_score": ats,
        "components": components,
        "missing_keywords": miss,
        "strengths": strengths,
        "improvements": improvements,
    }

def analyze_all_resumes(resume_texts: Dict[str, str], jd_text: str, llm_model: str = "gpt-4.1-mini", llm_temperature: float = 0.2, use_llm: bool = False) -> List[Dict[str, Any]]:
    results = []
    for fname, text in resume_texts.items():
        results.append(analyze_single_resume(
            filename=fname,
            resume_text=text,
            jd_text=jd_text,
            llm_model=llm_model,
            llm_temperature=llm_temperature,
            use_llm=use_llm
        ))
    return results
