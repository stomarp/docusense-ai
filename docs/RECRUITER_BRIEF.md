# DocuSense AI Recruiter Brief

DocuSense AI is a deployed full-stack document risk intelligence platform that analyzes PDF, DOCX, and TXT documents and generates structured review reports.

## One-Line Summary

A full-stack SaaS-style platform that turns long documents into structured risk reports with document classification, clause coverage, calibrated scoring, suggested rewrites, and exportable summaries.

## Live Links

- Live app: https://docusense-ai-six.vercel.app
- Production API: https://docusense-ai-api-vg1h.onrender.com
- Health check: https://docusense-ai-api-vg1h.onrender.com/health
- GitHub repo: https://github.com/stomarp/docusense-ai

## Why This Project Matters

Most document review tools are either manual checklists or simple chatbot wrappers. DocuSense AI is built as an end-to-end product workflow:

1. Upload a document
2. Extract document text
3. Classify document type
4. Analyze clause coverage
5. Detect risky language
6. Generate calibrated risk and quality scores
7. Produce structured recommendations
8. Export the result

## Engineering Signals

This project demonstrates:

- Backend API design with FastAPI
- PostgreSQL-backed document/report workflow
- Production deployment using Render, Vercel, and Neon
- Frontend runtime validation using Zod
- TypeScript UI development with Next.js
- PDF/DOCX/TXT document processing
- Domain-specific scoring and classification logic
- GitHub Actions CI with backend tests and frontend build checks
- Product-thinking through demo mode, export workflow, screenshots, and documentation

## Strong Technical Decisions

### Schema-Safe Frontend Contract

The frontend validates backend responses with Zod so API shape mismatches are caught immediately instead of silently breaking the UI.

### Calibrated Long-Document Scoring

Long HR manuals can contain many normal policy terms like "may" or "reasonable." The scoring engine is calibrated so long documents are not falsely marked as high risk only because of common policy language.

### Document Type vs. Domain Separation

The classifier separates document type from domain context. For example, a college HR manual should classify as an HR Policy Manual, not just an education policy.

### Recruiter-Friendly Demo Mode

The sample report lets reviewers test the product without uploading a document, which reduces friction during portfolio review.

### Production Deployment

The project is deployed with a real frontend, backend, production database, health check, deployment guide, and smoke test script.

## Current Scope

DocuSense AI currently supports:

- HR Policy Manual
- Education / School Policy
- Contract
- Lease Agreement
- Offer Letter
- HR Policy
- Compliance Document
- General Document

## Honest Limitations

- External LLM integration is not enabled yet
- AI-style review is deterministic and LLM-ready
- Outputs are informational and not legal advice
- Authentication and team workspaces are not implemented yet
- PDF export can be added after the current HTML export workflow

## Resume-Ready Summary

Built and deployed DocuSense AI, a full-stack document risk intelligence platform using FastAPI, PostgreSQL, Next.js, TypeScript, and Zod. The app analyzes uploaded PDF/DOCX/TXT documents, classifies document type, detects clause gaps and risky language, generates calibrated risk scores, provides AI-style review recommendations, and exports structured reports.
