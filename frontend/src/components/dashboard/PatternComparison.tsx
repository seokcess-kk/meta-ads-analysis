'use client';

import { Pattern } from '@/lib/api';

interface PatternComparisonProps {
  patterns: Pattern[];
}

const FIELD_LABELS: Record<string, string> = {
  color_tone: '색조',
  has_person: '인물 포함',
  layout_type: '레이아웃',
  saturation: '채도',
  atmosphere: '분위기',
  formality: '격식',
  emotion: '감정',
  style: '스타일',
  core_message: '핵심 메시지',
};

export function PatternComparison({ patterns }: PatternComparisonProps) {
  const significantPatterns = patterns.filter(p => p.is_pattern).sort((a, b) => b.lift - a.lift);

  if (significantPatterns.length === 0) {
    return (
      <div className="bg-card border rounded-lg p-6">
        <h3 className="text-md font-semibold mb-4">성공 vs 일반 광고 패턴 비교</h3>
        <div className="text-center py-8 text-muted-foreground">
          유의미한 패턴이 아직 발견되지 않았습니다.
        </div>
      </div>
    );
  }

  return (
    <div className="bg-card border rounded-lg p-6">
      <h3 className="text-md font-semibold mb-4">성공 vs 일반 광고 패턴 비교</h3>
      <p className="text-sm text-muted-foreground mb-4">
        Lift 1.5 이상인 패턴만 표시됩니다. Lift가 높을수록 성공 광고에서 더 자주 나타나는 특성입니다.
      </p>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b">
              <th className="text-left py-3 px-4 font-medium">분석 항목</th>
              <th className="text-left py-3 px-4 font-medium">값</th>
              <th className="text-right py-3 px-4 font-medium">성공 광고</th>
              <th className="text-right py-3 px-4 font-medium">일반 광고</th>
              <th className="text-right py-3 px-4 font-medium">Lift</th>
            </tr>
          </thead>
          <tbody>
            {significantPatterns.map((pattern) => (
              <tr key={pattern.id} className="border-b last:border-b-0 hover:bg-muted/50">
                <td className="py-3 px-4">
                  <span className="px-2 py-0.5 bg-muted rounded text-xs">
                    {pattern.analysis_type === 'image' ? '이미지' : '카피'}
                  </span>
                  <span className="ml-2">
                    {FIELD_LABELS[pattern.field_name] || pattern.field_name}
                  </span>
                </td>
                <td className="py-3 px-4 font-medium">{pattern.field_value}</td>
                <td className="py-3 px-4 text-right">
                  <div className="flex items-center justify-end gap-2">
                    <div className="w-20 h-2 bg-muted rounded-full overflow-hidden">
                      <div
                        className="h-full bg-yellow-500"
                        style={{ width: `${pattern.successful_ratio * 100}%` }}
                      />
                    </div>
                    <span className="w-12">{(pattern.successful_ratio * 100).toFixed(0)}%</span>
                  </div>
                </td>
                <td className="py-3 px-4 text-right">
                  <div className="flex items-center justify-end gap-2">
                    <div className="w-20 h-2 bg-muted rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gray-400"
                        style={{ width: `${pattern.general_ratio * 100}%` }}
                      />
                    </div>
                    <span className="w-12">{(pattern.general_ratio * 100).toFixed(0)}%</span>
                  </div>
                </td>
                <td className="py-3 px-4 text-right">
                  <span className={`font-medium ${pattern.lift >= 2 ? 'text-green-600' : 'text-yellow-600'}`}>
                    {pattern.lift.toFixed(2)}x
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
