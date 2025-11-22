"""
Agente de Análise Fundamental - Avalia métricas financeiras e saúde da empresa.
"""
import numpy as np
from typing import Dict, Any
from .base_agent import BaseAgent, AgentInsight


class FundamentalAgent(BaseAgent):
    """
    Agente especializado em análise fundamental.

    Avalia P/E, P/B, ROE, margens, crescimento, dividend yield, etc.
    """

    def __init__(self, weight: float = 1.0):
        super().__init__(name="Fundamental Analyst", weight=weight)

    def analyze(self, symbol: str, data: Dict[str, Any]) -> AgentInsight:
        """
        Analisa métricas fundamentais do ativo.

        Args:
            symbol: Símbolo do ativo
            data: Deve conter 'fundamentals' (dict com métricas)

        Returns:
            AgentInsight com análise fundamental
        """
        fundamentals = data.get('fundamentals', {})

        if not fundamentals:
            return AgentInsight(
                agent_name=self.name,
                score=0,
                confidence=0,
                reasoning="Dados fundamentais insuficientes para análise."
            )

        # Avalia cada categoria
        scores = {
            'valuation': self._evaluate_valuation(fundamentals),
            'profitability': self._evaluate_profitability(fundamentals),
            'growth': self._evaluate_growth(fundamentals),
            'financial_health': self._evaluate_financial_health(fundamentals),
            'dividends': self._evaluate_dividends(fundamentals)
        }

        # Remove scores None
        valid_scores = {k: v for k, v in scores.items() if v is not None}

        if not valid_scores:
            return AgentInsight(
                agent_name=self.name,
                score=0,
                confidence=0.2,
                reasoning="Métricas fundamentais insuficientes."
            )

        # Score final
        final_score = np.mean(list(valid_scores.values()))

        # Confiança baseada em quantas métricas temos
        confidence = min(0.9, 0.3 + (len(valid_scores) * 0.15))

        # Reasoning
        reasoning = self._generate_reasoning(valid_scores, fundamentals)

        return AgentInsight(
            agent_name=self.name,
            score=final_score,
            confidence=confidence,
            reasoning=reasoning,
            metadata={'fundamentals': fundamentals, 'scores': valid_scores}
        )

    def _evaluate_valuation(self, data: Dict[str, Any]) -> float:
        """
        Avalia valuation (P/E, P/B, PEG).
        Retorna score de -100 a 100.
        """
        score = 0
        count = 0

        # P/E Ratio
        pe = data.get('trailingPE') or data.get('forwardPE')
        if pe and pe > 0:
            if pe < 15:
                score += 60  # Muito barato
            elif pe < 25:
                score += 20  # Razoável
            elif pe < 35:
                score -= 20  # Caro
            else:
                score -= 60  # Muito caro
            count += 1

        # P/B Ratio
        pb = data.get('priceToBook')
        if pb and pb > 0:
            if pb < 1:
                score += 50  # Barato
            elif pb < 3:
                score += 10  # Razoável
            elif pb < 5:
                score -= 20  # Caro
            else:
                score -= 50  # Muito caro
            count += 1

        # PEG Ratio (P/E to Growth)
        peg = data.get('pegRatio')
        if peg and peg > 0:
            if peg < 1:
                score += 50  # Crescimento barato
            elif peg < 2:
                score += 20  # Razoável
            else:
                score -= 30  # Caro para o crescimento
            count += 1

        return score / count if count > 0 else None

    def _evaluate_profitability(self, data: Dict[str, Any]) -> float:
        """
        Avalia rentabilidade (ROE, ROA, margens).
        Retorna score de -100 a 100.
        """
        score = 0
        count = 0

        # ROE (Return on Equity)
        roe = data.get('returnOnEquity')
        if roe:
            roe_pct = roe * 100
            if roe_pct > 20:
                score += 60
            elif roe_pct > 15:
                score += 30
            elif roe_pct > 10:
                score += 10
            else:
                score -= 20
            count += 1

        # ROA (Return on Assets)
        roa = data.get('returnOnAssets')
        if roa:
            roa_pct = roa * 100
            if roa_pct > 10:
                score += 40
            elif roa_pct > 5:
                score += 20
            else:
                score -= 10
            count += 1

        # Profit Margin
        profit_margin = data.get('profitMargins')
        if profit_margin:
            margin_pct = profit_margin * 100
            if margin_pct > 20:
                score += 50
            elif margin_pct > 10:
                score += 25
            elif margin_pct > 5:
                score += 10
            else:
                score -= 20
            count += 1

        # Operating Margin
        op_margin = data.get('operatingMargins')
        if op_margin:
            op_pct = op_margin * 100
            if op_pct > 15:
                score += 40
            elif op_pct > 10:
                score += 20
            else:
                score -= 10
            count += 1

        return score / count if count > 0 else None

    def _evaluate_growth(self, data: Dict[str, Any]) -> float:
        """
        Avalia crescimento (receita, lucros).
        Retorna score de -100 a 100.
        """
        score = 0
        count = 0

        # Revenue Growth
        revenue_growth = data.get('revenueGrowth')
        if revenue_growth:
            growth_pct = revenue_growth * 100
            if growth_pct > 20:
                score += 70
            elif growth_pct > 10:
                score += 40
            elif growth_pct > 5:
                score += 20
            elif growth_pct > 0:
                score += 5
            else:
                score -= 50
            count += 1

        # Earnings Growth
        earnings_growth = data.get('earningsGrowth')
        if earnings_growth:
            eg_pct = earnings_growth * 100
            if eg_pct > 25:
                score += 70
            elif eg_pct > 15:
                score += 40
            elif eg_pct > 5:
                score += 20
            else:
                score -= 30
            count += 1

        # Quarterly Revenue Growth
        quarterly_growth = data.get('quarterlyRevenueGrowth')
        if quarterly_growth:
            qg_pct = quarterly_growth * 100
            if qg_pct > 15:
                score += 50
            elif qg_pct > 5:
                score += 25
            else:
                score -= 20
            count += 1

        return score / count if count > 0 else None

    def _evaluate_financial_health(self, data: Dict[str, Any]) -> float:
        """
        Avalia saúde financeira (dívida, liquidez).
        Retorna score de -100 a 100.
        """
        score = 0
        count = 0

        # Debt to Equity
        debt_to_equity = data.get('debtToEquity')
        if debt_to_equity is not None:
            if debt_to_equity < 0.3:
                score += 60  # Baixa dívida
            elif debt_to_equity < 0.7:
                score += 30  # Dívida moderada
            elif debt_to_equity < 1.5:
                score += 0   # Dívida razoável
            else:
                score -= 50  # Alta dívida
            count += 1

        # Current Ratio (liquidez)
        current_ratio = data.get('currentRatio')
        if current_ratio:
            if current_ratio > 2:
                score += 50  # Excelente liquidez
            elif current_ratio > 1.5:
                score += 30  # Boa liquidez
            elif current_ratio > 1:
                score += 10  # Liquidez adequada
            else:
                score -= 40  # Liquidez preocupante
            count += 1

        # Quick Ratio
        quick_ratio = data.get('quickRatio')
        if quick_ratio:
            if quick_ratio > 1.5:
                score += 40
            elif quick_ratio > 1:
                score += 20
            else:
                score -= 20
            count += 1

        return score / count if count > 0 else None

    def _evaluate_dividends(self, data: Dict[str, Any]) -> float:
        """
        Avalia política de dividendos.
        Retorna score de -100 a 100.
        """
        dividend_yield = data.get('dividendYield')
        payout_ratio = data.get('payoutRatio')

        if not dividend_yield:
            return 0  # Neutro se não paga dividendos

        score = 0

        # Dividend Yield
        yield_pct = dividend_yield * 100
        if yield_pct > 4:
            score += 50
        elif yield_pct > 2:
            score += 30
        elif yield_pct > 1:
            score += 15
        else:
            score += 5

        # Payout Ratio (sustentabilidade)
        if payout_ratio:
            if 0.3 < payout_ratio < 0.6:
                score += 30  # Sustentável
            elif payout_ratio < 0.3:
                score += 10  # Conservador
            elif payout_ratio < 0.8:
                score += 0   # Limite
            else:
                score -= 30  # Insustentável

        return np.clip(score, -100, 100)

    def _generate_reasoning(self, scores: Dict[str, float], fundamentals: Dict[str, Any]) -> str:
        """Gera explicação textual da análise."""
        parts = []

        # Valuation
        if 'valuation' in scores:
            pe = fundamentals.get('trailingPE')
            if pe and scores['valuation'] > 30:
                parts.append(f"Valuation atrativo (P/E: {pe:.1f})")
            elif pe and scores['valuation'] < -30:
                parts.append(f"Valuation elevado (P/E: {pe:.1f})")

        # Profitability
        if 'profitability' in scores:
            roe = fundamentals.get('returnOnEquity')
            if roe and scores['profitability'] > 20:
                parts.append(f"Alta rentabilidade (ROE: {roe*100:.1f}%)")

        # Growth
        if 'growth' in scores:
            rev_growth = fundamentals.get('revenueGrowth')
            if rev_growth and scores['growth'] > 30:
                parts.append(f"Forte crescimento de receita ({rev_growth*100:.1f}%)")
            elif rev_growth and scores['growth'] < -20:
                parts.append(f"Crescimento fraco ou negativo")

        # Financial Health
        if 'financial_health' in scores:
            if scores['financial_health'] > 30:
                parts.append("Balanço saudável")
            elif scores['financial_health'] < -20:
                parts.append("Preocupações com endividamento")

        # Dividends
        if 'dividends' in scores and scores['dividends'] > 20:
            div_yield = fundamentals.get('dividendYield')
            if div_yield:
                parts.append(f"Bom dividend yield ({div_yield*100:.2f}%)")

        return "; ".join(parts) if parts else "Análise fundamental mista"
