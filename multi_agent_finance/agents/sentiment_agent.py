"""
Agente de Análise de Sentimento - Avalia sentimento de mercado através de notícias e social media.
"""
import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timedelta
from .base_agent import BaseAgent, AgentInsight


class SentimentAgent(BaseAgent):
    """
    Agente especializado em análise de sentimento.

    Analisa notícias financeiras, social media, e outros indicadores de sentimento.

    Nota: Este agente requer dados de sentimento externos (news API, Twitter API, etc.)
    Por enquanto, trabalha com dados pré-processados fornecidos.
    """

    def __init__(self, weight: float = 1.0):
        super().__init__(name="Sentiment Analyst", weight=weight)

    def analyze(self, symbol: str, data: Dict[str, Any]) -> AgentInsight:
        """
        Analisa sentimento de mercado para o ativo.

        Args:
            symbol: Símbolo do ativo
            data: Deve conter 'sentiment' com:
                - 'news': lista de notícias com sentiment scores
                - 'social_media': dados de redes sociais
                - 'analyst_ratings': ratings de analistas

        Returns:
            AgentInsight com análise de sentimento
        """
        sentiment_data = data.get('sentiment', {})

        if not sentiment_data:
            # Se não há dados de sentimento, tenta inferir de outras fontes
            return self._fallback_analysis(symbol, data)

        scores = {}

        # Analisa notícias
        if 'news' in sentiment_data:
            scores['news'] = self._analyze_news(sentiment_data['news'])

        # Analisa social media
        if 'social_media' in sentiment_data:
            scores['social'] = self._analyze_social_media(sentiment_data['social_media'])

        # Analisa ratings de analistas
        if 'analyst_ratings' in sentiment_data:
            scores['analysts'] = self._analyze_analyst_ratings(sentiment_data['analyst_ratings'])

        # Analisa insider trading
        if 'insider_trades' in sentiment_data:
            scores['insider'] = self._analyze_insider_trades(sentiment_data['insider_trades'])

        if not scores:
            return self._fallback_analysis(symbol, data)

        # Score combinado
        final_score = np.mean(list(scores.values()))

        # Confiança baseada em consenso
        confidence = self._calculate_confidence(scores)

        # Reasoning
        reasoning = self._generate_reasoning(scores, sentiment_data)

        return AgentInsight(
            agent_name=self.name,
            score=final_score,
            confidence=confidence,
            reasoning=reasoning,
            metadata={'sentiment_scores': scores}
        )

    def _analyze_news(self, news: List[Dict[str, Any]]) -> float:
        """
        Analisa sentimento de notícias.

        Espera lista de dicts com:
        - 'title': título da notícia
        - 'sentiment': score de -1 a 1 (ou 'positive', 'negative', 'neutral')
        - 'date': data da notícia
        - 'source': fonte
        """
        if not news:
            return 0

        scores = []
        weights = []

        for item in news:
            # Converte sentimento para score numérico
            sentiment = item.get('sentiment', 0)
            if isinstance(sentiment, str):
                sentiment = {'positive': 0.7, 'negative': -0.7, 'neutral': 0}.get(sentiment.lower(), 0)

            # Peso baseado em recência (notícias mais recentes têm maior peso)
            date = item.get('date')
            if date:
                if isinstance(date, str):
                    date = datetime.fromisoformat(date.replace('Z', '+00:00'))
                days_ago = (datetime.now() - date).days
                weight = 1 / (1 + days_ago * 0.1)  # Decay exponencial
            else:
                weight = 0.5

            scores.append(sentiment)
            weights.append(weight)

        # Weighted average
        weighted_score = sum(s * w for s, w in zip(scores, weights)) / sum(weights)

        return weighted_score * 100  # Escala para -100 a 100

    def _analyze_social_media(self, social_data: Dict[str, Any]) -> float:
        """
        Analisa sentimento de redes sociais.

        Espera dict com:
        - 'mentions': número de menções
        - 'sentiment_score': score médio de -1 a 1
        - 'trending': bool indicando se está trending
        """
        score = 0

        sentiment = social_data.get('sentiment_score', 0)
        score += sentiment * 60

        # Bonus se está trending
        if social_data.get('trending', False):
            score += 30 if sentiment > 0 else -30

        # Volume de menções
        mentions = social_data.get('mentions', 0)
        if mentions > 10000:
            score += 20 * np.sign(sentiment)
        elif mentions > 1000:
            score += 10 * np.sign(sentiment)

        return np.clip(score, -100, 100)

    def _analyze_analyst_ratings(self, ratings: Dict[str, Any]) -> float:
        """
        Analisa ratings de analistas.

        Espera dict com:
        - 'strong_buy': número de strong buy
        - 'buy': número de buy
        - 'hold': número de hold
        - 'sell': número de sell
        - 'strong_sell': número de strong sell
        - 'target_price': preço alvo médio
        - 'current_price': preço atual
        """
        strong_buy = ratings.get('strong_buy', 0)
        buy = ratings.get('buy', 0)
        hold = ratings.get('hold', 0)
        sell = ratings.get('sell', 0)
        strong_sell = ratings.get('strong_sell', 0)

        total = strong_buy + buy + hold + sell + strong_sell

        if total == 0:
            return 0

        # Calcula score ponderado
        score = (strong_buy * 100 + buy * 50 + hold * 0 + sell * -50 + strong_sell * -100) / total

        # Ajusta baseado em target price
        target_price = ratings.get('target_price')
        current_price = ratings.get('current_price')

        if target_price and current_price and current_price > 0:
            upside = ((target_price - current_price) / current_price) * 100
            # Adiciona até ±30 pontos baseado no upside
            score += np.clip(upside * 0.5, -30, 30)

        return np.clip(score, -100, 100)

    def _analyze_insider_trades(self, trades: List[Dict[str, Any]]) -> float:
        """
        Analisa insider trading (compras/vendas de executivos).

        Espera lista de dicts com:
        - 'type': 'buy' ou 'sell'
        - 'value': valor da transação
        - 'date': data
        """
        if not trades:
            return 0

        # Considera apenas últimos 90 dias
        cutoff_date = datetime.now() - timedelta(days=90)

        buy_value = 0
        sell_value = 0

        for trade in trades:
            trade_date = trade.get('date')
            if isinstance(trade_date, str):
                trade_date = datetime.fromisoformat(trade_date.replace('Z', '+00:00'))

            if trade_date and trade_date < cutoff_date:
                continue

            value = trade.get('value', 0)
            trade_type = trade.get('type', '').lower()

            if trade_type == 'buy':
                buy_value += value
            elif trade_type == 'sell':
                sell_value += value

        # Net buying
        net_buying = buy_value - sell_value

        # Score baseado no net buying
        if buy_value + sell_value == 0:
            return 0

        net_ratio = net_buying / (buy_value + sell_value)

        return net_ratio * 100

    def _calculate_confidence(self, scores: Dict[str, float]) -> float:
        """Calcula confiança baseada em consenso entre fontes."""
        if not scores:
            return 0.1

        values = list(scores.values())

        # Se todas as fontes concordam
        all_positive = all(v > 20 for v in values)
        all_negative = all(v < -20 for v in values)

        if all_positive or all_negative:
            return 0.85

        # Consenso parcial
        positive_count = sum(1 for v in values if v > 20)
        negative_count = sum(1 for v in values if v < -20)

        if positive_count > len(values) * 0.6 or negative_count > len(values) * 0.6:
            return 0.7

        return 0.5

    def _generate_reasoning(self, scores: Dict[str, float], sentiment_data: Dict[str, Any]) -> str:
        """Gera explicação textual."""
        parts = []

        # News sentiment
        if 'news' in scores:
            news_count = len(sentiment_data.get('news', []))
            if scores['news'] > 30:
                parts.append(f"Sentimento positivo em {news_count} notícias recentes")
            elif scores['news'] < -30:
                parts.append(f"Sentimento negativo em {news_count} notícias recentes")

        # Social media
        if 'social' in scores:
            if scores['social'] > 30:
                parts.append("Buzz positivo nas redes sociais")
            elif scores['social'] < -30:
                parts.append("Sentimento negativo nas redes sociais")

        # Analyst ratings
        if 'analysts' in scores:
            ratings = sentiment_data.get('analyst_ratings', {})
            total = sum([ratings.get('strong_buy', 0), ratings.get('buy', 0),
                        ratings.get('hold', 0), ratings.get('sell', 0),
                        ratings.get('strong_sell', 0)])
            if total > 0:
                parts.append(f"{total} analistas cobrem o ativo")

        # Insider trades
        if 'insider' in scores:
            if scores['insider'] > 30:
                parts.append("Insiders comprando ações (sinal positivo)")
            elif scores['insider'] < -30:
                parts.append("Insiders vendendo ações (sinal negativo)")

        return "; ".join(parts) if parts else "Análise de sentimento mista"

    def _fallback_analysis(self, symbol: str, data: Dict[str, Any]) -> AgentInsight:
        """Análise fallback quando não há dados de sentimento."""
        # Tenta inferir sentimento de preço e volume
        price_data = data.get('price_history')

        if price_data is not None and not price_data.empty:
            # Momentum de preço recente como proxy de sentimento
            recent_return = (price_data['Close'].iloc[-1] - price_data['Close'].iloc[-20]) / price_data['Close'].iloc[-20]
            score = np.clip(recent_return * 200, -50, 50)

            return AgentInsight(
                agent_name=self.name,
                score=score,
                confidence=0.3,
                reasoning="Sentimento inferido de momentum de preço (dados diretos não disponíveis)"
            )

        return AgentInsight(
            agent_name=self.name,
            score=0,
            confidence=0.1,
            reasoning="Dados de sentimento não disponíveis"
        )
