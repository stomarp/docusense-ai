"""
DocuSense AI - Main FastAPI Application

This file:
- Handles file uploads
- Extracts document text
- Performs rule-based compliance analysis
- Runs ML section classification
- Saves documents and reports to PostgreSQL
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from pathlib import Path
import uuid

# DOCX reader (aliased to avoid name collision with DB model)
from docx import Document as DocxDocument

# PDF reader
from pypdf import PdfReader

# SQLAlchemy
from sqlalchemy.orm import Session

# Database setup
from backend.app.db.database import Base, engine, get_db
from backend.app.db.models import Document as DBDocument, AnalysisReport

# ML classifier
from backend.app.ml.section_classifier import SectionClassifier


# -------------------------------------------------------
# App Initialization
# -------------------------------------------------------

app = FastAPI(
    title="DocuSense AI",
    description="AI document risk analyzer backend for HR policies, leases, contracts, and compliance documents",
    version="0.1.0"
)

# Create DB tables if not present
Base.metadata.create_all(bind=engine)

# Load ML model once at startup
section_classifier = SectionClassifier()
try:
    section_classifier.load()
except Exception as e:
    print(f"[ML] Section classifier not loaded: {e}")


# -------------------------------------------------------
# File Storage Setup
# -------------------------------------------------------

UPLOAD_DIR = Path("backend/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------------------------------------
# Text Extraction Helpers
# -------------------------------------------------------

def extract_text_from_docx(file_path: Path) -> str:
    """Extract text from DOCX file."""
    doc = DocxDocument(str(file_path))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text from text-based PDF."""
    reader = PdfReader(str(file_path))
    pages_text = []

    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text.strip():
            pages_text.append(page_text)

    return "\n".join(pages_text)


def split_into_chunks(text: str) -> list[str]:
    """Split document into paragraph chunks for ML."""
    return [line.strip() for line in text.split("\n") if line.strip()]


# -------------------------------------------------------
# Rule-Based Logic
# -------------------------------------------------------

REQUIRED_SECTIONS = {
    "code_of_conduct": {
        "label": "Code of Conduct",
        "keywords": ["code of conduct", "conduct policy"]
    },
    "anti_harassment": {
        "label": "Anti-Harassment Policy",
        "keywords": ["anti-harassment", "harassment", "equal opportunity"]
    },
    "leave_policy": {
        "label": "Leave Policy",
        "keywords": ["leave policy", "vacation", "sick leave", "pto"]
    },
    "working_hours": {
        "label": "Working Hours & Attendance",
        "keywords": ["working hours", "attendance", "timekeeping"]
    },
    "disciplinary_action": {
        "label": "Disciplinary Action Policy",
        "keywords": ["disciplinary", "termination", "corrective action"]
    },
}

RISKY_PHRASES = [
    "may",
    "might",
    "as needed",
    "at management discretion",
    "reasonable",
]


def normalize_text(text: str) -> str:
    return text.lower()


def find_missing_sections(text: str):
    lower_text = normalize_text(text)
    missing = []

    for key, data in REQUIRED_SECTIONS.items():
        if not any(keyword in lower_text for keyword in data["keywords"]):
            missing.append({
                "key": key,
                "label": data["label"],
                "severity": "HIGH"
            })

    return missing


def count_risky_phrases(text: str):
    lower_text = normalize_text(text)
    return {
        phrase: lower_text.count(phrase)
        for phrase in RISKY_PHRASES
        if lower_text.count(phrase) > 0
    }


def calculate_risk_score(missing_sections, risky_phrases):
    score = len(missing_sections) * 20
    score += sum(risky_phrases.values())
    return min(score, 100)

def build_ml_summary(ml_sections: list[dict]) -> list[dict]:
    """
    Group ML predictions by label and compute a small summary:
    - count
    - average confidence
    - top example snippet
    """
    grouped: dict[str, list[dict]] = {}

    for item in ml_sections:
        label = item["label"]
        grouped.setdefault(label, []).append(item)

    summary = []
    for label, items in grouped.items():
        avg_conf = sum(x["confidence"] for x in items) / len(items)
        top_item = max(items, key=lambda x: x["confidence"])

        summary.append({
            "label": label,
            "count": len(items),
            "avg_confidence": round(avg_conf, 4),
            "top_example": top_item["text_preview"],
            "top_confidence": top_item["confidence"],
        })

    # Sort by avg confidence desc
    summary.sort(key=lambda x: x["avg_confidence"], reverse=True)
    return summary


# -------------------------------------------------------
# Health Endpoint
# -------------------------------------------------------

@app.get("/health")
def health_check():
    return {"status": "DocuSense AI is running"}


