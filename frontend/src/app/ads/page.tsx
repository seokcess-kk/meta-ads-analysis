'use client';

import { useState, useCallback } from 'react';
import { Ad, api } from '@/lib/api';
import { useAds } from '@/hooks/useAds';
import { AdGrid } from '@/components/ads/AdGrid';
import { AdFilter } from '@/components/ads/AdFilter';
import { AdDetailModal } from '@/components/ads/AdDetailModal';

export default function AdsPage() {
  const [filters, setFilters] = useState<{
    industry?: string;
    region?: string;
    min_duration?: number;
    sort?: string;
    page: number;
  }>({ page: 1 });

  const [selectedAdId, setSelectedAdId] = useState<string | null>(null);

  const { ads, total, page, pages, isLoading, mutate } = useAds({
    ...filters,
    limit: 20,
  });

  const handleFilterChange = useCallback((newFilters: Record<string, unknown>) => {
    setFilters((prev) => ({
      ...prev,
      ...newFilters,
      page: 1,
    }));
  }, []);

  const handleAdClick = useCallback((ad: Ad) => {
    setSelectedAdId(ad.ad_id);
  }, []);

  const handleCloseModal = useCallback(() => {
    setSelectedAdId(null);
  }, []);

  const handlePageChange = useCallback((newPage: number) => {
    setFilters((prev) => ({ ...prev, page: newPage }));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  const handleAdDelete = useCallback(async (ad: Ad) => {
    try {
      await api.deleteAd(ad.ad_id);
      mutate();
    } catch (error) {
      console.error('Failed to delete ad:', error);
      alert('광고 삭제에 실패했습니다.');
    }
  }, [mutate]);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Ad Gallery</h1>
        <p className="mt-2 text-muted-foreground">
          수집된 메타 광고를 탐색하고 AI 분석 결과를 확인하세요.
        </p>
      </div>

      <div className="mb-6">
        <AdFilter onFilterChange={handleFilterChange} />
      </div>

      <div className="mb-4 flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          총 <span className="font-medium text-foreground">{total}</span>개의 광고
        </p>
      </div>

      <AdGrid ads={ads} isLoading={isLoading} onAdClick={handleAdClick} onAdDelete={handleAdDelete} />

      {/* Pagination */}
      {pages > 1 && (
        <div className="mt-8 flex items-center justify-center gap-2">
          <button
            onClick={() => handlePageChange(page - 1)}
            disabled={page <= 1}
            className="px-4 py-2 text-sm font-medium rounded-md border bg-background hover:bg-muted disabled:opacity-50 disabled:cursor-not-allowed"
          >
            이전
          </button>
          <div className="flex items-center gap-1">
            {Array.from({ length: Math.min(5, pages) }, (_, i) => {
              let pageNum: number;
              if (pages <= 5) {
                pageNum = i + 1;
              } else if (page <= 3) {
                pageNum = i + 1;
              } else if (page >= pages - 2) {
                pageNum = pages - 4 + i;
              } else {
                pageNum = page - 2 + i;
              }
              return (
                <button
                  key={pageNum}
                  onClick={() => handlePageChange(pageNum)}
                  className={`w-10 h-10 text-sm font-medium rounded-md ${
                    pageNum === page
                      ? 'bg-primary text-primary-foreground'
                      : 'border bg-background hover:bg-muted'
                  }`}
                >
                  {pageNum}
                </button>
              );
            })}
          </div>
          <button
            onClick={() => handlePageChange(page + 1)}
            disabled={page >= pages}
            className="px-4 py-2 text-sm font-medium rounded-md border bg-background hover:bg-muted disabled:opacity-50 disabled:cursor-not-allowed"
          >
            다음
          </button>
        </div>
      )}

      {/* Detail Modal */}
      {selectedAdId && (
        <AdDetailModal adId={selectedAdId} onClose={handleCloseModal} />
      )}
    </div>
  );
}
