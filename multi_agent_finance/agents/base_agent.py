"""
Classe base abstrata para todos os agentes de análise financeira.

Cada agente especializado herda desta classe e implementa sua própria lógica de análise.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class AgentInsight:
    """Representa o insight/recomendação de um agente."""

    def __init__(
        self,
        agent_name: str,
        score: float,  # -100 a +100 (negativo = bearish, positivo = bullish)
        confidence: float,  # 0 a 1
        reasoning: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.agent_name = agent_name
        self.score = max(-100, min(100, score))  # Clamp entre -100 e 100
        self.confidence = max(0, min(1, confidence))  # Clamp entre 0 e 1
        self.reasoning = reasoning
        self.metadata = metadata or {}
        self.timestamp = datetime.now()

    def __repr__(self):
        return (f"AgentInsight(agent={self.agent_name}, "
                f"score={self.score:.2f}, confidence={self.confidence:.2f})")

    def to_dict(self) -> Dict[str, Any]:
        """Converte o insight para dicionário."""
        return {
            'agent_name': self.agent_name,
            'score': self.score,
            'confidence': self.confidence,
            'reasoning': self.reasoning,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }


class BaseAgent(ABC):
    """Classe base abstrata para agentes de análise financeira."""

    def __init__(self, name: str, weight: float = 1.0):
        """
        Inicializa o agente.

        Args:
            name: Nome do agente
            weight: Peso relativo deste agente na análise final (0-1)
        """
        self.name = name
        self.weight = max(0, min(1, weight))
        self.enabled = True

    @abstractmethod
    def analyze(self, symbol: str, data: Dict[str, Any]) -> AgentInsight:
        """
        Analisa um ativo e retorna um insight.

        Args:
            symbol: Símbolo do ativo (ex: "AAPL", "MSFT")
            data: Dados do ativo (preços históricos, fundamentals, etc.)

        Returns:
            AgentInsight com a análise do agente
        """
        pass

    def set_weight(self, weight: float):
        """Ajusta o peso do agente."""
        self.weight = max(0, min(1, weight))

    def enable(self):
        """Ativa o agente."""
        self.enabled = True

    def disable(self):
        """Desativa o agente."""
        self.enabled = False

    def __repr__(self):
        status = "enabled" if self.enabled else "disabled"
        return f"{self.__class__.__name__}(name={self.name}, weight={self.weight:.2f}, {status})"
