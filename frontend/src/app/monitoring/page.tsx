'use client';

import { useState, useEffect } from 'react';
import { api, MonitoringKeyword, MonitoringRun } from '@/lib/api';

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

export default function MonitoringPage() {
  const [keywords, setKeywords] = useState<MonitoringKeyword[]>([]);
  const [selectedKeyword, setSelectedKeyword] = useState<MonitoringKeyword | null>(null);
  const [runs, setRuns] = useState<MonitoringRun[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRunning, setIsRunning] = useState<number | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    keyword: '',
    industry: 'education',
    country: 'KR',
  });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadKeywords();
  }, []);

  const loadKeywords = async () => {
    setIsLoading(true);
    try {
      const data = await api.listKeywords();
      setKeywords(data);
    } catch (err) {
      setError('키워드 목록을 불러오는데 실패했습니다.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const loadRuns = async (keywordId: number) => {
    try {
      const data = await api.getKeywordRuns(keywordId, 10);
      setRuns(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSelectKeyword = (keyword: MonitoringKeyword) => {
    setSelectedKeyword(keyword);
    loadRuns(keyword.id);
  };

  const handleCreateKeyword = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createKeyword(formData);
      setFormData({ keyword: '', industry: 'education', country: 'KR' });
      setShowForm(false);
      await loadKeywords();
    } catch (err) {
      setError('키워드 등록에 실패했습니다.');
      console.error(err);
    }
  };

  const handleToggleActive = async (keyword: MonitoringKeyword) => {
    try {
      await api.updateKeyword(keyword.id, { is_active: !keyword.is_active });
      await loadKeywords();
    } catch (err) {
      setError('상태 변경에 실패했습니다.');
      console.error(err);
    }
  };

  const handleRunNow = async (keyword: MonitoringKeyword) => {
    setIsRunning(keyword.id);
    try {
      await api.runKeyword(keyword.id, 50);
      await loadKeywords();
      if (selectedKeyword?.id === keyword.id) {
        await loadRuns(keyword.id);
      }
    } catch (err) {
      setError('수집 실행에 실패했습니다.');
      console.error(err);
    } finally {
      setIsRunning(null);
    }
  };

  const handleDeleteKeyword = async (keyword: MonitoringKeyword) => {
    if (!confirm(`"${keyword.keyword}" 키워드를 삭제하시겠습니까?`)) return;
    try {
      await api.deleteKeyword(keyword.id);
      if (selectedKeyword?.id === keyword.id) {
        setSelectedKeyword(null);
        setRuns([]);
      }
      await loadKeywords();
    } catch (err) {
      setError('삭제에 실패했습니다.');
      console.error(err);
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleString('ko-KR');
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold">자동 모니터링</h1>
            <p className="text-muted-foreground mt-1">
              키워드를 등록하면 자동으로 새 광고를 수집합니다
            </p>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
          >
            키워드 등록
          </button>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
            {error}
            <button onClick={() => setError(null)} className="ml-4 underline">닫기</button>
          </div>
        )}

        {/* Add Keyword Form */}
        {showForm && (
          <div className="mb-6 bg-card border rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4">새 키워드 등록</h2>
            <form onSubmit={handleCreateKeyword} className="flex flex-wrap gap-4">
              <div className="flex-1 min-w-[200px]">
                <label className="block text-sm font-medium mb-1">키워드</label>
                <input
                  type="text"
                  value={formData.keyword}
                  onChange={(e) => setFormData({ ...formData, keyword: e.target.value })}
                  placeholder="검색할 키워드"
                  className="w-full px-3 py-2 border rounded-md bg-background"
                  required
                />
              </div>
              <div className="w-40">
                <label className="block text-sm font-medium mb-1">산업</label>
                <select
                  value={formData.industry}
                  onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                  className="w-full px-3 py-2 border rounded-md bg-background"
                >
                  {INDUSTRIES.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>
              <div className="w-24">
                <label className="block text-sm font-medium mb-1">국가</label>
                <select
                  value={formData.country}
                  onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                  className="w-full px-3 py-2 border rounded-md bg-background"
                >
                  <option value="KR">한국</option>
                  <option value="US">미국</option>
                  <option value="JP">일본</option>
                </select>
              </div>
              <div className="flex items-end gap-2">
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                >
                  등록
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="px-4 py-2 border rounded-md hover:bg-muted"
                >
                  취소
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Keywords List */}
          <div className="lg:col-span-2">
            <div className="bg-card border rounded-lg">
              <div className="p-4 border-b">
                <h2 className="font-semibold">등록된 키워드 ({keywords.length})</h2>
              </div>
              {keywords.length === 0 ? (
                <div className="p-8 text-center text-muted-foreground">
                  등록된 키워드가 없습니다.
                </div>
              ) : (
                <div className="divide-y">
                  {keywords.map((keyword) => (
                    <div
                      key={keyword.id}
                      className={`p-4 hover:bg-muted/50 cursor-pointer ${
                        selectedKeyword?.id === keyword.id ? 'bg-muted/50' : ''
                      }`}
                      onClick={() => handleSelectKeyword(keyword)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <span
                            className={`w-2 h-2 rounded-full ${
                              keyword.is_active ? 'bg-green-500' : 'bg-gray-400'
                            }`}
                          />
                          <div>
                            <span className="font-medium">{keyword.keyword}</span>
                            <div className="text-sm text-muted-foreground">
                              {INDUSTRIES.find(i => i.value === keyword.industry)?.label || keyword.industry}
                              {' | '}
                              {keyword.country}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleRunNow(keyword);
                            }}
                            disabled={isRunning === keyword.id}
                            className="px-3 py-1 text-sm bg-primary text-primary-foreground rounded hover:bg-primary/90 disabled:opacity-50"
                          >
                            {isRunning === keyword.id ? '수집중...' : '즉시 실행'}
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleToggleActive(keyword);
                            }}
                            className={`px-3 py-1 text-sm rounded ${
                              keyword.is_active
                                ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
                                : 'bg-green-100 text-green-700 hover:bg-green-200'
                            }`}
                          >
                            {keyword.is_active ? '일시정지' : '활성화'}
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteKeyword(keyword);
                            }}
                            className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200"
                          >
                            삭제
                          </button>
                        </div>
                      </div>
                      <div className="mt-2 text-xs text-muted-foreground">
                        마지막 실행: {formatDate(keyword.last_run_at)}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Run History */}
          <div>
            <div className="bg-card border rounded-lg">
              <div className="p-4 border-b">
                <h2 className="font-semibold">
                  실행 이력
                  {selectedKeyword && (
                    <span className="font-normal text-muted-foreground ml-2">
                      ({selectedKeyword.keyword})
                    </span>
                  )}
                </h2>
              </div>
              {!selectedKeyword ? (
                <div className="p-8 text-center text-muted-foreground text-sm">
                  키워드를 선택하면 실행 이력을 볼 수 있습니다
                </div>
              ) : runs.length === 0 ? (
                <div className="p-8 text-center text-muted-foreground text-sm">
                  실행 이력이 없습니다
                </div>
              ) : (
                <div className="divide-y max-h-96 overflow-y-auto">
                  {runs.map((run) => (
                    <div key={run.id} className="p-3">
                      <div className="flex items-center justify-between">
                        <span
                          className={`px-2 py-0.5 text-xs rounded ${
                            run.status === 'completed'
                              ? 'bg-green-100 text-green-700'
                              : run.status === 'failed'
                              ? 'bg-red-100 text-red-700'
                              : 'bg-yellow-100 text-yellow-700'
                          }`}
                        >
                          {run.status}
                        </span>
                        <span className="text-sm font-medium">
                          +{run.new_ads_count} ads
                        </span>
                      </div>
                      <div className="mt-1 text-xs text-muted-foreground">
                        {formatDate(run.started_at)}
                      </div>
                      {run.error_message && (
                        <div className="mt-1 text-xs text-red-600">
                          {run.error_message}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
