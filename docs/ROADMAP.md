# DocuSense AI Roadmap

## Phase 1: Rebrand and Stabilize Existing Backend

- Rename product from DocuGuard HR to DocuSense AI
- Update README and documentation
- Confirm FastAPI server runs locally
- Confirm PostgreSQL runs with Docker
- Confirm upload endpoint works
- Confirm text extraction works
- Confirm analyze endpoint works

## Phase 2: Broaden Analyzer

- Add document type detection
- Add support for:
  - HR policies
  - Leases
  - Contracts
  - Offer letters
  - Compliance documents
- Improve missing-section checks
- Improve risk scoring
- Add key obligations
- Add red flags
- Add suggested improvements
- Add plain-English summary

## Phase 3: API Cleanup

- Move endpoints into route modules
- Add Pydantic response schemas
- Improve error handling
- Improve API response names
- Add service layer for analysis logic

## Phase 4: Frontend MVP

- Add Next.js frontend
- Build upload page
- Build analysis result page
- Connect frontend to backend API
- Add SaaS-style UI

## Phase 5: AI Upgrade

- Add OpenAI-powered analysis
- Add document-specific prompt templates
- Add stronger explanation generation
- Add more useful suggestions

## Phase 6: Exportable Reports

- Add report template
- Add PDF export
- Add downloadable analysis report

## Phase 7: Production Deployment

- Prepare Render backend deployment
- Prepare Vercel frontend deployment
- Add production environment examples
- Add smoke test script
