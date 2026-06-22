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


def _rewrite_example_for_phrase(document_type: str, phrase: str, recommendation: str) -> tuple[str, str]:
    examples = {
        "education_hr_policy": {
            "may": (
                "Replace optional wording with a clear school policy requirement when the action is mandatory.",
                "Before: Staff may receive schedule updates as needed. After: Staff schedule updates must be published in writing at least five business days before the change takes effect."
            ),
            "as needed": (
                "Define the trigger, decision owner, and timeline for school policy actions.",
                "Before: Staffing assignments are updated as needed. After: Staffing assignments are reviewed by HR each semester and communicated before the start of the work period."
            ),
            "at management discretion": (
                "Define the approving school or HR role and the objective policy criteria.",
                "Before: Placement changes are at management discretion. After: Placement changes require written approval from HR based on documented staffing criteria."
            ),
            "reasonable": (
                "Replace subjective timing with a measurable school or HR timeline.",
                "Before: Staff will receive notice within a reasonable timeframe. After: Staff will receive written notice within ten business days."
            ),
            "without notice": (
                "Clarify whether notice is required and define any emergency exceptions.",
                "Before: Work assignments may change without notice. After: Work assignments require written notice unless an emergency closure or safety issue requires immediate action."
            ),
        },
        "offer_letter": {
            "may": (
                "Replace optional employment terms with clear written conditions.",
                "Before: Compensation may be adjusted. After: Compensation changes require written notice and approval before taking effect."
            ),
            "as needed": (
                "Define when the condition applies and who approves it.",
                "Before: Benefits may be updated as needed. After: Benefits changes are communicated in writing before the effective date."
            ),
            "at management discretion": (
                "Define approval authority and employee notice requirements.",
                "Before: Bonus eligibility is at management discretion. After: Bonus eligibility is determined by the written compensation plan and approved by the department leader."
            ),
            "without notice": (
                "Clarify notice rights and any at-will employment limitations.",
                "Before: Employment terms may change without notice. After: Material employment term changes will be communicated in writing before the effective date, subject to applicable law."
            ),
        },
        "lease_agreement": {
            "may": (
                "Replace optional property terms with clear tenant and landlord responsibilities.",
                "Before: The landlord may handle repairs. After: The landlord must acknowledge maintenance requests within two business days and resolve urgent issues according to severity."
            ),
            "as needed": (
                "Define maintenance triggers, response time, and responsible party.",
                "Before: Inspections occur as needed. After: Inspections require 48 hours written notice unless there is an emergency."
            ),
            "at management discretion": (
                "Define objective standards for fees, access, approvals, and enforcement.",
                "Before: Fees are charged at management discretion. After: Fees may be charged only when listed in the lease fee schedule."
            ),
            "without notice": (
                "Clarify notice period and emergency exceptions.",
                "Before: Entry may occur without notice. After: Entry requires at least 24 hours notice except in emergencies."
            ),
        },
        "contract": {
            "may": (
                "Replace optional service terms with specific obligations when performance is required.",
                "Before: The vendor may provide reports. After: The vendor must provide monthly reports by the fifth business day."
            ),
            "as needed": (
                "Define trigger, owner, and timeline for contract obligations.",
                "Before: Reviews occur as needed. After: Reviews occur quarterly or within five business days of a reported incident."
            ),
            "at management discretion": (
                "Define approval role, limits, and review process.",
                "Before: Approval is at management discretion. After: Approval requires written review by the contract owner based on documented criteria."
            ),
            "without notice": (
                "Clarify notice, termination, and cure periods.",
                "Before: Services may be terminated without notice. After: Either party may terminate with 30 days written notice, except for uncured material breach."
            ),
        },
        "hr_policy": {
            "may": (
                "Replace optional HR language with clear employee and manager responsibilities.",
                "Before: Employees may report concerns to management. After: Employees must report workplace safety concerns to HR or their manager within one business day."
            ),
            "as needed": (
                "Define when HR action is triggered and who owns it.",
                "Before: Training is provided as needed. After: Required training is assigned annually and tracked by HR."
            ),
            "at management discretion": (
                "Define the HR approval process and consistent criteria.",
                "Before: Discipline is at management discretion. After: Disciplinary action follows the documented corrective action process unless immediate action is required."
            ),
            "without notice": (
                "Clarify employee notice and emergency exceptions.",
                "Before: Policies may change without notice. After: Material policy changes are communicated in writing before the effective date when practical."
            ),
        },
        "compliance_document": {
            "may": (
                "Replace optional controls with clear control ownership and cadence.",
                "Before: Controls may be reviewed. After: Control owners must review assigned controls quarterly and document results."
            ),
            "as needed": (
                "Define the compliance trigger and escalation path.",
                "Before: Issues are escalated as needed. After: Critical issues must be escalated to the compliance owner within one business day."
            ),
            "at management discretion": (
                "Define approval authority and audit trail requirements.",
                "Before: Exceptions are approved at management discretion. After: Exceptions require documented approval from the compliance owner with expiration date and rationale."
            ),
            "without notice": (
                "Clarify notification and emergency exceptions.",
                "Before: Access may be revoked without notice. After: Access changes require documented reason and user notification unless immediate security risk exists."
            ),
        },
    }

    default_examples = examples.get(document_type, examples["contract"])
    strategy, example = default_examples.get(
        phrase,
        (
            recommendation,
            "Rewrite the clause with a specific owner, condition, timeline, approval path, and consequence."
        )
    )

    return strategy, example


def _build_suggested_rewrites(intelligence_report: dict) -> list[dict]:
    classification = intelligence_report.get("document_classification", {})
    document_type = classification.get("type", "general_document")
    findings = intelligence_report.get("risk_findings", {})
    language_risks = findings.get("language_risks", [])
    rewrites = []

    for risk in language_risks[:6]:
        phrase = risk.get("phrase", "")
        category = risk.get("category", "Risky language")
        recommendation = risk.get("recommendation", "Clarify this wording.")

        strategy, example = _rewrite_example_for_phrase(
            document_type=document_type,
            phrase=phrase,
            recommendation=recommendation,
        )

        rewrites.append({
            "original_phrase": phrase,
            "risk_category": category,
            "rewrite_strategy": strategy,
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
