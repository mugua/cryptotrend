"use client"

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
} from "recharts"
import { cn, formatNumber } from "@/lib/utils"

interface VolumeDataPoint {
  time: string
  volume: number
  isUp?: boolean
}

interface VolumeBarChartProps {
  data: VolumeDataPoint[]
  height?: number
  className?: string
}

function CustomTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean
  payload?: Array<{ value: number; payload: VolumeDataPoint }>
  label?: string
}) {
  if (!active || !payload || payload.length === 0) return null

  return (
    <div className="rounded-lg border bg-card px-3 py-2 shadow-md">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-sm font-semibold text-foreground">
        Volume: {formatNumber(payload[0].value)}
      </p>
    </div>
  )
}

export function VolumeBarChart({
  data,
  height = 200,
  className,
}: VolumeBarChartProps) {
  if (!data || data.length === 0) {
    return (
      <div
        className={cn(
          "flex items-center justify-center rounded-lg border bg-card text-muted-foreground",
          className
        )}
        style={{ height }}
      >
        No data available
      </div>
    )
  }

  return (
    <div className={cn("w-full", className)}>
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
          <CartesianGrid
            strokeDasharray="3 3"
            className="stroke-border"
            vertical={false}
          />
          <XAxis
            dataKey="time"
            axisLine={false}
            tickLine={false}
            className="text-xs fill-muted-foreground"
            tick={{ fontSize: 11 }}
          />
          <YAxis
            axisLine={false}
            tickLine={false}
            className="text-xs fill-muted-foreground"
            tick={{ fontSize: 11 }}
            tickFormatter={(value: number) => formatNumber(value)}
            width={60}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="volume" radius={[2, 2, 0, 0]}>
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.isUp !== false ? "#22C55E" : "#EF4444"}
                fillOpacity={0.8}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
