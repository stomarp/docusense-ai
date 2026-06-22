# DocuSense AI API Response Schema

## Endpoint

POST /analyze/{stored_filename}

## Purpose

Analyzes an uploaded document and returns a structured, frontend-ready risk intelligence report.

## Top-Level Response

The response is organized into these sections:

- status
- analysis
- document
- summary
- scores
- findings
- recommendations
- ai_review
- ml
- metadata
- debug

## analysis

Contains report identity and engine metadata.

Fields:

- document_id
- report_id
- analysis_version
- engine
- report_version

## document

Contains document classification output.

Fields:

- stored_filename
- type
- label
- classification_confidence
- classification_scores

## summary

Contains executive summary and user-facing next-step guidance.

Fields:

- executive_summary
- reviewer_verdict
- user_warning
- next_best_action

## scores

Contains product-grade risk scoring.

Fields:

- risk_score
- quality_score
- risk_level
- missing_clause_penalty
- language_risk_penalty

## findings

Contains structured risk findings.

Fields:

- clause_coverage
- top_risks
- language_risks
- missing_clauses
- key_obligations

## recommendations

Contains action-oriented suggestions.

Fields:

- action_plan
- suggested_next_step
- suggested_rewrites
- review_checklist

## ai_review

Contains AI-style review output.

Fields:

- mode
- enabled
- external_llm_used
- llm_upgrade_ready
- executive_review
- top_risk_explanations
- disclaimer

## ml

Contains ML classifier outputs.

Fields:

- summary
- sections
- insights

## metadata

Contains processing metadata.

Fields:

- characters
- words
- uses_ml_classifier
- llm_ready
- llm_enabled

## debug

Contains legacy and raw report data for development.

This section can be hidden later in production.

## Frontend Usage

The frontend should use:

- summary for hero report cards
- scores for score widgets
- findings for risk tables
- recommendations for action plans
- ai_review for AI explanation panels
- ml for advanced model insight panels

## Product Notes

This schema makes the response easier to use in a dashboard because the frontend no longer needs to parse duplicated top-level fields.
