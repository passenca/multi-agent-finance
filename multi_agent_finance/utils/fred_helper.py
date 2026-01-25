"""
Helper para buscar dados macroeconómicos da FRED API (Federal Reserve Economic Data).
API gratuita com limite de 120 requests/minuto.
Obter chave em: https://fred.stlouisfed.org/docs/api/api_key.html
"""
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import pandas as pd

# Cache simples em memória com TTL
_macro_cache: Dict[str, Any] = {}
_cache_timestamp: Optional[datetime] = None
CACHE_TTL_HOURS = 24  # Dados macro mudam lentamente


def get_fred_api_key() -> Optional[str]:
    """Obtém a chave FRED API de diferentes fontes."""
    key = os.getenv('FRED_API_KEY', None)
    if key:
        return key

    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'FRED_API_KEY' in st.secrets:
            return st.secrets['FRED_API_KEY']
    except Exception:
        pass

    return None


def _is_cache_valid() -> bool:
    """Verifica se o cache ainda é válido."""
    if not _cache_timestamp or not _macro_cache:
        return False
    return (datetime.now() - _cache_timestamp) < timedelta(hours=CACHE_TTL_HOURS)


def _calculate_trend(series: pd.Series, months_back: int = 3) -> str:
    """Calcula tendência comparando valor atual vs N meses atrás."""
    if series is None or series.empty or len(series) < 2:
        return 'unknown'

    current = series.iloc[-1]
    # Aproximar N meses atrás (~22 dias úteis por mês)
    lookback = min(months_back * 22, len(series) - 1)
    previous = series.iloc[-(lookback + 1)]

    if pd.isna(current) or pd.isna(previous):
        return 'unknown'

    diff = current - previous
    threshold = abs(previous) * 0.05  # 5% de variação para considerar mudança

    if diff > threshold:
        return 'rising'
    elif diff < -threshold:
        return 'falling'
    else:
        return 'stable'


def fetch_fred_data(api_key: str) -> Optional[Dict[str, Any]]:
    """
    Busca dados macroeconómicos reais da FRED API.

    Séries buscadas:
    - DFF: Federal Funds Rate (taxa de juro diária)
    - CPIAUCSL: CPI (Consumer Price Index) para calcular inflação YoY
    - A191RL1Q225SBEA: Crescimento real do PIB (trimestral)
    - UNRATE: Taxa de desemprego (mensal)
    - DGS10: Treasury 10-Year yield
    - DGS2: Treasury 2-Year yield (para yield curve spread)
    """
    try:
        from fredapi import Fred
    except ImportError:
        print("[FRED] Biblioteca fredapi não instalada. Execute: pip install fredapi")
        return None

    try:
        fred = Fred(api_key=api_key)
        result = {}

        # Período de busca: último ano para calcular tendências
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)

        # 1. Federal Funds Rate (taxa de juro)
        try:
            dff = fred.get_series('DFF', start_date, end_date)
            if dff is not None and not dff.empty:
                current_rate = float(dff.dropna().iloc[-1])
                result['interest_rates'] = {
                    'current_rate': round(current_rate, 2),
                    'trend': _calculate_trend(dff.dropna()),
                    'series_name': 'Federal Funds Rate'
                }
                print(f"[FRED OK] Taxa de juro: {current_rate:.2f}%")
        except Exception as e:
            print(f"[FRED AVISO] Falha ao buscar DFF: {e}")

        # 2. CPI para calcular inflação YoY
        try:
            cpi_start = end_date - timedelta(days=450)  # Precisa de 13+ meses para YoY
            cpi = fred.get_series('CPIAUCSL', cpi_start, end_date)
            if cpi is not None and len(cpi) >= 12:
                cpi_clean = cpi.dropna()
                current_cpi = float(cpi_clean.iloc[-1])
                # Inflação YoY: (CPI_atual - CPI_12m_atras) / CPI_12m_atras * 100
                cpi_12m_ago = float(cpi_clean.iloc[-13]) if len(cpi_clean) >= 13 else float(cpi_clean.iloc[0])
                inflation_rate = ((current_cpi - cpi_12m_ago) / cpi_12m_ago) * 100
                # Tendência: comparar inflação atual vs 3 meses atrás
                if len(cpi_clean) >= 16:
                    cpi_3m_ago = float(cpi_clean.iloc[-4])
                    cpi_15m_ago = float(cpi_clean.iloc[-16])
                    inflation_3m_ago = ((cpi_3m_ago - cpi_15m_ago) / cpi_15m_ago) * 100
                    if inflation_rate < inflation_3m_ago - 0.2:
                        inf_trend = 'falling'
                    elif inflation_rate > inflation_3m_ago + 0.2:
                        inf_trend = 'rising'
                    else:
                        inf_trend = 'stable'
                else:
                    inf_trend = 'unknown'

                result['inflation'] = {
                    'current_rate': round(inflation_rate, 2),
                    'target_rate': 2.0,
                    'trend': inf_trend
                }
                print(f"[FRED OK] Inflacao YoY: {inflation_rate:.2f}%")
        except Exception as e:
            print(f"[FRED AVISO] Falha ao buscar CPI: {e}")

        # 3. Crescimento real do PIB (trimestral)
        try:
            gdp_start = end_date - timedelta(days=730)  # 2 anos para tendência
            gdp = fred.get_series('A191RL1Q225SBEA', gdp_start, end_date)
            if gdp is not None and not gdp.empty:
                gdp_clean = gdp.dropna()
                current_gdp = float(gdp_clean.iloc[-1])
                result['gdp_growth'] = {
                    'growth_rate': round(current_gdp, 2),
                    'trend': _calculate_trend(gdp_clean, months_back=6)
                }
                print(f"[FRED OK] PIB crescimento: {current_gdp:.2f}%")
        except Exception as e:
            print(f"[FRED AVISO] Falha ao buscar GDP: {e}")

        # 4. Taxa de desemprego (mensal)
        try:
            unrate = fred.get_series('UNRATE', start_date, end_date)
            if unrate is not None and not unrate.empty:
                unrate_clean = unrate.dropna()
                current_unrate = float(unrate_clean.iloc[-1])
                result['unemployment'] = {
                    'unemployment_rate': round(current_unrate, 2),
                    'trend': _calculate_trend(unrate_clean)
                }
                print(f"[FRED OK] Desemprego: {current_unrate:.2f}%")
        except Exception as e:
            print(f"[FRED AVISO] Falha ao buscar UNRATE: {e}")

        # 5. Yield Curve (10Y - 2Y spread)
        try:
            dgs10 = fred.get_series('DGS10', start_date, end_date)
            dgs2 = fred.get_series('DGS2', start_date, end_date)
            if dgs10 is not None and dgs2 is not None:
                dgs10_clean = dgs10.dropna()
                dgs2_clean = dgs2.dropna()
                if not dgs10_clean.empty and not dgs2_clean.empty:
                    yield_10y = float(dgs10_clean.iloc[-1])
                    yield_2y = float(dgs2_clean.iloc[-1])
                    spread = yield_10y - yield_2y

                    if spread < 0:
                        curve_type = 'inverted'
                    elif spread < 0.5:
                        curve_type = 'flat'
                    else:
                        curve_type = 'normal'

                    result['yield_curve'] = {
                        'yield_10y': round(yield_10y, 2),
                        'yield_2y': round(yield_2y, 2),
                        'spread': round(spread, 2),
                        'type': curve_type
                    }
                    print(f"[FRED OK] Yield curve: 10Y={yield_10y:.2f}%, 2Y={yield_2y:.2f}%, spread={spread:.2f}%")
        except Exception as e:
            print(f"[FRED AVISO] Falha ao buscar yield curve: {e}")

        if not result:
            print("[FRED] Nenhum dado obtido com sucesso")
            return None

        return result

    except Exception as e:
        print(f"[FRED ERRO] Falha geral: {e}")
        return None


