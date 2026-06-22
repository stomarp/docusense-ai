"use client";

import { useState } from "react";
import { analyzeDocument, uploadDocument, type AnalysisResponse } from "../lib/api";
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

      setStatusMessage("Running DocuSense risk intelligence...");
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
        <div className="badge">Hybrid ML + AI Review</div>
        <h1>DocuSense AI</h1>
        <p className="hero-copy">
          Upload contracts, leases, HR policies, offer letters, or compliance documents and get a clean risk intelligence report with clause coverage, red flags, suggested rewrites, and next-best actions.
        </p>

        <div className="upload-panel">
          <div>
            <p className="card-label">Document Upload</p>
            <input
              className="file-input"
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={(event) => setFile(event.target.files?.[0] || null)}
            />
            <p className="muted">{file ? file.name : statusMessage}</p>
          </div>

          <button className="primary-button" onClick={handleAnalyze} disabled={loading}>
            {loading ? "Analyzing..." : "Analyze Document"}
          </button>
        </div>

        {error ? <p className="error">{error}</p> : null}
      </section>

      {report ? (
        <section className="report-grid">
          <div className="report-header">
            <div>
              <p className="card-label">Detected Document</p>
              <h2>{report.document.label}</h2>
              <p className="muted">
                Confidence: {Math.round(report.document.classification_confidence * 100)}%
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

          <div className="panel wide">
            <p className="card-label">Executive Summary</p>
            <h3>{report.summary.reviewer_verdict}</h3>
            <p>{report.summary.executive_summary}</p>
            <p className="warning">{report.summary.user_warning}</p>
          </div>

          <div className="panel">
            <p className="card-label">Top Risks</p>
            <div className="list">
              {report.findings.top_risks.map((risk, index) => (
                <div className="list-item" key={index}>
                  <span className="severity">{risk.severity}</span>
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
              {report.recommendations.suggested_rewrites.map((rewrite, index) => (
                <div className="list-item" key={index}>
                  <strong>{rewrite.original_phrase}</strong>
                  <p>{rewrite.example_rewrite}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="panel">
            <p className="card-label">AI Review Layer</p>
            <h3>{report.ai_review.mode}</h3>
            <p>{report.ai_review.executive_review}</p>
            <p className="muted">
              External LLM used: {report.ai_review.external_llm_used ? "Yes" : "No"} | LLM ready: {report.ai_review.llm_upgrade_ready ? "Yes" : "No"}
            </p>
          </div>

          <div className="panel wide">
            <p className="card-label">ML Intelligence</p>
            <h3>{report.ml.insights.status}</h3>
            <p>{report.ml.insights.summary}</p>
            <p className="muted">
              Characters: {report.metadata.characters} | Words: {report.metadata.words} | Uses ML classifier: {report.metadata.uses_ml_classifier ? "Yes" : "No"}
            </p>
          </div>
        </section>
      ) : null}
    </main>
  );
}
