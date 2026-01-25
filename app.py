"""
Interface Web Streamlit para o Sistema Multi-Agente de Análise Financeira
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
from pathlib import Path

# Adiciona o diretório multi_agent_finance ao sys.path
multi_agent_dir = Path(__file__).parent / "multi_agent_finance"
if str(multi_agent_dir) not in sys.path:
    sys.path.insert(0, str(multi_agent_dir))

# Importa módulos locais do submódulo multi_agent_finance
from agents.technical_agent import TechnicalAgent
from agents.fundamental_agent import FundamentalAgent
from agents.sentiment_agent import SentimentAgent
from agents.macro_agent import MacroAgent
from agents.risk_agent import RiskAgent
from agents.sector_agent import SectorAgent
from orchestrator.orchestrator import AgentOrchestrator
from utils.data_fetcher import DataFetcher

# Configuração da página
st.set_page_config(
    page_title="Sistema Multi-Agente - Análise Financeira",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .agent-insight {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border: 1px solid #e0e0e0;
    }
    .recommendation-strong-buy {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .recommendation-buy {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #17a2b8;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .recommendation-hold {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .recommendation-sell {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
        font-weight: bold;
        font-size: 1.2rem;
    }
    </style>
""", unsafe_allow_html=True)


def init_session_state():
    """Inicializa variáveis de sessão."""
    if 'analysis_cache' not in st.session_state:
        st.session_state.analysis_cache = {}
    if 'agent_weights' not in st.session_state:
        st.session_state.agent_weights = {
            'technical': 1.0,
            'fundamental': 1.2,
            'sentiment': 0.8,
            'macro': 0.9,
            'risk': 1.0,
            'sector': 1.0
        }


def render_sidebar():
    """Renderiza sidebar com configurações."""
    with st.sidebar:
        # Menu de navegação no topo
        st.markdown("### 📍 Navegação")
        page = st.radio(
            "Escolha a página:",
            ["🔍 Análise Individual", "📊 Comparação de Ações"],
            label_visibility="collapsed"
        )
        st.markdown("---")
        st.image("https://via.placeholder.com/300x100/1f77b4/ffffff?text=Multi-Agent+System", width='stretch')

        # Status de Configuração das APIs
        from utils.data_fetcher import ALPHA_VANTAGE_KEY
        from utils.fred_helper import get_fred_api_key
        fred_key = get_fred_api_key()

        st.markdown("### 🔑 Status das APIs")
        if ALPHA_VANTAGE_KEY:
            st.success("Alpha Vantage: Configurada")
        else:
            st.error("Alpha Vantage: NÃO configurada")
            with st.expander("Como configurar?"):
                st.markdown("""
                **Para obter dados reais, configure a chave Alpha Vantage:**
                1. Obtenha uma chave gratuita em: [alphavantage.co](https://www.alphavantage.co/support/#api-key)
                2. No Streamlit Cloud: Settings → Secrets
                3. Adicione: `ALPHA_VANTAGE_KEY = "sua_chave"`
                """)

        if fred_key:
            st.success("FRED API: Configurada")
        else:
            st.warning("FRED API: NÃO configurada (dados macro placeholder)")
            with st.expander("Como configurar?"):
                st.markdown("""
                **Para dados macroeconómicos reais, configure a chave FRED:**
                1. Obtenha uma chave gratuita em: [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html)
                2. No Streamlit Cloud: Settings → Secrets
                3. Adicione: `FRED_API_KEY = "sua_chave"`
                """)

        st.markdown("### ⚙️ Configurações")

        # Perfis pré-definidos
        st.markdown("#### 📊 Perfil de Investimento")
        profile = st.selectbox(
            "Escolha um perfil:",
            ["Moderado", "Conservador", "Agressivo", "Day Trader", "Personalizado"]
        )

        if profile == "Conservador":
            st.session_state.agent_weights = {
                'technical': 0.5, 'fundamental': 1.5, 'sentiment': 0.3,
                'macro': 1.2, 'risk': 1.8, 'sector': 1.0
            }
        elif profile == "Moderado":
            st.session_state.agent_weights = {
                'technical': 1.0, 'fundamental': 1.2, 'sentiment': 0.8,
                'macro': 0.9, 'risk': 1.0, 'sector': 1.0
            }
        elif profile == "Agressivo":
            st.session_state.agent_weights = {
                'technical': 2.0, 'fundamental': 0.8, 'sentiment': 1.5,
                'macro': 0.7, 'risk': 0.5, 'sector': 0.8
            }
        elif profile == "Day Trader":
            st.session_state.agent_weights = {
                'technical': 2.5, 'fundamental': 0.3, 'sentiment': 1.8,
                'macro': 0.5, 'risk': 0.4, 'sector': 0.3
            }

        # Ajuste fino dos pesos
        if profile == "Personalizado":
            st.markdown("#### 🎛️ Pesos dos Agentes")

            st.session_state.agent_weights['technical'] = st.slider(
                "📈 Técnico", 0.0, 3.0, st.session_state.agent_weights['technical'], 0.1
            )
            st.session_state.agent_weights['fundamental'] = st.slider(
                "📊 Fundamental", 0.0, 3.0, st.session_state.agent_weights['fundamental'], 0.1
            )
            st.session_state.agent_weights['sentiment'] = st.slider(
                "💬 Sentimento", 0.0, 3.0, st.session_state.agent_weights['sentiment'], 0.1
            )
            st.session_state.agent_weights['macro'] = st.slider(
                "🌍 Macro", 0.0, 3.0, st.session_state.agent_weights['macro'], 0.1
            )
            st.session_state.agent_weights['risk'] = st.slider(
                "⚠️ Risco", 0.0, 3.0, st.session_state.agent_weights['risk'], 0.1
            )
            st.session_state.agent_weights['sector'] = st.slider(
                "🏢 Setorial", 0.0, 3.0, st.session_state.agent_weights['sector'], 0.1
            )

        # Info
        st.markdown("---")
        st.markdown("### ℹ️ Sobre")
        st.info(
            "Sistema multi-agente que combina 6 especialistas para análise "
            "abrangente de investimentos."
        )

        st.warning(
            "⚠️ **AVISO**: Este sistema é educacional. "
            "Não constitui aconselhamento financeiro."
        )

        return page


