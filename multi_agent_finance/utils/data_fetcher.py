"""
Utilitário para buscar dados financeiros de múltiplas fontes com fallback automático.
Suporta: Yahoo Finance (yfinance) -> Alpha Vantage -> Demo Mode
"""
import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
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

# ===================== MAPEAMENTOS SETORIAIS =====================
# ETFs representativos de cada setor (S&P 500 sectors)
SECTOR_ETF_MAP = {
    'Technology': 'XLK',
    'Financial Services': 'XLF',
    'Financials': 'XLF',
    'Healthcare': 'XLV',
    'Consumer Cyclical': 'XLY',
    'Consumer Defensive': 'XLP',
    'Energy': 'XLE',
    'Industrials': 'XLI',
    'Materials': 'XLB',
    'Real Estate': 'XLRE',
    'Utilities': 'XLU',
    'Communication Services': 'XLC',
    'Basic Materials': 'XLB',
}

# Peers por indústria (3-4 empresas representativas)
INDUSTRY_PEERS = {
    'Consumer Electronics': ['AAPL', 'SONY', 'SAMSUNG', 'HPQ'],
    'Software - Infrastructure': ['MSFT', 'ORCL', 'CRM', 'NOW'],
    'Internet Content & Information': ['GOOGL', 'META', 'SNAP', 'PINS'],
    'Internet Retail': ['AMZN', 'BABA', 'JD', 'MELI'],
    'Semiconductors': ['NVDA', 'AMD', 'INTC', 'AVGO'],
    'Auto Manufacturers': ['TSLA', 'TM', 'F', 'GM'],
    'Drug Manufacturers - General': ['JNJ', 'PFE', 'MRK', 'ABBV'],
    'Banks - Diversified': ['JPM', 'BAC', 'WFC', 'C'],
    'Oil & Gas Integrated': ['XOM', 'CVX', 'COP', 'BP'],
    'Discount Stores': ['WMT', 'COST', 'TGT', 'DG'],
    'Beverages - Non-Alcoholic': ['KO', 'PEP', 'MNST', 'KDP'],
    'Credit Services': ['V', 'MA', 'AXP', 'PYPL'],
    'Aerospace & Defense': ['BA', 'LMT', 'RTX', 'NOC'],
    'Software - Application': ['CRM', 'ADBE', 'INTU', 'WDAY'],
    'Specialty Retail': ['HD', 'LOW', 'TJX', 'ROST'],
    'Biotechnology': ['AMGN', 'GILD', 'REGN', 'VRTX'],
    'Telecom Services': ['T', 'VZ', 'TMUS', 'CHTR'],
}

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
            'macro_data': self._fetch_macro_data(),
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
            print(f"[DEMO MODE FORCADO] Gerando dados de demonstracao para {symbol}")
            return self._generate_demo_data(symbol, period)

        print(f"[BUSCA] Buscando dados para {symbol}...")
        print(f"[CONFIG] Alpha Vantage Key configurada: {'SIM' if ALPHA_VANTAGE_KEY else 'NAO'}")

        # ===== TENTATIVA 1: YAHOO FINANCE (padrão) =====
        if not USE_ALPHA_VANTAGE_FIRST:
            print(f"[1/3] Tentando Yahoo Finance...")
            data = self._try_yahoo_finance(symbol, period)
            if data and not data.get('price_history', pd.DataFrame()).empty:
                print(f"[SUCESSO] Dados obtidos via Yahoo Finance")
                return data
            print(f"[FALLBACK] Yahoo Finance falhou, tentando Alpha Vantage...")

        # ===== TENTATIVA 2: ALPHA VANTAGE =====
        if ALPHA_VANTAGE_KEY:
            print(f"[2/3] Tentando Alpha Vantage...")
            data = self._try_alpha_vantage(symbol, period)
            if data and not data.get('price_history', pd.DataFrame()).empty:
                print(f"[SUCESSO] Dados obtidos via Alpha Vantage")
                return data
            print(f"[FALLBACK] Alpha Vantage tambem falhou")
        else:
            print(f"[AVISO] Alpha Vantage API key NAO CONFIGURADA - Configure em Streamlit Cloud Secrets!")

        # ===== TENTATIVA 3: YAHOO FINANCE (se Alpha foi primeiro) =====
        if USE_ALPHA_VANTAGE_FIRST:
            print(f"[3/3] Tentando Yahoo Finance (2a tentativa)...")
            data = self._try_yahoo_finance(symbol, period)
            if data and not data.get('price_history', pd.DataFrame()).empty:
                print(f"[SUCESSO] Dados obtidos via Yahoo Finance (2a tentativa)")
                return data

        # ===== FALLBACK FINAL: DEMO MODE =====
        print(f"[DEMO MODE AUTOMATICO] Todas as APIs falharam, usando dados simulados")
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

            # 3. Sector/Industry data (com peers reais via yfinance)
            data['sector_data'] = self._prepare_sector_data(ticker, data['fundamentals'])

            # 4. Sentiment data (Alpha Vantage NEWS + yfinance analyst ratings)
            data['sentiment'] = self._fetch_sentiment_data(symbol)

            # 5. Macro data (FRED API com fallback para placeholder)
            data['macro_data'] = self._fetch_macro_data()

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
            result['sentiment'] = self._fetch_sentiment_data(symbol)
            result['macro_data'] = self._fetch_macro_data()

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
        """
        Prepara dados setoriais com comparação real de peers via yfinance.
        Busca fundamentals de 3-4 peers da mesma indústria e calcula métricas comparativas.
        """
        sector = fundamentals.get('sector', 'Unknown')
        industry = fundamentals.get('industry', 'Unknown')
        symbol = fundamentals.get('symbol', '')

        sector_data = {
            'sector': sector,
            'industry': industry
        }

        # Tentar buscar dados reais de peers
        try:
            peer_data = self._fetch_peer_comparison(symbol, sector, industry, fundamentals)
            if peer_data:
                sector_data.update(peer_data)
                print(f"[SECTOR OK] Dados de peers obtidos para {symbol}")
            else:
                print(f"[SECTOR AVISO] Sem dados de peers para {symbol}")
        except Exception as e:
            print(f"[SECTOR ERRO] Falha ao buscar peers: {e}")

        # Buscar performance do ETF setorial
        try:
            etf_data = self._fetch_sector_etf_performance(sector)
            if etf_data:
                sector_data['sector_trends'] = etf_data
        except Exception as e:
            print(f"[SECTOR AVISO] Falha ao buscar ETF setorial: {e}")

        return sector_data

    def _fetch_peer_comparison(self, symbol: str, sector: str, industry: str,
                                fundamentals: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Busca e compara fundamentals de peers da mesma indústria."""
        # Encontrar peers
        peers = INDUSTRY_PEERS.get(industry, [])
        if not peers:
            # Fallback: tentar encontrar peers pelo setor
            for ind, peer_list in INDUSTRY_PEERS.items():
                if symbol.upper() in [p.upper() for p in peer_list]:
                    peers = peer_list
                    break

        if not peers:
            return None

        # Remover o próprio símbolo da lista de peers
        peers = [p for p in peers if p.upper() != symbol.upper()][:4]

        if not peers:
            return None

        # Buscar fundamentals dos peers
        peer_fundamentals: List[Dict[str, Any]] = []
        for peer_symbol in peers:
            try:
                self._enforce_rate_limit()
                peer_ticker = yf.Ticker(peer_symbol, session=session)
                peer_info = peer_ticker.info
                if peer_info and peer_info.get('marketCap'):
                    peer_fundamentals.append({
                        'symbol': peer_symbol,
                        'marketCap': peer_info.get('marketCap', 0),
                        'trailingPE': peer_info.get('trailingPE'),
                        'priceToBook': peer_info.get('priceToBook'),
                        'returnOnEquity': peer_info.get('returnOnEquity'),
                        'profitMargins': peer_info.get('profitMargins'),
                        'revenueGrowth': peer_info.get('revenueGrowth'),
                        'debtToEquity': peer_info.get('debtToEquity'),
                    })
                    print(f"[PEER OK] {peer_symbol} dados obtidos")
            except Exception as e:
                print(f"[PEER AVISO] Falha ao buscar {peer_symbol}: {e}")

        if not peer_fundamentals:
            return None

        # Calcular médianas do setor (mais robusta que média para outliers)
        def safe_median(values):
            clean = [v for v in values if v is not None and not pd.isna(v)]
            return float(np.median(clean)) if clean else None

        sector_averages = {
            'pe_ratio': safe_median([p.get('trailingPE') for p in peer_fundamentals]),
            'pb_ratio': safe_median([p.get('priceToBook') for p in peer_fundamentals]),
            'roe': safe_median([p.get('returnOnEquity') for p in peer_fundamentals]),
            'profit_margin': safe_median([p.get('profitMargins') for p in peer_fundamentals]),
            'revenue_growth': safe_median([p.get('revenueGrowth') for p in peer_fundamentals]),
            'debt_to_equity': safe_median([p.get('debtToEquity') for p in peer_fundamentals]),
        }

        # Market position (rank por market cap)
        all_caps = [(symbol, fundamentals.get('marketCap', 0))] + \
                   [(p['symbol'], p['marketCap']) for p in peer_fundamentals]
        all_caps.sort(key=lambda x: x[1] or 0, reverse=True)
        market_rank = next((i + 1 for i, (s, _) in enumerate(all_caps) if s.upper() == symbol.upper()), len(all_caps))

        market_position = {
            'rank': market_rank,
            'total_peers': len(all_caps),
            'is_leader': market_rank == 1,
        }

        # Peer performance YTD (comparar retornos)
        peer_performance = self._calculate_peer_performance(symbol, peers)

        return {
            'peers': [p['symbol'] for p in peer_fundamentals],
            'sector_averages': sector_averages,
            'market_position': market_position,
            'peer_performance': peer_performance,
        }

    def _calculate_peer_performance(self, symbol: str, peers: List[str]) -> Dict[str, Any]:
        """Calcula performance YTD do símbolo vs peers."""
        try:
            all_symbols = [symbol] + peers
            ytd_returns = {}

            for sym in all_symbols:
                try:
                    ticker = yf.Ticker(sym, session=session)
                    hist = ticker.history(period='ytd')
                    if hist is not None and len(hist) >= 2:
                        ytd_return = (hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100
                        ytd_returns[sym] = round(float(ytd_return), 2)
                except Exception:
                    pass

            if not ytd_returns or symbol not in ytd_returns:
                return {}

            symbol_return = ytd_returns[symbol]
            peer_returns = [v for k, v in ytd_returns.items() if k != symbol]

            if not peer_returns:
                return {'symbol_ytd': symbol_return}

            avg_peer_return = float(np.mean(peer_returns))
            # Percentil: que % dos peers a empresa supera
            peers_beaten = sum(1 for r in peer_returns if symbol_return > r)
            percentile = (peers_beaten / len(peer_returns)) * 100

            return {
                'symbol_ytd': symbol_return,
                'peer_avg_ytd': round(avg_peer_return, 2),
                'outperformance': round(symbol_return - avg_peer_return, 2),
                'percentile': round(percentile, 1),
            }
        except Exception as e:
            print(f"[PEER PERF AVISO] Falha ao calcular performance: {e}")
            return {}

    def _fetch_sector_etf_performance(self, sector: str) -> Optional[Dict[str, Any]]:
        """Busca performance do ETF setorial para tendências."""
        etf_symbol = SECTOR_ETF_MAP.get(sector)
        if not etf_symbol:
            return None

        try:
            self._enforce_rate_limit()
            etf = yf.Ticker(etf_symbol, session=session)
            hist = etf.history(period='6mo')

            if hist is None or hist.empty:
                return None

            # Performance em diferentes períodos
            current_price = hist['Close'].iloc[-1]
            result = {'etf_symbol': etf_symbol}

            if len(hist) >= 5:
                result['return_1w'] = round(
                    (current_price / hist['Close'].iloc[-5] - 1) * 100, 2)
            if len(hist) >= 22:
                result['return_1m'] = round(
                    (current_price / hist['Close'].iloc[-22] - 1) * 100, 2)
            if len(hist) >= 66:
                result['return_3m'] = round(
                    (current_price / hist['Close'].iloc[-66] - 1) * 100, 2)

            # Tendência geral
            if 'return_3m' in result:
                if result['return_3m'] > 5:
                    result['trend'] = 'bullish'
                elif result['return_3m'] < -5:
                    result['trend'] = 'bearish'
                else:
                    result['trend'] = 'neutral'

            print(f"[ETF OK] {etf_symbol}: retorno 3M = {result.get('return_3m', 'N/A')}%")
            return result

        except Exception as e:
            print(f"[ETF AVISO] Falha ao buscar {etf_symbol}: {e}")
            return None

    def _fetch_sentiment_data(self, symbol: str) -> Dict[str, Any]:
        """
        Busca dados de sentimento reais de múltiplas fontes:
        1. Alpha Vantage NEWS_SENTIMENT endpoint
        2. yfinance: analyst ratings, target prices
        3. yfinance: insider transactions
        Fallback para estrutura vazia se tudo falhar.
        """
        sentiment = {}

        # 1. News Sentiment via Alpha Vantage
        if ALPHA_VANTAGE_KEY:
            try:
                news_data = self._fetch_news_sentiment(symbol)
                if news_data:
                    sentiment['news'] = news_data
            except Exception as e:
                print(f"[SENTIMENT AVISO] Falha ao buscar news: {e}")

        # 2. Analyst Ratings via yfinance
        try:
            analyst_data = self._fetch_analyst_ratings(symbol)
            if analyst_data:
                sentiment['analyst_ratings'] = analyst_data
        except Exception as e:
            print(f"[SENTIMENT AVISO] Falha ao buscar analyst ratings: {e}")

        # 3. Insider Transactions via yfinance
        try:
            insider_data = self._fetch_insider_trades(symbol)
            if insider_data:
                sentiment['insider_trades'] = insider_data
        except Exception as e:
            print(f"[SENTIMENT AVISO] Falha ao buscar insider trades: {e}")

        if sentiment:
            print(f"[SENTIMENT OK] Dados obtidos: {list(sentiment.keys())}")
        else:
            print(f"[SENTIMENT] Sem dados de sentimento disponíveis para {symbol}")

        return sentiment

    def _fetch_news_sentiment(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Busca sentiment de notícias via Alpha Vantage NEWS_SENTIMENT."""
        try:
            url = (
                f"https://www.alphavantage.co/query"
                f"?function=NEWS_SENTIMENT"
                f"&tickers={symbol}"
                f"&limit=10"
                f"&apikey={ALPHA_VANTAGE_KEY}"
            )
            self._enforce_rate_limit()
            response = session.get(url, timeout=15)
            data = response.json()

            if 'feed' not in data:
                # Pode ser erro de rate limit ou key inválida
                if 'Information' in data or 'Note' in data:
                    print(f"[NEWS] Alpha Vantage limit: {data.get('Information', data.get('Note', ''))}")
                return None

            articles = data['feed']
            if not articles:
                return None

            # Processar artigos
            processed_articles = []
            sentiment_scores = []

            for article in articles[:10]:
                # Buscar sentiment específico do ticker
                ticker_sentiment = None
                for ts in article.get('ticker_sentiment', []):
                    if ts.get('ticker', '').upper() == symbol.upper():
                        ticker_sentiment = ts
                        break

                score = 0.0
                if ticker_sentiment:
                    score = float(ticker_sentiment.get('ticker_sentiment_score', 0))
                else:
                    score = float(article.get('overall_sentiment_score', 0))

                sentiment_scores.append(score)
                processed_articles.append({
                    'title': article.get('title', ''),
                    'source': article.get('source', ''),
                    'time_published': article.get('time_published', ''),
                    'sentiment_score': round(score, 4),
                    'sentiment_label': article.get('overall_sentiment_label', 'Neutral'),
                })

            # Calcular score agregado
            avg_sentiment = float(np.mean(sentiment_scores)) if sentiment_scores else 0.0

            return {
                'articles': processed_articles,
                'avg_sentiment_score': round(avg_sentiment, 4),
                'num_articles': len(processed_articles),
                'overall_sentiment': 'Bullish' if avg_sentiment > 0.15 else (
                    'Bearish' if avg_sentiment < -0.15 else 'Neutral'
                ),
            }

        except Exception as e:
            print(f"[NEWS ERRO] Falha ao buscar news sentiment: {e}")
            return None

    def _fetch_analyst_ratings(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Busca ratings de analistas via yfinance."""
        try:
            ticker = yf.Ticker(symbol, session=session)
            info = ticker.info

            if not info:
                return None

            recommendation_mean = info.get('recommendationMean')
            target_mean = info.get('targetMeanPrice')
            target_high = info.get('targetHighPrice')
            target_low = info.get('targetLowPrice')
            num_analysts = info.get('numberOfAnalystOpinions')
            recommendation_key = info.get('recommendationKey', '')
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')

            if recommendation_mean is None and target_mean is None:
                return None

            result = {}
            if recommendation_mean is not None:
                result['recommendation_mean'] = round(float(recommendation_mean), 2)
                # 1=Strong Buy, 2=Buy, 3=Hold, 4=Sell, 5=Strong Sell
                result['recommendation_label'] = recommendation_key

            if target_mean is not None:
                result['target_mean_price'] = round(float(target_mean), 2)
            if target_high is not None:
                result['target_high_price'] = round(float(target_high), 2)
            if target_low is not None:
                result['target_low_price'] = round(float(target_low), 2)
            if num_analysts is not None:
                result['num_analysts'] = int(num_analysts)

            # Calcular upside/downside potencial
            if current_price and target_mean:
                upside = ((target_mean - current_price) / current_price) * 100
                result['upside_potential'] = round(float(upside), 2)

            print(f"[ANALYST OK] {symbol}: rating={recommendation_key}, target=${target_mean}, analysts={num_analysts}")
            return result

        except Exception as e:
            print(f"[ANALYST AVISO] Falha: {e}")
            return None

    def _fetch_insider_trades(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Busca insider transactions via yfinance.
        Nota: Algumas versões do yfinance podem não suportar este endpoint.
        """
        try:
            ticker = yf.Ticker(symbol, session=session)

            # Tentar diferentes atributos conforme versão do yfinance
            insider_transactions = None
            for attr_name in ['insider_transactions', 'insider_purchases', 'get_insider_transactions']:
                if hasattr(ticker, attr_name):
                    attr = getattr(ticker, attr_name)
                    if callable(attr):
                        insider_transactions = attr()
                    else:
                        insider_transactions = attr
                    if insider_transactions is not None and not (hasattr(insider_transactions, 'empty') and insider_transactions.empty):
                        break
                    insider_transactions = None

            if insider_transactions is None:
                return None

            if hasattr(insider_transactions, 'empty') and insider_transactions.empty:
                return None

            # Analisar últimas transações
            recent = insider_transactions.head(20)

            buys = 0
            sells = 0
            total_buy_value = 0.0
            total_sell_value = 0.0

            for _, tx in recent.iterrows():
                # Tentar diferentes nomes de coluna conforme a versão
                tx_type = ''
                for col in ['Text', 'Transaction', 'transaction', 'text', 'type']:
                    if col in tx.index:
                        tx_type = str(tx[col]).lower()
                        break

                value = 0.0
                for col in ['Value', 'value', 'Total']:
                    if col in tx.index and pd.notna(tx[col]):
                        value = abs(float(tx[col]))
                        break

                if 'purchase' in tx_type or 'buy' in tx_type or 'acquisition' in tx_type:
                    buys += 1
                    total_buy_value += value
                elif 'sale' in tx_type or 'sell' in tx_type or 'disposition' in tx_type:
                    sells += 1
                    total_sell_value += value

            if buys == 0 and sells == 0:
                return None

            total = buys + sells
            buy_ratio = buys / total if total > 0 else 0.5

            if buy_ratio > 0.6:
                insider_sentiment = 'Bullish'
            elif buy_ratio < 0.4:
                insider_sentiment = 'Bearish'
            else:
                insider_sentiment = 'Neutral'

            result = {
                'recent_buys': buys,
                'recent_sells': sells,
                'buy_ratio': round(buy_ratio, 2),
                'total_buy_value': round(total_buy_value, 0),
                'total_sell_value': round(total_sell_value, 0),
                'insider_sentiment': insider_sentiment,
            }

            print(f"[INSIDER OK] {symbol}: buys={buys}, sells={sells}, sentiment={insider_sentiment}")
            return result

        except Exception as e:
            print(f"[INSIDER AVISO] Falha: {e}")
            return None

    def _fetch_sentiment_placeholder(self, symbol: str) -> Dict[str, Any]:
        """Fallback: retorna estrutura vazia quando APIs de sentimento falham."""
        return {}

    def _fetch_macro_data(self) -> Dict[str, Any]:
        """
        Busca dados macroeconómicos reais via FRED API com fallback para placeholder.
        """
        try:
            from utils.fred_helper import fetch_macro_data
            macro_data = fetch_macro_data()
            if macro_data:
                print("[MACRO OK] Dados reais obtidos via FRED API")
                return macro_data
        except ImportError:
            print("[MACRO AVISO] fred_helper não disponível")
        except Exception as e:
            print(f"[MACRO AVISO] Falha ao buscar dados FRED: {e}")

        print("[MACRO] Usando dados placeholder")
        return self._fetch_macro_placeholder()

    def _fetch_macro_placeholder(self) -> Dict[str, Any]:
        """Fallback: dados macroeconómicos estáticos quando FRED API não está disponível."""
        return {
            'interest_rates': {
                'current_rate': 5.25,
                'trend': 'stable',
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
