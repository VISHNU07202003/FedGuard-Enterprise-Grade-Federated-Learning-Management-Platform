import React from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, AreaChart, Area } from 'recharts';
import { cn } from '@/lib/utils';
import { MotionCard } from '@/components/ui/card';

// ============================================================================
// Tooltip
// ============================================================================

export function MinimalChartTooltip({ active, payload, label }: any) {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white border border-border shadow-sm rounded-lg p-3 text-sm">
        <p className="font-medium text-slate-900 mb-1">{label}</p>
        {payload.map((entry: any, index: number) => (
          <div key={index} className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
            <span className="text-slate-500">{entry.name}:</span>
            <span className="font-medium text-slate-900">{entry.value.toFixed(1)}</span>
          </div>
        ))}
      </div>
    );
  }
  return null;
}

// ============================================================================
// Cards Wrapper
// ============================================================================

interface ChartCardProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
}

export function ChartCard({ title, description, children, className }: ChartCardProps) {
  return (
    <MotionCard className={cn("p-6 flex flex-col", className)}>
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
        {description && <p className="text-sm text-slate-500">{description}</p>}
      </div>
      <div className="flex-1 w-full min-h-[250px]">
        {children}
      </div>
    </MotionCard>
  );
}

// ============================================================================
// Charts
// ============================================================================

interface PerformanceLineChartProps {
  data: any[];
  dataKeyX: string;
  lines: { key: string; color: string; name: string }[];
}

export function PerformanceLineChart({ data, dataKeyX, lines }: PerformanceLineChartProps) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
        <XAxis 
          dataKey={dataKeyX} 
          axisLine={false} 
          tickLine={false} 
          tick={{ fontSize: 12, fill: '#64748b' }} 
          dy={10}
        />
        <YAxis 
          axisLine={false} 
          tickLine={false} 
          tick={{ fontSize: 12, fill: '#64748b' }} 
        />
        <Tooltip content={<MinimalChartTooltip />} />
        {lines.map(line => (
          <Line 
            key={line.key}
            type="monotone" 
            dataKey={line.key} 
            name={line.name}
            stroke={line.color} 
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, strokeWidth: 0 }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}

interface AnomalyAreaChartProps {
  data: any[];
  dataKeyX: string;
  dataKeyY: string;
  color?: string;
  name?: string;
}

export function AnomalyAreaChart({ data, dataKeyX, dataKeyY, color = "#ef4444", name = "Volume" }: AnomalyAreaChartProps) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
        <defs>
          <linearGradient id={`color-${dataKeyY}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={color} stopOpacity={0.2}/>
            <stop offset="95%" stopColor={color} stopOpacity={0}/>
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
        <XAxis 
          dataKey={dataKeyX} 
          axisLine={false} 
          tickLine={false} 
          tick={{ fontSize: 12, fill: '#64748b' }} 
          dy={10}
        />
        <YAxis 
          axisLine={false} 
          tickLine={false} 
          tick={{ fontSize: 12, fill: '#64748b' }} 
        />
        <Tooltip content={<MinimalChartTooltip />} />
        <Area 
          type="monotone" 
          dataKey={dataKeyY} 
          name={name}
          stroke={color} 
          strokeWidth={2}
          fillOpacity={1} 
          fill={`url(#color-${dataKeyY})`} 
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