@st.cache_data(ttl=21600)  # Cache por 6 horas (reduz chamadas à API)
def fetch_stock_data(symbol, period):
    """Busca dados do ativo com cache."""
    fetcher = DataFetcher()
    data = fetcher.fetch_all_data(symbol, period)

    # Adicionar informação de debug sobre a fonte dos dados
    if data:
        source = data.get('source', 'Unknown')
        if source == 'Yahoo Finance':
            st.success(f"Dados obtidos via Yahoo Finance")
        elif source == 'Alpha Vantage':
            st.success(f"Dados obtidos via Alpha Vantage")
        else:
            st.warning(f"Modo DEMO ativo - dados simulados")

    return data


def create_agents(weights):
    """Cria lista de agentes com pesos configurados."""
    return [
        TechnicalAgent(weight=weights['technical']),
        FundamentalAgent(weight=weights['fundamental']),
        SentimentAgent(weight=weights['sentiment']),
        MacroAgent(weight=weights['macro']),
        RiskAgent(weight=weights['risk']),
        SectorAgent(weight=weights['sector'])
    ]


def get_recommendation_class(recommendation):
    """Retorna classe CSS baseada na recomendação."""
    rec_lower = recommendation.lower()
    if 'forte' in rec_lower and 'compra' in rec_lower:
        return 'recommendation-strong-buy'
    elif 'compra' in rec_lower:
        return 'recommendation-buy'
    elif 'manter' in rec_lower:
        return 'recommendation-hold'
    else:
        return 'recommendation-sell'


def render_recommendation_card(analysis):
    """Renderiza card com recomendação principal."""
    rec = analysis['recommendation']
    score = analysis['combined_score']
    confidence = analysis['combined_confidence']

    css_class = get_recommendation_class(rec)

    # Emoji baseado na recomendação
    emoji_map = {
        'COMPRA FORTE': '🟢',
        'COMPRA': '🟢',
        'MANTER': '🟡',
        'VENDA': '🔴',
        'VENDA FORTE': '🔴'
    }
    emoji = emoji_map.get(rec, '⚪')

    st.markdown(
        f'<div class="{css_class}">'
        f'{emoji} RECOMENDAÇÃO: {rec}<br>'
        f'Score: {score:+.2f}/100 | Confiança: {confidence:.0%}'
        f'</div>',
        unsafe_allow_html=True
    )


