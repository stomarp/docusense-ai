"use client";

import { useState } from "react";
import { analyzeDocument, uploadDocument, type AnalysisResponse } from "../lib/api";
import { PipelineStep } from "../components/PipelineStep";
import { ProductPillar } from "../components/ProductPillar";
import { ScoreCard } from "../components/ScoreCard";

export default function HomePage() {
  const [file, setFile] = useState<File | null>(null);
  const [report, setReport] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState("Upload a PDF, DOCX, or TXT document to begin.");
  const [error, setError] = useState("");

  async function handleAnalyze() {
    if (!file) {
      setError("Choose a document first.");
      return;
    }

    setLoading(true);
    setError("");
    setReport(null);

    try {
      setStatusMessage("Uploading document...");
      const upload = await uploadDocument(file);

      setStatusMessage("Running hybrid ML + AI risk intelligence...");
      const analysis = await analyzeDocument(upload.stored_filename);

      setReport(analysis);
      setStatusMessage("Analysis complete.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
      setStatusMessage("Analysis failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page-shell">
      <section className="hero">
        <nav className="top-nav">
          <div className="brand-mark">DocuSense AI</div>
          <div className="nav-links">
            <span>Risk Intelligence</span>
            <span>ML + AI Review</span>
            <span>Schema Validated</span>
          </div>
        </nav>

        <div className="hero-layout">
          <div>
            <div className="badge">Hybrid document intelligence platform</div>
            <h1>Turn complex documents into risk-ready decisions.</h1>
            <p className="hero-copy">
              DocuSense AI analyzes contracts, leases, HR policies, offer letters, and compliance documents using document classification, clause coverage, risky-language detection, ML signals, and an AI-style review layer.
            </p>

            <div className="hero-actions">
              <button className="primary-button" onClick={handleAnalyze} disabled={loading || !file}>
                {loading ? "Analyzing..." : "Analyze Document"}
              </button>
              <span className="muted">Backend: FastAPI. Intelligence: ML + AI review. Frontend: Next.js + TypeScript + Zod.</span>
            </div>
          </div>

          <div className="hero-card">
            <p className="card-label">Product Demo Flow</p>
            <div className="mini-metric-row">
              <span>Document Type</span>
              <strong>Contract / Lease / HR / Offer</strong>
            </div>
            <div className="mini-metric-row">
              <span>Risk Engine</span>
              <strong>Hybrid ML + Rules</strong>
            </div>
            <div className="mini-metric-row">
              <span>AI Layer</span>
              <strong>Review + Rewrites</strong>
            </div>
            <div className="mini-metric-row">
              <span>Frontend Contract</span>
              <strong>Zod Validated</strong>
            </div>
          </div>
        </div>

        <div className="upload-panel">
          <div className="upload-copy">
            <p className="card-label">Document Upload</p>
            <input
              className="file-input"
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={(event) => setFile(event.target.files?.[0] || null)}
            />
            <p className="muted">{file ? file.name : statusMessage}</p>
          </div>

          <button className="primary-button secondary-mobile" onClick={handleAnalyze} disabled={loading || !file}>
            {loading ? "Running intelligence..." : "Run Risk Intelligence"}
          </button>
        </div>

        {error ? <p className="error">{error}</p> : null}
      </section>

      {!report ? (
        <section className="product-story">
          <div className="section-heading">
            <p className="card-label">Why this is different</p>
            <h2>Not a generic chatbot. A structured document-risk product.</h2>
            <p className="muted">
              DocuSense is built around a predictable analysis pipeline and a frontend-ready report schema, so the UI can show reliable risk cards, AI explanations, clause coverage, and action plans.
            </p>
          </div>

          <div className="pillar-grid">
            <ProductPillar
              label="ML Layer"
              title="Document and section intelligence"
              description="Classifies document type and keeps ML section-classifier signals available for deeper reporting."
            />
            <ProductPillar
              label="Risk Engine"
              title="Clause coverage and red flags"
              description="Detects missing expected clauses, risky language, obligations, severity, and risk-score drivers."
            />
            <ProductPillar
              label="AI Review"
              title="Plain-English review and rewrites"
              description="Turns structured findings into executive review, suggested rewrites, warnings, and next-best actions."
            />
            <ProductPillar
              label="Frontend Contract"
              title="Runtime schema validation"
              description="Uses Zod to validate backend responses before rendering the report dashboard."
            />
          </div>

          <div className="pipeline-panel">
            <p className="card-label">Document Intelligence Pipeline</p>
            <div className="pipeline-grid">
              <PipelineStep step="01" title="Upload" detail="PDF, DOCX, or TXT documents are uploaded to the FastAPI backend." />
              <PipelineStep step="02" title="Extract" detail="Text is extracted and prepared for rule-based checks and ML signals." />
              <PipelineStep step="03" title="Classify" detail="DocuSense detects the document type and scores classification confidence." />
              <PipelineStep step="04" title="Analyze" detail="Risk engine checks clause coverage, obligations, and risky language patterns." />
              <PipelineStep step="05" title="Review" detail="AI-style review explains findings, rewrites risky language, and recommends actions." />
              <PipelineStep step="06" title="Render" detail="Next.js dashboard validates the response and renders a clean product report." />
            </div>
          </div>
        </section>
      ) : null}

      {report ? (
        <section className="report-grid">
          <div className="report-header">
            <div>
              <p className="card-label">Detected Document</p>
              <h2>{report.document.label}</h2>
              <p className="muted">
                Confidence: {Math.round(report.document.classification_confidence * 100)}% | Engine: {report.analysis.engine}
              </p>
            </div>
            <div className="risk-pill">{report.scores.risk_level} Risk</div>
          </div>

          <div className="score-grid">
            <ScoreCard label="Risk Score" value={report.scores.risk_score} helper="Higher means more risk" />
            <ScoreCard label="Quality Score" value={report.scores.quality_score} helper="Higher means cleaner document" />
            <ScoreCard label="Clause Coverage" value={String(report.findings.clause_coverage.coverage_percent) + "%"} helper="Expected clauses found" />
            <ScoreCard label="Top Risks" value={report.findings.top_risks.length} helper="Prioritized findings" />
          </div>

          <div className="panel wide executive-panel">
            <p className="card-label">Executive Review</p>
            <h3>{report.summary.reviewer_verdict || "Automated review completed."}</h3>
            <p>{report.summary.executive_summary}</p>
            <p className="warning">{report.summary.user_warning}</p>
            <div className="next-action">
              <span>Next best action</span>
              <strong>{report.summary.next_best_action}</strong>
            </div>
          </div>

          <div className="panel">
            <p className="card-label">Top Risks</p>
            <div className="list">
              {report.findings.top_risks.map((risk, index) => (
                <div className="list-item" key={index}>
                  <span className="severity">{risk.severity || "Risk"}</span>
                  <strong>{risk.message}</strong>
                  {risk.recommendation ? <p>{risk.recommendation}</p> : null}
                </div>
              ))}
            </div>
          </div>

          <div className="panel">
            <p className="card-label">Action Plan</p>
            <div className="list">
              {report.recommendations.action_plan.map((item, index) => (
                <div className="list-item" key={index}>
                  <span className="severity">{item.priority}</span>
                  <strong>{item.action}</strong>
                  <p>{item.reason}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="panel">
            <p className="card-label">Suggested Rewrites</p>
            <div className="list">
              {report.recommendations.suggested_rewrites.length ? (
                report.recommendations.suggested_rewrites.map((rewrite, index) => (
                  <div className="list-item" key={index}>
                    <span className="severity">{rewrite.risk_category}</span>
                    <strong>{rewrite.original_phrase}</strong>
                    <p>{rewrite.example_rewrite}</p>
                  </div>
                ))
              ) : (
                <p className="muted">No risky rewrite suggestions were generated for this document.</p>
              )}
            </div>
          </div>

          <div className="panel">
            <p className="card-label">AI Review Layer</p>
            <h3>Structured AI Review</h3>
            <p>{report.ai_review.executive_review}</p>
            <div className="tech-row">
              <span>External LLM: {report.ai_review.external_llm_used ? "Enabled" : "Ready"}</span>
              <span>LLM ready: {report.ai_review.llm_upgrade_ready ? "Yes" : "No"}</span>
            </div>
          </div>

          <div className="panel wide">
            <p className="card-label">ML and Schema Intelligence</p>
            <h3>{report.ml.insights.status === "model_loaded_no_confident_sections" ? "ML classifier ready" : report.ml.insights.status}</h3>
            <p>{report.ml.insights.summary}</p>
            <div className="tech-row">
              <span>Characters: {report.metadata.characters}</span>
              <span>Words: {report.metadata.words}</span>
              <span>ML classifier: {report.metadata.uses_ml_classifier ? "Enabled" : "Disabled"}</span>
              <span>Schema: Zod validated</span>
            </div>
          </div>
        </section>
      ) : null}
    </main>
  );
}
