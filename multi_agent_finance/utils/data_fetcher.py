"""
Utilitário para buscar dados financeiros de múltiplas fontes com fallback automático.
Suporta: Yahoo Finance (yfinance) -> Alpha Vantage -> Demo Mode
"""
import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do ficheiro .env
load_dotenv()

# Configurar headers para evitar rate limiting
import requests
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
})

# ===================== CONFIGURAÇÃO =====================
# ALPHA VANTAGE API KEY
# Obter chave gratuita em: https://www.alphavantage.co/support/#api-key
# Suporta tanto ambiente local (.env) como Streamlit Cloud (st.secrets)
def get_alpha_vantage_key():
    """Obtém a chave Alpha Vantage de diferentes fontes."""
    # Tentar primeiro do ambiente local (.env)
    key = os.getenv('ALPHA_VANTAGE_KEY', None)
    if key:
        return key

    # Tentar do Streamlit Cloud Secrets
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'ALPHA_VANTAGE_KEY' in st.secrets:
            return st.secrets['ALPHA_VANTAGE_KEY']
    except:
        pass

    return None

ALPHA_VANTAGE_KEY = get_alpha_vantage_key()

# Modo demo - usar apenas se todas as APIs falharem
DEMO_MODE = False  # Agora só ativa se TUDO falhar

# Modo de prioridade das fontes
USE_ALPHA_VANTAGE_FIRST = False  # True = tenta Alpha primeiro (se tiveres key)

# Configurações de rate limiting
RATE_LIMIT_DELAY = 3.0  # segundos entre chamadas
MAX_RETRIES = 2  # máximo de tentativas (reduzido de 3)
RETRY_BASE_DELAY = 5  # delay base para retry (aumentado de 2)