def render_agent_insights(analysis):
    """Renderiza insights individuais dos agentes."""
    st.markdown("### 🤖 Análises dos Agentes")

    # Cria DataFrame para visualização
    insights_data = []
    for insight in analysis['individual_insights']:
        insights_data.append({
            'Agente': insight['agent_name'],
            'Score': insight['score'],
            'Confiança': insight['confidence'],
            'Análise': insight['reasoning']
        })

    df = pd.DataFrame(insights_data)

    # Gráfico de barras com scores
    fig = go.Figure()

    colors = ['green' if s > 0 else 'red' for s in df['Score']]

    fig.add_trace(go.Bar(
        x=df['Score'],
        y=df['Agente'],
        orientation='h',
        marker=dict(
            color=df['Score'],
            colorscale='RdYlGn',
            cmin=-100,
            cmax=100,
            showscale=True,
            colorbar=dict(title="Score")
        ),
        text=df['Score'].apply(lambda x: f'{x:+.1f}'),
        textposition='outside'
    ))

    fig.update_layout(
        title="Scores dos Agentes",
        xaxis_title="Score (-100 a +100)",
        yaxis_title="",
        height=400,
        xaxis=dict(range=[-100, 100])
    )

    st.plotly_chart(fig, width='stretch')

    # Detalhes de cada agente
    for idx, row in df.iterrows():
        with st.expander(f"📋 {row['Agente']} (Score: {row['Score']:+.2f})"):
            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric("Score", f"{row['Score']:+.2f}/100")
                st.metric("Confiança", f"{row['Confiança']:.0%}")
            with col2:
                st.write("**Análise:**")
                st.write(row['Análise'])


