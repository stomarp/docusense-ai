# DocuSense AI Architecture

DocuSense AI is organized as a full-stack document intelligence product.

## High-Level Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend as Next.js Frontend
    participant API as FastAPI Backend
    participant DB as PostgreSQL
    participant Engine as Risk Intelligence Engine

    User->>Frontend: Upload PDF/DOCX/TXT
    Frontend->>API: POST /upload
    API->>DB: Save document metadata
    API-->>Frontend: stored_filename

    Frontend->>API: POST /analyze/{stored_filename}
    API->>API: Extract text
    API->>Engine: Classify document
    Engine->>Engine: Clause coverage analysis
    Engine->>Engine: Risk scoring
    Engine->>Engine: AI-style review
    API->>DB: Save report
    API-->>Frontend: Structured report response

    Frontend->>Frontend: Zod validation
    Frontend->>User: Render dashboard
    User->>Frontend: Copy / Print / Download HTML
```

## Backend Responsibilities

- Upload document
- Store file metadata
- Extract document text
- Classify document type
- Analyze clause coverage
- Detect risky language
- Score risk and quality
- Generate structured review recommendations
- Persist analysis reports

## Frontend Responsibilities

- Provide upload/demo workflow
- Call backend APIs
- Validate API responses with Zod
- Render structured report dashboard
- Support copy, print, and HTML export actions

## Product Design Principle

DocuSense AI separates document type, domain/industry context, risk findings, review recommendations, and export workflow.

This keeps the product extensible for additional document types and AI integrations.
