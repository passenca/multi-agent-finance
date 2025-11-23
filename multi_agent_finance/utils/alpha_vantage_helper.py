"""
Helper para buscar dados do Alpha Vantage como alternativa ao Yahoo Finance.
API Gratuita: https://www.alphavantage.co/support/#api-key
Limite gratuito: 25 chamadas/dia (suficiente para testes)
"""
import requests
import pandas as pd
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import time

def fetch_alpha_vantage_data(symbol: str, api_key: str, period: str = "1y") -> Optional[Dict[str, Any]]:
    """
    Busca dados de um símbolo usando Alpha Vantage API.

    Args:
        symbol: Símbolo da ação (ex: "AAPL")
        api_key: Chave da API Alpha Vantage
        period: Período de dados (ex: "1y", "6mo")

    Returns:
        Dicionário com price_history e fundamentals, ou None se falhar
    """
    if not api_key or api_key == "your_api_key_here":
        print("[ALPHA VANTAGE] API key não configurada")
        return None

    print(f"[ALPHA VANTAGE] Buscando dados para {symbol}...")

    try:
        # Determinar função baseada no período
        # Para períodos <= 3 meses: TIME_SERIES_DAILY
        # Para períodos > 3 meses: TIME_SERIES_DAILY (compact = últimos 100 dias) ou full
        outputsize = "compact" if period in ["1mo", "3mo"] else "full"

        # 1. Buscar histórico de preços (TIME_SERIES_DAILY)
        url_daily = f"https://www.alphavantage.co/query"
        params_daily = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": outputsize,
            "apikey": api_key
        }

        response = requests.get(url_daily, params=params_daily, timeout=10)
        response.raise_for_status()
        data_daily = response.json()

        # DEBUG: Mostrar chaves retornadas pela API
        print(f"[ALPHA VANTAGE DEBUG] Chaves na resposta: {list(data_daily.keys())}")

        # Verificar se há mensagem informativa
        if "Information" in data_daily:
            info_msg = data_daily['Information']
            print(f"[ALPHA VANTAGE INFO] {info_msg}")
            try:
                import streamlit as st
                st.warning(f"Alpha Vantage Info: {info_msg}")
            except:
                pass
            # Se só tem Information, retorna None
            if len(data_daily) == 1:
                return None

        # Verificar se houve erro
        if "Error Message" in data_daily:
            error_msg = data_daily['Error Message']
            print(f"[ALPHA VANTAGE ERRO] {error_msg}")
            try:
                import streamlit as st
                st.error(f"Alpha Vantage API Error: {error_msg}")
            except:
                pass
            return None

        if "Note" in data_daily:  # Rate limit atingido
            note_msg = data_daily['Note']
            print(f"[ALPHA VANTAGE LIMITE] {note_msg}")
            try:
                import streamlit as st
                st.warning(f"Alpha Vantage Rate Limit: {note_msg}")
            except:
                pass
            return None

        # Converter para DataFrame
        time_series = data_daily.get("Time Series (Daily)", {})
        if not time_series:
            print(f"[ALPHA VANTAGE] Sem dados de preços para {symbol}")
            print(f"[ALPHA VANTAGE DEBUG] Resposta completa: {data_daily}")
            try:
                import streamlit as st
                st.error(f"Alpha Vantage: Sem 'Time Series (Daily)' na resposta. Chaves recebidas: {list(data_daily.keys())}")
            except:
                pass
            return None

        # Criar DataFrame de preços
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()

        # Renomear colunas para formato padrão
        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        df = df.astype({
            'Open': float,
            'High': float,
            'Low': float,
            'Close': float,
            'Volume': int
        })

        # Filtrar por período
        df = _filter_by_period(df, period)

        print(f"[ALPHA VANTAGE OK] Histórico de preços: {len(df)} dias")

        # 2. Buscar dados fundamentais (OVERVIEW)
        # Delay para evitar rate limit (5 chamadas/minuto para API gratuita)
        print(f"[ALPHA VANTAGE] Aguardando antes de buscar fundamentals...")
        time.sleep(3)  # Reduzido de 12s para 3s

        url_overview = f"https://www.alphavantage.co/query"
        params_overview = {
            "function": "OVERVIEW",
            "symbol": symbol,
            "apikey": api_key
        }

        response_overview = requests.get(url_overview, params=params_overview, timeout=10)
        response_overview.raise_for_status()
        overview = response_overview.json()

        # Verificar se houve erro
        if "Error Message" in overview or not overview:
            print(f"[ALPHA VANTAGE] Sem dados fundamentais (overview vazio)")
            fundamentals = {}
        else:
            # Converter overview para formato similar ao yfinance
            fundamentals = _convert_alpha_to_yfinance_format(overview)
            print(f"[ALPHA VANTAGE OK] Dados fundamentais: {len(fundamentals)} campos")

        return {
            'price_history': df,
            'fundamentals': fundamentals,
            'source': 'Alpha Vantage'
        }

    except requests.exceptions.RequestException as e:
        print(f"[ALPHA VANTAGE ERRO] Erro de rede: {e}")
        return None
    except Exception as e:
        print(f"[ALPHA VANTAGE ERRO] {e}")
        return None


