"use client";

import { useState } from "react";
import { analyzeDocument, uploadDocument, type AnalysisResponse } from "../lib/api";
import { sampleReport } from "../lib/sampleReport";
import { PipelineStep } from "../components/PipelineStep";
import { ProductPillar } from "../components/ProductPillar";
import { ScoreCard } from "../components/ScoreCard";

export default function HomePage() {
  const [file, setFile] = useState<File | null>(null);
  const [report, setReport] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState("Upload a PDF, DOCX, or TXT document.");
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

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

      setStatusMessage("Analyzing document risk...");
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

  async function copyExecutiveSummary() {
    if (!report) {
      return;
    }

    const summary = [
      "DocuSense AI Report",
      "Document: " + report.document.label,
      "Risk level: " + report.scores.risk_level,
      "Risk score: " + report.scores.risk_score,
      "Quality score: " + report.scores.quality_score,
      "",
      report.summary.executive_summary,
      "",
      "Next action: " + report.summary.next_best_action
    ].join("\n");

    await navigator.clipboard.writeText(summary);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1800);
  }

  function printReport() {
    window.print();
  }

  function escapeHtml(value: string | number | null | undefined) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function downloadReport() {
    if (!report) {
      return;
    }

    const fileName = `${report.document.label.toLowerCase().replaceAll(" ", "-").replaceAll("/", "-")}-docusense-report.html`;

    const risks = report.findings.top_risks
      .map(
        (risk) => `<li><strong>${escapeHtml(risk.severity || "Risk")}:</strong> ${escapeHtml(risk.message)}<br/><span>${escapeHtml(risk.recommendation || "")}</span></li>`
      )
      .join("");

    const actions = report.recommendations.action_plan
      .map(
        (item) => `<li><strong>${escapeHtml(item.priority)}:</strong> ${escapeHtml(item.action)}<br/><span>${escapeHtml(item.reason)}</span></li>`
      )
      .join("");

    const rewrites = report.recommendations.suggested_rewrites
      .map(
        (rewrite) => `<li><strong>${escapeHtml(rewrite.risk_category)}:</strong> ${escapeHtml(rewrite.example_rewrite)}</li>`
      )
      .join("");

    const html = `<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>DocuSense AI Report</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 40px; color: #0f172a; line-height: 1.5; }
    .header { border-bottom: 1px solid #e5e7eb; padding-bottom: 20px; margin-bottom: 24px; }
    .label { color: #2563eb; font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: .12em; }
    h1 { margin: 8px 0; font-size: 34px; }
    .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 24px 0; }
    .card { border: 1px solid #e5e7eb; border-radius: 14px; padding: 16px; background: #f8fafc; }
    .value { font-size: 30px; font-weight: 900; }
    section { margin-top: 28px; }
    li { margin-bottom: 14px; }
    span { color: #475569; }
    .notice { background: #f0fdf4; border: 1px solid #bbf7d0; padding: 16px; border-radius: 14px; }
  </style>
</head>
<body>
  <div class="header">
    <div class="label">DocuSense AI Report</div>
    <h1>${escapeHtml(report.document.label)}</h1>
    <p>Risk level: <strong>${escapeHtml(report.scores.risk_level)}</strong> · Confidence: ${Math.round(report.document.classification_confidence * 100)}%</p>
  </div>

  <div class="grid">
    <div class="card"><div class="label">Risk Score</div><div class="value">${report.scores.risk_score}</div></div>
    <div class="card"><div class="label">Quality Score</div><div class="value">${report.scores.quality_score}</div></div>
    <div class="card"><div class="label">Clause Coverage</div><div class="value">${report.findings.clause_coverage.coverage_percent}%</div></div>
    <div class="card"><div class="label">Findings</div><div class="value">${report.findings.top_risks.length}</div></div>
  </div>

  <section>
    <div class="label">Executive Review</div>
    <h2>${escapeHtml(report.summary.reviewer_verdict)}</h2>
    <p>${escapeHtml(report.summary.executive_summary)}</p>
    <div class="notice"><strong>Recommended next action:</strong><br/>${escapeHtml(report.summary.next_best_action)}</div>
  </section>

  <section>
    <div class="label">Top Risks</div>
    <ul>${risks}</ul>
  </section>

  <section>
    <div class="label">Action Plan</div>
    <ul>${actions}</ul>
  </section>

  <section>
    <div class="label">Suggested Rewrites</div>
    <ul>${rewrites}</ul>
  </section>

  <section>
    <div class="label">AI Review Layer</div>
    <p>${escapeHtml(report.ai_review.executive_review)}</p>
    <p><em>${escapeHtml(report.ai_review.user_warning)}</em></p>
  </section>
</body>
</html>`;

    const blob = new Blob([html], {
      type: "text/html",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = fileName;
    link.click();

    URL.revokeObjectURL(url);
  }

  function loadSampleReport() {
    setReport(sampleReport);
    setFile(null);
    setError("");
    setStatusMessage("Sample report loaded.");
  }

  function clearReport() {
    setReport(null);
    setFile(null);
    setError("");
    setStatusMessage("Upload a PDF, DOCX, or TXT document.");
  }

  return (
    <main className="page-shell">
      <header className="app-header">
        <div>
          <strong>DocuSense AI</strong>
          <span>Document Risk Intelligence</span>
        </div>
        <nav>
          <span>FastAPI</span>
          <span>ML Classifier</span>
          <span>AI Review</span>
          <span>Zod Contract</span>
        </nav>
      </header>

      <section className="hero">
        <div className="hero-copy-block">
          <p className="eyebrow">Document review platform</p>
          <h1>Review policies, contracts, and agreements with structured risk intelligence.</h1>
          <p className="hero-copy">
            Upload a document and DocuSense returns a clean report with document classification, clause coverage, risk scoring, top findings, suggested rewrites, and AI-style review notes.
          </p>

          <div className="proof-row">
            <span>Backend: FastAPI + PostgreSQL</span>
            <span>Intelligence: ML + risk rules</span>
            <span>Frontend: Next.js + TypeScript + Zod</span>
          </div>
        </div>

        <div className="upload-card">
          <p className="card-label">Analyze a document</p>
          <h2>Upload file</h2>
          <p className="muted">Supports PDF, DOCX, and TXT documents.</p>

          <label className="upload-dropzone">
            <input
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={(event) => setFile(event.target.files?.[0] || null)}
            />
            <span>{file ? "Document selected" : "Choose document"}</span>
            <strong>{file ? file.name : statusMessage}</strong>
          </label>

          <button className="primary-button" onClick={handleAnalyze} disabled={loading || !file}>
            {loading ? "Analyzing..." : "Run analysis"}
          </button>

          <button className="secondary-button" onClick={loadSampleReport} type="button">
            Try sample report
          </button>

          {error ? <p className="error">{error}</p> : null}
        </div>
      </section>

      {!report ? (
        <section className="overview-section">
          <div className="section-heading">
            <p className="eyebrow">Product architecture</p>
            <h2>Built as a document intelligence workflow, not a chatbot wrapper.</h2>
          </div>

          <div className="pillar-grid">
            <ProductPillar
              label="Classification"
              title="Document type detection"
              description="Uses weighted text and filename signals to classify HR policies, school policies, leases, offer letters, contracts, and compliance documents."
            />
            <ProductPillar
              label="Risk Engine"
              title="Clause and language analysis"
              description="Checks missing clauses, risky language, obligations, severity, and risk-score drivers."
            />
            <ProductPillar
              label="AI Review"
              title="Readable decision support"
              description="Converts findings into executive review, warnings, rewrites, checklist items, and next-best actions."
            />
            <ProductPillar
              label="Schema Contract"
              title="Runtime validation"
              description="Uses Zod to validate backend API responses before rendering the frontend report."
            />
          </div>

          <div className="pipeline-panel">
            <p className="card-label">Workflow</p>
            <div className="pipeline-grid">
              <PipelineStep step="01" title="Upload" detail="User submits a PDF, DOCX, or TXT document." />
              <PipelineStep step="02" title="Extract" detail="Backend extracts text and prepares the document for analysis." />
              <PipelineStep step="03" title="Classify" detail="Risk engine detects document type and confidence." />
              <PipelineStep step="04" title="Analyze" detail="Rules and ML signals identify clauses, obligations, and risks." />
              <PipelineStep step="05" title="Review" detail="AI-style layer explains findings and rewrites risky language." />
              <PipelineStep step="06" title="Render" detail="Frontend validates and displays a structured report." />
            </div>
          </div>
        </section>
      ) : null}

      {report ? (
        <section className="report-section">
          <div className="report-title-card">
            <div>
              <p className="card-label">Detected document</p>
              <h2>{report.document.label}</h2>
              <p className="muted">
                Confidence {Math.round(report.document.classification_confidence * 100)}% · {report.analysis.engine}
              </p>
            </div>
            <span className={"risk-badge risk-" + report.scores.risk_level.toLowerCase()}>
              {report.scores.risk_level} risk
            </span>
          </div>

          <div className="score-grid">
            <ScoreCard label="Risk score" value={report.scores.risk_score} helper="Higher means more risk" />
            <ScoreCard label="Quality score" value={report.scores.quality_score} helper="Higher means cleaner document" />
            <ScoreCard label="Clause coverage" value={String(report.findings.clause_coverage.coverage_percent) + "%"} helper="Expected clauses found" />
            <ScoreCard label="Findings" value={report.findings.top_risks.length} helper="Prioritized risks" />
          </div>

          <div className="report-actions">
            <div>
              <strong>{report.debug?.demo ? "Sample report loaded" : "Analysis report ready"}</strong>
              <span>{report.document.original_filename}</span>
            </div>
            <button onClick={copyExecutiveSummary}>{copied ? "Copied summary" : "Copy summary"}</button>
            <button onClick={downloadReport}>Download HTML</button>
            <button onClick={printReport}>Print</button>
            <button onClick={clearReport}>Clear</button>
          </div>

          <div className="panel wide">
            <p className="card-label">Executive review</p>
            <h3>{report.summary.reviewer_verdict || "Automated review completed."}</h3>
            <p>{report.summary.executive_summary}</p>
            <div className="next-action">
              <span>Recommended next action</span>
              <strong>{report.summary.next_best_action}</strong>
            </div>
          </div>

          <div className="two-column">
            <div className="panel">
              <p className="card-label">Top risks</p>
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
              <p className="card-label">Action plan</p>
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
          </div>

          <div className="two-column">
            <div className="panel">
              <p className="card-label">Suggested rewrites</p>
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
                  <p className="muted">No rewrite suggestions generated.</p>
                )}
              </div>
            </div>

            <div className="panel">
              <p className="card-label">AI review layer</p>
              <h3>Structured AI review</h3>
              <p>{report.ai_review.executive_review}</p>
              <div className="tag-row">
                <span>External LLM: {report.ai_review.external_llm_used ? "Enabled" : "Not enabled"}</span>
                <span>LLM integration ready: {report.ai_review.llm_upgrade_ready ? "Yes" : "No"}</span>
              </div>
            </div>
          </div>

          <div className="panel wide">
            <p className="card-label">ML and validation metadata</p>
            <h3>{report.ml.insights.status === "model_loaded_no_confident_sections" ? "ML classifier ready" : report.ml.insights.status}</h3>
            <p>{report.ml.insights.summary}</p>
            <div className="tag-row">
              <span>Characters: {report.metadata.characters}</span>
              <span>Words: {report.metadata.words}</span>
              <span>ML classifier: {report.metadata.uses_ml_classifier ? "Enabled" : "Disabled"}</span>
              <span>Frontend schema: Zod validated</span>
            </div>
          </div>
        </section>
      ) : null}
    </main>
  );
}
