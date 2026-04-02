from __future__ import annotations
from app.engine.weights import ONCHAIN_WEIGHTS


class OnchainAnalyzer:
    """On-chain data analysis and scoring."""

    @staticmethod
    def analyze_active_addresses(data: dict) -> dict:
        latest = float(data.get("latest", 900_000))
        avg = float(data.get("avg_30d", 900_000))
        values = data.get("values", [])

        # Score: compare latest vs 30-day average
        if avg == 0:
            ratio = 1.0
        else:
            ratio = latest / avg

        if ratio >= 1.15:
            score = 80.0
            trend = "strongly_rising"
        elif ratio >= 1.05:
            score = 70.0
            trend = "rising"
        elif ratio >= 0.95:
            score = 50.0
            trend = "stable"
        elif ratio >= 0.85:
            score = 35.0
            trend = "falling"
        else:
            score = 20.0
            trend = "strongly_falling"

        # Check recent 7-day vs prior 7-day if enough data
        if len(values) >= 14:
            recent7 = sum(values[-7:]) / 7
            prior7 = sum(values[-14:-7]) / 7
            if prior7 > 0:
                week_change = (recent7 - prior7) / prior7
                score = min(100.0, max(0.0, score + week_change * 50))

        return {
            "score": round(score, 2),
            "trend": trend,
            "latest": latest,
            "avg_30d": avg,
            "ratio_vs_avg": round(ratio, 4),
        }

    @staticmethod
    def analyze_whale_transactions(data: list[dict]) -> dict:
        if not data:
            return {"score": 50.0, "signal": "neutral", "net_flow_usd": 0, "tx_count": 0}

        exchange_inflow_usd = 0.0
        exchange_outflow_usd = 0.0

        for tx in data:
            amount_usd = float(tx.get("amount_usd", 0))
            from_type = tx.get("from_type", "unknown")
            to_type = tx.get("to_type", "unknown")
            if to_type == "exchange":
                exchange_inflow_usd += amount_usd
            if from_type == "exchange":
                exchange_outflow_usd += amount_usd

        net_flow = exchange_outflow_usd - exchange_inflow_usd  # positive = outflow (bullish)
        total = exchange_inflow_usd + exchange_outflow_usd

        if total == 0:
            score = 50.0
            signal = "neutral"
        else:
            flow_ratio = net_flow / total
            score = 50.0 + flow_ratio * 50.0
            score = max(0.0, min(100.0, score))
            signal = "bullish" if flow_ratio > 0.1 else "bearish" if flow_ratio < -0.1 else "neutral"

        return {
            "score": round(score, 2),
            "signal": signal,
            "net_flow_usd": round(net_flow, 2),
            "exchange_inflow_usd": round(exchange_inflow_usd, 2),
            "exchange_outflow_usd": round(exchange_outflow_usd, 2),
            "tx_count": len(data),
        }

    @staticmethod
    def analyze_exchange_flow(data: dict) -> dict:
        # data: {'inflow': float, 'outflow': float} in BTC/ETH terms
        inflow = float(data.get("inflow", 1000))
        outflow = float(data.get("outflow", 1000))
        total = inflow + outflow

        net_flow = outflow - inflow  # positive = more leaving exchanges = bullish
        if total == 0:
            score = 50.0
        else:
            ratio = net_flow / total
            score = 50.0 + ratio * 50.0
            score = max(0.0, min(100.0, score))

        signal = "bullish" if net_flow > 0 else "bearish" if net_flow < 0 else "neutral"
        return {
            "score": round(score, 2),
            "signal": signal,
            "net_flow": round(net_flow, 4),
            "inflow": inflow,
            "outflow": outflow,
        }

    @staticmethod
    def analyze_hash_rate(data: dict) -> dict:
        latest = float(data.get("latest", 500e18))
        avg = float(data.get("avg_30d", 500e18))
        values = data.get("values", [])

        if avg == 0:
            ratio = 1.0
        else:
            ratio = latest / avg

        if ratio >= 1.1:
            score = 80.0
            trend = "rising"
        elif ratio >= 1.02:
            score = 65.0
            trend = "slightly_rising"
        elif ratio >= 0.98:
            score = 50.0
            trend = "stable"
        elif ratio >= 0.90:
            score = 35.0
            trend = "falling"
        else:
            score = 20.0
            trend = "strongly_falling"

        return {
            "score": round(score, 2),
            "trend": trend,
            "latest": latest,
            "avg_30d": avg,
            "ratio_vs_avg": round(ratio, 4),
        }

    @staticmethod
    def analyze_gas_fee(data: dict) -> dict:
        propose_gas = float(data.get("propose_gas", 25.0))

        # Low gas = low network congestion = mixed signal
        # Very high gas = high demand = slight bullish but costly
        if propose_gas < 5:
            score = 55.0
            signal = "low_activity"
        elif propose_gas < 20:
            score = 65.0
            signal = "normal"
        elif propose_gas < 50:
            score = 60.0
            signal = "elevated"
        elif propose_gas < 100:
            score = 50.0
            signal = "high"
        else:
            score = 40.0
            signal = "very_high"

        return {"score": round(score, 2), "signal": signal, "propose_gas_gwei": propose_gas}

    @staticmethod
    def calculate_mvrv(price: float, realized_value: float) -> float:
        if realized_value <= 0:
            return 1.0
        return price / realized_value

    @staticmethod
    def calculate_nvt(network_value: float, tx_volume: float) -> float:
        if tx_volume <= 0:
            return 50.0
        return network_value / tx_volume

    def score_onchain(self, coin_id: str, collectors_data: dict) -> dict:
        w = ONCHAIN_WEIGHTS

        # Active addresses
        addr_data = collectors_data.get("active_addresses", {})
        addr_result = self.analyze_active_addresses(addr_data)

        # Whale transactions
        whale_data = collectors_data.get("whale_transactions", [])
        whale_result = self.analyze_whale_transactions(whale_data)

        # Exchange flow (often not directly available; use whale data proxy)
        flow_data = collectors_data.get("exchange_flow", {"inflow": 1000, "outflow": 1000})
        flow_result = self.analyze_exchange_flow(flow_data)

        # Hash rate (BTC only; ETH uses gas)
        if coin_id == "bitcoin":
            hash_data = collectors_data.get("hash_rate", {})
            hr_result = self.analyze_hash_rate(hash_data)
        else:
            hr_result = {"score": 50.0, "trend": "n/a"}

        # Gas fee (ETH only; BTC uses hash rate proxy)
        if coin_id == "ethereum":
            gas_data = collectors_data.get("gas_price", {})
            gas_result = self.analyze_gas_fee(gas_data)
        else:
            gas_result = {"score": 50.0, "signal": "n/a"}

        composite = (
            addr_result["score"] * w["active_addresses"]
            + whale_result["score"] * w["whale_activity"]
            + flow_result["score"] * w["exchange_flow"]
            + hr_result["score"] * w["hash_rate"]
            + gas_result["score"] * w["gas_fee"]
        )

        return {
            "score": round(composite, 2),
            "active_addresses": addr_result,
            "whale_transactions": whale_result,
            "exchange_flow": flow_result,
            "hash_rate": hr_result,
            "gas_fee": gas_result,
        }
