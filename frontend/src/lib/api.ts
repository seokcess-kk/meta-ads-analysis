const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface FetchOptions extends RequestInit {
  params?: Record<string, string | number | undefined>;
}

async function fetchAPI<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
  const { params, ...fetchOptions } = options;

  let url = `${API_URL}${endpoint}`;

  // Add query params
  if (params) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        searchParams.append(key, String(value));
      }
    });
    const queryString = searchParams.toString();
    if (queryString) {
      url += `?${queryString}`;
    }
  }

  const response = await fetch(url, {
    ...fetchOptions,
    headers: {
      'Content-Type': 'application/json',
      ...fetchOptions.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// Ad Types
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
  success_score: number | null;
  is_successful: boolean;
}

export interface SuccessScoreDetail {
  duration_score: number;
  impressions_score: number;
  total_score: number;
  percentile: number;
  is_successful: boolean;
  calculated_at: string;
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

export interface ScoringStats {
  total_scored: number;
  successful_count: number;
  success_rate: number;
  avg_total_score: number;
  avg_duration_score: number;
  avg_impressions_score: number;
  max_score: number;
  min_score: number;
}

export interface ScoreCalculationResult {
  calculated: number;
  successful: number;
  max_impressions_mid: number;
}

// Pattern Types
export interface Pattern {
  id: number;
  analysis_type: string;
  field_name: string;
  field_value: string;
  successful_count: number;
  successful_ratio: number;
  general_count: number;
  general_ratio: number;
  lift: number;
  is_pattern: boolean;
}

export interface InsightItem {
  title: string;
  description: string;
}

export interface Formula {
  formula: string;
  insights: InsightItem[];
  strategies: InsightItem[];
  confidence: number;
  error?: string;
}

export interface PatternAnalysisResult {
  total_ads: number;
  successful_ads: number;
  general_ads: number;
  patterns_found: number;
  all_patterns_analyzed: number;
  message?: string;
}

export interface Insight {
  id: number;
  type: string;
  title: string;
  description: string;
  confidence: number;
  generated_at: string | null;
}

// Monitoring Types
export interface MonitoringKeyword {
  id: number;
  keyword: string;
  industry: string;
  country: string;
  is_active: boolean;
  schedule_cron: string;
  last_run_at: string | null;
  next_run_at: string | null;
  created_at: string;
}

export interface MonitoringRun {
  id: number;
  keyword_id: number;
  status: string;
  new_ads_count: number;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
}

export interface Notification {
  id: number;
  type: string;
  title: string;
  message: string;
  extra_data: Record<string, unknown> | null;
  is_read: boolean;
  created_at: string;
}

// API Functions
export const api = {
  // Ads
  async listAds(params?: {
    industry?: string;
    region?: string;
    min_duration?: number;
    page?: number;
    limit?: number;
    sort?: string;
    successful_only?: boolean;
  }): Promise<AdListResponse> {
    return fetchAPI('/api/v1/ads', { params });
  },

  async getAd(adId: string): Promise<AdDetail> {
    return fetchAPI(`/api/v1/ads/${adId}`);
  },

  async deleteAd(adId: string): Promise<void> {
    await fetch(`${API_URL}/api/v1/ads/${adId}`, { method: 'DELETE' });
  },

  // Collection
  async startCollection(data: {
    keywords: string[];
    industry: string;
    country?: string;
    limit?: number;
  }): Promise<CollectJobResponse> {
    return fetchAPI('/api/v1/ads/collect', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async getCollectionStatus(jobId: string): Promise<CollectJobStatus> {
    return fetchAPI(`/api/v1/ads/collect/${jobId}`);
  },

  // Analysis
  async analyzeImage(adId: string): Promise<{ status: string; message: string }> {
    return fetchAPI(`/api/v1/analysis/image/${adId}`, { method: 'POST' });
  },

  async analyzeCopy(adId: string): Promise<{ status: string; message: string }> {
    return fetchAPI(`/api/v1/analysis/copy/${adId}`, { method: 'POST' });
  },

  async analyzeBatch(
    adIds: string[],
    types: string[] = ['image', 'copy']
  ): Promise<{ queued_count: number; skipped_count: number; message: string }> {
    return fetchAPI('/api/v1/analysis/batch', {
      method: 'POST',
      body: JSON.stringify({ ad_ids: adIds, types }),
    });
  },

  // Screenshots
  async captureScreenshot(adId: string): Promise<{ screenshot_url: string }> {
    return fetchAPI(`/api/v1/ads/${adId}/screenshot`, { method: 'POST' });
  },

  async captureScreenshotsBatch(limit: number = 10): Promise<{ processed: number; captured: number; failed: number }> {
    return fetchAPI('/api/v1/ads/screenshots/batch', {
      method: 'POST',
      params: { limit },
    });
  },

  // Scoring
  async calculateScores(): Promise<ScoreCalculationResult> {
    return fetchAPI('/api/v1/scoring/calculate', { method: 'POST' });
  },

  async getScoringStats(): Promise<ScoringStats> {
    return fetchAPI('/api/v1/scoring/stats');
  },

  // Patterns
  async analyzePatterns(industry?: string): Promise<PatternAnalysisResult> {
    return fetchAPI('/api/v1/patterns/analyze', {
      method: 'POST',
      params: { industry },
    });
  },

  async getPatterns(params?: { industry?: string; patterns_only?: boolean }): Promise<Pattern[]> {
    return fetchAPI('/api/v1/patterns', { params });
  },

  async generateFormula(industry?: string): Promise<Formula> {
    return fetchAPI('/api/v1/patterns/formula', {
      method: 'POST',
      params: { industry },
    });
  },

  async getFormula(industry?: string): Promise<Formula> {
    return fetchAPI('/api/v1/patterns/formula', {
      params: { industry },
    });
  },

  async getInsights(params?: { industry?: string; type?: string }): Promise<Insight[]> {
    return fetchAPI('/api/v1/patterns/insights', { params });
  },

  // Monitoring
  async createKeyword(data: { keyword: string; industry: string; country?: string; schedule_cron?: string }): Promise<MonitoringKeyword> {
    return fetchAPI('/api/v1/monitoring/keywords', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async listKeywords(params?: { is_active?: boolean }): Promise<MonitoringKeyword[]> {
    return fetchAPI('/api/v1/monitoring/keywords', { params });
  },

  async getKeyword(keywordId: number): Promise<MonitoringKeyword> {
    return fetchAPI(`/api/v1/monitoring/keywords/${keywordId}`);
  },

  async updateKeyword(keywordId: number, data: Partial<MonitoringKeyword>): Promise<MonitoringKeyword> {
    return fetchAPI(`/api/v1/monitoring/keywords/${keywordId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async deleteKeyword(keywordId: number): Promise<void> {
    await fetch(`${API_URL}/api/v1/monitoring/keywords/${keywordId}`, { method: 'DELETE' });
  },

  async runKeyword(keywordId: number, limit?: number): Promise<MonitoringRun> {
    return fetchAPI(`/api/v1/monitoring/keywords/${keywordId}/run`, {
      method: 'POST',
      params: { limit },
    });
  },

  async getKeywordRuns(keywordId: number, limit?: number): Promise<MonitoringRun[]> {
    return fetchAPI(`/api/v1/monitoring/keywords/${keywordId}/runs`, {
      params: { limit },
    });
  },

  // Notifications
  async listNotifications(params?: { unread_only?: boolean; limit?: number }): Promise<Notification[]> {
    return fetchAPI('/api/v1/monitoring/notifications', { params });
  },

  async getNotificationCount(): Promise<{ unread_count: number }> {
    return fetchAPI('/api/v1/monitoring/notifications/count');
  },

  async markNotificationRead(notificationId: number): Promise<void> {
    await fetchAPI(`/api/v1/monitoring/notifications/${notificationId}/read`, { method: 'PUT' });
  },

  async markAllNotificationsRead(): Promise<void> {
    await fetchAPI('/api/v1/monitoring/notifications/read-all', { method: 'PUT' });
  },
};

// Helper to get the best available image URL
export function getAdImageUrl(ad: Ad | AdDetail): string | null {
  // Priority: image_s3_path (local screenshot) > image_url
  if (ad.image_s3_path) {
    // If it starts with /static, prepend API URL
    if (ad.image_s3_path.startsWith('/static')) {
      return `${API_URL}${ad.image_s3_path}`;
    }
    return ad.image_s3_path;
  }
  return ad.image_url;
}