class DataFetcher:
    """
    Classe para buscar e preparar dados financeiros para análise pelos agentes.
    """

    def __init__(self):
        self.cache = {}
        self.last_call_time = 0  # timestamp da última chamada

    def _generate_demo_data(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """Gera dados de demonstração realistas."""
        print(f"[DEMO MODE] Gerando dados de demonstracao para {symbol}...")

        # Configurações por símbolo
        demo_configs = {
            'AAPL': {'price': 175.0, 'pe': 28.5, 'market_cap': 2.7e12, 'sector': 'Technology', 'beta': 1.2},
            'MSFT': {'price': 370.0, 'pe': 35.2, 'market_cap': 2.8e12, 'sector': 'Technology', 'beta': 1.1},
            'GOOGL': {'price': 140.0, 'pe': 26.8, 'market_cap': 1.8e12, 'sector': 'Technology', 'beta': 1.05},
            'NVDA': {'price': 500.0, 'pe': 75.5, 'market_cap': 1.2e12, 'sector': 'Technology', 'beta': 1.8},
            'TSLA': {'price': 240.0, 'pe': 65.0, 'market_cap': 7.5e11, 'sector': 'Automotive', 'beta': 2.0},
        }

        config = demo_configs.get(symbol, {'price': 100.0, 'pe': 20.0, 'market_cap': 5e11, 'sector': 'Unknown', 'beta': 1.0})

        # Gerar histórico de preços
        days_map = {'1mo': 30, '3mo': 90, '6mo': 180, '1y': 252, '2y': 504, '5y': 1260}
        days = days_map.get(period, 252)

        dates = pd.date_range(end=datetime.now(), periods=days, freq='B')
        base_price = config['price']

        # Simular preços com tendência e volatilidade
        trend = np.linspace(0.8, 1.0, days) * base_price
        volatility = np.random.randn(days) * (base_price * 0.02)
        close_prices = trend + volatility

        # Criar OHLCV
        price_data = pd.DataFrame({
            'Open': close_prices * (1 + np.random.randn(days) * 0.005),
            'High': close_prices * (1 + abs(np.random.randn(days)) * 0.01),
            'Low': close_prices * (1 - abs(np.random.randn(days)) * 0.01),
            'Close': close_prices,
            'Volume': np.random.randint(50e6, 150e6, days)
        }, index=dates)

        # Fundamentals
        fundamentals = {
            'symbol': symbol,
            'shortName': f'{symbol} Inc.',
            'sector': config['sector'],
            'industry': 'Technology Hardware' if config['sector'] == 'Technology' else 'Automotive',
            'marketCap': config['market_cap'],
            'trailingPE': config['pe'],
            'forwardPE': config['pe'] * 0.9,
            'priceToBook': 10.5,
            'returnOnEquity': 0.45,
            'returnOnAssets': 0.22,
            'profitMargins': 0.25,
            'operatingMargins': 0.30,
            'revenueGrowth': 0.08,
            'earningsGrowth': 0.12,
            'currentRatio': 1.1,
            'debtToEquity': 150.0,
            'dividendYield': 0.005,
            'payoutRatio': 0.15,
            'beta': config['beta'],
            'fiftyTwoWeekHigh': base_price * 1.15,
            'fiftyTwoWeekLow': base_price * 0.75,
            'averageVolume': 80e6,
        }

        return {
            'symbol': symbol,
            'price_history': price_data,
            'fundamentals': fundamentals,
            'sector_data': {
                'sector': config['sector'],
                'industry': fundamentals['industry']
            },
            'sentiment': {},
            'macro_data': self._fetch_macro_placeholder(),
            'fetch_timestamp': datetime.now()
        }

    def _enforce_rate_limit(self):
        """Garante que respeitamos o rate limit entre chamadas."""
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time

        if time_since_last_call < RATE_LIMIT_DELAY:
            sleep_time = RATE_LIMIT_DELAY - time_since_last_call
            print(f"[RATE LIMIT] Aguardando {sleep_time:.1f}s para respeitar rate limit...")
            time.sleep(sleep_time)

        self.last_call_time = time.time()

    def _fetch_with_retry(self, func, max_retries=None, base_delay=None):
        """Helper para tentar fetch com retry exponencial."""
        max_retries = max_retries or MAX_RETRIES
        base_delay = base_delay or RETRY_BASE_DELAY

        for attempt in range(max_retries):
            try:
                self._enforce_rate_limit()  # Respeita rate limit antes de cada chamada
                result = func()
                return result, None
            except Exception as e:
                error_msg = str(e)
                # Se for 429 (Too Many Requests), aumenta o delay significativamente
                if "429" in error_msg or "Too Many Requests" in error_msg:
                    if attempt < max_retries - 1:
                        delay = base_delay * 3  # Delay muito maior para 429
                        print(f"[RATE LIMIT 429] Detectado bloqueio. Aguardando {delay}s...")
                        time.sleep(delay)
                    else:
                        return None, e
                elif attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    print(f"[RETRY] Tentativa {attempt+1} falhou. Aguardando {delay}s...")
                    time.sleep(delay)
                else:
                    return None, e
        return None, Exception("Max retries exceeded")

    def fetch_all_data(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """
        Busca todos os dados necessários para análise multi-agente com fallback automático.
        Prioridade: Yahoo Finance -> Alpha Vantage -> Demo Mode

        Args:
            symbol: Símbolo do ativo (ex: "AAPL")
            period: Período de histórico (ex: "1y", "6mo", "2y")

        Returns:
            Dicionário com todos os dados necessários
        """
        # Se modo demo forçado está ativo, retorna dados simulados
        if DEMO_MODE:
            print(f"⚠️ [DEMO MODE FORÇADO] Gerando dados de demonstração para {symbol}")
            return self._generate_demo_data(symbol, period)

        print(f"🔍 Buscando dados para {symbol}...")
        print(f"🔑 Alpha Vantage Key configurada: {'✅ SIM' if ALPHA_VANTAGE_KEY else '❌ NÃO'}")

        # ===== TENTATIVA 1: YAHOO FINANCE (padrão) =====
        if not USE_ALPHA_VANTAGE_FIRST:
            print(f"📊 [1/3] Tentando Yahoo Finance...")
            data = self._try_yahoo_finance(symbol, period)
            if data and not data.get('price_history', pd.DataFrame()).empty:
                print(f"✅ [SUCESSO] Dados obtidos via Yahoo Finance")
                return data
            print(f"⚠️ [FALLBACK] Yahoo Finance falhou, tentando Alpha Vantage...")

        # ===== TENTATIVA 2: ALPHA VANTAGE =====
        if ALPHA_VANTAGE_KEY:
            print(f"📊 [2/3] Tentando Alpha Vantage...")
            data = self._try_alpha_vantage(symbol, period)
            if data and not data.get('price_history', pd.DataFrame()).empty:
                print(f"✅ [SUCESSO] Dados obtidos via Alpha Vantage")
                return data
            print(f"⚠️ [FALLBACK] Alpha Vantage também falhou")
        else:
            print(f"❌ [AVISO] Alpha Vantage API key NÃO CONFIGURADA - Configure em Streamlit Cloud Secrets!")

        # ===== TENTATIVA 3: YAHOO FINANCE (se Alpha foi primeiro) =====
        if USE_ALPHA_VANTAGE_FIRST:
            print(f"📊 [3/3] Tentando Yahoo Finance (2ª tentativa)...")
            data = self._try_yahoo_finance(symbol, period)
            if data and not data.get('price_history', pd.DataFrame()).empty:
                print(f"✅ [SUCESSO] Dados obtidos via Yahoo Finance (2ª tentativa)")
                return data

        # ===== FALLBACK FINAL: DEMO MODE =====
        print(f"⚠️ [DEMO MODE AUTOMÁTICO] Todas as APIs falharam, usando dados simulados")
        return self._generate_demo_data(symbol, period)

    def _try_yahoo_finance(self, symbol: str, period: str) -> Optional[Dict[str, Any]]:
        """Tenta buscar dados do Yahoo Finance."""
        try:
            print(f"[YFINANCE] Tentando buscar dados de {symbol}...")

            data = {
                'symbol': symbol,
                'fetch_timestamp': datetime.now(),
                'source': 'Yahoo Finance'
            }

            # Busca dados básicos do Yahoo Finance com session customizada
            ticker = yf.Ticker(symbol, session=session)

            # 1. Price History (para análise técnica e de risco) com retry
            hist, err = self._fetch_with_retry(lambda: ticker.history(period=period))
            if hist is not None and not hist.empty:
                data['price_history'] = hist
                print(f"[YFINANCE OK] Historico de precos: {len(hist)} dias")
            else:
                print(f"[YFINANCE ERRO] Sem historico de precos: {err}")
                data['price_history'] = pd.DataFrame()
                return None  # Falha crítica se não tem preços

            # 2. Fundamentals (para análise fundamental e setorial) com retry
            info, err = self._fetch_with_retry(lambda: ticker.info)
            if info is not None:
                data['fundamentals'] = info
                print(f"[YFINANCE OK] Dados fundamentals: {len(info)} campos")
            else:
                print(f"[YFINANCE AVISO] Sem fundamentals: {err}")
                data['fundamentals'] = {}

            # 3. Sector/Industry data (para análise setorial)
            data['sector_data'] = self._prepare_sector_data(ticker, data['fundamentals'])

            # 4. Sentiment data (placeholder - requer APIs externas)
            data['sentiment'] = self._fetch_sentiment_placeholder(symbol)

            # 5. Macro data (placeholder - requer APIs externas)
            data['macro_data'] = self._fetch_macro_placeholder()

            return data

        except Exception as e:
            print(f"[YFINANCE ERRO] Falha geral: {e}")
            return None

    def _try_alpha_vantage(self, symbol: str, period: str) -> Optional[Dict[str, Any]]:
        """Tenta buscar dados do Alpha Vantage."""
        try:
            from utils.alpha_vantage_helper import fetch_alpha_vantage_data

            print(f"[ALPHA VANTAGE] Tentando buscar dados de {symbol}...")

            # Tentar importar streamlit para mostrar progresso na interface
            try:
                import streamlit as st
                st.info(f"Buscando dados via Alpha Vantage... (pode demorar alguns segundos)")
            except:
                pass

            result = fetch_alpha_vantage_data(symbol, ALPHA_VANTAGE_KEY, period)

            if not result:
                print(f"[ALPHA VANTAGE] Falhou ao buscar dados")
                try:
                    import streamlit as st
                    st.error(f"Alpha Vantage retornou dados vazios ou erro")
                except:
                    pass
                return None

            # Adicionar campos que faltam para compatibilidade com formato Yahoo Finance
            result['symbol'] = symbol
            result['fetch_timestamp'] = datetime.now()
            result['sector_data'] = self._prepare_sector_data(None, result.get('fundamentals', {}))
            result['sentiment'] = self._fetch_sentiment_placeholder(symbol)
            result['macro_data'] = self._fetch_macro_placeholder()

            return result

        except ImportError as e:
            print(f"[ALPHA VANTAGE ERRO] Módulo alpha_vantage_helper não encontrado: {e}")
            try:
                import streamlit as st
                st.error(f"Erro ao importar alpha_vantage_helper: {e}")
            except:
                pass
            return None
        except Exception as e:
            print(f"[ALPHA VANTAGE ERRO] Falha geral: {e}")
            try:
                import streamlit as st
                st.error(f"Erro ao buscar dados Alpha Vantage: {e}")
            except:
                pass
            return None

    def _prepare_sector_data(self, ticker: Optional[yf.Ticker], fundamentals: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara dados setoriais."""
        sector_data = {
            'sector': fundamentals.get('sector', 'Unknown'),
            'industry': fundamentals.get('industry', 'Unknown')
        }

        # Tenta buscar dados de peers (se disponível)
        # Nota: yfinance não fornece comparação direta com peers
        # Em produção, usaria APIs como FinancialModelingPrep, Alpha Vantage, etc.

        return sector_data

    def _fetch_sentiment_placeholder(self, symbol: str) -> Dict[str, Any]:
        """
        Placeholder para dados de sentimento.

        Em produção, usaria:
        - News API (newsapi.org)
        - Twitter API
        - Reddit API (praw)
        - FinBERT para sentiment analysis
        """
        # Por enquanto retorna estrutura vazia
        # O SentimentAgent usará fallback analysis
        return {}

    def _fetch_macro_placeholder(self) -> Dict[str, Any]:
        """
        Placeholder para dados macroeconómicos.

        Em produção, usaria:
        - FRED API (Federal Reserve Economic Data)
        - World Bank API
        - ECB Statistical Data Warehouse
        """
        # Retorna dados de exemplo para demonstração
        return {
            'interest_rates': {
                'current_rate': 5.25,
                'trend': 'stable',
                'next_meeting_expectation': 'hold'
            },
            'inflation': {
                'current_rate': 3.2,
                'target_rate': 2.0,
                'trend': 'falling'
            },
            'gdp_growth': {
                'growth_rate': 2.4,
                'trend': 'stable'
            },
            'unemployment': {
                'unemployment_rate': 3.8,
                'trend': 'stable'
            },
            'market_regime': {
                'type': 'risk_on',
                'vix': 14.5,
                'yield_curve': 'normal'
            }
        }

    def fetch_multiple_symbols(self, symbols: list, period: str = "1y") -> Dict[str, Dict[str, Any]]:
        """
        Busca dados para múltiplos símbolos.

        Args:
            symbols: Lista de símbolos
            period: Período de histórico

        Returns:
            Dicionário com dados de cada símbolo
        """
        results = {}

        for symbol in symbols:
            try:
                results[symbol] = self.fetch_all_data(symbol, period)
            except Exception as e:
                print(f"Erro ao buscar dados de {symbol}: {e}")
                results[symbol] = None

        return results

    def get_sp500_list(self, limit: Optional[int] = None) -> list:
        """
        Obtém lista de símbolos do S&P 500.

        Args:
            limit: Limita o número de símbolos retornados

        Returns:
            Lista de símbolos
        """
        # Lista simplificada de alguns símbolos populares do S&P 500
        # Em produção, poderia fazer scraping da Wikipedia ou usar API
        sp500_symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',
            'META', 'TSLA', 'BRK-B', 'UNH', 'JNJ',
            'V', 'WMT', 'XOM', 'JPM', 'PG',
            'MA', 'HD', 'CVX', 'ABBV', 'KO',
            'PEP', 'AVGO', 'COST', 'MRK', 'TMO'
        ]

        if limit:
            return sp500_symbols[:limit]

        return sp500_symbols

    def enrich_with_sentiment(self, data: Dict[str, Any], news_data: list = None,
                              social_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enriquece dados existentes com informações de sentimento.

        Use esta função se tiver acesso a APIs de notícias/social media.

        Args:
            data: Dados existentes
            news_data: Lista de notícias com sentiment
            social_data: Dados de redes sociais

        Returns:
            Dados enriquecidos
        """
        if news_data:
            data['sentiment']['news'] = news_data

        if social_data:
            data['sentiment']['social_media'] = social_data

        return data

    def enrich_with_macro(self, data: Dict[str, Any], macro_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enriquece dados com informações macroeconómicas atualizadas.

        Args:
            data: Dados existentes
            macro_data: Dados macroeconómicos

        Returns:
            Dados enriquecidos
        """
        data['macro_data'] = macro_data
        return data


# Exemplo de uso
if __name__ == "__main__":
    fetcher = DataFetcher()

    # Busca dados de uma ação
    data = fetcher.fetch_all_data("AAPL", period="1y")

    print("\n=== Resumo dos dados ===")
    print(f"Símbolo: {data['symbol']}")
    print(f"Preços: {len(data.get('price_history', []))} registros")
    print(f"Setor: {data['fundamentals'].get('sector', 'N/A')}")
    print(f"P/E Ratio: {data['fundamentals'].get('trailingPE', 'N/A')}")
