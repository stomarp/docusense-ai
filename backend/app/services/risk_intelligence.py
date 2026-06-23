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


def detect_document_type(text: str, filename: str = "") -> dict:
    lower_text = normalize_text(text)
    lower_filename = normalize_text(filename)
    combined_text = f"{lower_filename} {lower_text}"
    scores = {}

    for doc_type, keywords in DOCUMENT_TYPE_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword in lower_text:
                score += 1
            if keyword in lower_filename:
                score += 4
        scores[doc_type] = score

    education_signals = [
        "school", "employee group", "employee groups", "non-exempt",
        "classified", "certificated", "district", "lpsb", "bins"
    ]
    if any(signal in combined_text for signal in education_signals):
        scores["education_hr_policy"] = scores.get("education_hr_policy", 0) + 10

    offer_strong_signals = [
        "we are pleased to offer", "offer you", "position of",
        "start date", "employment offer", "base salary", "compensation"
    ]
    offer_signal_count = sum(1 for signal in offer_strong_signals if signal in combined_text)
    if offer_signal_count < 2:
        scores["offer_letter"] = max(0, scores.get("offer_letter", 0) - 8)

    best_type = max(scores, key=scores.get)
    total_score = sum(value for value in scores.values() if value > 0)

    if scores[best_type] <= 0:
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
    import re

    lower_text = normalize_text(text)
    word_count = max(1, len(re.findall(r"\b\w+\b", lower_text)))

    rules = [
        {
            "phrase": "without notice",
            "category": "Unilateral action",
            "severity": "High",
            "impact": 12,
            "recommendation": "Clarify notice periods, exceptions, and user rights.",
        },
        {
            "phrase": "sole discretion",
            "category": "Unilateral discretion",
            "severity": "High",
            "impact": 10,
            "recommendation": "Add objective standards and dispute/review rights.",
        },
        {
            "phrase": "at management discretion",
            "category": "Management discretion",
            "severity": "Medium",
            "impact": 8,
            "recommendation": "Define the approving role, criteria, and review process.",
        },
        {
            "phrase": "as needed",
            "category": "Unclear trigger",
            "severity": "Medium",
            "impact": 5,
            "recommendation": "Define who decides, when it applies, and what standard is used.",
        },
        {
            "phrase": "reasonable",
            "category": "Subjective standard",
            "severity": "Low",
            "impact": 3,
            "recommendation": "Define measurable timelines, thresholds, or examples.",
        },
        {
            "phrase": "might",
            "category": "Uncertain wording",
            "severity": "Low",
            "impact": 2,
            "recommendation": "Replace uncertain wording with specific conditions when appropriate.",
        },
        {
            "phrase": "may",
            "category": "Optional wording",
            "severity": "Low",
            "impact": 2,
            "recommendation": "Spot-check frequent optional wording, but do not treat every occurrence as a defect.",
        },
    ]

    risks = []

    for rule in rules:
        phrase = rule["phrase"]
        pattern = r"\b" + re.escape(phrase) + r"\b"
        count = len(re.findall(pattern, lower_text))

        if count == 0:
            continue

        # Long HR manuals naturally contain many policy words like "may".
        # We cap the risk contribution so a 60-page manual is not punished
        # just because common legal/policy language appears often.
        if phrase == "may":
            capped_count = min(count, 3)
            if word_count > 8000:
                severity = "Low"
                impact = 2
                message = (
                    f"Frequent optional wording detected ({count} occurrence(s)); "
                    "spot-check mandatory sections instead of treating every occurrence as high risk."
                )
            else:
                severity = rule["severity"]
                impact = capped_count * rule["impact"]
                message = f"'{phrase}' appears {count} time(s)."
        elif phrase in ["might", "reasonable"]:
            capped_count = min(count, 4)
            severity = rule["severity"]
            impact = capped_count * rule["impact"]
            message = f"'{phrase}' appears {count} time(s)."
        else:
            capped_count = min(count, 3)
            severity = rule["severity"]
            impact = capped_count * rule["impact"]
            message = f"'{phrase}' appears {count} time(s)."

        risks.append({
            "phrase": phrase,
            "category": rule["category"],
            "severity": severity,
            "count": count,
            "capped_count": capped_count,
            "impact": impact,
            "message": message,
            "recommendation": rule["recommendation"],
        })

    severity_rank = {"High": 3, "Medium": 2, "Low": 1}
    risks.sort(
        key=lambda item: (
            severity_rank.get(item.get("severity", "Low"), 1),
            item.get("impact", 0),
            item.get("count", 0),
        ),
        reverse=True,
    )

    return risks[:8]

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


