import useSWR from 'swr';
import { api, Ad, AdDetail, AdListResponse } from '@/lib/api';

interface UseAdsParams {
  industry?: string;
  region?: string;
  min_duration?: number;
  page?: number;
  limit?: number;
  sort?: string;
}

export function useAds(params: UseAdsParams = {}) {
  const { data, error, isLoading, mutate } = useSWR<AdListResponse>(
    ['ads', params],
    () => api.listAds(params),
    {
      revalidateOnFocus: false,
      keepPreviousData: true,
    }
  );

  return {
    ads: data?.items ?? [],
    total: data?.total ?? 0,
    page: data?.page ?? 1,
    pages: data?.pages ?? 1,
    hasNext: data?.has_next ?? false,
    isLoading,
    isError: error,
    mutate,
  };
}

export function useAd(adId: string | null) {
  const { data, error, isLoading, mutate } = useSWR<AdDetail>(
    adId ? ['ad', adId] : null,
    () => api.getAd(adId!),
    {
      revalidateOnFocus: false,
    }
  );

  return {
    ad: data,
    isLoading,
    isError: error,
    mutate,
  };
}

export function useAnalyze() {
  const analyzeImage = async (adId: string) => {
    return api.analyzeImage(adId);
  };

  const analyzeCopy = async (adId: string) => {
    return api.analyzeCopy(adId);
  };

  const analyzeBatch = async (adIds: string[], types: string[] = ['image', 'copy']) => {
    return api.analyzeBatch(adIds, types);
  };

  return {
    analyzeImage,
    analyzeCopy,
    analyzeBatch,
  };
}
