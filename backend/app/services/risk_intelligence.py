"""
DocuSense AI Risk Intelligence Engine

This service turns extracted document text plus ML classifier signals into a
product-grade risk intelligence report.

It is intentionally separate from FastAPI routes so the project looks like a
real backend product, not one large API file.
"""

from __future__ import annotations


DOCUMENT_TYPE_KEYWORDS = {
    "education_hr_policy": [
        "school", "teacher", "staff", "employee group", "employee groups",
        "non-exempt", "exempt", "classified", "certificated", "district",
        "school year", "benefits", "salary schedule", "work calendar",
        "bargaining", "lp", "lpsb", "bins"
    ],
    "hr_policy": [
        "employee", "handbook", "code of conduct", "harassment",
        "leave policy", "pto", "attendance", "disciplinary", "workplace"
    ],
    "lease_agreement": [
        "tenant", "landlord", "rent", "security deposit", "premises",
        "lease", "eviction", "utilities", "maintenance"
    ],
    "offer_letter": [
        "offer", "salary", "compensation", "start date", "employment",
        "benefits", "position", "bonus", "at-will"
    ],
    "contract": [
        "agreement", "services", "payment terms", "termination",
        "liability", "indemnification", "confidentiality", "governing law",
        "dispute", "vendor"
    ],
    "compliance_document": [
        "compliance", "audit", "regulatory", "procedure", "controls",
        "policy", "monitoring", "reporting", "escalation"
    ],
}

DOCUMENT_TYPE_LABELS = {
    "hr_policy": "HR Policy",
    "lease_agreement": "Lease Agreement",
    "offer_letter": "Offer Letter",
    "contract": "Contract",
    "compliance_document": "Compliance Document",
    "education_hr_policy": "Education / School Policy",
    "general_document": "General Document",
}

EXPECTED_CLAUSES = {
    "education_hr_policy": {
        "Employee Group / Classification": ["employee group", "employee groups", "exempt", "non-exempt", "classified", "certificated"],
        "Compensation / Salary Schedule": ["salary", "salary schedule", "pay", "compensation", "wage"],
        "Benefits": ["benefits", "insurance", "health", "retirement"],
        "Work Calendar / Schedule": ["calendar", "school year", "work day", "work schedule", "hours"],
        "Leave / Time Off": ["leave", "sick", "vacation", "pto", "time off"],
    },
    "hr_policy": {
        "Code of Conduct": ["code of conduct", "conduct policy"],
        "Anti-Harassment": ["anti-harassment", "harassment", "equal opportunity"],
        "Leave Policy": ["leave policy", "vacation", "sick leave", "pto"],
        "Working Hours": ["working hours", "attendance", "timekeeping"],
        "Disciplinary Action": ["disciplinary", "termination", "corrective action"],
    },
    "lease_agreement": {
        "Rent Payment Terms": ["rent", "monthly payment", "due date"],
        "Security Deposit": ["security deposit", "deposit"],
        "Maintenance Responsibilities": ["maintenance", "repairs"],
        "Utilities": ["utilities", "electricity", "water", "gas"],
        "Termination / Renewal": ["termination", "renewal", "notice"],
    },
    "offer_letter": {
        "Compensation": ["salary", "compensation", "pay"],
        "Role / Position": ["position", "title", "role"],
        "Start Date": ["start date", "begin"],
        "Benefits": ["benefits", "insurance", "pto"],
        "Employment Type": ["full-time", "part-time", "at-will", "contract"],
    },
    "contract": {
        "Scope of Services": ["services", "scope", "deliverables"],
        "Payment Terms": ["payment terms", "invoice", "fees"],
        "Confidentiality": ["confidentiality", "confidential"],
        "Termination": ["termination", "terminate"],
        "Liability / Indemnification": ["liability", "indemnification", "damages"],
        "Governing Law": ["governing law", "jurisdiction"],
    },
    "compliance_document": {
        "Owner / Accountability": ["owner", "responsible", "accountability"],
        "Controls": ["controls", "control"],
        "Audit Process": ["audit", "review"],
        "Reporting": ["reporting", "report"],
        "Escalation": ["escalation", "incident"],
    },
}

