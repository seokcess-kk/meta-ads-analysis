'use client';

import Image from 'next/image';
import { Ad } from '@/lib/api';

interface AdCardProps {
  ad: Ad;
  onClick?: (ad: Ad) => void;
  onDelete?: (ad: Ad) => void;
}

export function AdCard({ ad, onClick, onDelete }: AdCardProps) {
  const handleClick = () => {
    onClick?.(ad);
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm(`"${ad.page_name || 'Unknown'}" 광고를 삭제하시겠습니까?`)) {
      onDelete?.(ad);
    }
  };

  return (
    <div
      className="group cursor-pointer rounded-lg border bg-card overflow-hidden transition-shadow hover:shadow-lg relative"
      onClick={handleClick}
    >
      <div className="relative aspect-square bg-muted">
        {ad.image_url ? (
          <Image
            src={ad.image_url}
            alt={ad.page_name || 'Ad image'}
            fill
            className="object-cover"
            sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
          />
        ) : (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            No Image
          </div>
        )}
        <div className="absolute top-2 right-2 flex gap-1">
          {ad.has_image_analysis && (
            <span className="px-2 py-0.5 text-xs font-medium bg-green-500 text-white rounded-full">
              Image
            </span>
          )}
          {ad.has_copy_analysis && (
            <span className="px-2 py-0.5 text-xs font-medium bg-blue-500 text-white rounded-full">
              Copy
            </span>
          )}
        </div>
        {onDelete && (
          <button
            onClick={handleDelete}
            className="absolute top-2 left-2 w-7 h-7 flex items-center justify-center bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600"
            title="삭제"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 6h18" />
              <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
              <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
            </svg>
          </button>
        )}
      </div>
      <div className="p-4">
        <h3 className="font-semibold text-sm truncate group-hover:text-primary">
          {ad.page_name || 'Unknown Page'}
        </h3>
        <p className="mt-1 text-xs text-muted-foreground line-clamp-2">
          {ad.ad_creative_body || 'No description'}
        </p>
        <div className="mt-3 flex items-center justify-between text-xs text-muted-foreground">
          <span className="px-2 py-0.5 bg-secondary rounded">
            {ad.industry}
          </span>
          <span>{ad.duration_days}일</span>
        </div>
        <div className="mt-2 flex flex-wrap gap-1">
          {ad.platforms.map((platform) => (
            <span
              key={platform}
              className="px-1.5 py-0.5 text-xs bg-muted rounded"
            >
              {platform}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
