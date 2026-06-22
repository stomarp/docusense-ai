import type { AnalysisResponse } from "./api";

export const sampleReport = {
  status: "success",
  analysis: {
    engine: "Hybrid ML + Rules + AI Review",
    analysis_version: "demo_report_v1",
  },
  document: {
    stored_filename: "sample-school-policy.pdf",
    original_filename: "School Employee Policy 2024.pdf",
    label: "Education / School Policy",
    type: "education_hr_policy",
    classification_confidence: 0.93,
  },
  summary: {
    executive_summary:
      "This school policy document appears mostly complete, but the review identified vague scheduling language and missing clarity around employee notice, approval ownership, and policy change timelines.",
    reviewer_verdict:
      "The document is usable, but should be revised before final distribution to staff.",
    next_best_action:
      "Clarify schedule-change rules, notice periods, and HR approval ownership before publishing the policy.",
  },
  scores: {
    risk_score: 31,
    risk_level: "Medium",
    quality_score: 69,
  },
  findings: {
    clause_coverage: {
      coverage_percent: 80,
      found_clauses: [
        "Employee Group / Classification",
        "Compensation / Salary Schedule",
        "Benefits",
        "Work Calendar / Schedule",
      ],
      missing_clauses: ["Leave / Time Off"],
    },
    top_risks: [
      {
        severity: "Medium",
        message: "Vague scheduling language may create inconsistent employee expectations.",
        recommendation:
          "Add a measurable notice period and define who approves schedule changes.",
      },
      {
        severity: "Low",
        message: "Leave and time-off language is incomplete.",
        recommendation:
          "Add a dedicated leave/time-off section with eligibility, approval process, and timelines.",
      },
    ],
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
  },
  ai_review: {
    mode: "deterministic_ai_review_v1",
    executive_review:
      "The policy is structurally useful but needs clearer operational language before being shared with employees.",
    user_warning:
      "This automated review is not legal advice. A qualified reviewer should verify the final policy.",
    external_llm_used: false,
    llm_upgrade_ready: true,
    checklist: [
      "Confirm employee group definitions",
      "Add leave/time-off details",
      "Clarify schedule-change notice period",
      "Define HR approval ownership",
    ],
  },
  ml: {
    insights: {
      status: "model_loaded_no_confident_sections",
      summary:
        "The ML classifier is available and the document was classified using document signals and rule-based weighting.",
    },
  },
  metadata: {
    characters: 2840,
    words: 430,
    uses_ml_classifier: true,
    llm_ready: true,
  },
  debug: {
    demo: true,
  },
} as AnalysisResponse;
