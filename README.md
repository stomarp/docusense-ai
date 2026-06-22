# DocuSense AI

AI-powered document risk analyzer for HR policies, leases, contracts, offer letters, vendor agreements, and compliance documents.

DocuSense AI helps users upload complex documents and receive a clear, plain-English risk report with a summary, risk score, missing sections, key obligations, red flags, and suggested improvements.

---

## Overview

DocuSense AI is an end-to-end document intelligence system built from the original DocuGuard HR backend.

The project started as an HR policy compliance analyzer and is now being expanded into a broader document risk analyzer for multiple document types.

It currently demonstrates:

- FastAPI REST API backend
- PostgreSQL persistent storage
- SQLAlchemy database modeling
- Rule-based risk analysis
- Machine learning section classification
- PDF, DOCX, and TXT document handling
- Dockerized database setup

---

## Supported Document Types

The product roadmap supports:

- HR policies
- Employee handbooks
- Lease agreements
- Offer letters
- Vendor contracts
- Compliance documents
- General business documents

---

## Core Features

### Document Upload

- Upload PDF, DOCX, or TXT documents
- Store document metadata
- Save uploaded files locally
- Keep report history

### Document Intelligence

- Extract text from uploaded files
- Detect missing sections
- Identify vague or risky language
- Classify document sections using ML
- Generate structured analysis results

### Risk Report

Each report is designed to include:

- Plain-English summary
- Risk score
- Missing sections
- Key obligations
- Red flags
- Suggested improvements
- Exportable report in a future phase

---

## Current Backend Capabilities

The existing backend supports:

- Health check endpoint
- Document upload
- Text extraction
- Rule-based analysis
- ML section classification
- Document listing
- Report history

Existing API flow:

Upload Document
-> Extract Text
-> Analyze Risk
-> Store Report
-> Return Structured Result

---

## Architecture

DocuSense AI

- backend/
  - app/
    - db/
      - database.py
      - models.py
    - ml/
      - section_classifier.py
    - main.py
  - requirements.txt

- ml/
  - data/
    - sections_train.csv
  - src/
    - train.py
    - predict.py
  - models/

- docs/
- docker-compose.yml
- README.md

---

## Tech Stack

- Backend: FastAPI
- Database: PostgreSQL
- ORM: SQLAlchemy
- ML: scikit-learn
- Vectorizer: TF-IDF
- Model: Logistic Regression
- DevOps: Docker
- API Docs: OpenAPI / Swagger
- Frontend: Next.js in a later phase
- Deployment: Render and Vercel in a later phase

---

## MVP Scope

The first DocuSense AI MVP will focus on:

- Stabilizing the existing backend
- Rebranding DocuGuard HR into DocuSense AI
- Expanding risk analysis beyond HR documents
- Adding document type detection
- Returning clearer report fields:
  - Summary
  - Risk score
  - Missing sections
  - Key obligations
  - Red flags
  - Suggested improvements

---

## Roadmap

### Phase 1: Rebrand and Stabilize

- Rename product from DocuGuard HR to DocuSense AI
- Update README and documentation
- Confirm local setup
- Confirm existing endpoints work
- Clean API response naming

### Phase 2: Multi-Document Risk Analyzer

- Add document type detection
- Add support for leases, offer letters, contracts, and compliance documents
- Improve risk scoring
- Add key obligations
- Add red flags
- Add suggested improvements

### Phase 3: Frontend MVP

- Add Next.js frontend
- Upload page
- Analysis results page
- Clean SaaS-style dashboard
- Connect frontend to backend API

### Phase 4: AI Upgrade

- Add OpenAI-powered analysis
- Generate stronger summaries
- Add document-specific recommendations
- Improve red flag explanations

### Phase 5: Export and Deployment

- Add exportable PDF report
- Deploy backend to Render
- Deploy frontend to Vercel
- Add production smoke tests

---

## Why This Project Is Strong

DocuSense AI is not a simple CRUD project.

It demonstrates:

- Backend API design
- Database schema modeling
- File upload handling
- Text extraction
- Rule-based NLP
- Machine learning inference
- Risk scoring
- Document intelligence
- AI product thinking
- Dockerized infrastructure

---

## Author

Swati
MS Applied Computer Science
Software Development and AI/ML
