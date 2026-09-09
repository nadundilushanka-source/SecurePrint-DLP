"use client";

import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Label, Pie, PieChart, XAxis, YAxis } from "recharts";
import {
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";

const CATEGORY_PALETTE = ["#2563eb", "#0891b2", "#7c3aed", "#d97706", "#dc2626", "#059669", "#4f46e5", "#db2777"];

function EmptyState({ label = "No data yet" }: { label?: string }) {
  return <div className="flex h-full min-h-[200px] items-center justify-center text-sm text-muted-foreground">{label}</div>;
}

// ---------------------------------------------------------------------------
// Classification distribution - donut with a centered total
// ---------------------------------------------------------------------------

const CLASSIFICATION_CONFIG: ChartConfig = {
  count: { label: "Documents" },
  PUBLIC: { label: "Public", color: "#059669" },
  INTERNAL: { label: "Internal", color: "#0284c7" },
  CONFIDENTIAL: { label: "Confidential", color: "#d97706" },
  RESTRICTED: { label: "Restricted", color: "#dc2626" },
};

export function ClassificationDonut({ data }: { data: Record<string, number> }) {
  const rows = Object.entries(data)
    .map(([classification, count]) => ({ classification, count }))
    .filter((r) => r.count > 0);
  const total = rows.reduce((sum, r) => sum + r.count, 0);

  if (total === 0) return <EmptyState />;

  return (
    <ChartContainer config={CLASSIFICATION_CONFIG} className="mx-auto aspect-square max-h-[260px]">
      <PieChart>
        <ChartTooltip content={<ChartTooltipContent hideLabel />} />
        <Pie data={rows} dataKey="count" nameKey="classification" innerRadius={62} outerRadius={92} strokeWidth={3} paddingAngle={2}>
          {rows.map((r) => (
            <Cell key={r.classification} fill={`var(--color-${r.classification})`} stroke="var(--card)" />
          ))}
          <Label
            content={({ viewBox }) => {
              if (!viewBox || !("cx" in viewBox) || !("cy" in viewBox)) return null;
              return (
                <text x={viewBox.cx} y={viewBox.cy} textAnchor="middle" dominantBaseline="middle">
                  <tspan x={viewBox.cx} y={viewBox.cy} className="fill-foreground text-2xl font-bold">
                    {total.toLocaleString()}
                  </tspan>
                  <tspan x={viewBox.cx} y={(viewBox.cy ?? 0) + 20} className="fill-muted-foreground text-xs">
                    total
                  </tspan>
                </text>
              );
            }}
          />
        </Pie>
        <ChartLegend content={<ChartLegendContent nameKey="classification" />} />
      </PieChart>
    </ChartContainer>
  );
}

// ---------------------------------------------------------------------------
// Blocked vs allowed - compact two-slice donut
// ---------------------------------------------------------------------------

const BLOCKED_ALLOWED_CONFIG: ChartConfig = {
  count: { label: "Jobs" },
  allowed: { label: "Allowed", color: "#059669" },
  blocked: { label: "Blocked", color: "#dc2626" },
};

export function BlockedAllowedDonut({ allowed, blocked }: { allowed: number; blocked: number }) {
  const rows = [
    { key: "allowed", count: allowed },
    { key: "blocked", count: blocked },
  ].filter((r) => r.count > 0);
  const total = allowed + blocked;

  if (total === 0) return <EmptyState />;

  return (
    <ChartContainer config={BLOCKED_ALLOWED_CONFIG} className="mx-auto aspect-square max-h-[260px]">
      <PieChart>
        <ChartTooltip content={<ChartTooltipContent hideLabel />} />
        <Pie data={rows} dataKey="count" nameKey="key" innerRadius={62} outerRadius={92} strokeWidth={3} paddingAngle={2}>
          {rows.map((r) => (
            <Cell key={r.key} fill={`var(--color-${r.key})`} stroke="var(--card)" />
          ))}
          <Label
            content={({ viewBox }) => {
              if (!viewBox || !("cx" in viewBox) || !("cy" in viewBox)) return null;
              return (
                <text x={viewBox.cx} y={viewBox.cy} textAnchor="middle" dominantBaseline="middle">
                  <tspan x={viewBox.cx} y={viewBox.cy} className="fill-foreground text-2xl font-bold">
                    {total.toLocaleString()}
                  </tspan>
                  <tspan x={viewBox.cx} y={(viewBox.cy ?? 0) + 20} className="fill-muted-foreground text-xs">
                    total
                  </tspan>
                </text>
              );
            }}
          />
        </Pie>
        <ChartLegend content={<ChartLegendContent nameKey="key" />} />
      </PieChart>
    </ChartContainer>
  );
}

// ---------------------------------------------------------------------------
// Risk score distribution - vertical bars, colored by severity band
// ---------------------------------------------------------------------------

const RISK_BAND_COLORS: Record<string, string> = {
  "0-20": "#059669",
  "21-40": "#0284c7",
  "41-70": "#d97706",
  "71-100": "#dc2626",
};

const RISK_CONFIG: ChartConfig = { value: { label: "Documents" } };

export function RiskScoreBarChart({ data }: { data: Record<string, number> }) {
  const rows = Object.entries(data).map(([band, value]) => ({ band, value }));
  if (rows.every((r) => r.value === 0)) return <EmptyState />;

  return (
    <ChartContainer config={RISK_CONFIG} className="h-[260px] w-full">
      <BarChart data={rows} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
        <CartesianGrid vertical={false} strokeDasharray="3 3" />
        <XAxis dataKey="band" tickLine={false} axisLine={false} tickMargin={8} />
        <YAxis tickLine={false} axisLine={false} tickMargin={8} allowDecimals={false} width={30} />
        <ChartTooltip content={<ChartTooltipContent />} />
        <Bar dataKey="value" radius={[6, 6, 0, 0]}>
          {rows.map((r) => (
            <Cell key={r.band} fill={RISK_BAND_COLORS[r.band] ?? "#2563eb"} />
          ))}
        </Bar>
      </BarChart>
    </ChartContainer>
  );
}

// ---------------------------------------------------------------------------
// Detections by category - horizontal bars, one hue per category
// ---------------------------------------------------------------------------

const CATEGORY_CONFIG: ChartConfig = { value: { label: "Detections" } };

export function CategoryBarChart({ data }: { data: { label: string; value: number }[] }) {
  if (data.length === 0) return <EmptyState />;

  return (
    <ChartContainer config={CATEGORY_CONFIG} className="h-[260px] w-full">
      <BarChart data={data} layout="vertical" margin={{ top: 8, right: 16, left: 8, bottom: 0 }}>
        <CartesianGrid horizontal={false} strokeDasharray="3 3" />
        <XAxis type="number" tickLine={false} axisLine={false} allowDecimals={false} />
        <YAxis type="category" dataKey="label" tickLine={false} axisLine={false} width={110} tick={{ fontSize: 11 }} />
        <ChartTooltip content={<ChartTooltipContent />} />
        <Bar dataKey="value" radius={[0, 6, 6, 0]}>
          {data.map((d, i) => (
            <Cell key={d.label} fill={CATEGORY_PALETTE[i % CATEGORY_PALETTE.length]} />
          ))}
        </Bar>
      </BarChart>
    </ChartContainer>
  );
}

// ---------------------------------------------------------------------------
// Print jobs over time - gradient-filled area chart
// ---------------------------------------------------------------------------

const JOBS_OVER_TIME_CONFIG: ChartConfig = { count: { label: "Jobs", color: "#2563eb" } };

export function JobsOverTimeChart({ data }: { data: { date: string; count: number }[] }) {
  if (data.length === 0) return <EmptyState />;

  return (
    <ChartContainer config={JOBS_OVER_TIME_CONFIG} className="h-[220px] w-full">
      <AreaChart data={data} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
        <defs>
          <linearGradient id="fillJobsOverTime" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="var(--color-count)" stopOpacity={0.35} />
            <stop offset="95%" stopColor="var(--color-count)" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid vertical={false} strokeDasharray="3 3" />
        <XAxis
          dataKey="date"
          tickLine={false}
          axisLine={false}
          tickMargin={8}
          tickFormatter={(v: string) => v.slice(5)}
        />
        <YAxis tickLine={false} axisLine={false} tickMargin={8} allowDecimals={false} width={30} />
        <ChartTooltip content={<ChartTooltipContent indicator="line" />} />
        <Area dataKey="count" type="monotone" fill="url(#fillJobsOverTime)" stroke="var(--color-count)" strokeWidth={2} />
      </AreaChart>
    </ChartContainer>
  );
}
