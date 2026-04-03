"use client"

import { useEffect, useRef, useState } from "react"
import { createChart, IChartApi, ISeriesApi } from "lightweight-charts"
import { cn } from "@/lib/utils"

interface CandlestickData {
  time: string
  open: number
  high: number
  low: number
  close: number
}

interface TradingViewChartProps {
  data: CandlestickData[]
  height?: number
  className?: string
}

export function TradingViewChart({
  data,
  height = 400,
  className,
}: TradingViewChartProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const candlestickSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null)
  const volumeSeriesRef = useRef<ISeriesApi<"Histogram"> | null>(null)
  const [isEmpty, setIsEmpty] = useState(false)

  useEffect(() => {
    if (!data || data.length === 0) {
      setIsEmpty(true)
      return
    }
    setIsEmpty(false)
  }, [data])

  useEffect(() => {
    if (!containerRef.current || isEmpty) return

    const isDark = document.documentElement.classList.contains("dark")

    const chart = createChart(containerRef.current, {
      height,
      layout: {
        background: { color: isDark ? "#0F172A" : "#FFFFFF" },
        textColor: isDark ? "#E2E8F0" : "#1A1A2E",
      },
      grid: {
        vertLines: { color: isDark ? "#1E293B" : "#E5E7EB" },
        horzLines: { color: isDark ? "#1E293B" : "#E5E7EB" },
      },
      crosshair: {
        mode: 0,
      },
      rightPriceScale: {
        borderColor: isDark ? "#334155" : "#D1D5DB",
      },
      timeScale: {
        borderColor: isDark ? "#334155" : "#D1D5DB",
        timeVisible: true,
      },
    })

    chartRef.current = chart

    const candlestickSeries = chart.addCandlestickSeries({
      upColor: "#22C55E",
      downColor: "#EF4444",
      borderUpColor: "#22C55E",
      borderDownColor: "#EF4444",
      wickUpColor: "#22C55E",
      wickDownColor: "#EF4444",
    })

    candlestickSeriesRef.current = candlestickSeries
    candlestickSeries.setData(
      data.map((d) => ({
        time: d.time,
        open: d.open,
        high: d.high,
        low: d.low,
        close: d.close,
      }))
    )

    const volumeSeries = chart.addHistogramSeries({
      priceFormat: { type: "volume" },
      priceScaleId: "",
    })

    volumeSeriesRef.current = volumeSeries
    volumeSeries.priceScale().applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    })
    volumeSeries.setData(
      data.map((d) => ({
        time: d.time,
        value: Math.abs(d.close - d.open) * 1000,
        color: d.close >= d.open ? "rgba(34,197,94,0.3)" : "rgba(239,68,68,0.3)",
      }))
    )

    chart.timeScale().fitContent()

    const handleResize = () => {
      if (containerRef.current) {
        chart.applyOptions({ width: containerRef.current.clientWidth })
      }
    }

    window.addEventListener("resize", handleResize)
    handleResize()

    return () => {
      window.removeEventListener("resize", handleResize)
      chart.remove()
      chartRef.current = null
      candlestickSeriesRef.current = null
      volumeSeriesRef.current = null
    }
  }, [data, height, isEmpty])

  if (isEmpty) {
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
    <div
      ref={containerRef}
      className={cn("w-full rounded-lg overflow-hidden", className)}
      style={{ height }}
    />
  )
}
