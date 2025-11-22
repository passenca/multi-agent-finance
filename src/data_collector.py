"""
Módulo de Coleta de Dados Financeiros
Responsável por buscar dados de ações do S&P 500 e NASDAQ
Usando yahooquery em vez de yfinance
"""

import os
import ssl
import warnings

# Configurar ambiente
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['SSL_CERT_FILE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['PYTHONHTTPSVERIFY'] = '0'

# Desabilitar verificação SSL
ssl._create_default_https_context = ssl._create_unverified_context
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

from yahooquery import Ticker
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time


class DataCollector:
    """Classe para coletar dados financeiros de ações usando yahooquery"""

    # Lista de símbolos do S&P 500 (amostra - você pode expandir isso)
    SP500_SYMBOLS = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "JPM",
        "V", "JNJ", "WMT", "PG", "MA", "HD", "DIS", "BAC", "ADBE",
        "NFLX", "CRM", "CMCSA", "PFE", "KO", "PEP", "TMO", "ABBV",
        "AVGO", "COST", "MRK", "ACN", "CSCO", "NKE", "DHR", "TXN",
        "LIN", "UNP", "NEE", "BMY", "PM", "UPS", "RTX", "LOW", "ORCL"
    ]

    # Lista de símbolos do NASDAQ (amostra)
    NASDAQ_SYMBOLS = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "ADBE",
        "NFLX", "INTC", "CSCO", "CMCSA", "PEP", "AVGO", "TXN", "QCOM",
        "COST", "SBUX", "INTU", "AMGN", "ISRG", "AMD", "BKNG", "ADP"
    ]

    def __init__(self):
        """Inicializa o coletor de dados"""
        self.cache = {}

    def get_stock_list(self, index: str = "SP500") -> List[str]:
        """
        Retorna a lista de símbolos de ações para o índice especificado

        Args:
            index: "SP500", "NASDAQ", ou "BOTH"

        Returns:
            Lista de símbolos de ações
        """
        if index == "SP500":
            return self.SP500_SYMBOLS
        elif index == "NASDAQ":
            return self.NASDAQ_SYMBOLS
        elif index == "BOTH":
            # Combinar e remover duplicatas
            return list(set(self.SP500_SYMBOLS + self.NASDAQ_SYMBOLS))
        else:
            raise ValueError(f"Índice desconhecido: {index}")

    def _convert_period_to_dates(self, period: str):
        """Converte período string para datas"""
        end_date = datetime.now()

        period_map = {
            "1d": timedelta(days=1),
            "5d": timedelta(days=5),
            "1mo": timedelta(days=30),
            "3mo": timedelta(days=90),
            "6mo": timedelta(days=180),
            "1y": timedelta(days=365),
            "5y": timedelta(days=1825),
        }

        delta = period_map.get(period, timedelta(days=365))
        start_date = end_date - delta

        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

    def get_stock_data(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """
        Busca dados históricos de uma ação

        Args:
            symbol: Símbolo da ação (ex: "AAPL")
            period: Período de dados ("1d", "5d", "1mo", "3mo", "6mo", "1y", "5y")
            interval: Intervalo dos dados ("1m", "5m", "1h", "1d", "1wk", "1mo")

        Returns:
            DataFrame com dados históricos ou None se houver erro
        """
        try:
            ticker = Ticker(symbol, verify=False)
            start_date, end_date = self._convert_period_to_dates(period)

            # Buscar dados históricos
            data = ticker.history(start=start_date, end=end_date, interval=interval)

            if isinstance(data, pd.DataFrame) and not data.empty:
                # Se multi-index, pegar apenas o símbolo desejado
                if isinstance(data.index, pd.MultiIndex):
                    data = data.xs(symbol, level='symbol')

                # Garantir que temos as colunas esperadas
                expected_cols = ['open', 'high', 'low', 'close', 'volume']
                if all(col in data.columns for col in expected_cols):
                    # Capitalizar nomes das colunas para compatibilidade com yfinance
                    data.columns = [col.capitalize() for col in data.columns]
                    return data
                else:
                    print(f"[AVISO] Colunas inesperadas para {symbol}")
                    return None
            else:
                print(f"[AVISO] Sem dados para {symbol}")
                return None

        except Exception as e:
            print(f"[ERRO] Erro ao buscar dados para {symbol}: {str(e)}")
            return None

    def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """
        Busca informações fundamentais de uma ação

        Args:
            symbol: Símbolo da ação

        Returns:
            Dicionário com informações fundamentais ou None se houver erro
        """
        try:
            ticker = Ticker(symbol, verify=False)

            # Buscar informações summary
            summary = ticker.summary_detail.get(symbol, {})
            price_info = ticker.price.get(symbol, {})
            financial_data = ticker.financial_data.get(symbol, {})
            key_stats = ticker.key_stats.get(symbol, {})

            # Se algum retornou erro, avisar
            if isinstance(summary, str) or isinstance(price_info, str):
                print(f"[AVISO] Dados limitados para {symbol}")
                return None

            # Extrair informações relevantes
            fundamental_data = {
                'symbol': symbol,
                'name': price_info.get('longName', price_info.get('shortName', 'N/A')),
                'sector': summary.get('sector', price_info.get('sector', 'N/A')),
                'industry': summary.get('industry', price_info.get('industry', 'N/A')),
                'marketCap': price_info.get('marketCap', 0),
                'peRatio': summary.get('trailingPE', key_stats.get('trailingPE', None)),
                'forwardPE': summary.get('forwardPE', key_stats.get('forwardPE', None)),
                'priceToBook': key_stats.get('priceToBook', None),
                'dividendYield': summary.get('dividendYield', summary.get('yield', None)),
                'profitMargins': financial_data.get('profitMargins', None),
                'returnOnEquity': financial_data.get('returnOnEquity', None),
                'revenueGrowth': financial_data.get('revenueGrowth', None),
                'earningsGrowth': financial_data.get('earningsGrowth', None),
                'currentPrice': price_info.get('regularMarketPrice', summary.get('regularMarketPrice', None)),
                'targetMeanPrice': financial_data.get('targetMeanPrice', None),
                'recommendationKey': financial_data.get('recommendationKey', 'N/A'),
            }

            return fundamental_data

        except Exception as e:
            print(f"[ERRO] Erro ao buscar informações para {symbol}: {str(e)}")
            return None

    def get_multiple_stocks_data(
        self,
        symbols: List[str],
        period: str = "1y",
        progress_callback=None
    ) -> Dict[str, pd.DataFrame]:
        """
        Busca dados de múltiplas ações

        Args:
            symbols: Lista de símbolos
            period: Período de dados
            progress_callback: Função de callback para reportar progresso

        Returns:
            Dicionário com dados de cada ação
        """
        results = {}
        total = len(symbols)

        for i, symbol in enumerate(symbols):
            if progress_callback:
                progress_callback(i + 1, total, symbol)

            data = self.get_stock_data(symbol, period)
            if data is not None:
                results[symbol] = data

            # Pequena pausa para não sobrecarregar a API
            time.sleep(0.1)

        return results

    def get_multiple_stocks_info(
        self,
        symbols: List[str],
        progress_callback=None
    ) -> pd.DataFrame:
        """
        Busca informações fundamentais de múltiplas ações

        Args:
            symbols: Lista de símbolos
            progress_callback: Função de callback para reportar progresso

        Returns:
            DataFrame com informações fundamentais
        """
        results = []
        total = len(symbols)

        for i, symbol in enumerate(symbols):
            if progress_callback:
                progress_callback(i + 1, total, symbol)

            info = self.get_stock_info(symbol)
            if info:
                results.append(info)

            # Pequena pausa para não sobrecarregar a API
            time.sleep(0.1)

        return pd.DataFrame(results)

    def get_latest_price(self, symbol: str) -> Optional[float]:
        """
        Busca o preço mais recente de uma ação

        Args:
            symbol: Símbolo da ação

        Returns:
            Preço atual ou None se houver erro
        """
        try:
            ticker = Ticker(symbol, verify=False)
            price_info = ticker.price.get(symbol, {})

            if isinstance(price_info, dict):
                price = price_info.get('regularMarketPrice')
                if price:
                    return float(price)

            return None

        except Exception as e:
            print(f"[ERRO] Erro ao buscar preço para {symbol}: {str(e)}")
            return None
