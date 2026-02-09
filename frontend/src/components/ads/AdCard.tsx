'use client';

import Image from 'next/image';
import { Ad, getAdImageUrl } from '@/lib/api';

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

  const imageUrl = getAdImageUrl(ad);
  const isRenderAdUrl = ad.image_url?.includes('/ads/archive/render_ad/') && !ad.image_s3_path;

  const renderAdPreview = () => {
    if (!imageUrl) {
      return (
        <div className="flex items-center justify-center h-full text-muted-foreground">
          No Image
        </div>
      );
    }

    // Show placeholder for render_ad URLs (screenshot not captured yet)
    if (isRenderAdUrl) {
      return (
        <div className="flex flex-col items-center justify-center h-full text-muted-foreground bg-gradient-to-br from-muted to-muted/50">
          <svg className="w-12 h-12 mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <span className="text-xs">Click to view</span>
        </div>
      );
    }

    // Use Image for captured screenshots or direct image URLs
    return (
      <Image
        src={imageUrl}
        alt={ad.page_name || 'Ad image'}
        fill
        className="object-cover"
        sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
        unoptimized={imageUrl.includes('localhost')}
      />
    );
  };

  return (
    <div
      className="group cursor-pointer rounded-lg border bg-card overflow-hidden transition-shadow hover:shadow-lg relative"
      onClick={handleClick}
    >
      <div className="relative aspect-square bg-muted overflow-hidden">
        {renderAdPreview()}
        <div className="absolute top-2 right-2 flex gap-1">
          {ad.is_successful && (
            <span className="px-2 py-0.5 text-xs font-medium bg-yellow-500 text-white rounded-full flex items-center gap-1">
              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
              TOP
            </span>
          )}
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
          <div className="flex items-center gap-2">
            {ad.success_score !== null && (
              <span className={`font-medium ${ad.is_successful ? 'text-yellow-600' : ''}`}>
                {ad.success_score.toFixed(0)}점
              </span>
            )}
            <span>{ad.duration_days}일</span>
          </div>
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