def fetch_vix() -> Optional[Dict[str, float]]:
    """Busca VIX (índice de volatilidade) via yfinance."""
    try:
        import yfinance as yf
        vix = yf.Ticker('^VIX')
        hist = vix.history(period='3mo')
        if hist is not None and not hist.empty:
            current_vix = float(hist['Close'].iloc[-1])
            avg_vix = float(hist['Close'].mean())
            return {
                'current': round(current_vix, 2),
                'average_3m': round(avg_vix, 2)
            }
    except Exception as e:
        print(f"[VIX AVISO] Falha ao buscar VIX: {e}")
    return None


def fetch_macro_data() -> Optional[Dict[str, Any]]:
    """
    Busca todos os dados macroeconómicos (FRED + VIX).
    Usa cache de 24h para evitar chamadas desnecessárias.

    Returns:
        Dicionário com dados macro formatados para o MacroAgent,
        ou None se não conseguir buscar nenhum dado.
    """
    global _macro_cache, _cache_timestamp

    # Verificar cache
    if _is_cache_valid():
        print("[FRED] Usando dados em cache (válido por 24h)")
        return _macro_cache

    api_key = get_fred_api_key()
    if not api_key:
        print("[FRED] API key não configurada")
        return None

    print("[FRED] Buscando dados macroeconómicos reais...")
    fred_data = fetch_fred_data(api_key)

    if not fred_data:
        return None

    # Buscar VIX separadamente (via yfinance, não precisa de key)
    vix_data = fetch_vix()

    # Montar estrutura compatível com o MacroAgent
    macro_result = {}

    if 'interest_rates' in fred_data:
        macro_result['interest_rates'] = fred_data['interest_rates']

    if 'inflation' in fred_data:
        macro_result['inflation'] = fred_data['inflation']

    if 'gdp_growth' in fred_data:
        macro_result['gdp_growth'] = fred_data['gdp_growth']

    if 'unemployment' in fred_data:
        macro_result['unemployment'] = fred_data['unemployment']

    # Market regime baseado em VIX e yield curve
    market_regime = {'type': 'neutral'}
    if vix_data:
        market_regime['vix'] = vix_data['current']
        if vix_data['current'] < 15:
            market_regime['type'] = 'risk_on'
        elif vix_data['current'] > 25:
            market_regime['type'] = 'risk_off'
        else:
            market_regime['type'] = 'neutral'

    if 'yield_curve' in fred_data:
        market_regime['yield_curve'] = fred_data['yield_curve']['type']
        market_regime['yield_spread'] = fred_data['yield_curve']['spread']
    macro_result['market_regime'] = market_regime

    # Atualizar cache
    _macro_cache = macro_result
    _cache_timestamp = datetime.now()

    return macro_result
