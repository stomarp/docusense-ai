import { z } from "zod";

const UnknownRecord = z.record(z.string(), z.unknown());

const RiskItemSchema = z.object({
  type: z.string().optional(),
  severity: z.string().optional(),
  message: z.string(),
  recommendation: z.string().optional()
});

const ActionItemSchema = z.object({
  priority: z.string(),
  action: z.string(),
  reason: z.string()
});

const RewriteSchema = z.object({
  original_phrase: z.string(),
  risk_category: z.string(),
  rewrite_strategy: z.string(),
  example_rewrite: z.string(),
  why_it_matters: z.string()
});

const ObligationSchema = z.object({
  text: z.string(),
  matched_keywords: z.array(z.string()).optional(),
  source: z.string()
});

export const UploadResponseSchema = z.object({
  message: z.string(),
  document_id: z.number(),
  stored_filename: z.string()
});

export const AnalysisResponseSchema = z.object({
  status: z.string(),
  analysis: z.object({
    document_id: z.number(),
    report_id: z.number(),
    analysis_version: z.string(),
    engine: z.string(),
    report_version: z.string()
  }),
  document: z.object({
    stored_filename: z.string(),
    type: z.string(),
    label: z.string(),
    classification_confidence: z.number(),
    classification_scores: z.record(z.string(), z.number())
  }),
  summary: z.object({
    executive_summary: z.string(),
    reviewer_verdict: z.string().nullable().optional(),
    user_warning: z.string(),
    next_best_action: z.string()
  }),
  scores: z.object({
    risk_score: z.number(),
    quality_score: z.number(),
    risk_level: z.string(),
    missing_clause_penalty: z.number(),
    language_risk_penalty: z.number()
  }),
  findings: z.object({
    clause_coverage: z.object({
      coverage_percent: z.number(),
      expected_clause_count: z.number(),
      missing_clause_count: z.number(),
      present: z.array(UnknownRecord),
      missing: z.array(UnknownRecord)
    }),
    top_risks: z.array(RiskItemSchema),
    language_risks: z.array(UnknownRecord),
    missing_clauses: z.array(UnknownRecord),
    key_obligations: z.array(ObligationSchema)
  }),
  recommendations: z.object({
    action_plan: z.array(ActionItemSchema),
    suggested_next_step: z.string(),
    suggested_rewrites: z.array(RewriteSchema),
    review_checklist: z.array(z.string())
  }),
  ai_review: z.object({
    mode: z.string(),
    enabled: z.boolean(),
    external_llm_used: z.boolean(),
    llm_upgrade_ready: z.boolean(),
    executive_review: z.string(),
    top_risk_explanations: z.array(z.string()),
    disclaimer: z.string()
  }),
  ml: z.object({
    summary: z.array(UnknownRecord),
    sections: z.array(UnknownRecord),
    insights: z.object({
      status: z.string(),
      summary: z.string(),
      detected_section_count: z.number(),
      top_sections: z.array(UnknownRecord),
      top_predictions: z.array(UnknownRecord)
    })
  }),
  metadata: z.object({
    characters: z.number(),
    words: z.number(),
    uses_ml_classifier: z.boolean(),
    llm_ready: z.boolean(),
    llm_enabled: z.boolean()
  }),
  debug: UnknownRecord.optional()
});

export type UploadResponse = z.infer<typeof UploadResponseSchema>;
export type AnalysisResponse = z.infer<typeof AnalysisResponseSchema>;
