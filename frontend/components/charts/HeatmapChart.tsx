"use client"

import { useState } from "react"
import { cn } from "@/lib/utils"

interface HeatmapDataPoint {
  name: string
  score: number
  category: string
}

interface HeatmapChartProps {
  data: HeatmapDataPoint[]
  className?: string
}

function getCellColor(score: number): string {
  if (score >= 75) return "bg-green-700 dark:bg-green-800"
  if (score >= 50) return "bg-yellow-500 dark:bg-yellow-600"
  if (score >= 25) return "bg-orange-500 dark:bg-orange-600"
  return "bg-red-500 dark:bg-red-600"
}

function getCellTextColor(score: number): string {
  if (score >= 75) return "text-white"
  if (score >= 50) return "text-gray-900 dark:text-white"
  if (score >= 25) return "text-white"
  return "text-white"
}

export function HeatmapChart({ data, className }: HeatmapChartProps) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null)

  if (!data || data.length === 0) {
    return (
      <div
        className={cn(
          "flex h-[200px] items-center justify-center rounded-lg border bg-card text-muted-foreground",
          className
        )}
      >
        No data available
      </div>
    )
  }

  return (
    <div className={cn("w-full", className)}>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-4">
        {data.map((item, index) => (
          <div
            key={`${item.category}-${item.name}`}
            className={cn(
              "relative flex flex-col items-center justify-center rounded-lg p-3 transition-all duration-200",
              getCellColor(item.score),
              getCellTextColor(item.score),
              hoveredIndex === index && "ring-2 ring-primary ring-offset-2 ring-offset-background scale-105"
            )}
            onMouseEnter={() => setHoveredIndex(index)}
            onMouseLeave={() => setHoveredIndex(null)}
          >
            <span className="text-xs font-medium leading-tight text-center truncate w-full">
              {item.name}
            </span>
            <span className="text-lg font-bold mt-1">
              {Math.round(item.score)}
            </span>

            {hoveredIndex === index && (
              <div className="absolute -top-16 left-1/2 -translate-x-1/2 z-10 whitespace-nowrap rounded-lg border bg-card px-3 py-2 shadow-lg">
                <p className="text-sm font-medium text-foreground">{item.name}</p>
                <p className="text-xs text-muted-foreground">
                  Category: {item.category}
                </p>
                <p className="text-xs text-muted-foreground">
                  Score: <span className="font-semibold text-foreground">{item.score}</span> / 100
                </p>
                <div className="absolute left-1/2 -bottom-1 -translate-x-1/2 h-2 w-2 rotate-45 border-b border-r bg-card" />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
