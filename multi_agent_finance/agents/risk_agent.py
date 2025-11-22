"""
Agente de Análise de Risco - Avalia perfil de risco e volatilidade.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
from .base_agent import BaseAgent, AgentInsight


class RiskAgent(BaseAgent):
    """
    Agente especializado em análise de risco.

    Avalia volatilidade, Sharpe ratio, drawdowns, Value at Risk (VaR),
    correlações e outros indicadores de risco.
    """

    def __init__(self, weight: float = 1.0):
        super().__init__(name="Risk Analyst", weight=weight)

    def analyze(self, symbol: str, data: Dict[str, Any]) -> AgentInsight:
        """
        Analisa perfil de risco do ativo.

        Args:
            symbol: Símbolo do ativo
            data: Deve conter 'price_history' (DataFrame com OHLCV)

        Returns:
            AgentInsight com análise de risco
        """
        price_data = data.get('price_history')

        if price_data is None or price_data.empty or len(price_data) < 30:
            return AgentInsight(
                agent_name=self.name,
                score=0,
                confidence=0,
                reasoning="Dados insuficientes para análise de risco"
            )

        # Calcula métricas de risco
        risk_metrics = self._calculate_risk_metrics(price_data)

        # Avalia cada métrica
        scores = {
            'volatility': self._evaluate_volatility(risk_metrics.get('volatility')),
            'sharpe': self._evaluate_sharpe(risk_metrics.get('sharpe_ratio')),
            'max_drawdown': self._evaluate_drawdown(risk_metrics.get('max_drawdown')),
            'var': self._evaluate_var(risk_metrics.get('var_95')),
            'beta': self._evaluate_beta(risk_metrics.get('beta'))
        }

        # Remove scores None
        valid_scores = {k: v for k, v in scores.items() if v is not None}

        if not valid_scores:
            return AgentInsight(
                agent_name=self.name,
                score=0,
                confidence=0.2,
                reasoning="Métricas de risco insuficientes"
            )

        # Score final (negativo = muito arriscado, positivo = risco aceitável)
        final_score = np.mean(list(valid_scores.values()))

        # Confiança
        confidence = min(0.85, 0.5 + (len(valid_scores) * 0.08))

        # Reasoning
        reasoning = self._generate_reasoning(valid_scores, risk_metrics)

        return AgentInsight(
            agent_name=self.name,
            score=final_score,
            confidence=confidence,
            reasoning=reasoning,
            metadata={'risk_metrics': risk_metrics, 'scores': valid_scores}
        )

    def _calculate_risk_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calcula métricas de risco."""
        metrics = {}

        try:
            # Retornos diários
            returns = df['Close'].pct_change().dropna()

            # Volatilidade anualizada
            volatility = returns.std() * np.sqrt(252)
            metrics['volatility'] = volatility

            # Retorno anualizado
            total_return = (df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1
            years = len(df) / 252
            annual_return = (1 + total_return) ** (1 / years) - 1
            metrics['annual_return'] = annual_return

            # Sharpe Ratio (assumindo risk-free rate de 2%)
            risk_free_rate = 0.02
            excess_return = annual_return - risk_free_rate
            sharpe_ratio = excess_return / volatility if volatility > 0 else 0
            metrics['sharpe_ratio'] = sharpe_ratio

            # Sortino Ratio (só considera downside volatility)
            downside_returns = returns[returns < 0]
            downside_std = downside_returns.std() * np.sqrt(252)
            sortino_ratio = excess_return / downside_std if downside_std > 0 else 0
            metrics['sortino_ratio'] = sortino_ratio

            # Maximum Drawdown
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min()
            metrics['max_drawdown'] = max_drawdown

            # Value at Risk (95% confidence)
            var_95 = returns.quantile(0.05)
            metrics['var_95'] = var_95

            # Conditional VaR (CVaR or Expected Shortfall)
            cvar_95 = returns[returns <= var_95].mean()
            metrics['cvar_95'] = cvar_95

            # Beta (vs market - se disponível)
            market_data = df.get('Market_Return')  # Seria necessário passar retornos do mercado
            if market_data is not None:
                market_returns = market_data.pct_change().dropna()
                # Alinha os índices
                aligned_returns = returns.align(market_returns, join='inner')
                if len(aligned_returns[0]) > 0:
                    covariance = aligned_returns[0].cov(aligned_returns[1])
                    market_variance = aligned_returns[1].var()
                    beta = covariance / market_variance if market_variance > 0 else 1
                    metrics['beta'] = beta
            else:
                metrics['beta'] = None

            # Downside deviation
            metrics['downside_deviation'] = downside_std

            # Ulcer Index (measure of downside volatility)
            squared_drawdown = drawdown ** 2
            ulcer_index = np.sqrt(squared_drawdown.mean())
            metrics['ulcer_index'] = ulcer_index

        except Exception as e:
            print(f"Erro ao calcular métricas de risco: {e}")

        return metrics

    def _evaluate_volatility(self, volatility: float) -> float:
        """
        Avalia volatilidade. Menor volatilidade = melhor score.
        Retorna score de -100 a 100.
        """
        if volatility is None:
            return None

        # Volatilidade anualizada típica de ações: 15-25%
        if volatility < 0.15:
            return 60  # Baixa volatilidade
        elif volatility < 0.25:
            return 30  # Volatilidade normal
        elif volatility < 0.35:
            return 0   # Volatilidade elevada
        elif volatility < 0.50:
            return -40  # Muito volátil
        else:
            return -70  # Extremamente volátil

    def _evaluate_sharpe(self, sharpe_ratio: float) -> float:
        """
        Avalia Sharpe Ratio. Maior = melhor retorno ajustado ao risco.
        Retorna score de -100 a 100.
        """
        if sharpe_ratio is None:
            return None

        # Sharpe > 1 é considerado bom, > 2 é excelente
        if sharpe_ratio > 2:
            return 80
        elif sharpe_ratio > 1:
            return 50
        elif sharpe_ratio > 0.5:
            return 20
        elif sharpe_ratio > 0:
            return -10
        else:
            return -60  # Sharpe negativo = retorno pior que risk-free

    def _evaluate_drawdown(self, max_drawdown: float) -> float:
        """
        Avalia Maximum Drawdown. Menor drawdown = melhor.
        Retorna score de -100 a 100.
        """
        if max_drawdown is None:
            return None

        # max_drawdown é negativo (ex: -0.3 = 30% de queda)
        drawdown_pct = abs(max_drawdown) * 100

        if drawdown_pct < 10:
            return 70  # Drawdown pequeno
        elif drawdown_pct < 20:
            return 40  # Aceitável
        elif drawdown_pct < 30:
            return 10  # Moderado
        elif drawdown_pct < 50:
            return -30  # Alto
        else:
            return -70  # Muito alto

    def _evaluate_var(self, var_95: float) -> float:
        """
        Avalia Value at Risk (95%). Menor VaR = menor risco de perdas extremas.
        Retorna score de -100 a 100.
        """
        if var_95 is None:
            return None

        # VaR é negativo (ex: -0.03 = risco de perder 3% num dia ruim)
        var_pct = abs(var_95) * 100

        if var_pct < 2:
            return 60  # Baixo risco de perdas diárias
        elif var_pct < 3:
            return 30
        elif var_pct < 5:
            return 0
        elif var_pct < 7:
            return -30
        else:
            return -60  # Alto risco de perdas diárias

    def _evaluate_beta(self, beta: float) -> float:
        """
        Avalia Beta (sensibilidade ao mercado).
        Beta < 1 = menos volátil que mercado
        Beta > 1 = mais volátil que mercado
        Retorna score de -100 a 100.
        """
        if beta is None:
            return None

        # Beta baixo é "mais seguro" mas pode significar menor upside
        if beta < 0:
            return -50  # Correlação negativa com mercado (raro)
        elif beta < 0.7:
            return 40  # Defensivo
        elif beta < 1.2:
            return 20  # Próximo do mercado
        elif beta < 1.5:
            return -10  # Mais volátil que mercado
        else:
            return -40  # Muito mais volátil

    def _generate_reasoning(self, scores: Dict[str, float], metrics: Dict[str, float]) -> str:
        """Gera explicação textual."""
        parts = []

        # Volatility
        vol = metrics.get('volatility')
        if vol:
            parts.append(f"Volatilidade anual: {vol*100:.1f}%")

        # Sharpe
        sharpe = metrics.get('sharpe_ratio')
        if sharpe:
            quality = "excelente" if sharpe > 2 else "bom" if sharpe > 1 else "fraco"
            parts.append(f"Sharpe ratio: {sharpe:.2f} ({quality} retorno/risco)")

        # Drawdown
        dd = metrics.get('max_drawdown')
        if dd:
            parts.append(f"Max drawdown: {abs(dd)*100:.1f}%")

        # VaR
        var = metrics.get('var_95')
        if var:
            parts.append(f"VaR (95%): {abs(var)*100:.1f}% perda potencial num dia ruim")

        # Beta
        beta = metrics.get('beta')
        if beta:
            volatility_desc = "defensivo" if beta < 0.8 else "agressivo" if beta > 1.2 else "alinhado com mercado"
            parts.append(f"Beta: {beta:.2f} ({volatility_desc})")

        # Overall assessment
        avg_score = np.mean(list(scores.values()))
        if avg_score > 30:
            risk_level = "Perfil de risco favorável"
        elif avg_score > 0:
            risk_level = "Risco moderado"
        elif avg_score > -30:
            risk_level = "Risco elevado"
        else:
            risk_level = "Risco muito elevado"

        parts.insert(0, risk_level)

        return "; ".join(parts)
