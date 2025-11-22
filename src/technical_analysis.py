"""
Módulo de Análise Técnica
Calcula indicadores técnicos para análise de ações
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
import pandas_ta as ta


class TechnicalAnalyzer:
    """Classe para realizar análise técnica de ações"""

    def __init__(self):
        """Inicializa o analisador técnico"""
        pass

    def calculate_sma(self, data: pd.DataFrame, periods: list = [20, 50, 200]) -> pd.DataFrame:
        """
        Calcula Médias Móveis Simples (SMA)

        Args:
            data: DataFrame com dados históricos
            periods: Lista de períodos para calcular SMA

        Returns:
            DataFrame com SMAs adicionadas
        """
        df = data.copy()

        for period in periods:
            df[f'SMA_{period}'] = df['Close'].rolling(window=period).mean()

        return df

    def calculate_ema(self, data: pd.DataFrame, periods: list = [12, 26]) -> pd.DataFrame:
        """
        Calcula Médias Móveis Exponenciais (EMA)

        Args:
            data: DataFrame com dados históricos
            periods: Lista de períodos para calcular EMA

        Returns:
            DataFrame com EMAs adicionadas
        """
        df = data.copy()

        for period in periods:
            df[f'EMA_{period}'] = df['Close'].ewm(span=period, adjust=False).mean()

        return df

    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Calcula o RSI (Relative Strength Index)

        Args:
            data: DataFrame com dados históricos
            period: Período para cálculo do RSI

        Returns:
            DataFrame com RSI adicionado
        """
        df = data.copy()

        # Calcular variações
        delta = df['Close'].diff()

        # Separar ganhos e perdas
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        # Calcular RS e RSI
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        return df

    def calculate_macd(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula o MACD (Moving Average Convergence Divergence)

        Args:
            data: DataFrame com dados históricos

        Returns:
            DataFrame com MACD, Signal e Histogram adicionados
        """
        df = data.copy()

        # Calcular EMAs
        ema_12 = df['Close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['Close'].ewm(span=26, adjust=False).mean()

        # Calcular MACD e Signal
        df['MACD'] = ema_12 - ema_26
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']

        return df

    def calculate_bollinger_bands(
        self,
        data: pd.DataFrame,
        period: int = 20,
        std_dev: int = 2
    ) -> pd.DataFrame:
        """
        Calcula Bandas de Bollinger

        Args:
            data: DataFrame com dados históricos
            period: Período para média móvel
            std_dev: Número de desvios padrão

        Returns:
            DataFrame com Bandas de Bollinger adicionadas
        """
        df = data.copy()

        # Calcular média móvel
        df['BB_Middle'] = df['Close'].rolling(window=period).mean()

        # Calcular desvio padrão
        rolling_std = df['Close'].rolling(window=period).std()

        # Calcular bandas superior e inferior
        df['BB_Upper'] = df['BB_Middle'] + (rolling_std * std_dev)
        df['BB_Lower'] = df['BB_Middle'] - (rolling_std * std_dev)

        return df

    def calculate_stochastic(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Calcula o Oscilador Estocástico

        Args:
            data: DataFrame com dados históricos
            period: Período para cálculo

        Returns:
            DataFrame com Estocástico adicionado
        """
        df = data.copy()

        # Calcular %K
        low_min = df['Low'].rolling(window=period).min()
        high_max = df['High'].rolling(window=period).max()

        df['Stoch_K'] = 100 * (df['Close'] - low_min) / (high_max - low_min)

        # Calcular %D (média móvel de %K)
        df['Stoch_D'] = df['Stoch_K'].rolling(window=3).mean()

        return df

    def calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Calcula o ATR (Average True Range)

        Args:
            data: DataFrame com dados históricos
            period: Período para cálculo

        Returns:
            DataFrame com ATR adicionado
        """
        df = data.copy()

        # Calcular True Range
        df['H-L'] = df['High'] - df['Low']
        df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
        df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))

        df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
        df['ATR'] = df['TR'].rolling(window=period).mean()

        # Remover colunas auxiliares
        df.drop(['H-L', 'H-PC', 'L-PC', 'TR'], axis=1, inplace=True)

        return df

    def calculate_all_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula todos os indicadores técnicos

        Args:
            data: DataFrame com dados históricos

        Returns:
            DataFrame com todos os indicadores
        """
        df = data.copy()

        # Médias móveis
        df = self.calculate_sma(df, periods=[20, 50, 200])
        df = self.calculate_ema(df, periods=[12, 26])

        # Indicadores de momentum
        df = self.calculate_rsi(df)
        df = self.calculate_macd(df)
        df = self.calculate_stochastic(df)

        # Volatilidade
        df = self.calculate_bollinger_bands(df)
        df = self.calculate_atr(df)

        return df

    def generate_signals(self, data: pd.DataFrame) -> Dict[str, str]:
        """
        Gera sinais de compra/venda baseados nos indicadores

        Args:
            data: DataFrame com indicadores calculados

        Returns:
            Dicionário com sinais para cada indicador
        """
        if data.empty or len(data) < 2:
            return {}

        signals = {}

        # Sinal RSI
        latest_rsi = data['RSI'].iloc[-1]
        if pd.notna(latest_rsi):
            if latest_rsi < 30:
                signals['RSI'] = 'COMPRA (Sobrevendido)'
            elif latest_rsi > 70:
                signals['RSI'] = 'VENDA (Sobrecomprado)'
            else:
                signals['RSI'] = 'NEUTRO'

        # Sinal MACD
        if 'MACD' in data.columns and 'MACD_Signal' in data.columns:
            macd_current = data['MACD'].iloc[-1]
            signal_current = data['MACD_Signal'].iloc[-1]
            macd_prev = data['MACD'].iloc[-2]
            signal_prev = data['MACD_Signal'].iloc[-2]

            if pd.notna(macd_current) and pd.notna(signal_current):
                if macd_prev < signal_prev and macd_current > signal_current:
                    signals['MACD'] = 'COMPRA (Cruzamento positivo)'
                elif macd_prev > signal_prev and macd_current < signal_current:
                    signals['MACD'] = 'VENDA (Cruzamento negativo)'
                else:
                    signals['MACD'] = 'NEUTRO'

        # Sinal de Médias Móveis
        if 'SMA_50' in data.columns and 'SMA_200' in data.columns:
            sma50 = data['SMA_50'].iloc[-1]
            sma200 = data['SMA_200'].iloc[-1]

            if pd.notna(sma50) and pd.notna(sma200):
                if sma50 > sma200:
                    signals['SMA_Cross'] = 'TENDÊNCIA ALTA (Golden Cross)'
                else:
                    signals['SMA_Cross'] = 'TENDÊNCIA BAIXA (Death Cross)'

        # Sinal de Bandas de Bollinger
        if all(col in data.columns for col in ['Close', 'BB_Upper', 'BB_Lower']):
            price = data['Close'].iloc[-1]
            bb_upper = data['BB_Upper'].iloc[-1]
            bb_lower = data['BB_Lower'].iloc[-1]

            if pd.notna(bb_upper) and pd.notna(bb_lower):
                if price > bb_upper:
                    signals['Bollinger'] = 'VENDA (Acima banda superior)'
                elif price < bb_lower:
                    signals['Bollinger'] = 'COMPRA (Abaixo banda inferior)'
                else:
                    signals['Bollinger'] = 'NEUTRO'

        return signals

    def calculate_trend_strength(self, data: pd.DataFrame) -> Optional[float]:
        """
        Calcula a força da tendência (0-100)

        Args:
            data: DataFrame com indicadores

        Returns:
            Força da tendência (0-100) ou None
        """
        if data.empty or len(data) < 50:
            return None

        score = 0
        max_score = 5

        # Critério 1: Preço acima de SMA 200
        if 'SMA_200' in data.columns:
            if data['Close'].iloc[-1] > data['SMA_200'].iloc[-1]:
                score += 1

        # Critério 2: SMA 50 acima de SMA 200
        if 'SMA_50' in data.columns and 'SMA_200' in data.columns:
            if data['SMA_50'].iloc[-1] > data['SMA_200'].iloc[-1]:
                score += 1

        # Critério 3: RSI entre 40 e 70
        if 'RSI' in data.columns:
            rsi = data['RSI'].iloc[-1]
            if 40 <= rsi <= 70:
                score += 1

        # Critério 4: MACD positivo
        if 'MACD' in data.columns:
            if data['MACD'].iloc[-1] > 0:
                score += 1

        # Critério 5: Preço acima de SMA 50
        if 'SMA_50' in data.columns:
            if data['Close'].iloc[-1] > data['SMA_50'].iloc[-1]:
                score += 1

        return (score / max_score) * 100
