import re
from typing import List, Set

def normalize(text: str) -> str:
    text = text or ""
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def tokens(text: str) -> List[str]:
    text = text.lower()
    # keep words and +/#
    toks = re.findall(r"[a-zA-Z0-9\+\#\-\.]+", text)
    return toks

def keyword_set(text: str) -> Set[str]:
    toks = tokens(text)
    return set(toks)

def extract_hard_requirements(jd_text: str) -> List[str]:
    jd = jd_text.lower()
    # crude heuristic: capture bullet lists near "must", "requirements", "qualifications"
    import re
    blocks = []
    for head in ["must have", "requirements", "qualifications", "required", "you must", "need to have"]:
        if head in jd:
            idx = jd.index(head)
            snippet = jd[idx: idx + 1000]
            blocks.append(snippet)
    bullets = []
    for b in blocks:
        bullets.extend(re.findall(r"(?:^|\n)[\-\*\u2022]\s*(.+)", b))
    # dedupe / fallback
    if not bullets:
        # take top N frequent keywords as pseudo-reqs
        words = tokens(jd_text)
        # pick specific-looking tokens (avoid stopwords here for simplicity)
        candidates = [w for w in words if len(w) >= 4]
        bullets = list(dict.fromkeys(candidates[:10]))
    cleaned = [re.sub(r"[\.\;\:\,]+$", "", x).strip() for x in bullets if x.strip()]
    return cleaned[:20]
