"""
Agente de Análise Setorial - Compara empresa com peers do mesmo setor.
"""
import numpy as np
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentInsight


class SectorAgent(BaseAgent):
    """
    Agente especializado em análise setorial.

    Compara a empresa com seus pares do mesmo setor, avaliando
    posicionamento competitivo, market share, e performance relativa.
    """

    def __init__(self, weight: float = 1.0):
        super().__init__(name="Sector Analyst", weight=weight)

    def analyze(self, symbol: str, data: Dict[str, Any]) -> AgentInsight:
        """
        Analisa posicionamento setorial do ativo.

        Args:
            symbol: Símbolo do ativo
            data: Deve conter 'sector_data' com:
                - 'sector': nome do setor
                - 'industry': indústria específica
                - 'peers': lista de empresas comparáveis
                - 'company_metrics': métricas da empresa
                - 'sector_averages': médias do setor

        Returns:
            AgentInsight com análise setorial
        """
        sector_data = data.get('sector_data', {})
        fundamentals = data.get('fundamentals', {})

        if not sector_data and not fundamentals:
            return AgentInsight(
                agent_name=self.name,
                score=0,
                confidence=0.1,
                reasoning="Dados setoriais não disponíveis"
            )

        scores = {}

        # Compara métricas fundamentais com setor
        if 'sector_averages' in sector_data:
            scores['fundamental_comparison'] = self._compare_fundamentals(
                fundamentals,
                sector_data['sector_averages']
            )

        # Avalia posição de mercado
        if 'market_position' in sector_data:
            scores['market_position'] = self._evaluate_market_position(
                sector_data['market_position']
            )

        # Compara performance com peers
        if 'peer_performance' in sector_data:
            scores['peer_performance'] = self._compare_peer_performance(
                sector_data['peer_performance']
            )

        # Avalia tendências do setor
        if 'sector_trends' in sector_data:
            scores['sector_trends'] = self._evaluate_sector_trends(
                sector_data['sector_trends']
            )

        # Se não conseguiu calcular nenhum score, retorna análise básica
        if not scores:
            return self._basic_sector_analysis(symbol, fundamentals)

        # Score combinado
        final_score = np.mean(list(scores.values()))

        # Confiança
        confidence = min(0.85, 0.4 + (len(scores) * 0.12))

        # Reasoning
        reasoning = self._generate_reasoning(scores, sector_data, fundamentals)

        return AgentInsight(
            agent_name=self.name,
            score=final_score,
            confidence=confidence,
            reasoning=reasoning,
            metadata={'sector_scores': scores, 'sector': sector_data.get('sector')}
        )

    def _compare_fundamentals(self, company: Dict[str, Any], sector_avg: Dict[str, Any]) -> float:
        """
        Compara métricas fundamentais da empresa com médias do setor.
        Retorna score de -100 a 100.
        """
        score = 0
        count = 0

        comparisons = [
            ('trailingPE', 'lower_is_better'),  # P/E menor = melhor valuation
            ('priceToBook', 'lower_is_better'),  # P/B menor = melhor valuation
            ('returnOnEquity', 'higher_is_better'),  # ROE maior = melhor
            ('profitMargins', 'higher_is_better'),  # Margem maior = melhor
            ('revenueGrowth', 'higher_is_better'),  # Crescimento maior = melhor
            ('debtToEquity', 'lower_is_better'),  # Dívida menor = melhor
        ]

        for metric, direction in comparisons:
            company_val = company.get(metric)
            sector_val = sector_avg.get(metric)

            if company_val is not None and sector_val is not None and sector_val != 0:
                ratio = company_val / sector_val

                if direction == 'higher_is_better':
                    # Quanto maior que a média, melhor
                    if ratio > 1.3:
                        score += 60  # Muito acima da média
                    elif ratio > 1.1:
                        score += 30  # Acima da média
                    elif ratio > 0.9:
                        score += 0   # Na média
                    else:
                        score -= 40  # Abaixo da média
                else:  # lower_is_better
                    # Quanto menor que a média, melhor
                    if ratio < 0.7:
                        score += 60  # Muito abaixo (bom)
                    elif ratio < 0.9:
                        score += 30  # Abaixo (bom)
                    elif ratio < 1.1:
                        score += 0   # Na média
                    else:
                        score -= 40  # Acima (ruim)

                count += 1

        return score / count if count > 0 else 0

    def _evaluate_market_position(self, position_data: Dict[str, Any]) -> float:
        """
        Avalia posição de mercado da empresa.

        Espera:
        - 'market_share': % de market share
        - 'rank': ranking no setor (1 = líder)
        - 'competitive_advantage': 'strong', 'moderate', 'weak'
        """
        score = 0

        # Market share
        market_share = position_data.get('market_share')
        if market_share:
            if market_share > 20:
                score += 60  # Líder dominante
            elif market_share > 10:
                score += 40  # Líder forte
            elif market_share > 5:
                score += 20  # Player relevante
            else:
                score += 0   # Player pequeno

        # Rank no setor
        rank = position_data.get('rank')
        if rank:
            if rank == 1:
                score += 50  # Líder
            elif rank <= 3:
                score += 30  # Top 3
            elif rank <= 10:
                score += 10  # Top 10
            else:
                score -= 10  # Fora do top

        # Vantagem competitiva
        advantage = position_data.get('competitive_advantage', '').lower()
        if advantage == 'strong':
            score += 40
        elif advantage == 'moderate':
            score += 15
        elif advantage == 'weak':
            score -= 20

        return np.clip(score, -100, 100)

    def _compare_peer_performance(self, peer_data: Dict[str, Any]) -> float:
        """
        Compara performance com peers.

        Espera:
        - 'ytd_performance': performance YTD da empresa
        - 'peer_avg_ytd': performance média dos peers
        - 'percentile': percentil de performance (0-100)
        """
        score = 0

        # Performance relativa
        company_perf = peer_data.get('ytd_performance')
        peer_avg = peer_data.get('peer_avg_ytd')

        if company_perf is not None and peer_avg is not None:
            outperformance = company_perf - peer_avg

            if outperformance > 10:
                score += 60  # Muito acima dos peers
            elif outperformance > 5:
                score += 35  # Acima dos peers
            elif outperformance > -5:
                score += 10  # Em linha
            elif outperformance > -10:
                score -= 30  # Abaixo dos peers
            else:
                score -= 60  # Muito abaixo

        # Percentil
        percentile = peer_data.get('percentile')
        if percentile is not None:
            if percentile > 80:
                score += 50  # Top 20%
            elif percentile > 60:
                score += 25  # Top 40%
            elif percentile > 40:
                score += 0   # Mediano
            else:
                score -= 30  # Bottom 40%

        return np.clip(score, -100, 100)

    def _evaluate_sector_trends(self, trends_data: Dict[str, Any]) -> float:
        """
        Avalia tendências do setor.

        Espera:
        - 'sector_momentum': 'strong', 'moderate', 'weak', 'negative'
        - 'outlook': 'bullish', 'neutral', 'bearish'
        - 'regulatory_environment': 'favorable', 'neutral', 'unfavorable'
        """
        score = 0

        # Momentum do setor
        momentum = trends_data.get('sector_momentum', '').lower()
        momentum_scores = {
            'strong': 50,
            'moderate': 20,
            'weak': -10,
            'negative': -50
        }
        score += momentum_scores.get(momentum, 0)

        # Outlook
        outlook = trends_data.get('outlook', '').lower()
        outlook_scores = {
            'bullish': 40,
            'positive': 40,
            'neutral': 0,
            'bearish': -40,
            'negative': -40
        }
        score += outlook_scores.get(outlook, 0)

        # Ambiente regulatório
        regulatory = trends_data.get('regulatory_environment', '').lower()
        regulatory_scores = {
            'favorable': 30,
            'supportive': 30,
            'neutral': 0,
            'unfavorable': -30,
            'hostile': -50
        }
        score += regulatory_scores.get(regulatory, 0)

        return np.clip(score, -100, 100)

    def _generate_reasoning(self, scores: Dict[str, float], sector_data: Dict[str, Any],
                          fundamentals: Dict[str, Any]) -> str:
        """Gera explicação textual."""
        parts = []

        # Setor
        sector = sector_data.get('sector')
        industry = sector_data.get('industry')
        if sector:
            parts.append(f"Setor: {sector}")
        if industry:
            parts.append(f"Indústria: {industry}")

        # Comparação fundamental
        if 'fundamental_comparison' in scores:
            if scores['fundamental_comparison'] > 30:
                parts.append("Métricas acima da média do setor")
            elif scores['fundamental_comparison'] < -30:
                parts.append("Métricas abaixo da média do setor")

        # Market position
        if 'market_position' in scores:
            position = sector_data.get('market_position', {})
            rank = position.get('rank')
            if rank and scores['market_position'] > 30:
                parts.append(f"Bem posicionada no setor (rank #{rank})")

        # Peer performance
        if 'peer_performance' in scores:
            peer_data = sector_data.get('peer_performance', {})
            percentile = peer_data.get('percentile')
            if percentile:
                parts.append(f"Performance no percentil {percentile:.0f} vs peers")

        # Sector trends
        if 'sector_trends' in scores:
            trends = sector_data.get('sector_trends', {})
            outlook = trends.get('outlook', '').capitalize()
            if outlook:
                parts.append(f"Outlook do setor: {outlook}")

        return "; ".join(parts) if parts else "Análise setorial limitada"

    def _basic_sector_analysis(self, symbol: str, fundamentals: Dict[str, Any]) -> AgentInsight:
        """Análise setorial básica quando dados completos não estão disponíveis."""
        sector = fundamentals.get('sector', 'Unknown')
        industry = fundamentals.get('industry', 'Unknown')

        reasoning = f"Setor: {sector}, Indústria: {industry}"

        # Analisa alguns setores conhecidos
        favorable_sectors = ['Technology', 'Healthcare', 'Consumer Discretionary']
        unfavorable_sectors = ['Energy', 'Utilities']

        score = 0
        if sector in favorable_sectors:
            score = 20
            reasoning += " (setor com outlook positivo)"
        elif sector in unfavorable_sectors:
            score = -20
            reasoning += " (setor com desafios)"

        return AgentInsight(
            agent_name=self.name,
            score=score,
            confidence=0.3,
            reasoning=reasoning
        )
