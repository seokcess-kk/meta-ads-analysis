'use client';

import { useState } from 'react';
import { api, Formula } from '@/lib/api';

interface SuccessFormulaProps {
  formula: Formula | null;
  onGenerate?: () => void;
  isLoading?: boolean;
}

export function SuccessFormula({ formula, onGenerate, isLoading }: SuccessFormulaProps) {
  const [activeTab, setActiveTab] = useState<'insights' | 'strategies'>('insights');

  if (!formula || !formula.formula) {
    return (
      <div className="bg-card border rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">성공 광고 공식</h2>
        <div className="text-center py-8">
          <p className="text-muted-foreground mb-4">
            아직 성공 공식이 생성되지 않았습니다.
          </p>
          <button
            onClick={onGenerate}
            disabled={isLoading}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
          >
            {isLoading ? '생성 중...' : '공식 생성하기'}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-card border rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">성공 광고 공식</h2>
        <span className="text-sm text-muted-foreground">
          신뢰도: {(formula.confidence * 100).toFixed(0)}%
        </span>
      </div>

      {/* Formula */}
      <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-lg p-4 mb-6">
        <div className="flex items-start gap-3">
          <svg className="w-6 h-6 text-yellow-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
          <p className="text-lg font-medium text-gray-800">{formula.formula}</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setActiveTab('insights')}
          className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
            activeTab === 'insights'
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted text-muted-foreground hover:bg-muted/80'
          }`}
        >
          핵심 인사이트 ({formula.insights.length})
        </button>
        <button
          onClick={() => setActiveTab('strategies')}
          className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
            activeTab === 'strategies'
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted text-muted-foreground hover:bg-muted/80'
          }`}
        >
          추천 전략 ({formula.strategies.length})
        </button>
      </div>

      {/* Tab Content */}
      <div className="space-y-3">
        {activeTab === 'insights' && formula.insights.map((insight, index) => (
          <div key={index} className="bg-muted/50 rounded-lg p-4">
            <h4 className="font-medium text-sm">{insight.title}</h4>
            <p className="mt-1 text-sm text-muted-foreground">{insight.description}</p>
          </div>
        ))}
        {activeTab === 'strategies' && formula.strategies.map((strategy, index) => (
          <div key={index} className="bg-muted/50 rounded-lg p-4">
            <h4 className="font-medium text-sm">{strategy.title}</h4>
            <p className="mt-1 text-sm text-muted-foreground">{strategy.description}</p>
          </div>
        ))}
      </div>

      {/* Regenerate Button */}
      <div className="mt-6 pt-4 border-t">
        <button
          onClick={onGenerate}
          disabled={isLoading}
          className="text-sm text-primary hover:underline disabled:opacity-50"
        >
          {isLoading ? '생성 중...' : '공식 다시 생성하기'}
        </button>
      </div>
    </div>
  );
}
