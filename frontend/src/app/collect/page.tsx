'use client';

import { useState, useEffect } from 'react';
import { api, CollectJobStatus } from '@/lib/api';

const INDUSTRIES = [
  { value: 'education', label: '교육' },
  { value: 'ecommerce', label: '이커머스' },
  { value: 'finance', label: '금융' },
  { value: 'healthcare', label: '헬스케어' },
  { value: 'technology', label: '기술' },
  { value: 'food', label: '식품' },
  { value: 'fashion', label: '패션' },
  { value: 'travel', label: '여행' },
  { value: 'entertainment', label: '엔터테인먼트' },
  { value: 'other', label: '기타' },
];

const COUNTRIES = [
  { value: 'KR', label: '한국' },
  { value: 'US', label: '미국' },
  { value: 'JP', label: '일본' },
  { value: 'GB', label: '영국' },
  { value: 'DE', label: '독일' },
];

export default function CollectPage() {
  const [keywords, setKeywords] = useState('');
  const [industry, setIndustry] = useState('education');
  const [country, setCountry] = useState('KR');
  const [limit, setLimit] = useState(50);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<CollectJobStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) return;

    const pollStatus = async () => {
      try {
        const status = await api.getCollectionStatus(jobId);
        setJobStatus(status);

        if (status.status === 'completed' || status.status === 'failed') {
          return;
        }
      } catch (err) {
        console.error('Failed to fetch job status:', err);
      }
    };

    pollStatus();
    const interval = setInterval(pollStatus, 2000);
    return () => clearInterval(interval);
  }, [jobId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    setJobStatus(null);

    try {
      const keywordList = keywords
        .split(',')
        .map((k) => k.trim())
        .filter((k) => k.length > 0);

      if (keywordList.length === 0) {
        throw new Error('최소 1개의 키워드를 입력해주세요.');
      }

      const response = await api.startCollection({
        keywords: keywordList,
        industry,
        country,
        limit,
      });

      setJobId(response.job_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start collection');
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setJobId(null);
    setJobStatus(null);
    setError(null);
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Collect Ads</h1>
        <p className="mt-2 text-muted-foreground">
          Meta Ad Library에서 광고를 수집합니다.
        </p>
      </div>

      {!jobId ? (
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2">
              키워드 (쉼표로 구분)
            </label>
            <textarea
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              placeholder="예: 영어교육, 온라인강의, 어학원"
              className="w-full px-4 py-3 border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary resize-none"
              rows={3}
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">산업</label>
              <select
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                className="w-full px-4 py-3 border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
              >
                {INDUSTRIES.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">국가</label>
              <select
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                className="w-full px-4 py-3 border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
              >
                {COUNTRIES.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              수집 개수 (최대)
            </label>
            <input
              type="number"
              value={limit}
              onChange={(e) => setLimit(Number(e.target.value))}
              min={1}
              max={500}
              className="w-full px-4 py-3 border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          {error && (
            <div className="p-4 bg-destructive/10 text-destructive rounded-lg text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-3 px-4 bg-primary text-primary-foreground font-medium rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? '시작 중...' : '수집 시작'}
          </button>
        </form>
      ) : (
        <div className="space-y-6">
          <div className="p-6 border rounded-lg bg-card">
            <h2 className="text-lg font-semibold mb-4">수집 진행 상황</h2>

            {jobStatus ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">상태</span>
                  <span
                    className={`font-medium ${
                      jobStatus.status === 'completed'
                        ? 'text-green-600'
                        : jobStatus.status === 'failed'
                        ? 'text-red-600'
                        : 'text-blue-600'
                    }`}
                  >
                    {jobStatus.status === 'completed'
                      ? '완료'
                      : jobStatus.status === 'failed'
                      ? '실패'
                      : jobStatus.status === 'running'
                      ? '진행 중'
                      : '대기 중'}
                  </span>
                </div>

                <div className="w-full bg-muted rounded-full h-2">
                  <div
                    className="bg-primary h-2 rounded-full transition-all duration-300"
                    style={{ width: `${jobStatus.progress}%` }}
                  />
                </div>

                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">수집된 광고</span>
                  <span className="font-medium">
                    {jobStatus.collected_count}
                    {jobStatus.target_count && ` / ${jobStatus.target_count}`}
                  </span>
                </div>

                {jobStatus.error_message && (
                  <div className="p-3 bg-destructive/10 text-destructive rounded text-sm">
                    {jobStatus.error_message}
                  </div>
                )}

                {(jobStatus.status === 'completed' ||
                  jobStatus.status === 'failed') && (
                  <div className="flex gap-3 pt-4">
                    <button
                      onClick={resetForm}
                      className="flex-1 py-2 px-4 border rounded-lg hover:bg-muted"
                    >
                      새로운 수집
                    </button>
                    <a
                      href="/ads"
                      className="flex-1 py-2 px-4 bg-primary text-primary-foreground text-center rounded-lg hover:bg-primary/90"
                    >
                      갤러리로 이동
                    </a>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
              </div>
            )}
          </div>

          <p className="text-sm text-muted-foreground text-center">
            Job ID: {jobId}
          </p>
        </div>
      )}
    </div>
  );
}
