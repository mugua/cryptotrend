"use client"

import { useMemo } from "react"
import { cn } from "@/lib/utils"

interface TrendScoreGaugeProps {
  score: number
  label?: string
  size?: "sm" | "md" | "lg"
  className?: string
}

const SIZE_MAP = {
  sm: 120,
  md: 200,
  lg: 280,
} as const

function getScoreColor(score: number): string {
  if (score >= 80) return "#15803D"
  if (score >= 60) return "#22C55E"
  if (score >= 40) return "#EAB308"
  if (score >= 20) return "#F97316"
  return "#EF4444"
}

function getScoreLabel(score: number): string {
  if (score >= 80) return "Strong Bullish"
  if (score >= 60) return "Bullish"
  if (score >= 40) return "Neutral"
  if (score >= 20) return "Bearish"
  return "Strong Bearish"
}

export function TrendScoreGauge({
  score,
  label,
  size = "md",
  className,
}: TrendScoreGaugeProps) {
  const clampedScore = Math.max(0, Math.min(100, score))
  const dimension = SIZE_MAP[size]

  const gaugeConfig = useMemo(() => {
    const cx = dimension / 2
    const cy = dimension / 2
    const strokeWidth = dimension * 0.08
    const radius = (dimension - strokeWidth) / 2 - 4
    const startAngle = 135
    const endAngle = 405
    const totalArc = endAngle - startAngle

    const circumference = 2 * Math.PI * radius
    const arcLength = (totalArc / 360) * circumference
    const filledLength = (clampedScore / 100) * arcLength

    const startRad = (startAngle * Math.PI) / 180
    const startX = cx + radius * Math.cos(startRad)
    const startY = cy + radius * Math.sin(startRad)

    const endRad = ((startAngle + totalArc) * Math.PI) / 180
    const endX = cx + radius * Math.cos(endRad)
    const endY = cy + radius * Math.sin(endRad)

    const largeArcFlag = totalArc > 180 ? 1 : 0

    const arcPath = `M ${startX} ${startY} A ${radius} ${radius} 0 ${largeArcFlag} 1 ${endX} ${endY}`

    return {
      cx,
      cy,
      strokeWidth,
      radius,
      arcPath,
      arcLength,
      filledLength,
      dashOffset: arcLength - filledLength,
    }
  }, [dimension, clampedScore])

  const color = getScoreColor(clampedScore)
  const displayLabel = label ?? getScoreLabel(clampedScore)

  const fontSizeScore = dimension * 0.2
  const fontSizeLabel = dimension * 0.08

  if (score === null || score === undefined) {
    return (
      <div
        className={cn(
          "flex items-center justify-center text-muted-foreground",
          className
        )}
        style={{ width: dimension, height: dimension }}
      >
        No data
      </div>
    )
  }

  return (
    <div
      className={cn("inline-flex flex-col items-center", className)}
      style={{ width: dimension, height: dimension }}
    >
      <svg
        width={dimension}
        height={dimension}
        viewBox={`0 0 ${dimension} ${dimension}`}
      >
        {/* Background arc */}
        <path
          d={gaugeConfig.arcPath}
          fill="none"
          className="stroke-muted"
          strokeWidth={gaugeConfig.strokeWidth}
          strokeLinecap="round"
        />

        {/* Filled arc */}
        <path
          d={gaugeConfig.arcPath}
          fill="none"
          stroke={color}
          strokeWidth={gaugeConfig.strokeWidth}
          strokeLinecap="round"
          strokeDasharray={gaugeConfig.arcLength}
          strokeDashoffset={gaugeConfig.dashOffset}
          style={{
            transition: "stroke-dashoffset 1s ease-out, stroke 0.5s ease",
          }}
        />

        {/* Score text */}
        <text
          x={gaugeConfig.cx}
          y={gaugeConfig.cy - fontSizeLabel * 0.2}
          textAnchor="middle"
          dominantBaseline="central"
          className="fill-foreground"
          style={{
            fontSize: fontSizeScore,
            fontWeight: 700,
          }}
        >
          {Math.round(clampedScore)}
        </text>

        {/* Label text */}
        <text
          x={gaugeConfig.cx}
          y={gaugeConfig.cy + fontSizeScore * 0.7}
          textAnchor="middle"
          dominantBaseline="central"
          className="fill-muted-foreground"
          style={{
            fontSize: fontSizeLabel,
            fontWeight: 500,
          }}
        >
          {displayLabel}
        </text>
      </svg>
    </div>
  )
}
