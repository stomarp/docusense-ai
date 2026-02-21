# Entry point for DocuGuard backend
# Import FastAPI class from the fastapi library
# FastAPI is the framework we use to build our backend APIs
from fastapi import FastAPI
# Import UploadFile and File to handle file uploads
from fastapi import UploadFile, File
# Standard library imports for file handling
from pathlib import Path
import uuid


# Create an instance of the FastAPI application
# This 'app' object represents our backend server
app = FastAPI(
    title="DocuGuard",                  # Name of the application
    description="HR Policy Compliance Analyzer Backend",
    version="0.1.0"
)

# Folder where uploaded files will be stored
UPLOAD_DIR = Path("backend/uploads")

# Ensure the upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

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