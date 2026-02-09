'use client';

import { Ad } from '@/lib/api';
import { AdCard } from './AdCard';

interface AdGridProps {
  ads: Ad[];
  isLoading?: boolean;
  onAdClick?: (ad: Ad) => void;
}

export function AdGrid({ ads, isLoading, onAdClick }: AdGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="aspect-square bg-muted rounded-lg" />
            <div className="mt-4 space-y-2">
              <div className="h-4 bg-muted rounded w-3/4" />
              <div className="h-3 bg-muted rounded w-full" />
              <div className="h-3 bg-muted rounded w-1/2" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (ads.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="text-6xl mb-4">📭</div>
        <h3 className="text-lg font-semibold text-foreground">
          광고를 찾을 수 없습니다
        </h3>
        <p className="mt-2 text-sm text-muted-foreground">
          필터 조건을 변경하거나 새로운 광고를 수집해보세요.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {ads.map((ad) => (
        <AdCard key={ad.id} ad={ad} onClick={onAdClick} />
      ))}
    </div>
  );
}