RISK_LANGUAGE_RULES = [
    {
        "phrase": "may",
        "severity": "LOW",
        "category": "Vague discretion",
        "recommendation": "Replace with must, shall, or a specific decision rule when the requirement is mandatory.",
    },
    {
        "phrase": "might",
        "severity": "LOW",
        "category": "Vague discretion",
        "recommendation": "Replace uncertain wording with specific conditions.",
    },
    {
        "phrase": "as needed",
        "severity": "MEDIUM",
        "category": "Unclear trigger",
        "recommendation": "Define who decides, when it applies, and what standard is used.",
    },
    {
        "phrase": "at management discretion",
        "severity": "MEDIUM",
        "category": "Broad discretion",
        "recommendation": "Define approval authority, limits, and review process.",
    },
    {
        "phrase": "reasonable",
        "severity": "LOW",
        "category": "Subjective standard",
        "recommendation": "Define measurable timelines, thresholds, or examples.",
    },
    {
        "phrase": "without notice",
        "severity": "HIGH",
        "category": "Unilateral action",
        "recommendation": "Clarify notice periods, exceptions, and user rights.",
    },
    {
        "phrase": "sole discretion",
        "severity": "HIGH",
        "category": "Unilateral discretion",
        "recommendation": "Add objective standards and dispute/review rights.",
    },
    {
        "phrase": "unlimited liability",
        "severity": "HIGH",
        "category": "Liability exposure",
        "recommendation": "Add liability caps, carve-outs, and indemnity limits.",
    },
    {
        "phrase": "non-refundable",
        "severity": "MEDIUM",
        "category": "Financial risk",
        "recommendation": "Clarify refund exceptions and timing.",
    },
    {
        "phrase": "automatic renewal",
        "severity": "MEDIUM",
        "category": "Renewal risk",
        "recommendation": "Add renewal notice windows and cancellation steps.",
    },
]


def normalize_text(text: str) -> str:
    return text.lower()


def detect_document_type(text: str) -> dict:
    lower_text = normalize_text(text)
    scores = {}

    for doc_type, keywords in DOCUMENT_TYPE_KEYWORDS.items():
        scores[doc_type] = sum(1 for keyword in keywords if keyword in lower_text)

    best_type = max(scores, key=scores.get)
    total_score = sum(scores.values())

    if scores[best_type] == 0:
        best_type = "general_document"

    confidence = 0.0
    if total_score:
        confidence = round(scores[best_type] / total_score, 3)

    return {
        "type": best_type,
        "label": DOCUMENT_TYPE_LABELS.get(best_type, "General Document"),
        "confidence": confidence,
        "scores": scores,
    }


def build_clause_coverage(text: str, document_type: str) -> dict:
    lower_text = normalize_text(text)
    expected = EXPECTED_CLAUSES.get(document_type, {})
    present = []
    missing = []

    for clause_name, keywords in expected.items():
        matched_keywords = [keyword for keyword in keywords if keyword in lower_text]
        if matched_keywords:
            present.append({
                "clause": clause_name,
                "matched_keywords": matched_keywords,
                "status": "present",
            })
        else:
            missing.append({
                "clause": clause_name,
                "severity": "HIGH",
                "status": "missing",
                "recommendation": f"Add a clear {clause_name} clause.",
            })

    total = len(expected)
    coverage_percent = 100
    if total:
        coverage_percent = round((len(present) / total) * 100)

    return {
        "coverage_percent": coverage_percent,
        "present": present,
        "missing": missing,
        "expected_clause_count": total,
        "missing_clause_count": len(missing),
    }


def extract_language_risks(text: str) -> list[dict]:
    lower_text = normalize_text(text)
    risks = []

    for rule in RISK_LANGUAGE_RULES:
        count = lower_text.count(rule["phrase"])
        if count:
            risks.append({
                "type": "risky_language",
                "phrase": rule["phrase"],
                "count": count,
                "severity": rule["severity"],
                "category": rule["category"],
                "message": f"'{rule['phrase']}' appears {count} time(s).",
                "recommendation": rule["recommendation"],
            })

    return risks


def extract_key_obligations(text: str) -> list[dict]:
    keywords = [
        "must", "shall", "required", "responsible for", "agree to",
        "obligation", "pay", "provide", "maintain", "comply"
    ]

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    obligations = []

    for line in lines:
        lower_line = normalize_text(line)
        matched = [keyword for keyword in keywords if keyword in lower_line]
        if matched:
            obligations.append({
                "text": line[:320],
                "matched_keywords": matched,
                "source": "obligation_keyword_match",
            })

    return obligations[:10]


def build_ml_insights(ml_summary: list[dict], ml_sections: list[dict]) -> dict:
    if not ml_summary and not ml_sections:
        return {
            "status": "model_loaded_no_confident_sections",
            "summary": "The ML classifier ran, but no section predictions passed the confidence threshold.",
            "detected_section_count": 0,
            "top_sections": [],
            "top_predictions": [],
        }

    return {
        "status": "ml_sections_detected",
        "summary": "The ML classifier identified document sections that can support risk review.",
        "detected_section_count": len(ml_sections),
        "top_sections": ml_summary[:5],
        "top_predictions": ml_sections[:5],
    }


def severity_points(severity: str) -> int:
    return {
        "HIGH": 18,
        "MEDIUM": 9,
        "LOW": 3,
    }.get(severity.upper(), 3)


