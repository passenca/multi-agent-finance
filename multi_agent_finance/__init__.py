"""
Sistema Multi-Agente de Análise Financeira

Um sistema abrangente que utiliza múltiplos agentes especializados para
análise de investimentos em ações e ETFs.
"""

__version__ = "1.0.0"
__author__ = "Paulo Assenção"

from .agents.base_agent import BaseAgent, AgentInsight
from .agents.technical_agent import TechnicalAgent
from .agents.fundamental_agent import FundamentalAgent
from .agents.sentiment_agent import SentimentAgent
from .agents.macro_agent import MacroAgent
from .agents.risk_agent import RiskAgent
from .agents.sector_agent import SectorAgent
from .orchestrator.orchestrator import AgentOrchestrator
from .utils.data_fetcher import DataFetcher

__all__ = [
    'BaseAgent',
    'AgentInsight',
    'TechnicalAgent',
    'FundamentalAgent',
    'SentimentAgent',
    'MacroAgent',
    'RiskAgent',
    'SectorAgent',
    'AgentOrchestrator',
    'DataFetcher'
]
