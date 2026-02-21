# Entry point for DocuGuard backend
# Import FastAPI class from the fastapi library
# FastAPI is the framework we use to build our backend APIs
from fastapi import FastAPI
# Import UploadFile and File to handle file uploads
from fastapi import UploadFile, File
# Standard library imports for file handling
from pathlib import Path
import uuid

# To return proper HTTP error messages
from fastapi import HTTPException

# Library to read .docx files
from docx import Document
# PDF reader library (for text-based PDFs)
from pypdf import PdfReader

from backend.app.db.database import Base, engine
from backend.app.db import models  # noqa: F401

# SQLAlchemy session for DB operations
from sqlalchemy.orm import Session

# FastAPI dependency injection helper
from fastapi import Depends

# Our DB session provider + models
from backend.app.db.database import get_db
from backend.app.db.models import Document, AnalysisReport


# Create an instance of the FastAPI application
# This 'app' object represents our backend server
app = FastAPI(
    title="DocuGuard",                  # Name of the application
    description="HR Policy Compliance Analyzer Backend",
    version="0.1.0"
)
Base.metadata.create_all(bind=engine)

# Folder where uploaded files will be stored
UPLOAD_DIR = Path("backend/uploads")
def extract_text_from_docx(file_path: Path) -> str:
    """
    Extract all text from a .docx file and return it as a single string.
    """
    doc = Document(str(file_path))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)

def extract_text_from_pdf(file_path: Path) -> str:
    """
    Extract text from a PDF file and return it as a single string.

    NOTE:
    - This works well for PDFs that contain selectable text.
    - For scanned/image-only PDFs, this may return empty text.
    """
    reader = PdfReader(str(file_path))
    pages_text = []

    # Loop through each page and extract text
    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text.strip():
            pages_text.append(page_text)

    return "\n".join(pages_text)

def normalize_text(text: str) -> str:
    """
    Make text easier to search by converting it to lowercase.
    """
    return text.lower()

def find_missing_sections(text: str) -> list[dict]:
    lower_text = normalize_text(text)
    missing = []

    for section_key, section_data in REQUIRED_SECTIONS.items():
        keywords = section_data["keywords"]
        label = section_data["label"]

        if not any(keyword in lower_text for keyword in keywords):
            missing.append({
                "key": section_key,
                "label": label,
                "severity": "HIGH"
            })

    return missing



def count_risky_phrases(text: str) -> dict[str, int]:
    """
    Count how many times risky phrases appear in the document.

    Returns:
        A dict like {"may": 10, "as needed": 2}
        Only phrases that appear at least once are included.
    """
    lower_text = normalize_text(text)
    counts: dict[str, int] = {}

    for phrase in RISKY_PHRASES:
        c = lower_text.count(phrase)
        if c > 0:
            counts[phrase] = c

    return counts

def calculate_risk_score(missing_sections: list, risky_phrase_counts: dict) -> int:
    """
    Very simple scoring logic:
    - Each missing section = +20
    - Each risky phrase occurrence = +1
    """
    score = 0

    score += len(missing_sections) * 20
    score += sum(risky_phrase_counts.values())

    return min(score, 100)  # cap at 100

# Ensure the upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------
# Basic rule-based checks (V1)
# -------------------------------------------------------------------

# These are HR policy sections we expect in most employee handbooks/policies.
# We will search the document text for these keywords.
# Human-friendly structure for required sections
REQUIRED_SECTIONS = {
    "code_of_conduct": {
        "label": "Code of Conduct",
        "keywords": ["code of conduct", "conduct policy"]
    },
    "anti_harassment": {
        "label": "Anti-Harassment Policy",
        "keywords": ["anti-harassment", "harassment", "anti discrimination", "equal opportunity"]
    },
    "leave_policy": {
        "label": "Leave Policy",
        "keywords": ["leave policy", "vacation", "sick leave", "pto", "paid time off"]
    },
    "working_hours": {
        "label": "Working Hours & Attendance",
        "keywords": ["working hours", "attendance", "work schedule", "timekeeping"]
    },
    "disciplinary_action": {
        "label": "Disciplinary Action Policy",
        "keywords": ["disciplinary", "termination", "discipline", "corrective action"]
    },
}


# Words/phrases that often indicate vague or risky language in policies.
RISKY_PHRASES = [
    "may",
    "might",
    "as needed",
    "at management discretion",
    "depending",
    "from time to time",
    "usually",
    "reasonable",
    "best effort",
]

# This is a simple GET API endpoint
# Endpoint URL: /health
# Purpose: Check if the backend server is running correctly
@app.get("/health")
def health_check():
    """
    Health check endpoint.

    This endpoint is used to verify that:
    - The FastAPI server is running
    - The application is reachable

    It returns a simple JSON response.
    """

    # Return a JSON response
    # This will be shown in the browser or API client
    return {
        "status": "DocuGuard is running"
    }

# This endpoint allows users to upload a document file

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload document endpoint.

    1) Save file to disk
    2) Insert document metadata into DB
    3) Return document_id + file info
    """

    # Generate unique file name
    unique_id = uuid.uuid4().hex
    original_name = file.filename or "uploaded_file"
    ext = Path(original_name).suffix

    stored_filename = f"{unique_id}{ext}"
    stored_path = UPLOAD_DIR / stored_filename

    # Save file to disk
    contents = await file.read()
    stored_path.write_bytes(contents)

    # ---------------------------
    # SAVE DOCUMENT TO DATABASE
    # ---------------------------
    doc = Document(
        original_filename=original_name,
        stored_filename=stored_filename,
        file_type=ext.lstrip(".") if ext else "unknown",
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)  # This populates doc.id

    # Return response including DB ID
    return {
        "message": "File uploaded and saved",
        "document_id": doc.id,
        "original_filename": original_name,
        "stored_filename": stored_filename,
        "stored_path": str(stored_path),
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

@app.post("/analyze/{stored_filename}")
def analyze_document(
    stored_filename: str,
    db: Session = Depends(get_db)
):
    """
    Analyze uploaded document and save report to DB.
    """

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

    # Run analysis
    missing_sections = find_missing_sections(text)
    risky_phrase_counts = count_risky_phrases(text)
    risk_score = calculate_risk_score(missing_sections, risky_phrase_counts)

    # -----------------------------------
    # FIND DOCUMENT IN DATABASE
    # -----------------------------------
    doc = db.query(Document).filter(
        Document.stored_filename == stored_filename
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found in DB")

    # -----------------------------------
    # SAVE REPORT TO DATABASE
    # -----------------------------------
    report = AnalysisReport(
        document_id=doc.id,
        risk_score=risk_score,
        missing_sections=missing_sections,
        risky_phrases=risky_phrase_counts,
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    # Return structured response
    return {
        "document_id": doc.id,
        "report_id": report.id,
        "report": {
            "risk_score": risk_score,
            "missing_sections": missing_sections,
            "risky_phrases": risky_phrase_counts,
        },
        "metadata": {
            "extracted_characters": len(text),
            "analysis_type": "rule_based_v1",
        },
    }

