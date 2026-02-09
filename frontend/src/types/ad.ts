export interface Ad {
  id: number;
  ad_id: string;
  page_name: string | null;
  ad_creative_body: string | null;
  start_date: string | null;
  stop_date: string | null;
  duration_days: number;
  platforms: string[];
  industry: string;
  region: string | null;
  image_url: string | null;
  image_s3_path: string | null;
  has_image_analysis: boolean;
  has_copy_analysis: boolean;
  collected_at: string;
  // Success score fields
  success_score: number | null;
  is_successful: boolean;
}

export interface AdDetail extends Ad {
  ad_creative_link_title: string | null;
  ad_creative_link_description: string | null;
  ad_snapshot_url: string | null;
  currency: string | null;
  spend_lower: number | null;
  spend_upper: number | null;
  impressions_lower: number | null;
  impressions_upper: number | null;
  target_country: string;
  image_analysis: ImageAnalysis | null;
  copy_analysis: CopyAnalysis | null;
  success_score_detail: SuccessScoreDetail | null;
}

export interface ImageAnalysis {
  composition: {
    has_person: boolean;
    person_type: string | null;
    text_ratio: number;
    has_chart: boolean;
    logo_position: string | null;
  };
  colors: {
    primary: string | null;
    secondary: string | null;
    tertiary: string | null;
    tone: string | null;
    saturation: string | null;
  };
  layout: {
    type: string | null;
    atmosphere: string | null;
    emphasis_elements: string[];
  };
  mentioned_regions: string[];
  analyzed_at: string;
}

export interface CopyAnalysis {
  structure: {
    headline: string | null;
    headline_length: number;
    body: string | null;
    cta: string | null;
    core_message: string | null;
  };
  numbers: Array<{ value: number; unit: string; context: string }>;
  offer: {
    discount_info: string | null;
    free_benefit: string | null;
    social_proof: string | null;
    urgency: string | null;
    differentiation: string | null;
  };
  tone: {
    formality: string | null;
    emotion: string | null;
    style: string | null;
  };
  target_audience: string | null;
  keywords: string[];
  regions: string[];
  analyzed_at: string;
}

export interface SuccessScoreDetail {
  duration_score: number;
  impressions_score: number;
  total_score: number;
  percentile: number;
  is_successful: boolean;
  calculated_at: string;
}

export interface AdListResponse {
  items: Ad[];
  total: number;
  page: number;
  pages: number;
  has_next: boolean;
}

export interface CollectJobResponse {
  job_id: string;
  status: string;
  estimated_time: number;
}

export interface CollectJobStatus {
  job_id: string;
  status: string;
  progress: number;
  collected_count: number;
  target_count: number | null;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
}
