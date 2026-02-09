'use client';

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { Pattern } from '@/lib/api';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

interface PatternChartProps {
  patterns: Pattern[];
  type: 'bar' | 'pie';
  title: string;
  fieldName: string;
}

export function PatternChart({ patterns, type, title, fieldName }: PatternChartProps) {
  const filteredPatterns = patterns.filter(p => p.field_name === fieldName);

  if (filteredPatterns.length === 0) {
    return (
      <div className="bg-card border rounded-lg p-6">
        <h3 className="text-md font-semibold mb-4">{title}</h3>
        <div className="h-64 flex items-center justify-center text-muted-foreground">
          데이터 없음
        </div>
      </div>
    );
  }

  const chartData = filteredPatterns.map(p => ({
    name: p.field_value,
    '성공 광고': Math.round(p.successful_ratio * 100),
    '일반 광고': Math.round(p.general_ratio * 100),
    lift: p.lift,
  }));

  if (type === 'pie') {
    const pieData = filteredPatterns.map(p => ({
      name: p.field_value,
      value: p.successful_count,
    }));

    return (
      <div className="bg-card border rounded-lg p-6">
        <h3 className="text-md font-semibold mb-4">{title}</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {pieData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
    );
  }

  return (
    <div className="bg-card border rounded-lg p-6">
      <h3 className="text-md font-semibold mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} domain={[0, 100]} />
          <Tooltip
            formatter={(value: number, name: string) => [`${value}%`, name]}
            contentStyle={{ fontSize: 12 }}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar dataKey="성공 광고" fill="#FBBF24" />
          <Bar dataKey="일반 광고" fill="#94A3B8" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
