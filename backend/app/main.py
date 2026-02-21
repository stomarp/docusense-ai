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


# Create an instance of the FastAPI application
# This 'app' object represents our backend server
app = FastAPI(
    title="DocuGuard",                  # Name of the application
    description="HR Policy Compliance Analyzer Backend",
    version="0.1.0"
)

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


def find_missing_sections(text: str) -> list[str]:
    """
    Check whether required sections appear to exist in the document.

    Returns:
        A list of section keys that appear to be missing.
    """
    lower_text = normalize_text(text)
    missing: list[str] = []

    for section_key, keywords in REQUIRED_SECTIONS.items():
        # If none of the keywords appear, we consider the section missing
        if not any(keyword in lower_text for keyword in keywords):
            missing.append(section_key)

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

# Ensure the upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------
# Basic rule-based checks (V1)
# -------------------------------------------------------------------

# These are HR policy sections we expect in most employee handbooks/policies.
# We will search the document text for these keywords.
REQUIRED_SECTIONS = {
    "code_of_conduct": ["code of conduct", "conduct policy"],
    "anti_harassment": ["anti-harassment", "harassment", "anti discrimination", "equal opportunity"],
    "leave_policy": ["leave policy", "vacation", "sick leave", "pto", "paid time off"],
    "working_hours": ["working hours", "attendance", "work schedule", "timekeeping"],
    "disciplinary_action": ["disciplinary", "termination", "discipline", "corrective action"],
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
async def upload_document(file: UploadFile = File(...)):
    """
    Upload document endpoint.

    What this does:
    1) Receives a file from the client (PDF/text/etc.)
    2) Saves it to backend/uploads/
    3) Returns the saved file name and path

    Why we save the file:
    - Next steps (text extraction + ML) need access to the document contents.
    """

    # Create a unique ID so files don't overwrite each other
    # Example: "3f2a9c1d9c0b4a1aa2f8f0d2c0e5c8e3"
    unique_id = uuid.uuid4().hex

    # Get the original file extension (e.g., ".pdf", ".txt")
    # If extension is missing, we keep it empty safely
    original_name = file.filename or "uploaded_file"
    ext = Path(original_name).suffix

    # Build a safe stored filename like: "3f2a...e3.pdf"
    stored_filename = f"{unique_id}{ext}"

    # Create the full path where we will save the file
    stored_path = UPLOAD_DIR / stored_filename

    # Read the uploaded file content into memory
    contents = await file.read()

    # Write bytes to disk
    stored_path.write_bytes(contents)

    # Return a clean response
    return {
        "message": "File uploaded and saved",
        "original_filename": original_name,
        "stored_filename": stored_filename,
        "stored_path": str(stored_path)
         
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
def analyze_document(stored_filename: str):
    """
    Analyze an uploaded document and return a simple compliance report.

    V1 (rule-based):
    - Checks if key HR sections are missing
    - Counts vague/risky phrases
    """

    # Build the path to the uploaded file
    file_path = UPLOAD_DIR / stored_filename

    # If file does not exist, return a 404 error
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Extract text based on file extension
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
            detail="Unsupported file type for analysis (supported: .docx, .pdf, .txt)"
        )

    # Run rule-based checks
    missing_sections = find_missing_sections(text)
    risky_phrase_counts = count_risky_phrases(text)

    # Create a simple report response
    return {
        "stored_filename": stored_filename,
        "summary": {
            "missing_sections_count": len(missing_sections),
            "risky_phrases_found": len(risky_phrase_counts),
            "extracted_characters": len(text),
        },
        "missing_sections": missing_sections,
        "risky_phrases": risky_phrase_counts,
    }