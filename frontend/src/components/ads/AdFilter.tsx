'use client';

import { useState } from 'react';

interface FilterValues {
  industry: string;
  region: string;
  min_duration: string;
  sort: string;
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
];

export function AdFilter({ onFilterChange, initialValues = {} }: AdFilterProps) {
  const [filters, setFilters] = useState<FilterValues>({
    industry: initialValues.industry || '',
    region: initialValues.region || '',
    min_duration: initialValues.min_duration || '',
    sort: initialValues.sort || '-collected_at',
  });

  const handleChange = (key: keyof FilterValues, value: string) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFilterChange({ [key]: value || undefined });
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
    </div>
  );
}
