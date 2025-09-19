# MonochromeMatch — ATS Resume Screener (Streamlit)

A black-and-white, enterprise-style Streamlit app to evaluate multiple resumes against a Job Description (JD). It ranks candidates by an ATS-style score, lists strengths, identifies gaps, and suggests improvements. Supports **PDF** and **DOCX** resumes. Optional **OpenAI** integration enhances the analysis.

## Features
- Upload **multiple resumes** (PDF/DOCX) + a **JD** (paste or file).
- ATS-style score combining **semantic match**, **keyword overlap**, and **hard-requirements coverage**.
- Per-resume report with strengths, missing keywords, and improvement tips.
- Unique, **monochrome UI** tuned for large screens and enterprise use.
- Optional OpenAI LLM analysis (uses `OPENAI_API_KEY`). Falls back to rule-based analysis if no key is set.

## Quickstart (macOS)
```bash
# 1) Create a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate

# 2) Install deps
pip install -r requirements.txt

# 3) (Optional) Provide your OpenAI key
export OPENAI_API_KEY="sk-..."
# Or create a .env file and export before running

# 4) Launch
streamlit run app.py
```

## Using in PyCharm
- Open the folder as a project.
- Set the interpreter to your `.venv`.
- Add an environment variable `OPENAI_API_KEY` under **Run/Debug Configurations** if you want LLM analysis.
- Run `app.py`.

## Notes
- **DOC (legacy .doc)** files are not supported out-of-the-box. Convert to **DOCX** or PDF before uploading.
- If you **don’t** set `OPENAI_API_KEY`, the app still works via robust **rule-based** scoring.
- Default model is `gpt-4.1-mini` (update as needed). You can change it in the sidebar.

## How scoring works
- **Semantic match (45%)** – TF‑IDF cosine similarity between resume and JD.
- **Keyword overlap (35%)** – Overlap of token sets.
- **Hard requirements (20%)** – Heuristic extraction of required bullets from the JD and coverage in the resume.

You can tune these weights in `utils/scoring.py`.

## File layout
```
.
├── app.py
├── requirements.txt
├── README.md
├── prompts.py
├── utils
│   ├── analysis.py
│   ├── llm.py
│   ├── parsers.py
│   ├── scoring.py
│   └── text_utils.py
└── .streamlit
    └── config.toml
```

## Security
- **Never** hardcode your API key. The app reads it from the environment. You can also paste it in the sidebar just for a local session.

## License
MIT