def calculate_intelligence_score(clause_coverage: dict, language_risks: list[dict]) -> dict:
    missing_clause_penalty = clause_coverage["missing_clause_count"] * 12
    language_penalty = sum(severity_points(risk["severity"]) * risk["count"] for risk in language_risks)
    risk_score = min(100, missing_clause_penalty + language_penalty)
    quality_score = max(0, 100 - risk_score)

    if risk_score >= 75:
        risk_level = "Critical"
    elif risk_score >= 50:
        risk_level = "High"
    elif risk_score >= 25:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "risk_score": risk_score,
        "quality_score": quality_score,
        "risk_level": risk_level,
        "missing_clause_penalty": missing_clause_penalty,
        "language_risk_penalty": language_penalty,
    }


def build_top_risks(clause_coverage: dict, language_risks: list[dict]) -> list[dict]:
    risks = []

    for item in clause_coverage["missing"]:
        risks.append({
            "type": "missing_clause",
            "severity": item["severity"],
            "message": f"Missing clause: {item['clause']}",
            "recommendation": item["recommendation"],
        })

    for risk in language_risks:
        risks.append({
            "type": risk["type"],
            "severity": risk["severity"],
            "message": risk["message"],
            "recommendation": risk["recommendation"],
        })

    rank = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    return sorted(risks, key=lambda item: rank.get(item["severity"], 0), reverse=True)[:8]


def build_action_plan(top_risks: list[dict]) -> list[dict]:
    actions = []

    for risk in top_risks:
        priority = "High" if risk["severity"] == "HIGH" else "Medium"
        if risk["severity"] == "LOW":
            priority = "Low"

        actions.append({
            "priority": priority,
            "action": risk["recommendation"],
            "reason": risk["message"],
        })

    if not actions:
        actions.append({
            "priority": "Low",
            "action": "Perform a final human review before approval or signature.",
            "reason": "No major automated risk findings were detected.",
        })

    return actions[:8]


def build_ai_review_notes(document_label: str, score: dict, top_risks: list[dict]) -> dict:
    if score["risk_level"] in ["Critical", "High"]:
        verdict = "This document should not be approved until the high-priority findings are reviewed."
    elif score["risk_level"] == "Medium":
        verdict = "This document is usable as a draft, but should be revised before final use."
    else:
        verdict = "This document appears low-risk based on the current automated review."

    focus_areas = [risk["message"] for risk in top_risks[:3]]

    return {
        "reviewer_verdict": verdict,
        "recommended_reviewer": "Legal, HR, compliance, or operations owner depending on document type",
        "focus_areas": focus_areas,
        "ai_positioning": (
            f"DocuSense reviewed this {document_label} using rule-based risk checks, "
            "ML section signals, and product-grade risk heuristics. LLM review can be added next."
        ),
    }


def build_executive_summary(document_label: str, score: dict, clause_coverage: dict, language_risks: list[dict]) -> str:
    return (
        f"DocuSense classified this document as {document_label}. "
        f"The risk level is {score['risk_level']} with a risk score of {score['risk_score']}/100 "
        f"and a quality score of {score['quality_score']}/100. "
        f"Clause coverage is {clause_coverage['coverage_percent']}%, with "
        f"{clause_coverage['missing_clause_count']} missing expected clause(s) and "
        f"{len(language_risks)} risky language pattern(s) detected."
    )


def build_risk_intelligence_report(
    text: str,
    source_filename: str,
    ml_summary: list[dict] | None = None,
    ml_sections: list[dict] | None = None,
) -> dict:
    ml_summary = ml_summary or []
    ml_sections = ml_sections or []

    classification = detect_document_type(text, source_filename)
    document_type = classification["type"]
    document_label = classification["label"]

    clause_coverage = build_clause_coverage(text, document_type)
    language_risks = extract_language_risks(text)
    obligations = extract_key_obligations(text)
    ml_insights = build_ml_insights(ml_summary, ml_sections)
    score = calculate_intelligence_score(clause_coverage, language_risks)
    top_risks = build_top_risks(clause_coverage, language_risks)
    action_plan = build_action_plan(top_risks)
    ai_review_notes = build_ai_review_notes(document_label, score, top_risks)

    return {
        "report_version": "risk_intelligence_v1",
        "engine": "hybrid_rule_based_ml_intelligence",
        "source_filename": source_filename,
        "executive_summary": build_executive_summary(
            document_label,
            score,
            clause_coverage,
            language_risks,
        ),
        "document_classification": classification,
        "risk_scores": score,
        "clause_coverage": clause_coverage,
        "risk_findings": {
            "top_risks": top_risks,
            "language_risks": language_risks,
            "missing_clauses": clause_coverage["missing"],
        },
        "key_obligations": obligations,
        "recommendations": {
            "action_plan": action_plan,
            "suggested_next_step": ai_review_notes["reviewer_verdict"],
        },
        "ml_insights": ml_insights,
        "ai_review_notes": ai_review_notes,
        "metadata": {
            "characters": len(text),
            "words": len([word for word in text.split() if word.strip()]),
            "uses_ml_classifier": True,
            "llm_ready": True,
            "llm_enabled": False,
        },
    }
