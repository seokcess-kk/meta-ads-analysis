'use client';

import { useState, useEffect } from 'react';
import { api, ScoringStats, Pattern, Formula } from '@/lib/api';
import { StatCard, SuccessFormula, PatternChart, PatternComparison } from '@/components/dashboard';

export default function DashboardPage() {
  const [stats, setStats] = useState<ScoringStats | null>(null);
  const [patterns, setPatterns] = useState<Pattern[]>([]);
  const [formula, setFormula] = useState<Formula | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [statsData, patternsData, formulaData] = await Promise.all([
        api.getScoringStats(),
        api.getPatterns({ patterns_only: false }),
        api.getFormula(),
      ]);
      setStats(statsData);
      setPatterns(patternsData);
      setFormula(formulaData);
    } catch (err) {
      setError('데이터를 불러오는데 실패했습니다.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCalculateScores = async () => {
    setIsAnalyzing(true);
    try {
      await api.calculateScores();
      await loadData();
    } catch (err) {
      setError('점수 계산에 실패했습니다.');
      console.error(err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleAnalyzePatterns = async () => {
    setIsAnalyzing(true);
    try {
      await api.analyzePatterns();
      const patternsData = await api.getPatterns({ patterns_only: false });
      setPatterns(patternsData);
    } catch (err) {
      setError('패턴 분석에 실패했습니다.');
      console.error(err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleGenerateFormula = async () => {
    setIsGenerating(true);
    try {
      const result = await api.generateFormula();
      setFormula(result);
    } catch (err) {
      setError('공식 생성에 실패했습니다.');
      console.error(err);
    } finally {
      setIsGenerating(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    );
  }

  const significantPatterns = patterns.filter(p => p.is_pattern);

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold">인사이트 대시보드</h1>
            <p className="text-muted-foreground mt-1">
              성공 광고의 패턴과 공통 인사이트를 확인하세요
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleCalculateScores}
              disabled={isAnalyzing}
              className="px-4 py-2 text-sm font-medium border rounded-md hover:bg-muted disabled:opacity-50"
            >
              {isAnalyzing ? '처리 중...' : '점수 재계산'}
            </button>
            <button
              onClick={handleAnalyzePatterns}
              disabled={isAnalyzing}
              className="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
            >
              {isAnalyzing ? '분석 중...' : '패턴 분석'}
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard
            title="총 광고 수"
            value={stats?.total_scored || 0}
            subtitle="점수 계산 완료"
            icon={
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            }
          />
          <StatCard
            title="성공 광고"
            value={stats?.successful_count || 0}
            subtitle={`상위 ${stats?.success_rate?.toFixed(1) || 0}%`}
            icon={
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
            }
          />
          <StatCard
            title="평균 점수"
            value={stats?.avg_total_score?.toFixed(1) || 0}
            subtitle={`최고: ${stats?.max_score?.toFixed(1) || 0}`}
            icon={
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            }
          />
          <StatCard
            title="발견된 패턴"
            value={significantPatterns.length}
            subtitle="Lift >= 1.5"
            icon={
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            }
          />
        </div>

        {/* Success Formula */}
        <div className="mb-8">
          <SuccessFormula
            formula={formula}
            onGenerate={handleGenerateFormula}
            isLoading={isGenerating}
          />
        </div>

        {/* Charts */}
        {patterns.length > 0 && (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <PatternChart
                patterns={patterns}
                type="bar"
                title="색조별 분포"
                fieldName="color_tone"
              />
              <PatternChart
                patterns={patterns}
                type="bar"
                title="레이아웃별 분포"
                fieldName="layout_type"
              />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <PatternChart
                patterns={patterns}
                type="bar"
                title="카피 톤 (격식)"
                fieldName="formality"
              />
              <PatternChart
                patterns={patterns}
                type="bar"
                title="감정 소구"
                fieldName="emotion"
              />
            </div>

            {/* Pattern Comparison Table */}
            <div className="mb-8">
              <PatternComparison patterns={patterns} />
            </div>
          </>
        )}

        {patterns.length === 0 && (
          <div className="text-center py-12 bg-card border rounded-lg">
            <p className="text-muted-foreground mb-4">
              아직 분석된 패턴이 없습니다.
            </p>
            <button
              onClick={handleAnalyzePatterns}
              disabled={isAnalyzing}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
            >
              패턴 분석 시작
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
