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
};
