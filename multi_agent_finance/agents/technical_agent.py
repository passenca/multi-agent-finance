"""
Agente de Análise Técnica - Avalia indicadores técnicos e padrões de preço.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
from .base_agent import BaseAgent, AgentInsight


class TechnicalAgent(BaseAgent):
    """
    Agente especializado em análise técnica.

    Avalia indicadores como RSI, MACD, médias móveis, Bollinger Bands, etc.
    """

    def __init__(self, weight: float = 1.0):
        super().__init__(name="Technical Analyst", weight=weight)

    def analyze(self, symbol: str, data: Dict[str, Any]) -> AgentInsight:
        """
        Analisa indicadores técnicos do ativo.

        Args:
            symbol: Símbolo do ativo
            data: Deve conter 'price_history' (DataFrame com OHLCV)

        Returns:
            AgentInsight com análise técnica
        """
        price_data = data.get('price_history')
        if price_data is None or price_data.empty:
            return AgentInsight(
                agent_name=self.name,
                score=0,
                confidence=0,
                reasoning="Dados de preço insuficientes para análise técnica."
            )

        # Calcula indicadores
        indicators = self._calculate_indicators(price_data)

        # Avalia cada indicador
        scores = {
            'rsi': self._evaluate_rsi(indicators.get('rsi')),
            'macd': self._evaluate_macd(indicators.get('macd'), indicators.get('signal')),
            'moving_averages': self._evaluate_moving_averages(
                indicators.get('sma_50'),
                indicators.get('sma_200'),
                price_data['Close'].iloc[-1]
            ),
            'bollinger': self._evaluate_bollinger(
                price_data['Close'].iloc[-1],
                indicators.get('bb_upper'),
                indicators.get('bb_lower'),
                indicators.get('bb_middle')
            ),
            'volume': self._evaluate_volume(price_data)
        }

        # Combina scores
        final_score = np.mean(list(scores.values()))

        # Calcula confiança baseada em consenso entre indicadores
        confidence = self._calculate_confidence(scores)

        # Gera reasoning
        reasoning = self._generate_reasoning(scores, indicators)

        return AgentInsight(
            agent_name=self.name,
            score=final_score,
            confidence=confidence,
            reasoning=reasoning,
            metadata={'indicators': indicators, 'individual_scores': scores}
        )

    def _calculate_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calcula indicadores técnicos."""
        indicators = {}

        try:
            # RSI (14 períodos)
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators['rsi'] = (100 - (100 / (1 + rs))).iloc[-1]

            # MACD
            exp1 = df['Close'].ewm(span=12, adjust=False).mean()
            exp2 = df['Close'].ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            indicators['macd'] = macd.iloc[-1]
            indicators['signal'] = signal.iloc[-1]
            indicators['macd_histogram'] = (macd - signal).iloc[-1]

            # Médias Móveis
            indicators['sma_50'] = df['Close'].rolling(window=50).mean().iloc[-1]
            indicators['sma_200'] = df['Close'].rolling(window=200).mean().iloc[-1]
            indicators['ema_20'] = df['Close'].ewm(span=20, adjust=False).mean().iloc[-1]

            # Bollinger Bands
            sma_20 = df['Close'].rolling(window=20).mean()
            std_20 = df['Close'].rolling(window=20).std()
            indicators['bb_upper'] = (sma_20 + 2 * std_20).iloc[-1]
            indicators['bb_middle'] = sma_20.iloc[-1]
            indicators['bb_lower'] = (sma_20 - 2 * std_20).iloc[-1]

            # Volume médio
            indicators['avg_volume'] = df['Volume'].rolling(window=20).mean().iloc[-1]
            indicators['current_volume'] = df['Volume'].iloc[-1]

        except Exception as e:
            print(f"Erro ao calcular indicadores: {e}")

        return indicators

    def _evaluate_rsi(self, rsi: float) -> float:
        """Avalia RSI. Retorna score de -100 a 100."""
        if rsi is None or np.isnan(rsi):
            return 0

        if rsi < 30:
            # Oversold - potencial de compra
            return min(100, (30 - rsi) * 3)
        elif rsi > 70:
            # Overbought - potencial de venda
            return max(-100, (70 - rsi) * 3)
        else:
            # Neutro
            return (50 - rsi) * 0.5

    def _evaluate_macd(self, macd: float, signal: float) -> float:
        """Avalia MACD. Retorna score de -100 a 100."""
        if macd is None or signal is None:
            return 0

        histogram = macd - signal

        if histogram > 0 and macd > signal:
            # Sinal bullish
            return min(100, abs(histogram) * 50)
        elif histogram < 0 and macd < signal:
            # Sinal bearish
            return max(-100, -abs(histogram) * 50)
        else:
            return 0

    def _evaluate_moving_averages(self, sma_50: float, sma_200: float, current_price: float) -> float:
        """Avalia médias móveis. Retorna score de -100 a 100."""
        if sma_50 is None or sma_200 is None or current_price is None:
            return 0

        score = 0

        # Golden Cross / Death Cross
        if sma_50 > sma_200:
            score += 50  # Bullish
        else:
            score -= 50  # Bearish

        # Preço vs SMA 50
        price_vs_sma50 = ((current_price - sma_50) / sma_50) * 100
        score += np.clip(price_vs_sma50 * 2, -50, 50)

        return np.clip(score, -100, 100)

    def _evaluate_bollinger(self, price: float, upper: float, lower: float, middle: float) -> float:
        """Avalia Bollinger Bands. Retorna score de -100 a 100."""
        if any(x is None for x in [price, upper, lower, middle]):
            return 0

        band_width = upper - lower
        position = (price - lower) / band_width  # 0 = banda inferior, 1 = banda superior

        if position < 0.2:
            # Próximo da banda inferior - oversold
            return 60
        elif position > 0.8:
            # Próximo da banda superior - overbought
            return -60
        else:
            # No meio
            return (0.5 - position) * 40

    def _evaluate_volume(self, df: pd.DataFrame) -> float:
        """Avalia tendência de volume. Retorna score de -100 a 100."""
        try:
            current_volume = df['Volume'].iloc[-1]
            avg_volume = df['Volume'].rolling(window=20).mean().iloc[-1]

            # Tendência de preço recente
            price_change = (df['Close'].iloc[-1] - df['Close'].iloc[-5]) / df['Close'].iloc[-5]

            # Volume acima da média + preço subindo = bullish
            volume_ratio = current_volume / avg_volume

            if volume_ratio > 1.5 and price_change > 0:
                return 40
            elif volume_ratio > 1.5 and price_change < 0:
                return -40
            else:
                return 0

        except Exception:
            return 0

    def _calculate_confidence(self, scores: Dict[str, float]) -> float:
        """Calcula confiança baseada em consenso entre indicadores."""
        values = list(scores.values())

        # Se todos os indicadores concordam na direção
        all_bullish = all(v > 20 for v in values)
        all_bearish = all(v < -20 for v in values)

        if all_bullish or all_bearish:
            return 0.9

        # Calcula dispersão
        std_dev = np.std(values)

        # Menor dispersão = maior confiança
        confidence = max(0.3, 1 - (std_dev / 100))

        return confidence

    def _generate_reasoning(self, scores: Dict[str, float], indicators: Dict[str, float]) -> str:
        """Gera explicação textual da análise."""
        parts = []

        # RSI
        rsi = indicators.get('rsi')
        if rsi:
            if rsi < 30:
                parts.append(f"RSI em {rsi:.1f} (oversold - oportunidade de compra)")
            elif rsi > 70:
                parts.append(f"RSI em {rsi:.1f} (overbought - cautela)")
            else:
                parts.append(f"RSI em {rsi:.1f} (neutro)")

        # MACD
        if scores['macd'] > 30:
            parts.append("MACD mostra momentum bullish")
        elif scores['macd'] < -30:
            parts.append("MACD mostra momentum bearish")

        # Médias móveis
        sma_50 = indicators.get('sma_50')
        sma_200 = indicators.get('sma_200')
        if sma_50 and sma_200:
            if sma_50 > sma_200:
                parts.append("Golden Cross (SMA 50 > SMA 200) - tendência de alta")
            else:
                parts.append("Death Cross (SMA 50 < SMA 200) - tendência de baixa")

        return "; ".join(parts) if parts else "Análise técnica inconclusiva"
