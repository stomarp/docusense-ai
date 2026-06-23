# DocuSense AI Deployment Guide

This guide explains how to deploy DocuSense AI with:

- Backend API on Render
- PostgreSQL on Render
- Frontend on Vercel

## Deployment Architecture

```text
User
  |
  v
Vercel Frontend
  |
  v
Render FastAPI Backend
  |
  v
Render PostgreSQL
```

## Backend: Render

Use the root `render.yaml` file to create a Render Blueprint.

### Render service

- Service name: `docusense-ai-api`
- Runtime: Python
- Build command: `pip install -r backend/requirements.txt`
- Start command: `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`

### Render database

The Blueprint also creates:

- Database name: `docusense`
- User: `docusense`
- Service name: `docusense-ai-db`

### Required backend environment variables

```text
DATABASE_URL=provided by Render PostgreSQL
ENVIRONMENT=production
APP_ENV=production
LOG_LEVEL=info
LLM_ENABLED=false
FRONTEND_URL=https://your-vercel-app.vercel.app
CORS_ORIGINS=https://your-vercel-app.vercel.app
```

## Frontend: Vercel

Create a new Vercel project from the GitHub repo.

Recommended Vercel settings:

```text
Framework Preset: Next.js
Root Directory: frontend
Build Command: npm run build
Install Command: npm install
```

Required frontend environment variable:

```text
NEXT_PUBLIC_API_BASE_URL=https://your-render-api.onrender.com
```

## Production Smoke Test

After Render deploys, run:

```bash
API_BASE_URL=https://your-render-api.onrender.com ./scripts/smoke_production.sh
```

Expected result:

```text
Checking health endpoint...
{"status":"DocuSense AI is running"}
Smoke check passed.
```

## Deployment Checklist

- Render Blueprint created
- Render PostgreSQL database created
- Backend health check passes
- Vercel frontend deploys successfully
- `NEXT_PUBLIC_API_BASE_URL` points to Render backend
- README Live Demo link updated after deployment
