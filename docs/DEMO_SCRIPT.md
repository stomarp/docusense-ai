# DocuSense AI Demo Script

Use this script for a recruiter screen, interview walkthrough, LinkedIn post, or portfolio demo.

## 30-Second Version

DocuSense AI is a deployed full-stack document risk intelligence platform. It lets users upload PDF, DOCX, or TXT documents and generates a structured report with document classification, clause coverage, calibrated risk scoring, top findings, suggested rewrites, and export actions.

The stack is FastAPI, PostgreSQL, Next.js, TypeScript, Zod, Render, Vercel, and Neon.

## 60-Second Walkthrough

1. Open the live app.
2. Show the landing page and upload area.
3. Click Try sample report.
4. Point out:
   - Detected document type
   - Risk score
   - Quality score
   - Clause coverage
   - Top risks
   - Action plan
   - Suggested rewrites
5. Explain that the frontend validates API responses with Zod.
6. Upload a real HR Policy Manual PDF.
7. Run analysis.
8. Show that the classifier detects HR Policy Manual and generates a calibrated report.
9. Use Copy Summary or Download HTML to show the export workflow.

## Interview Talking Points

### Why did you build it?

I wanted to build a practical AI-style SaaS product that goes beyond a chatbot. The goal was to create a real document workflow with upload, extraction, classification, scoring, recommendations, and export.

### What was technically challenging?

The hardest parts were keeping the backend and frontend response contracts aligned, calibrating risk scoring for long documents, and making classification accurate enough to separate HR policy manuals from education-domain documents.

### What are you most proud of?

The project feels like a real product. It has a deployed frontend and backend, structured API responses, Zod validation, report exports, documentation, screenshots, tests, CI, and a production smoke test.

### What would you improve next?

I would add OpenAI-powered review mode, PDF export, authentication, document comparison, organization workspaces, and more backend tests around scoring edge cases.

## Demo Checklist

Before sharing the project:

- Live app opens
- Sample report works
- Real upload works
- Render health check works
- README screenshots load
- GitHub Actions CI is green
- Repository About section has live website link
- Resume and LinkedIn mention the live demo
