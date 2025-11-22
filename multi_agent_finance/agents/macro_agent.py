"""
Agente de Análise Macroeconómica - Avalia condições macroeconómicas e seu impacto.
"""
import numpy as np
from typing import Dict, Any
from .base_agent import BaseAgent, AgentInsight


class MacroAgent(BaseAgent):
    """
    Agente especializado em análise macroeconómica.

    Avalia taxas de juro, inflação, PIB, políticas monetárias/fiscais e seu impacto
    nos mercados financeiros.
    """

    def __init__(self, weight: float = 1.0):
        super().__init__(name="Macro Analyst", weight=weight)

    def analyze(self, symbol: str, data: Dict[str, Any]) -> AgentInsight:
        """
        Analisa condições macroeconómicas.

        Args:
            symbol: Símbolo do ativo
            data: Deve conter 'macro_data' com:
                - 'interest_rates': taxas de juro
                - 'inflation': dados de inflação
                - 'gdp_growth': crescimento do PIB
                - 'unemployment': taxa de desemprego
                - 'market_regime': regime de mercado

        Returns:
            AgentInsight com análise macroeconómica
        """
        macro_data = data.get('macro_data', {})

        if not macro_data:
            return self._default_analysis(symbol, data)

        scores = {}

        # Analisa taxas de juro
        if 'interest_rates' in macro_data:
            scores['rates'] = self._analyze_interest_rates(macro_data['interest_rates'])

        # Analisa inflação
        if 'inflation' in macro_data:
            scores['inflation'] = self._analyze_inflation(macro_data['inflation'])

        # Analisa crescimento económico
        if 'gdp_growth' in macro_data:
            scores['gdp'] = self._analyze_gdp(macro_data['gdp_growth'])

        # Analisa emprego
        if 'unemployment' in macro_data:
            scores['employment'] = self._analyze_employment(macro_data['unemployment'])

        # Analisa regime de mercado
        if 'market_regime' in macro_data:
            scores['regime'] = self._analyze_market_regime(macro_data['market_regime'])

        if not scores:
            return self._default_analysis(symbol, data)

        # Score combinado
        final_score = np.mean(list(scores.values()))

        # Confiança
        confidence = min(0.8, 0.4 + (len(scores) * 0.1))

        # Reasoning
        reasoning = self._generate_reasoning(scores, macro_data)

        return AgentInsight(
            agent_name=self.name,
            score=final_score,
            confidence=confidence,
            reasoning=reasoning,
            metadata={'macro_scores': scores, 'macro_data': macro_data}
        )

    def _analyze_interest_rates(self, rates_data: Dict[str, Any]) -> float:
        """
        Analisa taxas de juro e tendência.

        Espera:
        - 'current_rate': taxa atual
        - 'trend': 'rising', 'falling', 'stable'
        - 'next_meeting_expectation': expectativa para próxima reunião
        """
        score = 0

        trend = rates_data.get('trend', '').lower()
        current_rate = rates_data.get('current_rate', 0)

        # Taxas baixas = bom para ações (dinheiro barato)
        # Taxas altas = ruim para ações (dinheiro caro)
        if current_rate < 2:
            score += 40  # Ambiente muito favorável
        elif current_rate < 4:
            score += 20  # Favorável
        elif current_rate < 6:
            score -= 10  # Neutro/desfavorável
        else:
            score -= 40  # Muito desfavorável

        # Tendência
        if trend == 'falling':
            score += 30  # Cortes de taxa = bullish
        elif trend == 'rising':
            score -= 30  # Aumentos = bearish
        elif trend == 'stable':
            score += 10  # Estabilidade = bom

        # Expectativa futura
        expectation = rates_data.get('next_meeting_expectation', '').lower()
        if 'cut' in expectation or 'decrease' in expectation:
            score += 20
        elif 'hike' in expectation or 'increase' in expectation:
            score -= 20

        return np.clip(score, -100, 100)

    def _analyze_inflation(self, inflation_data: Dict[str, Any]) -> float:
        """
        Analisa inflação.

        Espera:
        - 'current_rate': taxa atual (%)
        - 'target_rate': meta do banco central
        - 'trend': 'rising', 'falling', 'stable'
        """
        score = 0

        current = inflation_data.get('current_rate', 2)
        target = inflation_data.get('target_rate', 2)
        trend = inflation_data.get('trend', '').lower()

        # Inflação próxima do alvo = bom
        deviation = abs(current - target)

        if deviation < 0.5:
            score += 40  # Muito próximo do alvo
        elif deviation < 1:
            score += 20  # Razoavelmente próximo
        elif deviation < 2:
            score -= 10  # Afastado
        else:
            score -= 40  # Muito afastado

        # Tendência
        if current > target:
            # Inflação acima do alvo
            if trend == 'falling':
                score += 30  # Melhorando
            elif trend == 'rising':
                score -= 40  # Piorando (Fed pode subir taxas)
        else:
            # Inflação abaixo do alvo
            if trend == 'rising':
                score += 20  # Normalizando
            elif trend == 'falling':
                score -= 20  # Risco deflacionário

        # Inflação muito alta = muito ruim para ações
        if current > 5:
            score -= 30

        return np.clip(score, -100, 100)

    def _analyze_gdp(self, gdp_data: Dict[str, Any]) -> float:
        """
        Analisa crescimento do PIB.

        Espera:
        - 'growth_rate': taxa de crescimento (%)
        - 'trend': tendência
        """
        growth_rate = gdp_data.get('growth_rate', 2)
        trend = gdp_data.get('trend', '').lower()

        score = 0

        # Crescimento saudável = bom para ações
        if growth_rate > 4:
            score += 50  # Crescimento forte
        elif growth_rate > 2:
            score += 30  # Crescimento saudável
        elif growth_rate > 0:
            score += 10  # Crescimento fraco
        elif growth_rate > -1:
            score -= 30  # Estagnação
        else:
            score -= 60  # Recessão

        # Tendência
        if trend == 'accelerating':
            score += 20
        elif trend == 'decelerating':
            score -= 20

        return np.clip(score, -100, 100)

    def _analyze_employment(self, employment_data: Dict[str, Any]) -> float:
        """
        Analisa mercado de trabalho.

        Espera:
        - 'unemployment_rate': taxa de desemprego (%)
        - 'trend': tendência
        """
        unemployment = employment_data.get('unemployment_rate', 5)
        trend = employment_data.get('trend', '').lower()

        score = 0

        # Desemprego baixo = economia saudável
        if unemployment < 4:
            score += 40
        elif unemployment < 5:
            score += 20
        elif unemployment < 7:
            score += 0
        else:
            score -= 40

        # Tendência
        if trend == 'falling':
            score += 20  # Melhorando
        elif trend == 'rising':
            score -= 30  # Piorando

        return np.clip(score, -100, 100)

    def _analyze_market_regime(self, regime_data: Dict[str, Any]) -> float:
        """
        Analisa regime de mercado.

        Espera:
        - 'type': 'risk_on', 'risk_off', 'neutral'
        - 'vix': índice de volatilidade
        - 'yield_curve': 'normal', 'flat', 'inverted'
        """
        regime_type = regime_data.get('type', '').lower()
        vix = regime_data.get('vix')
        yield_curve = regime_data.get('yield_curve', '').lower()

        score = 0

        # Regime de mercado
        if regime_type == 'risk_on':
            score += 50  # Apetite por risco
        elif regime_type == 'risk_off':
            score -= 50  # Aversão ao risco
        elif regime_type == 'neutral':
            score += 0

        # VIX (fear index)
        if vix is not None:
            if vix < 15:
                score += 30  # Baixa volatilidade
            elif vix < 20:
                score += 10  # Volatilidade normal
            elif vix < 30:
                score -= 20  # Volatilidade elevada
            else:
                score -= 40  # Pânico

        # Yield curve (curva de rendimentos)
        if yield_curve == 'normal':
            score += 20  # Saudável
        elif yield_curve == 'flat':
            score -= 10  # Sinal de cautela
        elif yield_curve == 'inverted':
            score -= 50  # Sinal de recessão

        return np.clip(score, -100, 100)

    def _generate_reasoning(self, scores: Dict[str, float], macro_data: Dict[str, Any]) -> str:
        """Gera explicação textual."""
        parts = []

        # Interest rates
        if 'rates' in scores:
            rates = macro_data.get('interest_rates', {})
            current = rates.get('current_rate')
            trend = rates.get('trend', '')
            if current:
                parts.append(f"Taxas de juro em {current:.2f}% ({trend})")

        # Inflation
        if 'inflation' in scores:
            inflation = macro_data.get('inflation', {})
            current = inflation.get('current_rate')
            if current:
                parts.append(f"Inflação em {current:.1f}%")

        # GDP
        if 'gdp' in scores:
            gdp = macro_data.get('gdp_growth', {})
            growth = gdp.get('growth_rate')
            if growth:
                parts.append(f"PIB crescendo {growth:.1f}%")

        # Market regime
        if 'regime' in scores:
            regime = macro_data.get('market_regime', {})
            regime_type = regime.get('type', '').replace('_', '-')
            vix = regime.get('vix')
            if regime_type:
                parts.append(f"Regime {regime_type}")
            if vix:
                parts.append(f"VIX: {vix:.1f}")

        return "; ".join(parts) if parts else "Ambiente macro misto"

    def _default_analysis(self, symbol: str, data: Dict[str, Any]) -> AgentInsight:
        """Análise padrão quando não há dados macro."""
        return AgentInsight(
            agent_name=self.name,
            score=0,
            confidence=0.2,
            reasoning="Dados macroeconómicos não disponíveis para análise detalhada"
        )
