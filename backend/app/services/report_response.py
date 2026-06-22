"""
DocuSense API Response Builder

Builds a clean, frontend-ready response for the analysis endpoint.
"""

from __future__ import annotations


def build_analysis_response(
    document_id: int,
    report_id: int,
    stored_filename: str,
    intelligence_report: dict,
    ai_review: dict,
    ml_summary: list[dict],
    ml_sections: list[dict],
    legacy_report: dict,
) -> dict:
    classification = intelligence_report.get("document_classification", {})
    scores = intelligence_report.get("risk_scores", {})
    findings = intelligence_report.get("risk_findings", {})
    clause_coverage = intelligence_report.get("clause_coverage", {})
    recommendations = intelligence_report.get("recommendations", {})
    metadata = intelligence_report.get("metadata", {})

    return {
        "status": "success",
        "analysis": {
            "document_id": document_id,
            "report_id": report_id,
            "analysis_version": "api_response_v1",
            "engine": intelligence_report.get("engine"),
            "report_version": intelligence_report.get("report_version"),
        },
        "document": {
            "stored_filename": stored_filename,
            "type": classification.get("type"),
            "label": classification.get("label"),
            "classification_confidence": classification.get("confidence"),
            "classification_scores": classification.get("scores", {}),
        },
        "summary": {
            "executive_summary": intelligence_report.get("executive_summary"),
            "reviewer_verdict": intelligence_report.get("ai_review_notes", {}).get("reviewer_verdict"),
            "user_warning": ai_review.get("user_warning"),
            "next_best_action": ai_review.get("next_best_action"),
        },
        "scores": {
            "risk_score": scores.get("risk_score"),
            "quality_score": scores.get("quality_score"),
            "risk_level": scores.get("risk_level"),
            "missing_clause_penalty": scores.get("missing_clause_penalty"),
            "language_risk_penalty": scores.get("language_risk_penalty"),
        },
        "findings": {
            "clause_coverage": {
                "coverage_percent": clause_coverage.get("coverage_percent"),
                "expected_clause_count": clause_coverage.get("expected_clause_count"),
                "missing_clause_count": clause_coverage.get("missing_clause_count"),
                "present": clause_coverage.get("present", []),
                "missing": clause_coverage.get("missing", []),
            },
            "top_risks": findings.get("top_risks", []),
            "language_risks": findings.get("language_risks", []),
            "missing_clauses": findings.get("missing_clauses", []),
            "key_obligations": intelligence_report.get("key_obligations", []),
        },
        "recommendations": {
            "action_plan": recommendations.get("action_plan", []),
            "suggested_next_step": recommendations.get("suggested_next_step"),
            "suggested_rewrites": ai_review.get("suggested_rewrites", []),
            "review_checklist": ai_review.get("review_checklist", []),
        },
        "ai_review": {
            "mode": ai_review.get("mode"),
            "enabled": ai_review.get("enabled"),
            "external_llm_used": ai_review.get("external_llm_used"),
            "llm_upgrade_ready": ai_review.get("llm_upgrade_ready"),
            "executive_review": ai_review.get("executive_review"),
            "top_risk_explanations": ai_review.get("top_risk_explanations", []),
            "disclaimer": ai_review.get("disclaimer"),
        },
        "ml": {
            "summary": ml_summary,
            "sections": ml_sections,
            "insights": intelligence_report.get("ml_insights", {}),
        },
        "metadata": {
            "characters": metadata.get("characters"),
            "words": metadata.get("words"),
            "uses_ml_classifier": metadata.get("uses_ml_classifier"),
            "llm_ready": metadata.get("llm_ready"),
            "llm_enabled": metadata.get("llm_enabled"),
        },
        "debug": {
            "legacy_report": legacy_report,
            "raw_intelligence_report": intelligence_report,
        },
    }
