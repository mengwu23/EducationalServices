export type CustomerJudgementStatus = "pending" | "completed" | "failed" | string;
export type CustomerMatchLevel = "high" | "medium" | "low" | string;

export interface CustomerProfileInfo {
  core_tags: string[];
  education_level: string | null;
  school_name: string | null;
  major: string | null;
  current_grade: string | null;
  language_scores: string | null;
  target_country: string | null;
  target_program: string | null;
  budget_range: string | null;
  key_strengths: string | null;
  potential_risks: string | null;
}

export interface DimensionAnalysis {
  dimension: string;
  customer_value: string | null;
  rule_requirement: string | null;
  is_match: boolean;
  evidence: string | null;
}

export interface ProductEvaluation {
  product_name: string | null;
  conclusion: string;
  match_score: number | null;
  match_level: CustomerMatchLevel | null;
  dimension_analysis: DimensionAnalysis[];
  summary_reason: string | null;
  missing_info: string[];
  actionable_advice: string | null;
}

export interface CustomerJudgementResult {
  executive_summary: string | null;
  is_target_customer: boolean | null;
  overall_match_score: number | null;
  overall_match_level: CustomerMatchLevel | null;
  customer_profile: CustomerProfileInfo | null;
  product_a_evaluation: ProductEvaluation | null;
  product_b_evaluation: ProductEvaluation | null;
  reason_summary: string | null;
  suggestion: string | null;
  final_next_steps: string[];
}

export interface JudgementRecordItem {
  id: number;
  analysis_no: string;
  source_type: string;
  source_file_name: string | null;
  target_product: string | null;
  lead_id: number | null;
  is_target_customer: number | null;
  match_score: number | null;
  match_level: CustomerMatchLevel | null;
  reason_summary: string | null;
  suggestion: string | null;
  status: CustomerJudgementStatus;
  submitter_user_id: number | null;
  create_time: string;
  update_time: string;
}

export interface JudgementRecordDetail extends JudgementRecordItem {
  raw_content: string | null;
  executive_summary: string | null;
  ai_result: CustomerJudgementResult | null;
}

export interface JudgementPage {
  total: number;
  page: number;
  page_size: number;
  items: JudgementRecordItem[];
}

export interface JudgementListParams {
  page?: number;
  page_size?: number;
  status?: string;
  lead_id?: number;
  match_level?: string;
  date_start?: string;
  date_end?: string;
}

export interface CustomerAnalyzePayload {
  text: string;
  sys_query?: string;
  lead_id?: number | null;
  target_product?: string;
  files?: File[];
}
