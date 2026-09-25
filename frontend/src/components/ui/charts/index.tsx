import React from 'react';
import { DataState } from '@/components/ui/data-state';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, AreaChart, Area, Legend } from 'recharts';
import { cn } from '@/lib/utils';
import { MotionCard } from '@/components/ui/card';

// ============================================================================
// Tooltip
// ============================================================================

export function MinimalChartTooltip({ active, payload, label }: { active?: boolean; payload?: { color?: string; name?: string; value?: number | string }[]; label?: string | number }) {
  if (active && payload && payload.length) {
    return (
      <div className="bg-card border border-border shadow-sm rounded-lg p-3 text-sm">
        <p className="font-medium text-foreground mb-1">{label}</p>
        {payload.map((entry, index) => (
          <div key={index} className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
            <span className="text-muted-foreground">{entry.name}:</span>
            <span className="font-medium text-foreground">{typeof entry.value === 'number' ? entry.value.toLocaleString(undefined, { maximumSignificantDigits: 6 }) : entry.value ?? 'Unavailable'}</span>
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
    <MotionCard className={cn("p-5 sm:p-6 min-w-0 flex flex-col", className)}>
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-foreground">{title}</h3>
        {description && <p className="text-sm text-muted-foreground">{description}</p>}
      </div>
      <div className="w-full h-[280px] min-w-0">
        {children}
      </div>
    </MotionCard>
  );
}

// ============================================================================
// Charts
// ============================================================================

interface PerformanceLineChartProps {
  data: Record<string, unknown>[];
  dataKeyX: string;
  lines: { key: string; color: string; name: string }[];
}

export function PerformanceLineChart({ data, dataKeyX, lines }: PerformanceLineChartProps) {
  if (!data.length) return <DataState title="No measurements yet" description="Reported measurements will appear here when available." />;
  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart accessibilityLayer data={data} margin={{ top: 5, right: 10, left: 0, bottom: 12 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#263448" />
        <XAxis
          dataKey={dataKeyX}
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 12, fill: '#9dacc1' }}
          dy={8}
          minTickGap={28}
        />
        <YAxis
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 12, fill: '#9dacc1' }}
        />
        <Tooltip content={<MinimalChartTooltip />} />
        <Legend iconType="plainline" wrapperStyle={{ fontSize: 12, paddingTop: 16 }} />
        {lines.map(line => (
          <Line
            key={line.key}
            type="linear"
            isAnimationActive={false}
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
  data: Record<string, unknown>[];
  dataKeyX: string;
  dataKeyY: string;
  color?: string;
  name?: string;
}

export function AnomalyAreaChart({ data, dataKeyX, dataKeyY, color = "#ef4444", name = "Volume" }: AnomalyAreaChartProps) {
  if (!data.length) return <DataState title="No measurements yet" description="Reported measurements will appear here when available." />;
  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart accessibilityLayer data={data} margin={{ top: 5, right: 10, left: 0, bottom: 12 }}>
        <defs>
          <linearGradient id={`color-${dataKeyY}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={color} stopOpacity={0.2}/>
            <stop offset="95%" stopColor={color} stopOpacity={0}/>
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#263448" />
        <XAxis
          dataKey={dataKeyX}
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 12, fill: '#9dacc1' }}
          dy={8}
          minTickGap={28}
        />
        <YAxis
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 12, fill: '#9dacc1' }}
        />
        <Tooltip content={<MinimalChartTooltip />} />
        <Area
          type="linear"
            isAnimationActive={false}
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
