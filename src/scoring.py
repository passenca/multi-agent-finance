"""
Módulo de Sistema de Pontuação
Combina análise técnica e fundamental para ranquear ações
"""

import pandas as pd
from typing import Dict, List
from .technical_analysis import TechnicalAnalyzer
from .fundamental_analysis import FundamentalAnalyzer


class ScoringSystem:
    """Classe para calcular pontuação combinada de ações"""

    def __init__(self, technical_weight: float = 0.4, fundamental_weight: float = 0.6):
        """
        Inicializa o sistema de pontuação

        Args:
            technical_weight: Peso da análise técnica (0-1)
            fundamental_weight: Peso da análise fundamental (0-1)
        """
        self.technical_weight = technical_weight
        self.fundamental_weight = fundamental_weight
        self.technical_analyzer = TechnicalAnalyzer()
        self.fundamental_analyzer = FundamentalAnalyzer()

        # Garantir que os pesos somem 1
        total = technical_weight + fundamental_weight
        self.technical_weight = technical_weight / total
        self.fundamental_weight = fundamental_weight / total

    def calculate_technical_score(self, historical_data: pd.DataFrame) -> Dict[str, any]:
        """
        Calcula a pontuação técnica de uma ação

        Args:
            historical_data: DataFrame com dados históricos

        Returns:
            Dicionário com pontuação e detalhes
        """
        if historical_data is None or historical_data.empty:
            return {
                'score': 0,
                'trend_strength': 0,
                'signals': {},
                'status': 'Sem dados'
            }

        # Calcular todos os indicadores
        data_with_indicators = self.technical_analyzer.calculate_all_indicators(historical_data)

        # Calcular força da tendência
        trend_strength = self.technical_analyzer.calculate_trend_strength(data_with_indicators)

        # Gerar sinais
        signals = self.technical_analyzer.generate_signals(data_with_indicators)

        # Calcular pontuação baseada nos sinais
        signal_score = 0
        buy_signals = 0
        sell_signals = 0
        neutral_signals = 0

        for indicator, signal in signals.items():
            if 'COMPRA' in signal or 'ALTA' in signal:
                buy_signals += 1
                signal_score += 100
            elif 'VENDA' in signal or 'BAIXA' in signal:
                sell_signals += 1
                signal_score += 0
            else:
                neutral_signals += 1
                signal_score += 50

        # Média dos sinais
        total_signals = buy_signals + sell_signals + neutral_signals
        if total_signals > 0:
            signal_score = signal_score / total_signals
        else:
            signal_score = 50

        # Combinar força da tendência e sinais (50% cada)
        if trend_strength is not None:
            technical_score = (signal_score * 0.5) + (trend_strength * 0.5)
        else:
            technical_score = signal_score

        return {
            'score': technical_score,
            'trend_strength': trend_strength,
            'signals': signals,
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'neutral_signals': neutral_signals,
            'status': self._get_technical_status(technical_score)
        }

    def calculate_fundamental_score(self, stock_info: Dict) -> Dict[str, any]:
        """
        Calcula a pontuação fundamental de uma ação

        Args:
            stock_info: Dicionário com informações fundamentais

        Returns:
            Dicionário com pontuação e detalhes
        """
        if not stock_info:
            return {
                'score': 0,
                'analysis': {},
                'status': 'Sem dados'
            }

        # Realizar análise fundamental
        analysis = self.fundamental_analyzer.analyze_stock(stock_info)

        return {
            'score': analysis['overall_score'],
            'rating': analysis['overall_rating'],
            'analysis': analysis,
            'status': self._get_fundamental_status(analysis['overall_score'])
        }

    def calculate_combined_score(
        self,
        symbol: str,
        historical_data: pd.DataFrame,
        stock_info: Dict
    ) -> Dict[str, any]:
        """
        Calcula a pontuação combinada (técnica + fundamental)

        Args:
            symbol: Símbolo da ação
            historical_data: Dados históricos
            stock_info: Informações fundamentais

        Returns:
            Dicionário com pontuação combinada e detalhes
        """
        # Calcular pontuações individuais
        technical_result = self.calculate_technical_score(historical_data)
        fundamental_result = self.calculate_fundamental_score(stock_info)

        # Calcular pontuação combinada
        combined_score = (
            technical_result['score'] * self.technical_weight +
            fundamental_result['score'] * self.fundamental_weight
        )

        # Determinar recomendação
        recommendation = self._get_recommendation(combined_score, technical_result, fundamental_result)

        return {
            'symbol': symbol,
            'name': stock_info.get('name', 'N/A') if stock_info else 'N/A',
            'sector': stock_info.get('sector', 'N/A') if stock_info else 'N/A',
            'combined_score': round(combined_score, 2),
            'technical_score': round(technical_result['score'], 2),
            'fundamental_score': round(fundamental_result['score'], 2),
            'technical_details': technical_result,
            'fundamental_details': fundamental_result,
            'recommendation': recommendation,
            'current_price': stock_info.get('currentPrice') if stock_info else None,
            'target_price': stock_info.get('targetMeanPrice') if stock_info else None
        }

    def rank_stocks(self, stocks_data: List[Dict]) -> pd.DataFrame:
        """
        Ranqueia uma lista de ações por pontuação

        Args:
            stocks_data: Lista de dicionários com dados das ações

        Returns:
            DataFrame ranqueado por pontuação
        """
        df = pd.DataFrame(stocks_data)

        # Ordenar por pontuação combinada (decrescente)
        df = df.sort_values('combined_score', ascending=False)

        # Adicionar posição no ranking
        df.insert(0, 'rank', range(1, len(df) + 1))

        return df

    def filter_by_score(
        self,
        ranked_df: pd.DataFrame,
        min_score: float = 60,
        min_technical: float = None,
        min_fundamental: float = None
    ) -> pd.DataFrame:
        """
        Filtra ações por pontuação mínima

        Args:
            ranked_df: DataFrame ranqueado
            min_score: Pontuação mínima combinada
            min_technical: Pontuação técnica mínima (opcional)
            min_fundamental: Pontuação fundamental mínima (opcional)

        Returns:
            DataFrame filtrado
        """
        filtered = ranked_df[ranked_df['combined_score'] >= min_score]

        if min_technical is not None:
            filtered = filtered[filtered['technical_score'] >= min_technical]

        if min_fundamental is not None:
            filtered = filtered[filtered['fundamental_score'] >= min_fundamental]

        return filtered

    def get_top_stocks(
        self,
        ranked_df: pd.DataFrame,
        n: int = 10,
        sector: str = None
    ) -> pd.DataFrame:
        """
        Retorna as top N ações

        Args:
            ranked_df: DataFrame ranqueado
            n: Número de ações a retornar
            sector: Filtrar por setor (opcional)

        Returns:
            DataFrame com top N ações
        """
        if sector:
            filtered = ranked_df[ranked_df['sector'] == sector]
        else:
            filtered = ranked_df

        return filtered.head(n)

    def _get_technical_status(self, score: float) -> str:
        """Retorna status baseado na pontuação técnica"""
        if score >= 80:
            return 'Muito Forte'
        elif score >= 60:
            return 'Forte'
        elif score >= 40:
            return 'Neutro'
        elif score >= 20:
            return 'Fraco'
        else:
            return 'Muito Fraco'

    def _get_fundamental_status(self, score: float) -> str:
        """Retorna status baseado na pontuação fundamental"""
        if score >= 80:
            return 'Excelente'
        elif score >= 60:
            return 'Bom'
        elif score >= 40:
            return 'Moderado'
        else:
            return 'Fraco'

    def _get_recommendation(
        self,
        combined_score: float,
        technical_result: Dict,
        fundamental_result: Dict
    ) -> str:
        """
        Determina a recomendação baseada nas pontuações

        Args:
            combined_score: Pontuação combinada
            technical_result: Resultado da análise técnica
            fundamental_result: Resultado da análise fundamental

        Returns:
            Recomendação (COMPRA FORTE, COMPRA, MANTER, VENDA, VENDA FORTE)
        """
        tech_score = technical_result['score']
        fund_score = fundamental_result['score']
        buy_signals = technical_result.get('buy_signals', 0)
        sell_signals = technical_result.get('sell_signals', 0)

        # COMPRA FORTE: Pontuação alta em ambas as análises
        if combined_score >= 80 and tech_score >= 70 and fund_score >= 70:
            return '🟢 COMPRA FORTE'

        # COMPRA: Pontuação boa com mais sinais de compra
        elif combined_score >= 65 and (tech_score >= 60 or fund_score >= 70):
            if buy_signals > sell_signals:
                return '🟢 COMPRA'
            else:
                return '🟡 MANTER/COMPRA'

        # MANTER: Pontuação moderada
        elif combined_score >= 45:
            return '🟡 MANTER'

        # VENDA: Pontuação baixa ou muitos sinais de venda
        elif combined_score >= 30 or sell_signals > buy_signals + 1:
            return '🔴 VENDA'

        # VENDA FORTE: Pontuação muito baixa
        else:
            return '🔴 VENDA FORTE'

    def generate_summary(self, ranked_df: pd.DataFrame) -> Dict[str, any]:
        """
        Gera um resumo estatístico das ações analisadas

        Args:
            ranked_df: DataFrame ranqueado

        Returns:
            Dicionário com estatísticas
        """
        if ranked_df.empty:
            return {
                'total_stocks': 0,
                'buy_recommendations': 0,
                'hold_recommendations': 0,
                'sell_recommendations': 0,
                'avg_combined_score': 0,
                'avg_technical_score': 0,
                'avg_fundamental_score': 0
            }

        # Contar recomendações
        buy_count = ranked_df['recommendation'].str.contains('COMPRA', na=False).sum()
        hold_count = ranked_df['recommendation'].str.contains('MANTER', na=False).sum()
        sell_count = ranked_df['recommendation'].str.contains('VENDA', na=False).sum()

        return {
            'total_stocks': len(ranked_df),
            'buy_recommendations': int(buy_count),
            'hold_recommendations': int(hold_count),
            'sell_recommendations': int(sell_count),
            'avg_combined_score': round(ranked_df['combined_score'].mean(), 2),
            'avg_technical_score': round(ranked_df['technical_score'].mean(), 2),
            'avg_fundamental_score': round(ranked_df['fundamental_score'].mean(), 2),
            'top_sector': ranked_df['sector'].mode()[0] if not ranked_df['sector'].mode().empty else 'N/A'
        }
