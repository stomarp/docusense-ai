"""
DocuSense AI Review Layer

This service creates an AI-style review on top of the hybrid ML/rule-based
risk intelligence report.

Current mode:
- Works without an external API key
- Generates structured executive review, suggested rewrites, warnings, and next actions

Future mode:
- Can be connected to an LLM provider using the same service interface
"""

from __future__ import annotations


def _get_top_risk_messages(intelligence_report: dict) -> list[str]:
    findings = intelligence_report.get("risk_findings", {})
    top_risks = findings.get("top_risks", [])

    messages = []
    for risk in top_risks[:5]:
        message = risk.get("message")
        recommendation = risk.get("recommendation")
        if message and recommendation:
            messages.append(f"{message} Recommendation: {recommendation}")
        elif message:
            messages.append(message)

    return messages


def _build_executive_review(intelligence_report: dict) -> str:
    summary = intelligence_report.get("executive_summary", "")
    scores = intelligence_report.get("risk_scores", {})
    risk_level = scores.get("risk_level", "Unknown")
    risk_score = scores.get("risk_score", "N/A")
    quality_score = scores.get("quality_score", "N/A")

    return (
        f"{summary} Overall, this document is rated {risk_level} risk "
        f"with a risk score of {risk_score}/100 and quality score of {quality_score}/100. "
        "The review should focus on the highest-impact risks first, especially missing clauses, "
        "vague discretionary language, and unclear obligations."
    )


def _build_suggested_rewrites(intelligence_report: dict) -> list[dict]:
    findings = intelligence_report.get("risk_findings", {})
    language_risks = findings.get("language_risks", [])
    rewrites = []

    for risk in language_risks[:6]:
        phrase = risk.get("phrase", "")
        category = risk.get("category", "Risky language")
        recommendation = risk.get("recommendation", "Clarify this wording.")

        if phrase in ["may", "might"]:
            replacement = "Replace optional wording with a mandatory rule only when the obligation is required."
            example = "Before: The vendor may provide reports. After: The vendor must provide monthly reports by the fifth business day."
        elif phrase == "as needed":
            replacement = "Define the trigger, owner, and timeline."
            example = "Before: Reviews occur as needed. After: Reviews occur quarterly or within five business days of a reported incident."
        elif phrase == "at management discretion":
            replacement = "Define the approving role and objective standard."
            example = "Before: Approval is at management discretion. After: Approval requires written review by the HR manager based on documented policy criteria."
        elif phrase == "reasonable":
            replacement = "Replace subjective timing with a measurable timeline."
            example = "Before: Within a reasonable timeframe. After: Within ten business days."
        else:
            replacement = recommendation
            example = "Rewrite the clause with a specific owner, condition, timeline, and consequence."

        rewrites.append({
            "original_phrase": phrase,
            "risk_category": category,
            "rewrite_strategy": replacement,
            "example_rewrite": example,
            "why_it_matters": recommendation,
        })

    return rewrites


def _build_user_warning(intelligence_report: dict) -> str:
    scores = intelligence_report.get("risk_scores", {})
    risk_level = scores.get("risk_level", "Unknown")
    findings = intelligence_report.get("risk_findings", {})
    missing = findings.get("missing_clauses", [])

    if risk_level in ["Critical", "High"]:
        return "Do not approve or sign this document until the high-risk findings are reviewed by the appropriate expert."
    if missing:
        return "This document is missing expected clauses. Add or revise those sections before final use."
    if risk_level == "Medium":
        return "This document is usable as a draft, but should be revised before approval or signature."

    return "No major automated warnings were detected, but a final human review is still recommended."


def _build_next_best_action(intelligence_report: dict) -> str:
    findings = intelligence_report.get("risk_findings", {})
    top_risks = findings.get("top_risks", [])

    if top_risks:
        first = top_risks[0]
        return first.get("recommendation", "Review the highest-priority risk first.")

    return "Run a final human review and export the report for recordkeeping."


def _build_review_checklist(intelligence_report: dict) -> list[str]:
    checklist = [
        "Confirm the detected document type is correct.",
        "Review all high-severity findings first.",
        "Check whether missing clauses should be added.",
        "Replace vague language with specific obligations, owners, and timelines.",
        "Verify key obligations match the intended business or compliance requirement.",
    ]

    metadata = intelligence_report.get("metadata", {})
    if metadata.get("llm_ready"):
        checklist.append("Optionally run an LLM-powered review for deeper plain-English explanation.")

    return checklist


def build_ai_review(intelligence_report: dict) -> dict:
    top_risk_messages = _get_top_risk_messages(intelligence_report)

    return {
        "mode": "deterministic_ai_review_v1",
        "enabled": True,
        "external_llm_used": False,
        "executive_review": _build_executive_review(intelligence_report),
        "top_risk_explanations": top_risk_messages,
        "suggested_rewrites": _build_suggested_rewrites(intelligence_report),
        "user_warning": _build_user_warning(intelligence_report),
        "next_best_action": _build_next_best_action(intelligence_report),
        "review_checklist": _build_review_checklist(intelligence_report),
        "llm_upgrade_ready": True,
        "disclaimer": (
            "This AI review is an automated document-risk aid and should not be treated "
            "as legal, HR, financial, or compliance advice."
        ),
    }