def calculate_intelligence_score(*args, **kwargs) -> dict:
    clause_coverage = kwargs.get("clause_coverage")
    language_risks = kwargs.get("language_risks")
    key_obligations = kwargs.get("key_obligations")

    if clause_coverage is None and len(args) >= 1:
        clause_coverage = args[0]
    if language_risks is None and len(args) >= 2:
        language_risks = args[1]
    if key_obligations is None and len(args) >= 3:
        key_obligations = args[2]

    clause_coverage = clause_coverage or {}
    language_risks = language_risks or []
    key_obligations = key_obligations or []

    coverage_percent = clause_coverage.get("coverage_percent", 0) or 0
    missing_clauses = clause_coverage.get("missing_clauses", []) or []

    missing_penalty = min(45, len(missing_clauses) * 12)
    coverage_penalty = max(0, round((100 - coverage_percent) * 0.35))
    language_penalty = min(40, sum(risk.get("impact", 0) for risk in language_risks))

    # Small positive credit for clear obligations and strong clause coverage.
    obligation_credit = min(8, len(key_obligations))
    coverage_credit = 8 if coverage_percent >= 80 else 0
    complete_manual_credit = 10 if coverage_percent == 100 and not missing_clauses else 0

    raw_score = missing_penalty + coverage_penalty + language_penalty
    risk_score = max(0, min(100, raw_score - obligation_credit - coverage_credit - complete_manual_credit))

    if risk_score >= 75:
        risk_level = "Critical"
    elif risk_score >= 50:
        risk_level = "High"
    elif risk_score >= 25:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    # Quality should not simply be 100-risk. A complete document with targeted wording risks
    # can still be high quality.
    quality_score = round((coverage_percent * 0.55) + ((100 - risk_score) * 0.45))
    quality_score = max(0, min(100, quality_score))

    drivers = []

    if missing_clauses:
        drivers.append({
            "factor": "Missing expected clauses",
            "impact": missing_penalty,
            "explanation": "Expected sections are missing or not clearly labeled.",
        })

    if language_risks:
        drivers.append({
            "factor": "Risky or ambiguous language",
            "impact": language_penalty,
            "explanation": "Risk language is capped and calibrated so long documents are not over-penalized.",
        })

    if coverage_percent >= 80:
        drivers.append({
            "factor": "Strong clause coverage",
            "impact": -coverage_credit,
            "explanation": "The document includes most expected sections for this document type.",
        })

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "quality_score": quality_score,
        "coverage_penalty": coverage_penalty,
        "missing_clause_penalty": missing_penalty,
        "language_penalty": language_penalty,
        "obligation_credit": obligation_credit,
        "coverage_credit": coverage_credit,
        "drivers": drivers,
    }

def build_top_risks(*args, **kwargs) -> list[dict]:
    clause_coverage = kwargs.get("clause_coverage")
    language_risks = kwargs.get("language_risks")

    if clause_coverage is None and len(args) >= 1:
        clause_coverage = args[0]
    if language_risks is None and len(args) >= 2:
        language_risks = args[1]

    clause_coverage = clause_coverage or {}
    language_risks = language_risks or []

    top_risks = []

    for clause in clause_coverage.get("missing_clauses", [])[:3]:
        top_risks.append({
            "type": "missing_clause",
            "severity": "High",
            "message": f"Missing clause: {clause}",
            "recommendation": f"Add a clear {clause} clause.",
        })

    for risk in language_risks:
        top_risks.append({
            "type": "language_risk",
            "severity": risk.get("severity", "Low"),
            "message": risk.get("message", f"{risk.get('phrase', 'Risky wording')} detected."),
            "recommendation": risk.get("recommendation", "Clarify this wording."),
        })

    severity_rank = {"High": 3, "Medium": 2, "Low": 1}
    top_risks.sort(
        key=lambda item: severity_rank.get(item.get("severity", "Low"), 1),
        reverse=True,
    )

    return top_risks[:6]

def build_action_plan(*args, **kwargs) -> list[dict]:
    top_risks = kwargs.get("top_risks")
    if top_risks is None and len(args) >= 1:
        top_risks = args[0]

    top_risks = top_risks or []
    actions = []

    for risk in top_risks[:6]:
        severity = risk.get("severity", "Medium")
        recommendation = risk.get("recommendation", "Clarify this issue.")
        message = risk.get("message", "Risk finding detected.")

        priority = "High" if severity == "High" else "Medium" if severity == "Medium" else "Low"

        actions.append({
            "priority": priority,
            "action": recommendation,
            "reason": message,
        })

    if not actions:
        actions.append({
            "priority": "Low",
            "action": "No immediate high-priority action detected.",
            "reason": "The document includes the expected clauses and no major risk language was found.",
        })

    return actions

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


def build_executive_summary(*args, **kwargs) -> str:
    classification = kwargs.get("classification")
    risk_scores = kwargs.get("risk_scores")
    clause_coverage = kwargs.get("clause_coverage")
    language_risks = kwargs.get("language_risks")

    if classification is None and len(args) >= 1:
        classification = args[0]
    if risk_scores is None and len(args) >= 2:
        risk_scores = args[1]
    if clause_coverage is None and len(args) >= 3:
        clause_coverage = args[2]
    if language_risks is None and len(args) >= 4:
        language_risks = args[3]

    classification = classification or {}
    risk_scores = risk_scores or {}
    clause_coverage = clause_coverage or {}
    language_risks = language_risks or []

    label = classification.get("label", "General Document")
    risk_level = risk_scores.get("risk_level", "Unknown")
    risk_score = risk_scores.get("risk_score", "N/A")
    quality_score = risk_scores.get("quality_score", "N/A")
    coverage = clause_coverage.get("coverage_percent", 0)

    if risk_level in ["Low", "Medium"] and coverage >= 80:
        verdict = "This document appears structurally complete and needs targeted wording review before final use."
    elif risk_level == "High":
        verdict = "This document should be reviewed before approval because several issues may affect interpretation or enforcement."
    elif risk_level == "Critical":
        verdict = "This document should not be approved until the highest-priority findings are reviewed."
    else:
        verdict = "This document was analyzed successfully."

    return (
        f"{verdict} DocuSense classified this document as {label}. "
        f"The calibrated risk level is {risk_level} with a risk score of {risk_score}/100 "
        f"and a quality score of {quality_score}/100. Clause coverage is {coverage}%, "
        f"with {len(clause_coverage.get('missing_clauses', []) or [])} missing expected clause(s) "
        f"and {len(language_risks)} prioritized language finding(s)."
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