# -------------------------------------------------------
# Upload Endpoint
# -------------------------------------------------------

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    unique_id = uuid.uuid4().hex
    original_name = file.filename or "uploaded_file"
    ext = Path(original_name).suffix

    stored_filename = f"{unique_id}{ext}"
    stored_path = UPLOAD_DIR / stored_filename

    contents = await file.read()
    stored_path.write_bytes(contents)

    # Save to DB
    doc = DBDocument(
        original_filename=original_name,
        stored_filename=stored_filename,
        file_type=ext.lstrip(".") if ext else "unknown",
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {
        "message": "File uploaded and saved",
        "document_id": doc.id,
        "stored_filename": stored_filename
    }


@app.post("/extract-text/{stored_filename}")
def extract_text(stored_filename: str):
    """
    Extract text from a previously uploaded file.

    For now, we support:
    - .docx (Word documents)
    - .txt  (plain text)

    Later we will add:
    - PDF extraction
    """
    file_path = UPLOAD_DIR / stored_filename

    # If file does not exist, return a 404 error
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Detect file type by extension
    ext = file_path.suffix.lower()

    if ext == ".docx":
      text = extract_text_from_docx(file_path)
    elif ext == ".pdf":
      text = extract_text_from_pdf(file_path)
    elif ext == ".txt":
      text = file_path.read_text(encoding="utf-8", errors="ignore")
    else:
      raise HTTPException(
        status_code=400,
        detail="Unsupported file type for text extraction (supported: .docx, .pdf, .txt)"
    )

    # Return extracted text (we'll store it in DB in next steps)
    return {
        "stored_filename": stored_filename,
        "characters": len(text),
        "preview": text[:500],   # show only first 500 chars
        "text": text             # full text (ok for now; later we may not return full)
    }


# -------------------------------------------------------
# Analyze Endpoint
# -------------------------------------------------------

@app.post("/analyze/{stored_filename}")
def analyze_document(
    stored_filename: str,
    db: Session = Depends(get_db)
):
    file_path = UPLOAD_DIR / stored_filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    ext = file_path.suffix.lower()

    if ext == ".docx":
        text = extract_text_from_docx(file_path)
    elif ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif ext == ".txt":
        text = file_path.read_text(encoding="utf-8", errors="ignore")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Rule-based analysis
    missing_sections = find_missing_sections(text)
    risky_phrases = count_risky_phrases(text)
    risk_score = calculate_risk_score(missing_sections, risky_phrases)

    # ML Section Classification

    # ML Section Classification (optional)
    ml_sections = []
    ml_summary = []

    if section_classifier.is_ready():
      chunks = split_into_chunks(text)

    # Predict for all chunks
      raw_predictions = section_classifier.predict_many(chunks)

    # Keep only confident predictions
      CONF_THRESHOLD = 0.35  # you can tune this
      ml_sections = [p for p in raw_predictions if p["confidence"] >= CONF_THRESHOLD]

    # Limit raw output (avoid huge response)
      ml_sections = sorted(ml_sections, key=lambda x: x["confidence"], reverse=True)[:10]

    # Build grouped summary
      ml_summary = build_ml_summary(ml_sections)
   


    # Find document in DB
    doc = db.query(DBDocument).filter(
        DBDocument.stored_filename == stored_filename
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found in DB")

    # Save report
    report = AnalysisReport(
        document_id=doc.id,
        risk_score=risk_score,
        missing_sections=missing_sections,
        risky_phrases=risky_phrases,
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return {
    "document_id": doc.id,
    "report_id": report.id,
    "report": {
        "risk_score": risk_score,
        "missing_sections": missing_sections,
        "risky_phrases": risky_phrases,
    },
    "ml_summary": ml_summary,          # 👈 ADD THIS
    "ml_sections": ml_sections,        # 👈 KEEP THIS
    "metadata": {
        "extracted_characters": len(text),
        "analysis_type": "rule_based_v1 + ml_classifier",
        "ml_conf_threshold": CONF_THRESHOLD,          # 👈 ADD THIS
        "ml_sections_returned": len(ml_sections),     # 👈 ADD THIS
    }
}

    
# -------------------------------------------------------
# Documents + Reports History Endpoints
# -------------------------------------------------------

@app.get("/documents")
def list_documents(db: Session = Depends(get_db)):
    """
    List all uploaded documents.
    For each document, include the most recent report (if it exists).
    """
    docs = db.query(DBDocument).order_by(DBDocument.id.desc()).all()
    results = []

    for doc in docs:
        latest_report = (
            db.query(AnalysisReport)
            .filter(AnalysisReport.document_id == doc.id)
            .order_by(AnalysisReport.id.desc())
            .first()
        )

        results.append({
            "document_id": doc.id,
            "original_filename": doc.original_filename,
            "stored_filename": doc.stored_filename,
            "file_type": doc.file_type,
            "created_at": str(doc.created_at),
            "latest_report": None if not latest_report else {
                "report_id": latest_report.id,
                "risk_score": latest_report.risk_score,
                "created_at": str(latest_report.created_at),
            }
        })

    return results


@app.get("/documents/{document_id}/reports")
def list_reports(document_id: int, db: Session = Depends(get_db)):
    """
    List all analysis reports for a specific document (report history).
    """
    doc = db.query(DBDocument).filter(DBDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    reports = (
        db.query(AnalysisReport)
        .filter(AnalysisReport.document_id == document_id)
        .order_by(AnalysisReport.id.desc())
        .all()
    )

    return {
        "document_id": doc.id,
        "original_filename": doc.original_filename,
        "stored_filename": doc.stored_filename,
        "reports": [
            {
                "report_id": r.id,
                "risk_score": r.risk_score,
                "missing_sections": r.missing_sections,
                "risky_phrases": r.risky_phrases,
                "created_at": str(r.created_at),
            }
            for r in reports
        ],
    }