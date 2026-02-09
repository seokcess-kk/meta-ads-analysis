'use client';

import { useState } from 'react';

interface FilterValues {
  industry: string;
  region: string;
  min_duration: string;
  sort: string;
  successful_only: boolean;
}

interface AdFilterProps {
  onFilterChange: (filters: Partial<FilterValues>) => void;
  initialValues?: Partial<FilterValues>;
}

const INDUSTRIES = [
  { value: '', label: '전체 산업' },
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

const REGIONS = [
  { value: '', label: '전체 지역' },
  { value: 'KR', label: '한국' },
  { value: 'US', label: '미국' },
  { value: 'JP', label: '일본' },
  { value: 'GB', label: '영국' },
  { value: 'DE', label: '독일' },
];

const DURATIONS = [
  { value: '', label: '모든 기간' },
  { value: '7', label: '7일 이상' },
  { value: '14', label: '14일 이상' },
  { value: '30', label: '30일 이상' },
  { value: '60', label: '60일 이상' },
];

const SORT_OPTIONS = [
  { value: '-collected_at', label: '최신순' },
  { value: 'collected_at', label: '오래된순' },
  { value: '-duration_days', label: '집행기간 긴순' },
  { value: 'duration_days', label: '집행기간 짧은순' },
  { value: '-success_score', label: '성공점수 높은순' },
];

export function AdFilter({ onFilterChange, initialValues = {} }: AdFilterProps) {
  const [filters, setFilters] = useState<FilterValues>({
    industry: initialValues.industry || '',
    region: initialValues.region || '',
    min_duration: initialValues.min_duration || '',
    sort: initialValues.sort || '-collected_at',
    successful_only: false,
  });

  const handleChange = (key: keyof FilterValues, value: string | boolean) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    if (key === 'successful_only') {
      onFilterChange({ [key]: value as boolean });
    } else {
      onFilterChange({ [key]: value || undefined });
    }
  };

  return (
    <div className="flex flex-wrap gap-4 p-4 bg-card rounded-lg border">
      <div className="flex-1 min-w-[150px]">
        <label className="block text-xs font-medium text-muted-foreground mb-1">
          산업
        </label>
        <select
          value={filters.industry}
          onChange={(e) => handleChange('industry', e.target.value)}
          className="w-full px-3 py-2 text-sm border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
        >
          {INDUSTRIES.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      <div className="flex-1 min-w-[150px]">
        <label className="block text-xs font-medium text-muted-foreground mb-1">
          지역
        </label>
        <select
          value={filters.region}
          onChange={(e) => handleChange('region', e.target.value)}
          className="w-full px-3 py-2 text-sm border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
        >
          {REGIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      <div className="flex-1 min-w-[150px]">
        <label className="block text-xs font-medium text-muted-foreground mb-1">
          최소 집행기간
        </label>
        <select
          value={filters.min_duration}
          onChange={(e) => handleChange('min_duration', e.target.value)}
          className="w-full px-3 py-2 text-sm border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
        >
          {DURATIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      <div className="flex-1 min-w-[150px]">
        <label className="block text-xs font-medium text-muted-foreground mb-1">
          정렬
        </label>
        <select
          value={filters.sort}
          onChange={(e) => handleChange('sort', e.target.value)}
          className="w-full px-3 py-2 text-sm border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
        >
          {SORT_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      <div className="flex items-end min-w-[150px]">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={filters.successful_only}
            onChange={(e) => handleChange('successful_only', e.target.checked)}
            className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
          />
          <span className="text-sm font-medium flex items-center gap-1">
            <svg className="w-4 h-4 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            성공 광고만
          </span>
        </label>
      </div>
    </div>
  );
}
