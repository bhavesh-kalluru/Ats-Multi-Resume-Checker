import os
import io
import tempfile
from typing import Union
from pypdf import PdfReader
import docx2txt

TEXT_EXTS = {".txt"}
DOCX_EXTS = {".docx"}
PDF_EXTS = {".pdf"}

def _extract_pdf(file_like) -> str:
    reader = PdfReader(file_like)
    out = []
    for page in reader.pages:
        try:
            out.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(out)

def _extract_docx(file_like) -> str:
    # docx2txt expects a path; write to temp
    with tempfile.NamedTemporaryFile(delete=True, suffix=".docx") as tmp:
        tmp.write(file_like.read())
        tmp.flush()
        text = docx2txt.process(tmp.name) or ""
    return text

def extract_text_from_file(uploaded_file) -> str:
    """Accepts Streamlit UploadedFile or file-like; returns text."""
    name = getattr(uploaded_file, "name", "uploaded")
    suffix = os.path.splitext(name)[1].lower()

    # Reset pointer for repeated reads
    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)

    if suffix in PDF_EXTS:
        return _extract_pdf(uploaded_file)
    elif suffix in DOCX_EXTS:
        return _extract_docx(uploaded_file)
    elif suffix in TEXT_EXTS:
        return uploaded_file.read().decode("utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file type: {suffix}. Use PDF or DOCX.")