def render_price_chart(data, symbol):
    """Renderiza gráfico de preços."""
    st.markdown("### 📈 Histórico de Preços")

    price_data = data.get('price_history')
    if price_data is None or price_data.empty:
        st.warning("Dados de preço não disponíveis")
        return

    # Candlestick chart
    fig = go.Figure(data=[go.Candlestick(
        x=price_data.index,
        open=price_data['Open'],
        high=price_data['High'],
        low=price_data['Low'],
        close=price_data['Close'],
        name=symbol
    )])

    # Adiciona médias móveis
    if len(price_data) >= 50:
        sma_50 = price_data['Close'].rolling(window=50).mean()
        fig.add_trace(go.Scatter(
            x=price_data.index,
            y=sma_50,
            mode='lines',
            name='SMA 50',
            line=dict(color='orange', width=1)
        ))

    if len(price_data) >= 200:
        sma_200 = price_data['Close'].rolling(window=200).mean()
        fig.add_trace(go.Scatter(
            x=price_data.index,
            y=sma_200,
            mode='lines',
            name='SMA 200',
            line=dict(color='blue', width=1)
        ))

    fig.update_layout(
        title=f"{symbol} - Preços e Médias Móveis",
        yaxis_title="Preço (USD)",
        xaxis_title="Data",
        height=500,
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(fig, width='stretch')

    # Volume
    fig_vol = go.Figure(data=[go.Bar(
        x=price_data.index,
        y=price_data['Volume'],
        name='Volume'
    )])

    fig_vol.update_layout(
        title="Volume",
        yaxis_title="Volume",
        xaxis_title="Data",
        height=200
    )

    st.plotly_chart(fig_vol, width='stretch')


def render_fundamentals(data):
    """Renderiza métricas fundamentais."""
    st.markdown("### 📊 Métricas Fundamentais")

    fundamentals = data.get('fundamentals', {})

    if not fundamentals:
        st.warning("Dados fundamentais não disponíveis")
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        pe = fundamentals.get('trailingPE', 'N/A')
        st.metric("P/E Ratio", f"{pe:.2f}" if isinstance(pe, (int, float)) else pe)

        pb = fundamentals.get('priceToBook', 'N/A')
        st.metric("P/B Ratio", f"{pb:.2f}" if isinstance(pb, (int, float)) else pb)

    with col2:
        roe = fundamentals.get('returnOnEquity', 'N/A')
        st.metric("ROE", f"{roe*100:.2f}%" if isinstance(roe, (int, float)) else roe)

        margin = fundamentals.get('profitMargins', 'N/A')
        st.metric("Margem Lucro", f"{margin*100:.2f}%" if isinstance(margin, (int, float)) else margin)

    with col3:
        rev_growth = fundamentals.get('revenueGrowth', 'N/A')
        st.metric("Crescimento Receita", f"{rev_growth*100:.2f}%" if isinstance(rev_growth, (int, float)) else rev_growth)

        debt_equity = fundamentals.get('debtToEquity', 'N/A')
        st.metric("Debt/Equity", f"{debt_equity:.2f}" if isinstance(debt_equity, (int, float)) else debt_equity)

    with col4:
        div_yield = fundamentals.get('dividendYield', 'N/A')
        st.metric("Dividend Yield", f"{div_yield*100:.2f}%" if isinstance(div_yield, (int, float)) else div_yield)

        market_cap = fundamentals.get('marketCap', 'N/A')
        if isinstance(market_cap, (int, float)):
            market_cap_b = market_cap / 1e9
            st.metric("Market Cap", f"${market_cap_b:.2f}B")
        else:
            st.metric("Market Cap", market_cap)

    # Info adicional
    with st.expander("ℹ️ Informações da Empresa"):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Setor:** {fundamentals.get('sector', 'N/A')}")
            st.write(f"**Indústria:** {fundamentals.get('industry', 'N/A')}")
            st.write(f"**Website:** {fundamentals.get('website', 'N/A')}")
        with col2:
            st.write(f"**Funcionários:** {fundamentals.get('fullTimeEmployees', 'N/A')}")
            st.write(f"**País:** {fundamentals.get('country', 'N/A')}")
            st.write(f"**Exchange:** {fundamentals.get('exchange', 'N/A')}")

        summary = fundamentals.get('longBusinessSummary', '')
        if summary:
            st.write("**Descrição:**")
            st.write(summary)


def page_single_analysis():
    """Página de análise de ação individual."""
    st.markdown('<p class="main-header">🔍 Análise Individual de Ação</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        symbol = st.text_input(
            "Digite o símbolo da ação:",
            value="",
            help="Ex: AAPL, MSFT, GOOGL",
            placeholder="Digite um símbolo..."
        ).upper()

    with col2:
        st.write("")  # Espaçamento
        st.write("")
        analyze_button = st.button("🔍 Analisar", type="primary", width='stretch')

    with col3:
        st.write("")
        st.write("")
        period = st.selectbox("Período", ["1mo", "3mo", "6mo", "1y", "2y"], index=3)

    if analyze_button:
        if not symbol:
            st.warning("⚠️ Por favor, digite um símbolo de ação.")
            return

        with st.spinner(f"🔄 Buscando dados de {symbol}..."):
            try:
                data = fetch_stock_data(symbol, period)

                if data['price_history'].empty:
                    st.error(f"❌ Não foi possível buscar dados para {symbol}")
                    return

            except Exception as e:
                st.error(f"❌ Erro ao buscar dados: {str(e)}")
                return

        with st.spinner("🤖 Executando análise multi-agente..."):
            agents = create_agents(st.session_state.agent_weights)
            orchestrator = AgentOrchestrator(agents)
            analysis = orchestrator.analyze(symbol, data)

        # Renderiza resultados
        st.success(f"✅ Análise de {symbol} concluída!")

        # Card de recomendação
        render_recommendation_card(analysis)

        # Tabs com diferentes visualizações
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Resumo", "📈 Preços", "💼 Fundamentals", "🤖 Agentes"])

        with tab1:
            st.markdown("### 📝 Raciocínio Combinado")
            st.info(analysis['reasoning'])

            # Métricas principais
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Score Combinado", f"{analysis['combined_score']:+.2f}/100")
            with col2:
                st.metric("Confiança", f"{analysis['combined_confidence']:.0%}")
            with col3:
                st.metric("Agentes Consultados", analysis['total_agents'])

            # Gráfico de pizza com distribuição de pesos
            weights = st.session_state.agent_weights
            fig = go.Figure(data=[go.Pie(
                labels=list(weights.keys()),
                values=list(weights.values()),
                hole=.3
            )])
            fig.update_layout(title="Distribuição de Pesos dos Agentes", height=400)
            st.plotly_chart(fig, width='stretch')

        with tab2:
            render_price_chart(data, symbol)

        with tab3:
            render_fundamentals(data)

        with tab4:
            render_agent_insights(analysis)


def page_comparison():
    """Página de comparação de múltiplas ações."""
    st.markdown('<p class="main-header">📊 Comparação de Ações</p>', unsafe_allow_html=True)

    # Input de símbolos
    symbols_input = st.text_input(
        "Digite os símbolos separados por vírgula:",
        value="",
        help="Ex: AAPL,MSFT,GOOGL",
        placeholder="Digite símbolos separados por vírgula..."
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        compare_button = st.button("📊 Comparar", type="primary", width='stretch')
    with col2:
        period = st.selectbox("Período de análise", ["1mo", "3mo", "6mo", "1y", "2y"], index=3)

    if compare_button:
        symbols = [s.strip().upper() for s in symbols_input.split(',') if s.strip()]

        if len(symbols) < 2:
            st.warning("Por favor, digite pelo menos 2 símbolos para comparar.")
            return

        # Limitar número de símbolos para evitar rate limiting
        if len(symbols) > 4:
            st.warning("⚠️ Limite: máximo 4 símbolos por vez para evitar bloqueio da API. Usando os primeiros 4.")
            symbols = symbols[:4]

        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()

        agents = create_agents(st.session_state.agent_weights)
        orchestrator = AgentOrchestrator(agents)

        for i, symbol in enumerate(symbols):
            status_text.text(f"Analisando {symbol}... ({i+1}/{len(symbols)})")

            try:
                data = fetch_stock_data(symbol, period)
                if not data['price_history'].empty:
                    analysis = orchestrator.analyze(symbol, data)
                    results.append({
                        'Símbolo': symbol,
                        'Score': analysis['combined_score'],
                        'Recomendação': analysis['recommendation'],
                        'Confiança': analysis['combined_confidence'],
                        'Setor': data['fundamentals'].get('sector', 'N/A')
                    })
            except Exception as e:
                st.warning(f"Erro ao analisar {symbol}: {str(e)}")

            progress_bar.progress((i + 1) / len(symbols))

        status_text.empty()
        progress_bar.empty()

        if not results:
            st.error("Nenhum resultado obtido.")
            return

        # DataFrame com resultados
        df = pd.DataFrame(results)
        df = df.sort_values('Score', ascending=False)

        st.markdown("### 🏆 Ranking")

        # Gráfico de barras
        fig = px.bar(
            df,
            x='Símbolo',
            y='Score',
            color='Score',
            color_continuous_scale='RdYlGn',
            range_color=[-100, 100],
            text='Score',
            hover_data=['Recomendação', 'Confiança']
        )
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig.update_layout(title="Ranking por Score", height=500)
        st.plotly_chart(fig, width='stretch')

        # Tabela detalhada
        st.markdown("### 📋 Detalhes")

        # Formata DataFrame para exibição
        df_display = df.copy()
        df_display['Score'] = df_display['Score'].apply(lambda x: f"{x:+.2f}")
        df_display['Confiança'] = df_display['Confiança'].apply(lambda x: f"{x:.0%}")
        df_display.index = range(1, len(df_display) + 1)

        st.dataframe(df_display, width='stretch')

        # Download CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"comparacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )


def main():
    """Função principal da aplicação."""
    init_session_state()
    page = render_sidebar()

    if page == "🔍 Análise Individual":
        page_single_analysis()
    else:
        page_comparison()

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "🤖 Sistema Multi-Agente de Análise Financeira | "
        f"Desenvolvido com Streamlit @ Novembro 2025 | {datetime.now().year}"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