def _filter_by_period(df: pd.DataFrame, period: str) -> pd.DataFrame:
    """Filtra DataFrame por período especificado."""
    period_map = {
        '1mo': 30,
        '3mo': 90,
        '6mo': 180,
        '1y': 365,
        '2y': 730,
        '5y': 1825
    }

    days = period_map.get(period, 365)
    cutoff_date = datetime.now() - timedelta(days=days)
    return df[df.index >= cutoff_date]


def _convert_alpha_to_yfinance_format(overview: Dict[str, str]) -> Dict[str, Any]:
    """
    Converte dados do Alpha Vantage OVERVIEW para formato similar ao yfinance.
    """
    def safe_float(value, default=None):
        try:
            return float(value) if value and value != "None" else default
        except (ValueError, TypeError):
            return default

    def safe_int(value, default=None):
        try:
            return int(value) if value and value != "None" else default
        except (ValueError, TypeError):
            return default

    return {
        # Informações básicas
        'symbol': overview.get('Symbol'),
        'shortName': overview.get('Name'),
        'sector': overview.get('Sector'),
        'industry': overview.get('Industry'),
        'country': overview.get('Country'),
        'currency': overview.get('Currency'),
        'exchange': overview.get('Exchange'),

        # Métricas de valuation
        'marketCap': safe_int(overview.get('MarketCapitalization')),
        'trailingPE': safe_float(overview.get('TrailingPE')),
        'forwardPE': safe_float(overview.get('ForwardPE')),
        'priceToBook': safe_float(overview.get('PriceToBookRatio')),
        'enterpriseValue': safe_int(overview.get('MarketCapitalization')),  # Aproximação
        'pegRatio': safe_float(overview.get('PEGRatio')),

        # Métricas financeiras
        'profitMargins': safe_float(overview.get('ProfitMargin')),
        'operatingMargins': safe_float(overview.get('OperatingMarginTTM')),
        'returnOnAssets': safe_float(overview.get('ReturnOnAssetsTTM')),
        'returnOnEquity': safe_float(overview.get('ReturnOnEquityTTM')),

        # Crescimento
        'revenueGrowth': safe_float(overview.get('QuarterlyRevenueGrowthYOY')),
        'earningsGrowth': safe_float(overview.get('QuarterlyEarningsGrowthYOY')),

        # Saúde financeira
        'currentRatio': safe_float(overview.get('CurrentRatio')),
        'debtToEquity': safe_float(overview.get('DebtToEquity')),

        # Dividendos
        'dividendYield': safe_float(overview.get('DividendYield')),
        'payoutRatio': safe_float(overview.get('PayoutRatio')),
        'dividendDate': overview.get('DividendDate'),
        'exDividendDate': overview.get('ExDividendDate'),

        # Preço
        'fiftyTwoWeekHigh': safe_float(overview.get('52WeekHigh')),
        'fiftyTwoWeekLow': safe_float(overview.get('52WeekLow')),
        'beta': safe_float(overview.get('Beta')),

        # Outros
        'sharesOutstanding': safe_int(overview.get('SharesOutstanding')),
        'bookValue': safe_float(overview.get('BookValue')),
        'description': overview.get('Description', ''),

        # Metadata
        '_source': 'Alpha Vantage',
        '_last_update': datetime.now().isoformat()
    }
