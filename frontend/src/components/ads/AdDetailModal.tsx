'use client';

import { useEffect, useCallback } from 'react';
import Image from 'next/image';
import { AdDetail } from '@/lib/api';
import { useAd, useAnalyze } from '@/hooks/useAds';

interface AdDetailModalProps {
  adId: string | null;
  onClose: () => void;
}

export function AdDetailModal({ adId, onClose }: AdDetailModalProps) {
  const { ad, isLoading, mutate } = useAd(adId);
  const { analyzeImage, analyzeCopy } = useAnalyze();

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    },
    [onClose]
  );

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [handleKeyDown]);

  const handleAnalyzeImage = async () => {
    if (!adId) return;
    try {
      await analyzeImage(adId);
      setTimeout(() => mutate(), 2000);
    } catch (error) {
      console.error('Image analysis failed:', error);
    }
  };

  const handleAnalyzeCopy = async () => {
    if (!adId) return;
    try {
      await analyzeCopy(adId);
      setTimeout(() => mutate(), 2000);
    } catch (error) {
      console.error('Copy analysis failed:', error);
    }
  };

  if (!adId) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
      />
      <div className="relative bg-background rounded-lg shadow-xl max-w-5xl w-full max-h-[90vh] overflow-hidden mx-4">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-10 p-2 rounded-full bg-background/80 hover:bg-background text-foreground"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        {isLoading ? (
          <div className="flex items-center justify-center h-96">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
          </div>
        ) : ad ? (
          <div className="flex flex-col lg:flex-row h-full max-h-[90vh]">
            {/* Image Section */}
            <div className="lg:w-1/2 bg-muted">
              <div className="relative aspect-square lg:h-full">
                {ad.image_url ? (
                  <Image
                    src={ad.image_url}
                    alt={ad.page_name || 'Ad image'}
                    fill
                    className="object-contain"
                  />
                ) : (
                  <div className="flex items-center justify-center h-full text-muted-foreground">
                    No Image
                  </div>
                )}
              </div>
            </div>

            {/* Detail Section */}
            <div className="lg:w-1/2 p-6 overflow-y-auto max-h-[50vh] lg:max-h-[90vh]">
              <div className="space-y-6">
                {/* Header */}
                <div>
                  <h2 className="text-xl font-bold">{ad.page_name || 'Unknown Page'}</h2>
                  <p className="mt-1 text-sm text-muted-foreground">
                    Ad ID: {ad.ad_id}
                  </p>
                </div>

                {/* Basic Info */}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">산업:</span>
                    <span className="ml-2 font-medium">{ad.industry}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">지역:</span>
                    <span className="ml-2 font-medium">{ad.region || ad.target_country}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">집행기간:</span>
                    <span className="ml-2 font-medium">{ad.duration_days}일</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">플랫폼:</span>
                    <span className="ml-2 font-medium">{ad.platforms.join(', ')}</span>
                  </div>
                </div>

                {/* Ad Copy */}
                <div>
                  <h3 className="font-semibold mb-2">광고 문구</h3>
                  <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                    {ad.ad_creative_body || 'No copy available'}
                  </p>
                  {ad.ad_creative_link_title && (
                    <p className="mt-2 text-sm font-medium">
                      {ad.ad_creative_link_title}
                    </p>
                  )}
                </div>

                {/* Analysis Actions */}
                <div className="flex gap-2">
                  <button
                    onClick={handleAnalyzeImage}
                    disabled={ad.has_image_analysis}
                    className="px-4 py-2 text-sm font-medium rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {ad.has_image_analysis ? '이미지 분석 완료' : '이미지 분석'}
                  </button>
                  <button
                    onClick={handleAnalyzeCopy}
                    disabled={ad.has_copy_analysis}
                    className="px-4 py-2 text-sm font-medium rounded-md bg-secondary text-secondary-foreground hover:bg-secondary/90 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {ad.has_copy_analysis ? '카피 분석 완료' : '카피 분석'}
                  </button>
                </div>

                {/* Image Analysis Results */}
                {ad.image_analysis && (
                  <div className="border-t pt-4">
                    <h3 className="font-semibold mb-3">이미지 분석 결과</h3>
                    <div className="space-y-3 text-sm">
                      <div>
                        <h4 className="font-medium text-muted-foreground">구성</h4>
                        <ul className="mt-1 space-y-1">
                          <li>인물 포함: {ad.image_analysis.composition.has_person ? '예' : '아니오'}</li>
                          {ad.image_analysis.composition.person_type && (
                            <li>인물 유형: {ad.image_analysis.composition.person_type}</li>
                          )}
                          <li>텍스트 비율: {Math.round(ad.image_analysis.composition.text_ratio * 100)}%</li>
                          <li>차트 포함: {ad.image_analysis.composition.has_chart ? '예' : '아니오'}</li>
                        </ul>
                      </div>
                      <div>
                        <h4 className="font-medium text-muted-foreground">색상</h4>
                        <ul className="mt-1 space-y-1">
                          <li>주요 색상: {ad.image_analysis.colors.primary || '-'}</li>
                          <li>색감: {ad.image_analysis.colors.tone || '-'}</li>
                        </ul>
                      </div>
                      <div>
                        <h4 className="font-medium text-muted-foreground">레이아웃</h4>
                        <ul className="mt-1 space-y-1">
                          <li>유형: {ad.image_analysis.layout.type || '-'}</li>
                          <li>분위기: {ad.image_analysis.layout.atmosphere || '-'}</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                )}

                {/* Copy Analysis Results */}
                {ad.copy_analysis && (
                  <div className="border-t pt-4">
                    <h3 className="font-semibold mb-3">카피 분석 결과</h3>
                    <div className="space-y-3 text-sm">
                      <div>
                        <h4 className="font-medium text-muted-foreground">구조</h4>
                        <ul className="mt-1 space-y-1">
                          {ad.copy_analysis.structure.headline && (
                            <li>헤드라인: {ad.copy_analysis.structure.headline}</li>
                          )}
                          {ad.copy_analysis.structure.cta && (
                            <li>CTA: {ad.copy_analysis.structure.cta}</li>
                          )}
                          {ad.copy_analysis.structure.core_message && (
                            <li>핵심 메시지: {ad.copy_analysis.structure.core_message}</li>
                          )}
                        </ul>
                      </div>
                      <div>
                        <h4 className="font-medium text-muted-foreground">오퍼</h4>
                        <ul className="mt-1 space-y-1">
                          {ad.copy_analysis.offer.discount_info && (
                            <li>할인: {ad.copy_analysis.offer.discount_info}</li>
                          )}
                          {ad.copy_analysis.offer.free_benefit && (
                            <li>무료 혜택: {ad.copy_analysis.offer.free_benefit}</li>
                          )}
                          {ad.copy_analysis.offer.urgency && (
                            <li>긴급성: {ad.copy_analysis.offer.urgency}</li>
                          )}
                        </ul>
                      </div>
                      <div>
                        <h4 className="font-medium text-muted-foreground">톤</h4>
                        <ul className="mt-1 space-y-1">
                          <li>격식: {ad.copy_analysis.tone.formality || '-'}</li>
                          <li>감정: {ad.copy_analysis.tone.emotion || '-'}</li>
                          <li>스타일: {ad.copy_analysis.tone.style || '-'}</li>
                        </ul>
                      </div>
                      {ad.copy_analysis.keywords.length > 0 && (
                        <div>
                          <h4 className="font-medium text-muted-foreground">키워드</h4>
                          <div className="mt-1 flex flex-wrap gap-1">
                            {ad.copy_analysis.keywords.map((keyword, i) => (
                              <span key={i} className="px-2 py-0.5 bg-muted rounded text-xs">
                                {keyword}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* External Link */}
                {ad.ad_snapshot_url && (
                  <div className="border-t pt-4">
                    <a
                      href={ad.ad_snapshot_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-primary hover:underline"
                    >
                      Meta Ad Library에서 보기 →
                    </a>
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-96 text-muted-foreground">
            Ad not found
          </div>
        )}
      </div>
    </div>
  );
}
