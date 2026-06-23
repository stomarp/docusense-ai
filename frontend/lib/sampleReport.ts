import type { AnalysisResponse } from "./api";

export const sampleReport: AnalysisResponse = {
  status: "success",
  analysis: {
    document_id: 0,
    report_id: 0,
    analysis_version: "demo_report_v1",
    engine: "Hybrid ML + Rules + AI Review",
    report_version: "sample_demo_v1",
  },
  document: {
    stored_filename: "sample-school-policy.pdf",
    type: "education_hr_policy",
    label: "Education / School Policy",
    classification_confidence: 0.93,
    classification_scores: {
      education_hr_policy: 24,
      hr_policy: 13,
      compliance_document: 4,
      contract: 2,
      offer_letter: 0,
      lease_agreement: 0,
    },
  },
  summary: {
    executive_summary:
      "This school policy document appears structurally complete, but the review identified vague scheduling language and missing clarity around employee notice, approval ownership, and policy-change timelines.",
    user_warning:
      "This automated review is not legal advice. A qualified reviewer should verify the final policy before use.",
    reviewer_verdict:
      "The document is usable, but should be revised before final distribution to staff.",
    next_best_action:
      "Clarify schedule-change rules, notice periods, and HR approval ownership before publishing the policy.",
  },
  scores: {
    risk_score: 31,
    quality_score: 69,
    risk_level: "Medium",
    missing_clause_penalty: 12,
    language_risk_penalty: 8,
  },
  findings: {
    clause_coverage: {
      coverage_percent: 80,
      expected_clause_count: 5,
      missing_clause_count: 1,
      present: [
        {
          clause: "Employee Group / Classification",
          evidence: "Employee group classifications are described.",
        },
        {
          clause: "Compensation / Salary Schedule",
          evidence: "Salary schedule and pay rules are included.",
        },
        {
          clause: "Benefits",
          evidence: "Benefits language is present.",
        },
        {
          clause: "Work Calendar / Schedule",
          evidence: "Work calendar and schedule expectations are described.",
        },
      ],
      missing: [
        {
          clause: "Leave / Time Off",
          recommendation:
            "Add a dedicated leave/time-off section with eligibility, approval process, and timelines.",
        },
      ],
    },
    top_risks: [
      {
        type: "language_risk",
        severity: "Medium",
        message:
          "Vague scheduling language may create inconsistent employee expectations.",
        recommendation:
          "Add a measurable notice period and define who approves schedule changes.",
      },
      {
        type: "missing_clause",
        severity: "Low",
        message: "Leave and time-off language is incomplete.",
        recommendation:
          "Add a dedicated leave/time-off section with eligibility, approval process, and timelines.",
      },
    ],
    language_risks: [],
    missing_clauses: [],
    key_obligations: [],
  },
  recommendations: {
    action_plan: [
      {
        priority: "High",
        action: "Clarify schedule-change notice requirements.",
        reason:
          "Employees should know when schedule updates can happen and how much notice is required.",
      },
      {
        priority: "Medium",
        action: "Add a leave and time-off section.",
        reason:
          "Missing leave details can create policy ambiguity and inconsistent HR handling.",
      },
    ],
    suggested_next_step:
      "Clarify schedule-change rules, notice periods, and HR approval ownership before publishing the policy.",
    suggested_rewrites: [
      {
        original_phrase: "may",
        risk_category: "Vague discretion",
        rewrite_strategy:
          "Replace optional wording with a clear school policy requirement when the action is mandatory.",
        example_rewrite:
          "Before: Staff may receive schedule updates as needed. After: Staff schedule updates must be published in writing at least five business days before the change takes effect.",
        why_it_matters:
          "Clear timelines reduce ambiguity and improve policy consistency.",
      },
    ],
    review_checklist: [
      "Confirm employee group definitions are correct.",
      "Review schedule-change notice requirements.",
      "Add or verify leave and time-off language.",
      "Confirm HR approval ownership.",
      "Have a qualified reviewer verify final policy language.",
    ],
  },
  ai_review: {
    mode: "deterministic_ai_review_v1",
    enabled: true,
    external_llm_used: false,
    llm_upgrade_ready: true,
    executive_review:
      "The policy is structurally useful but needs clearer operational language before being shared with employees.",
    top_risk_explanations: [
      "Schedule-change language should include a measurable notice period.",
      "Leave and time-off expectations should be documented clearly.",
    ],
    disclaimer:
      "This automated review is not legal advice. A qualified reviewer should verify the final policy.",
  },
  ml: {
    summary: [],
    sections: [],
    insights: {
      status: "model_loaded_no_confident_sections",
      summary:
        "The ML classifier is available and the document was classified using document signals and rule-based weighting.",
      detected_section_count: 0,
      top_sections: [],
      top_predictions: [],
    },
  },
  metadata: {
    characters: 2840,
    words: 430,
    uses_ml_classifier: true,
    llm_ready: true,
    llm_enabled: false,
  },
  debug: {
    demo: true,
  },
};
