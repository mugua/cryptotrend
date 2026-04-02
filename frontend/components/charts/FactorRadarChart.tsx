"use client"

import {
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Tooltip,
} from "recharts"
import { cn } from "@/lib/utils"

interface RadarDataPoint {
  category: string
  score: number
  fullMark: number
}

interface FactorRadarChartProps {
  data: RadarDataPoint[]
  className?: string
}

function CustomTooltip({
  active,
  payload,
}: {
  active?: boolean
  payload?: Array<{ payload: RadarDataPoint }>
}) {
  if (!active || !payload || payload.length === 0) return null

  const item = payload[0].payload

  return (
    <div className="rounded-lg border bg-card px-3 py-2 shadow-md">
      <p className="text-sm font-medium text-foreground">{item.category}</p>
      <p className="text-sm text-muted-foreground">
        Score: <span className="font-semibold text-foreground">{item.score}</span>
        <span className="text-xs"> / {item.fullMark}</span>
      </p>
    </div>
  )
}

export function FactorRadarChart({ data, className }: FactorRadarChartProps) {
  if (!data || data.length === 0) {
    return (
      <div
        className={cn(
          "flex h-[300px] items-center justify-center rounded-lg border bg-card text-muted-foreground",
          className
        )}
      >
        No data available
      </div>
    )
  }

  return (
    <div className={cn("w-full", className)}>
      <ResponsiveContainer width="100%" height={300}>
        <RadarChart cx="50%" cy="50%" outerRadius="70%" data={data}>
          <PolarGrid
            className="stroke-border"
            strokeDasharray="3 3"
          />
          <PolarAngleAxis
            dataKey="category"
            className="text-xs fill-foreground"
            tick={{ fontSize: 12 }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, "dataMax"]}
            className="text-xs fill-muted-foreground"
            tick={{ fontSize: 10 }}
          />
          <Radar
            name="Score"
            dataKey="score"
            stroke="hsl(var(--primary))"
            fill="hsl(var(--primary))"
            fillOpacity={0.25}
            strokeWidth={2}
          />
          <Tooltip content={<CustomTooltip />} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}
