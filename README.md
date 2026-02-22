#  DocuGuard HR

> Intelligent HR Policy Compliance Analyzer  
> Hybrid Rule-Based + Machine Learning Document Intelligence System

---

##  Overview

DocuGuard HR is a backend system that analyzes HR policy documents for compliance risks using:

-  FastAPI (REST API backend)
-  PostgreSQL (persistent storage)
-  Rule-based compliance engine
-  Machine Learning section classifier (TF-IDF + Logistic Regression)
-  Dockerized database setup

It allows uploading HR documents (PDF, DOCX, TXT), extracting text, analyzing compliance risk, classifying sections using ML, and storing full analysis history.

---

##  Architecture
```text
DocuGuard HR
│
├── backend/
│ ├── app/
│ │ ├── db/
│ │ │ ├── database.py
│ │ │ └── models.py
│ │ ├── ml/
│ │ │ └── section_classifier.py
│ │ └── main.py
│ └── requirements.txt
│
├── ml/
│ ├── data/
│ │ └── sections_train.csv
│ ├── src/
│ │ ├── train.py
│ │ └── predict.py
│ └── models/
│
└── docker-compose.yml
```

---

##  Features

###  Document Management

- Upload PDF, DOCX, TXT
- Store files locally
- Persist metadata in PostgreSQL
- Maintain full report history

---

### ⚖️ Rule-Based Compliance Engine

Checks for required HR sections:

- Code of Conduct  
- Anti-Harassment Policy  
- Leave Policy  
- Working Hours & Attendance  
- Disciplinary Action Policy  

Detects:
- Missing mandatory sections  
- Risky / vague language  
- Calculates risk score (0–100)

#### Risk Score Formula

```text
Risk Score = (20 × Missing Sections) + Risky Phrase Occurrences
(Max capped at 100)
```
---


##  Machine Learning Section Classification

### Model

- TF-IDF Vectorizer (1–2 grams)
- Logistic Regression classifier

### Capabilities

- Paragraph-level classification  
- Confidence scoring  
- Confidence threshold filtering  
- ML summary grouping  
- Hybrid rule-based + ML analysis  

---

##  Database Schema

### Documents Table

- id  
- original_filename  
- stored_filename  
- file_type  
- created_at  

### Analysis Reports Table

- id  
- document_id (Foreign Key)  
- risk_score  
- missing_sections (JSON)  
- risky_phrases (JSON)  
- created_at  

---

##  Setup Instructions

### 1️ Start PostgreSQL (Docker)

```bash
docker compose up -d
```

Database connection:

```
postgresql://docuguard:docuguard@localhost:5433/docuguard
```

---

###  Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

---

###  Train ML Model

```bash
python ml/src/train.py
```

Model will be saved to:

```
ml/models/section_model.joblib
```

---

###  Run FastAPI Server

```bash
uvicorn backend.app.main:app --reload
```

Open Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

##  API Endpoints

###  Health Check

```
GET /health
```

---

###  Upload Document

```
POST /upload
```

Response:

```json
{
  "message": "File uploaded and saved",
  "document_id": 1,
  "stored_filename": "abc123.pdf"
}
```

---

###  Extract Text

```
POST /extract-text/{stored_filename}
```

---

###  Analyze Document

```
POST /analyze/{stored_filename}
```

Returns:

- Risk Score  
- Missing Sections  
- Risky Phrase Counts  
- ML Section Predictions  
- ML Summary  
- Metadata  

---

###  List All Documents

```
GET /documents
```

---

###  Get Report History

```
GET /documents/{document_id}/reports
```

---

## Example Analysis Response

```json
{
  "document_id": 8,
  "report_id": 5,
  "report": {
    "risk_score": 80,
    "missing_sections": [...],
    "risky_phrases": {...}
  },
  "ml_summary": {...},
  "metadata": {
    "analysis_type": "rule_based_v1 + ml_classifier",
    "ml_conf_threshold": 0.35
  }
}
```

---

##  Tech Stack

| Layer     | Technology |
|-----------|------------|
| Backend   | FastAPI |
| Database  | PostgreSQL |
| ORM       | SQLAlchemy |
| ML        | scikit-learn |
| Vectorizer| TF-IDF |
| Model     | Logistic Regression |
| DevOps    | Docker |
| API Docs  | OpenAPI 3.1 (Swagger) |

---

##  Why This Project Is Strong

This project demonstrates:

- REST API design  
- Database schema modeling  
- File handling  
- Text extraction  
- Rule-based NLP  
- ML training + inference pipeline  
- Confidence-based filtering  
- Dockerized infrastructure  
- Hybrid AI system design  

This is not CRUD — it's an intelligent document analysis system.

---

## Roadmap

- OCR support for scanned PDFs  
- Larger HR dataset for ML  
- Transformer-based model (BERT)  
- Frontend dashboard (React)  
- Authentication & RBAC  
- Deployment to AWS / Azure  
- CI/CD pipeline  
- Background job processing  

---

##  Author

Swati   
MS Applied Computer Science  
Software Development & AI/ML