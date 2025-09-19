#!/usr/bin/env python3
# MonochromeMatch — ATS Resume Screener
import os
import io
import time
import json
import tempfile
from typing import List, Dict, Any

import streamlit as st
from utils.parsers import extract_text_from_file
from utils.analysis import analyze_all_resumes
from utils.scoring import rank_candidates
from utils.llm import set_api_key_from_env

st.set_page_config(page_title="MonochromeMatch — ATS Resume Screener", page_icon="🖤", layout="wide")

# --- Pure black & white styling ---
st.markdown('''
    <style>
        :root { 
            --mm-black: #000000; 
            --mm-white: #ffffff; 
            --mm-gray: #f2f2f2; 
            --mm-mid: #e8e8e8;
        }
        .stApp { background-color: var(--mm-white) !important; }
        header, .st-emotion-cache-18ni7ap, .st-emotion-cache-1629p8f { background: var(--mm-white) !important; }
        .block-container { padding-top: 1.5rem; }
        h1, h2, h3, h4, h5, h6, p, li, label, span, div { color: var(--mm-black) !important; }
        /* cards */
        .mm-card {
            border: 1px solid var(--mm-mid);
            border-radius: 16px;
            padding: 18px;
            background: var(--mm-white);
            box-shadow: 0 2px 0 var(--mm-gray);
        }
        /* buttons (black outlines only) */
        .stButton>button {
            color: var(--mm-black) !important;
            background: var(--mm-white) !important;
            border: 1px solid var(--mm-black) !important;
            border-radius: 999px !important;
        }
        .stFileUploader label div { color: var(--mm-black) !important; }
        .stProgress>div>div>div { background: var(--mm-black) !important; }
        .stTabs [data-baseweb="tab-list"] button { color: var(--mm-black) !important; }
        .stDataFrame, .dataframe { filter: grayscale(100%); }
    </style>
''', unsafe_allow_html=True)

st.title("🖤 MonochromeMatch — ATS Resume Screener")
st.caption("Black & white, enterprise-ready resume-to-JD fit analysis with ATS-style scoring and targeted improvement tips.")

with st.sidebar:
    st.subheader("Setup")
    st.write("Provide a Job Description (paste text or upload a file). Then upload multiple resumes (PDF/DOCX).")
    use_env_key = st.checkbox("Use OPENAI_API_KEY from environment", value=True)
    manual_key = None
    if not use_env_key:
        manual_key = st.text_input("Or paste an OpenAI API key (optional)", type="password")
    model_name = st.text_input("Model (when using OpenAI, optional)", value="gpt-4.1-mini")
    temp = st.slider("LLM temperature", 0.0, 1.0, 0.2, 0.05)

    st.divider()
    st.markdown("**Theme:** Black & White only.")

# JD input
jd_col, opt_col = st.columns([3, 2])
with jd_col:
    jd_text = st.text_area("Paste Job Description (JD)", height=220, placeholder="Paste the job description here...")
with opt_col:
    jd_file = st.file_uploader("Or upload JD file (.pdf / .docx / .txt)", type=["pdf", "docx", "txt"], accept_multiple_files=False)

if jd_file is not None and not jd_text:
    jd_text = extract_text_from_file(jd_file)

st.markdown("---")
st.subheader("Upload Resumes")
resume_files = st.file_uploader("Upload multiple resumes (.pdf / .docx)", type=["pdf", "docx"], accept_multiple_files=True)

st.markdown("---")

if st.button("Analyze resumes", type="primary"):

    if not jd_text or (not resume_files or len(resume_files) == 0):
        st.error("Please provide a JD and at least one resume.")
        st.stop()

    with st.status("Processing files...", expanded=False) as status:
        # Prepare OpenAI
        api_key_used = None
        if use_env_key:
            api_key_used = set_api_key_from_env()
        else:
            if manual_key:
                os.environ["OPENAI_API_KEY"] = manual_key
                api_key_used = manual_key

        # Extract texts
        resume_texts: Dict[str, str] = {}
        for f in resume_files:
            try:
                text = extract_text_from_file(f)
            except Exception as e:
                text = ""
                st.warning(f"Could not parse {f.name}: {e}")
            resume_texts[f.name] = text

        status.update(label="Analyzing with rules + (optional) LLM…", state="running")

        # Analysis
        results = analyze_all_resumes(
            resume_texts=resume_texts,
            jd_text=jd_text,
            llm_model=model_name.strip() if model_name else None,
            llm_temperature=float(temp),
            use_llm=bool(api_key_used)
        )

        # Ranking
        ranked = rank_candidates(results)

        status.update(label="Done", state="complete")

    # Display results
    st.subheader("🏁 Best Fit")
    top_candidate = ranked[0]
    st.success(f"**Top Match:** {top_candidate['filename']} — ATS Score: {top_candidate['ats_score']:.1f} / 100")

    st.subheader("Leaderboard")
    st.dataframe(
        { "Resume": [r["filename"] for r in ranked],
          "ATS Score": [round(r["ats_score"], 1) for r in ranked],
          "Keyword Match": [round(r["components"].get("keyword_score", 0), 1) for r in ranked],
          "Semantic Match": [round(r["components"].get("semantic_score", 0), 1) for r in ranked],
          "Hard Reqs Coverage": [round(r["components"].get("hard_requirements_score", 0), 1) for r in ranked],
        },
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    st.subheader("Per-Resume Reports")

    for row in ranked:
        with st.expander(f"{row['filename']} — ATS: {row['ats_score']:.1f}"):
            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown("**Component Scores**")
                st.json({k: round(v, 2) for k, v in row["components"].items()})
            with c2:
                st.markdown("**Strengths**")
                st.write("- " + "\n- ".join(row.get("strengths", []) or ["—"]))
                st.markdown("**Gaps / Improvements**")
                st.write("- " + "\n- ".join(row.get("improvements", []) or ["—"]))
                st.markdown("**Missing Keywords**")
                miss = row.get("missing_keywords", [])
                st.write(", ".join(miss) if miss else "—")

    # Download artifacts
    export = {
        "job_description": jd_text,
        "results": ranked,
    }
    b = io.BytesIO()
    b.write(json.dumps(export, ensure_ascii=False, indent=2).encode("utf-8"))
    b.seek(0)
    st.download_button("Download JSON report", b, file_name="monochrome_match_report.json", mime="application/json")

else:
    st.info("Paste or upload the JD, upload multiple resumes, and click **Analyze resumes**.")
