"""
Orquestrador que coordena múltiplos agentes e combina seus insights.
"""
from typing import List, Dict, Any
from agents.base_agent import BaseAgent, AgentInsight


class AgentOrchestrator:
    """Coordena múltiplos agentes de análise e combina seus insights."""

    def __init__(self, agents: List[BaseAgent] = None):
        """
        Inicializa o orquestrador.

        Args:
            agents: Lista de agentes a coordenar
        """
        self.agents: List[BaseAgent] = agents or []

    def add_agent(self, agent: BaseAgent):
        """Adiciona um agente ao orquestrador."""
        self.agents.append(agent)

    def remove_agent(self, agent_name: str):
        """Remove um agente pelo nome."""
        self.agents = [a for a in self.agents if a.name != agent_name]

    def analyze(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa análise de todos os agentes e combina os resultados.

        Args:
            symbol: Símbolo do ativo
            data: Dados do ativo

        Returns:
            Dicionário com análise combinada e insights individuais
        """
        insights: List[AgentInsight] = []

        # Coleta insights de todos os agentes ativos
        for agent in self.agents:
            if agent.enabled:
                try:
                    insight = agent.analyze(symbol, data)
                    insights.append(insight)
                except Exception as e:
                    print(f"Erro no agente {agent.name}: {str(e)}")

        # Combina os insights
        combined_analysis = self._combine_insights(insights)

        return {
            'symbol': symbol,
            'individual_insights': [i.to_dict() for i in insights],
            'combined_score': combined_analysis['score'],
            'combined_confidence': combined_analysis['confidence'],
            'recommendation': combined_analysis['recommendation'],
            'reasoning': combined_analysis['reasoning'],
            'total_agents': len(insights)
        }

    def _combine_insights(self, insights: List[AgentInsight]) -> Dict[str, Any]:
        """
        Combina múltiplos insights num score final ponderado.

        Args:
            insights: Lista de insights dos agentes

        Returns:
            Dicionário com score combinado e recomendação
        """
        if not insights:
            return {
                'score': 0,
                'confidence': 0,
                'recommendation': 'INSUFFICIENT DATA',
                'reasoning': 'Nenhum agente forneceu insights.'
            }

        # Calcula score ponderado (peso do agente * confiança * score)
        total_weighted_score = 0
        total_weight = 0

        for insight in insights:
            # Busca o agente correspondente para obter o peso
            agent = next((a for a in self.agents if a.name == insight.agent_name), None)
            if agent:
                weight = agent.weight * insight.confidence
                total_weighted_score += insight.score * weight
                total_weight += weight

        # Score final
        final_score = total_weighted_score / total_weight if total_weight > 0 else 0

        # Confiança média ponderada
        total_confidence = sum(i.confidence for i in insights) / len(insights)

        # Gera recomendação baseada no score
        recommendation = self._get_recommendation(final_score, total_confidence)

        # Gera reasoning agregado
        reasoning = self._generate_reasoning(insights, final_score)

        return {
            'score': final_score,
            'confidence': total_confidence,
            'recommendation': recommendation,
            'reasoning': reasoning
        }

    def _get_recommendation(self, score: float, confidence: float) -> str:
        """
        Converte score numérico em recomendação textual.

        Args:
            score: Score de -100 a +100
            confidence: Confiança de 0 a 1

        Returns:
            Recomendação textual
        """
        # Ajusta thresholds baseado na confiança
        if confidence < 0.3:
            return "INSUFFICIENT CONFIDENCE"

        if score >= 60:
            return "COMPRA FORTE"
        elif score >= 30:
            return "COMPRA"
        elif score >= -30:
            return "MANTER"
        elif score >= -60:
            return "VENDA"
        else:
            return "VENDA FORTE"

    def _generate_reasoning(self, insights: List[AgentInsight], final_score: float) -> str:
        """Gera texto de raciocínio agregado."""
        reasoning_parts = []

        # Score geral
        reasoning_parts.append(f"Score combinado: {final_score:.2f}/100")

        # Consenso ou divergência
        scores = [i.score for i in insights]
        if all(s > 30 for s in scores):
            reasoning_parts.append("Consenso BULLISH entre agentes.")
        elif all(s < -30 for s in scores):
            reasoning_parts.append("Consenso BEARISH entre agentes.")
        else:
            reasoning_parts.append("Opiniões divergentes entre agentes.")

        # Top insights
        reasoning_parts.append("\nPrincipais insights:")
        for insight in sorted(insights, key=lambda x: abs(x.score), reverse=True)[:3]:
            reasoning_parts.append(f"- {insight.agent_name}: {insight.reasoning}")

        return "\n".join(reasoning_parts)

    def get_agent_summary(self) -> List[Dict[str, Any]]:
        """Retorna sumário de todos os agentes registrados."""
        return [
            {
                'name': agent.name,
                'type': agent.__class__.__name__,
                'weight': agent.weight,
                'enabled': agent.enabled
            }
            for agent in self.agents
        ]
