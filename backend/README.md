# DocuGuard Backend

DocuGuard backend is a FastAPI microservice responsible for:

- Document ingestion (PDF / DOCX / TXT)
- Compliance risk analysis (rule-based)
- Section classification (ML)
- Report persistence (PostgreSQL)

This service is stateless and designed for containerized deployment.

---

## Responsibilities

- File upload and storage
- Text extraction
- Rule-based compliance scoring
- ML-based section classification
- Structured report generation
- Persistent storage of documents and analysis reports

---

## Architecture

```
Client
  │
  ▼
FastAPI Service
  ├── Upload + Storage
  ├── Text Extraction
  ├── Rule-Based Engine
  ├── ML Classifier
  └── PostgreSQL (SQLAlchemy ORM)
```

---

## Tech Stack

- Python 3.11+
- FastAPI
- PostgreSQL
- SQLAlchemy
- scikit-learn
- Docker

---

## Database

### Tables

**documents**
- id (PK)
- original_filename
- stored_filename (unique)
- file_type
- created_at

**analysis_reports**
- id (PK)
- document_id (FK)
- risk_score
- missing_sections (JSON)
- risky_phrases (JSON)
- created_at

---

## Local Development

### Start Database

```bash
docker compose up -d
```

Connection string:

```
postgresql://docuguard:docuguard@localhost:5433/docuguard
```

---

### Install Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

---

### Train ML Model

```bash
python ml/src/train.py
```

---

### Run Service

```bash
uvicorn backend.app.main:app --reload
```

API docs:

```
http://127.0.0.1:8000/docs
```

---

## API Endpoints

- `GET /health`
- `POST /upload`
- `POST /extract-text/{stored_filename}`
- `POST /analyze/{stored_filename}`
- `GET /documents`
- `GET /documents/{document_id}/reports`

---

## Notes

- Uploaded files are stored locally (ignored in Git).
- ML model is loaded at application startup.
- Reports are immutable once generated.
- Service designed to be extended with OCR and async processing.

---

