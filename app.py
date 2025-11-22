"""
Aplicação de Análise de Mercado Financeiro
Análise Fundamental e Técnica de Ações do S&P 500 e NASDAQ
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time

# Importar módulos customizados
from src.data_collector import DataCollector
from src.technical_analysis import TechnicalAnalyzer
from src.fundamental_analysis import FundamentalAnalyzer
from src.scoring import ScoringSystem
from src.database import DatabaseManager

# Configuração da página
st.set_page_config(
    page_title="Análise de Mercado Financeiro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar session state
if 'analyzed_data' not in st.session_state:
    st.session_state['analyzed_data'] = None
if 'last_update' not in st.session_state:
    st.session_state['last_update'] = None
if 'watchlist' not in st.session_state:
    st.session_state['watchlist'] = []
if 'db' not in st.session_state:
    st.session_state['db'] = DatabaseManager()


def convert_period_to_yfinance(period_str):
    """Converte período selecionado para formato yfinance"""
    period_map = {
        "1 mês": "1mo",
        "3 meses": "3mo",
        "6 meses": "6mo",
        "1 ano": "1y",
        "5 anos": "5y"
    }
    return period_map.get(period_str, "1y")


def convert_index_to_code(index_str):
    """Converte índice selecionado para código interno"""
    index_map = {
        "S&P 500": "SP500",
        "NASDAQ": "NASDAQ",
        "Ambos": "BOTH"
    }
    return index_map.get(index_str, "SP500")


def fetch_and_analyze_stocks(index_code, period, progress_bar=None, status_text=None):
    """
    Busca e analisa ações

    Args:
        index_code: Código do índice (SP500, NASDAQ, BOTH)
        period: Período de análise (formato yfinance)
        progress_bar: Widget de progress bar do Streamlit
        status_text: Widget de texto para status

    Returns:
        DataFrame com análises completas
    """
    # Inicializar componentes
    collector = DataCollector()
    scoring = ScoringSystem(technical_weight=0.4, fundamental_weight=0.6)
    db = st.session_state.get('db')

    # Obter lista de símbolos
    symbols = collector.get_stock_list(index_code)

    results = []
    total = len(symbols)

    for i, symbol in enumerate(symbols):
        # Atualizar progresso
        if progress_bar is not None:
            progress = (i + 1) / total
            progress_bar.progress(progress)

        if status_text is not None:
            status_text.text(f'Analisando {symbol} ({i + 1}/{total})...')

        try:
            # Buscar dados históricos
            historical_data = collector.get_stock_data(symbol, period=period)

            # Buscar dados fundamentais
            stock_info = collector.get_stock_info(symbol)

            # Se temos dados, fazer análise
            if historical_data is not None and stock_info is not None:
                # Calcular pontuação combinada
                analysis = scoring.calculate_combined_score(
                    symbol,
                    historical_data,
                    stock_info
                )
                results.append(analysis)

                # Se esta ação está na watchlist, salvar no histórico
                if db and symbol in st.session_state.get('watchlist', []):
                    save_to_history(db, symbol, analysis, historical_data, stock_info)

        except Exception as e:
            print(f"Erro ao analisar {symbol}: {str(e)}")
            continue

    # Criar DataFrame e ranquear
    if results:
        df = scoring.rank_stocks(results)
        return df
    else:
        return pd.DataFrame()


def save_to_history(db, symbol, analysis, historical_data, stock_info):
    """
    Salva dados de uma ação no histórico do banco de dados

    Args:
        db: Instância do DatabaseManager
        symbol: Símbolo da ação
        analysis: Dicionário com análise completa
        historical_data: DataFrame com dados históricos
        stock_info: Dicionário com informações fundamentais
    """
    try:
        # Preparar dados para salvar
        latest_price = historical_data['Close'].iloc[-1] if not historical_data.empty else None
        latest_open = historical_data['Open'].iloc[-1] if not historical_data.empty else None
        latest_high = historical_data['High'].iloc[-1] if not historical_data.empty else None
        latest_low = historical_data['Low'].iloc[-1] if not historical_data.empty else None
        latest_volume = historical_data['Volume'].iloc[-1] if not historical_data.empty else None

        # Extrair indicadores técnicos
        tech_details = analysis.get('technical_details', {})
        indicators = tech_details.get('indicators', {})

        # Extrair métricas fundamentais
        fund_details = analysis.get('fundamental_details', {})
        fund_analysis = fund_details.get('analysis', {})

        data_to_save = {
            'current_price': latest_price,
            'open_price': latest_open,
            'high_price': latest_high,
            'low_price': latest_low,
            'volume': latest_volume,
            'total_score': analysis.get('combined_score'),
            'technical_score': analysis.get('technical_score'),
            'fundamental_score': analysis.get('fundamental_score'),
            # Indicadores técnicos
            'rsi': indicators.get('RSI'),
            'macd': indicators.get('MACD'),
            'macd_signal': indicators.get('MACD_Signal'),
            'sma_20': indicators.get('SMA_20'),
            'sma_50': indicators.get('SMA_50'),
            'ema_20': indicators.get('EMA_20'),
            'bb_upper': indicators.get('BB_Upper'),
            'bb_lower': indicators.get('BB_Lower'),
            'stoch_k': indicators.get('Stochastic_K'),
            'atr': indicators.get('ATR'),
            # Métricas fundamentais
            'pe_ratio': fund_analysis.get('pe_analysis', {}).get('value'),
            'pb_ratio': fund_analysis.get('pb_analysis', {}).get('value'),
            'dividend_yield': fund_analysis.get('dividend_analysis', {}).get('value'),
            'roe': fund_analysis.get('roe_analysis', {}).get('value'),
            'profit_margin': fund_analysis.get('margin_analysis', {}).get('value'),
            'revenue_growth': fund_analysis.get('growth_analysis', {}).get('revenue_growth'),
            'earnings_growth': fund_analysis.get('growth_analysis', {}).get('earnings_growth'),
            'market_cap': stock_info.get('marketCap'),
            'target_price': stock_info.get('targetMeanPrice')
        }

        # Salvar no banco de dados (substitui se já existe para hoje)
        db.save_stock_data(symbol, data_to_save)

    except Exception as e:
        print(f"Erro ao salvar histórico de {symbol}: {str(e)}")


def create_price_chart(symbol, data):
    """Cria gráfico de preço com médias móveis"""
    fig = go.Figure()

    # Preço de fechamento
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        name='Preço',
        line=dict(color='#1f77b4', width=2)
    ))

    # Médias móveis se disponíveis
    if 'SMA_50' in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['SMA_50'],
            name='SMA 50',
            line=dict(color='orange', width=1, dash='dash')
        ))

    if 'SMA_200' in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['SMA_200'],
            name='SMA 200',
            line=dict(color='red', width=1, dash='dash')
        ))

    # Bandas de Bollinger se disponíveis
    if all(col in data.columns for col in ['BB_Upper', 'BB_Lower', 'BB_Middle']):
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['BB_Upper'],
            name='BB Superior',
            line=dict(color='gray', width=1),
            opacity=0.3
        ))
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['BB_Lower'],
            name='BB Inferior',
            line=dict(color='gray', width=1),
            fill='tonexty',
            opacity=0.3
        ))

    fig.update_layout(
        title=f'{symbol} - Preço e Médias Móveis',
        xaxis_title='Data',
        yaxis_title='Preço (USD)',
        hovermode='x unified',
        height=400
    )

    return fig


def create_indicators_chart(data):
    """Cria gráfico de indicadores técnicos (RSI e MACD)"""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=('RSI', 'MACD')
    )

    # RSI
    if 'RSI' in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['RSI'],
            name='RSI',
            line=dict(color='purple', width=2)
        ), row=1, col=1)

        # Linhas de referência RSI
        fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=1, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=1, col=1)

    # MACD
    if all(col in data.columns for col in ['MACD', 'MACD_Signal', 'MACD_Histogram']):
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['MACD'],
            name='MACD',
            line=dict(color='blue', width=2)
        ), row=2, col=1)

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['MACD_Signal'],
            name='Signal',
            line=dict(color='orange', width=1)
        ), row=2, col=1)

        # Histograma MACD
        colors = ['green' if val >= 0 else 'red' for val in data['MACD_Histogram']]
        fig.add_trace(go.Bar(
            x=data.index,
            y=data['MACD_Histogram'],
            name='Histogram',
            marker_color=colors,
            opacity=0.3
        ), row=2, col=1)

    fig.update_layout(height=500, hovermode='x unified')
    fig.update_yaxes(title_text="RSI", row=1, col=1)
    fig.update_yaxes(title_text="MACD", row=2, col=1)

    return fig


# =======================
# INTERFACE PRINCIPAL
# =======================

# Título principal
st.title("📈 Análise de Mercado Financeiro")
st.markdown("### Acompanhamento de Ações com Maior Potencial de Crescimento")

# Sidebar para configurações
with st.sidebar:
    st.header("⚙️ Configurações")

    # Seleção de índice
    index_selection = st.selectbox(
        "Índice:",
        ["S&P 500", "NASDAQ", "Ambos"]
    )

    # Período de análise
    period_selection = st.selectbox(
        "Período de análise:",
        ["1 mês", "3 meses", "6 meses", "1 ano", "5 anos"],
        index=3
    )

    # Número de ações a mostrar
    top_n = st.slider("Top N ações:", 5, 50, 10)

    # Botão para atualizar dados
    update_button = st.button("🔄 Atualizar Dados", use_container_width=True)

    st.divider()

    # Filtros de análise
    st.subheader("Filtros")
    min_score = st.slider("Pontuação mínima:", 0, 100, 60)

# Processar atualização de dados
if update_button:
    with st.spinner('🔍 Analisando mercado... Isso pode levar alguns minutos.'):
        # Converter seleções
        index_code = convert_index_to_code(index_selection)
        period = convert_period_to_yfinance(period_selection)

        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Buscar e analisar dados
        try:
            analyzed_df = fetch_and_analyze_stocks(
                index_code,
                period,
                progress_bar=progress_bar,
                status_text=status_text
            )

            if not analyzed_df.empty:
                st.session_state['analyzed_data'] = analyzed_df
                st.session_state['last_update'] = datetime.now()
                st.success(f'✅ Análise concluída! {len(analyzed_df)} ações analisadas.')
            else:
                st.error('❌ Nenhum dado foi obtido. Tente novamente mais tarde.')

        except Exception as e:
            st.error(f'❌ Erro durante análise: {str(e)}')

        finally:
            progress_bar.empty()
            status_text.empty()

# Obter dados analisados
analyzed_df = st.session_state.get('analyzed_data')
last_update = st.session_state.get('last_update')

# Abas principais
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Dashboard Principal",
    "📊 Análise Técnica",
    "💼 Análise Fundamental",
    "📋 Watchlist"
])

# ===========================
# TAB 1: Dashboard Principal
# ===========================
with tab1:
    st.header("Visão Geral do Mercado")

    if analyzed_df is not None and not analyzed_df.empty:
        # Filtrar por pontuação mínima
        filtered_df = analyzed_df[analyzed_df['combined_score'] >= min_score]

        # Estatísticas gerais
        buy_count = filtered_df['recommendation'].str.contains('COMPRA', na=False).sum()
        hold_count = filtered_df['recommendation'].str.contains('MANTER', na=False).sum()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="Ações Analisadas",
                value=len(analyzed_df)
            )

        with col2:
            st.metric(
                label="Acima do Filtro",
                value=len(filtered_df)
            )

        with col3:
            st.metric(
                label="Sinais de Compra",
                value=int(buy_count)
            )

        with col4:
            if last_update:
                st.metric(
                    label="Última Atualização",
                    value=last_update.strftime("%H:%M")
                )

        st.divider()

        # Tabela de top ações
        st.subheader(f"Top {top_n} Ações com Maior Potencial")

        # Preparar dados para exibição
        display_df = filtered_df.head(top_n)[[
            'rank', 'symbol', 'name', 'sector',
            'combined_score', 'technical_score', 'fundamental_score',
            'recommendation', 'current_price'
        ]].copy()

        # Renomear colunas
        display_df.columns = [
            'Rank', 'Símbolo', 'Nome', 'Setor',
            'Pontuação', 'Téc.', 'Fund.',
            'Recomendação', 'Preço'
        ]

        # Formatar
        display_df['Pontuação'] = display_df['Pontuação'].round(1)
        display_df['Téc.'] = display_df['Téc.'].round(1)
        display_df['Fund.'] = display_df['Fund.'].round(1)
        display_df['Preço'] = display_df['Preço'].apply(lambda x: f'${x:.2f}' if pd.notna(x) else 'N/A')

        # Exibir tabela
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

        # Download de dados
        st.download_button(
            label="📥 Download CSV",
            data=filtered_df.to_csv(index=False).encode('utf-8'),
            file_name=f'analise_acoes_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
            mime='text/csv'
        )

    else:
        st.info("👋 Bem-vindo! Clique em 'Atualizar Dados' na barra lateral para começar a análise.")

# ===========================
# TAB 2: Análise Técnica
# ===========================
with tab2:
    st.header("Análise Técnica Detalhada")

    if analyzed_df is not None and not analyzed_df.empty:
        # Seletor de ação
        symbols_list = analyzed_df['symbol'].tolist()
        selected_symbol = st.selectbox("Selecione uma ação:", symbols_list, key='tech_symbol')

        if selected_symbol:
            # Buscar dados da ação selecionada
            with st.spinner(f'Carregando dados de {selected_symbol}...'):
                collector = DataCollector()
                tech_analyzer = TechnicalAnalyzer()

                period = convert_period_to_yfinance(period_selection)
                stock_data = collector.get_stock_data(selected_symbol, period=period)

                if stock_data is not None and not stock_data.empty:
                    # Calcular indicadores
                    stock_data = tech_analyzer.calculate_all_indicators(stock_data)
                    signals = tech_analyzer.generate_signals(stock_data)
                    trend_strength = tech_analyzer.calculate_trend_strength(stock_data)

                    # Métricas técnicas
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        latest_rsi = stock_data['RSI'].iloc[-1] if 'RSI' in stock_data.columns else None
                        st.metric(
                            "RSI (14)",
                            f"{latest_rsi:.1f}" if pd.notna(latest_rsi) else "N/A",
                            help="Índice de Força Relativa"
                        )

                    with col2:
                        st.metric(
                            "Força da Tendência",
                            f"{trend_strength:.0f}%" if trend_strength else "N/A",
                            help="0-100: Força da tendência de alta"
                        )

                    with col3:
                        latest_price = stock_data['Close'].iloc[-1]
                        st.metric(
                            "Preço Atual",
                            f"${latest_price:.2f}"
                        )

                    # Sinais de trading
                    st.subheader("Sinais de Trading")
                    signal_cols = st.columns(len(signals) if signals else 1)

                    for idx, (indicator, signal) in enumerate(signals.items()):
                        with signal_cols[idx]:
                            if 'COMPRA' in signal:
                                st.success(f"**{indicator}**\n\n{signal}")
                            elif 'VENDA' in signal:
                                st.error(f"**{indicator}**\n\n{signal}")
                            else:
                                st.info(f"**{indicator}**\n\n{signal}")

                    st.divider()

                    # Gráficos
                    col1, col2 = st.columns([1, 1])

                    with col1:
                        st.plotly_chart(
                            create_price_chart(selected_symbol, stock_data),
                            use_container_width=True
                        )

                    with col2:
                        st.plotly_chart(
                            create_indicators_chart(stock_data),
                            use_container_width=True
                        )

                else:
                    st.error(f"Não foi possível carregar dados para {selected_symbol}")

    else:
        st.info("Faça uma análise primeiro para ver os detalhes técnicos.")

# ===========================
# TAB 3: Análise Fundamental
# ===========================
with tab3:
    st.header("Análise Fundamental Detalhada")

    if analyzed_df is not None and not analyzed_df.empty:
        # Seletor de ação
        symbols_list = analyzed_df['symbol'].tolist()
        selected_symbol = st.selectbox("Selecione uma ação:", symbols_list, key='fund_symbol')

        if selected_symbol:
            # Obter dados da ação selecionada
            stock_row = analyzed_df[analyzed_df['symbol'] == selected_symbol].iloc[0]
            fund_details = stock_row['fundamental_details']

            # Informações básicas
            st.subheader(f"{stock_row['name']} ({selected_symbol})")
            st.write(f"**Setor:** {stock_row['sector']}")
            st.write(f"**Pontuação Fundamental:** {stock_row['fundamental_score']:.1f}/100")
            st.write(f"**Classificação:** {fund_details['rating']}")

            st.divider()

            # Análise detalhada
            analysis = fund_details['analysis']

            # Métricas em colunas
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "P/E Ratio",
                    f"{analysis['pe_analysis']['value']:.2f}" if 'value' in analysis['pe_analysis'] and analysis['pe_analysis']['value'] else "N/A",
                    help=analysis['pe_analysis']['description']
                )
                st.caption(f"Status: {analysis['pe_analysis']['status']}")

            with col2:
                st.metric(
                    "ROE",
                    f"{analysis['roe_analysis']['value']:.1f}%" if 'value' in analysis['roe_analysis'] and analysis['roe_analysis']['value'] else "N/A",
                    help=analysis['roe_analysis']['description']
                )
                st.caption(f"Status: {analysis['roe_analysis']['status']}")

            with col3:
                st.metric(
                    "Margem de Lucro",
                    f"{analysis['margin_analysis']['value']:.1f}%" if 'value' in analysis['margin_analysis'] and analysis['margin_analysis']['value'] else "N/A",
                    help=analysis['margin_analysis']['description']
                )
                st.caption(f"Status: {analysis['margin_analysis']['status']}")

            st.divider()

            # Segunda linha de métricas
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "P/B Ratio",
                    f"{analysis['pb_analysis']['value']:.2f}" if 'value' in analysis['pb_analysis'] and analysis['pb_analysis']['value'] else "N/A",
                    help=analysis['pb_analysis']['description']
                )
                st.caption(f"Status: {analysis['pb_analysis']['status']}")

            with col2:
                st.metric(
                    "Dividend Yield",
                    f"{analysis['dividend_analysis']['value']:.2f}%" if 'value' in analysis['dividend_analysis'] and analysis['dividend_analysis']['value'] else "N/A",
                    help=analysis['dividend_analysis']['description']
                )
                st.caption(f"Status: {analysis['dividend_analysis']['status']}")

            with col3:
                st.metric(
                    "Crescimento",
                    f"{analysis['growth_analysis']['value']:.1f}%" if 'value' in analysis['growth_analysis'] and analysis['growth_analysis']['value'] else "N/A",
                    help=analysis['growth_analysis']['description']
                )
                st.caption(f"Status: {analysis['growth_analysis']['status']}")

    else:
        st.info("Faça uma análise primeiro para ver os detalhes fundamentais.")

# ===========================
# TAB 4: Watchlist
# ===========================
with tab4:
    st.header("📋 Ações em Observação")

    db = st.session_state.get('db')

    # Adicionar ação à watchlist
    col1, col2 = st.columns([3, 1])

    with col1:
        new_stock = st.text_input(
            "Adicionar ação ao watchlist:",
            placeholder="Ex: AAPL",
            key="new_watchlist_stock"
        )

    with col2:
        if st.button("➕ Adicionar", use_container_width=True):
            if new_stock:
                new_stock = new_stock.upper().strip()
                if new_stock not in st.session_state['watchlist']:
                    st.session_state['watchlist'].append(new_stock)
                    # Adicionar ao banco de dados
                    if db:
                        # Tentar obter nome da ação se já analisamos
                        name = None
                        if analyzed_df is not None and new_stock in analyzed_df['symbol'].values:
                            name = analyzed_df[analyzed_df['symbol'] == new_stock].iloc[0]['name']
                        db.add_to_watchlist(new_stock, name)
                    st.success(f"✅ {new_stock} adicionado!")
                    st.rerun()
                else:
                    st.warning(f"{new_stock} já está na watchlist")

    st.divider()

    # Mostrar watchlist
    if st.session_state['watchlist']:
        st.subheader("Suas Ações em Observação")

        # Seletor para período de histórico
        col1, col2 = st.columns([3, 1])
        with col1:
            history_days = st.selectbox(
                "Período de histórico:",
                [7, 14, 30, 60, 90],
                index=2,
                format_func=lambda x: f"Últimos {x} dias",
                key="history_period"
            )

        # Mostrar estatísticas do banco de dados
        if db:
            stats = db.get_statistics()
            with col2:
                st.metric("Registros Históricos", stats['total_records'])

        st.divider()

        # Iterar sobre a watchlist
        for symbol in st.session_state['watchlist']:
            with st.expander(f"📊 {symbol}", expanded=False):
                col1, col2 = st.columns([4, 1])

                with col1:
                    # Se temos dados analisados, mostrar info
                    if analyzed_df is not None and symbol in analyzed_df['symbol'].values:
                        stock_data = analyzed_df[analyzed_df['symbol'] == symbol].iloc[0]
                        st.write(f"**{stock_data['name']}**")
                        st.write(f"Pontuação Atual: {stock_data['combined_score']:.1f} | {stock_data['recommendation']}")
                    else:
                        st.write(f"**{symbol}**")
                        st.caption("Execute 'Atualizar Dados' para ver detalhes")

                with col2:
                    if st.button("🗑️ Remover", key=f"remove_{symbol}"):
                        st.session_state['watchlist'].remove(symbol)
                        if db:
                            db.remove_from_watchlist(symbol)
                        st.rerun()

                # Mostrar histórico se disponível
                if db:
                    history_df = db.get_stock_history(symbol, days=history_days)

                    if not history_df.empty and len(history_df) > 1:
                        st.subheader("Evolução Histórica")

                        # Gráfico de evolução do preço
                        fig = go.Figure()

                        fig.add_trace(go.Scatter(
                            x=history_df['date'],
                            y=history_df['current_price'],
                            mode='lines+markers',
                            name='Preço',
                            line=dict(color='#1f77b4', width=2),
                            marker=dict(size=6)
                        ))

                        fig.update_layout(
                            title=f"Evolução do Preço - {symbol}",
                            xaxis_title="Data",
                            yaxis_title="Preço (USD)",
                            hovermode='x unified',
                            height=300
                        )

                        st.plotly_chart(fig, use_container_width=True)

                        # Gráfico de evolução dos scores
                        fig_scores = go.Figure()

                        fig_scores.add_trace(go.Scatter(
                            x=history_df['date'],
                            y=history_df['total_score'],
                            mode='lines+markers',
                            name='Score Total',
                            line=dict(color='#2ca02c', width=2)
                        ))

                        fig_scores.add_trace(go.Scatter(
                            x=history_df['date'],
                            y=history_df['technical_score'],
                            mode='lines',
                            name='Score Técnico',
                            line=dict(color='#ff7f0e', width=1, dash='dash')
                        ))

                        fig_scores.add_trace(go.Scatter(
                            x=history_df['date'],
                            y=history_df['fundamental_score'],
                            mode='lines',
                            name='Score Fundamental',
                            line=dict(color='#d62728', width=1, dash='dash')
                        ))

                        fig_scores.update_layout(
                            title=f"Evolução dos Scores - {symbol}",
                            xaxis_title="Data",
                            yaxis_title="Score",
                            hovermode='x unified',
                            height=300
                        )

                        st.plotly_chart(fig_scores, use_container_width=True)

                        # Tabela com dados históricos
                        st.subheader("Dados Históricos")

                        # Selecionar colunas mais importantes
                        display_cols = ['date', 'current_price', 'total_score', 'technical_score',
                                       'fundamental_score', 'rsi', 'macd', 'pe_ratio', 'roe']

                        # Filtrar apenas colunas que existem
                        available_cols = [col for col in display_cols if col in history_df.columns]

                        display_df = history_df[available_cols].copy()
                        display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d')

                        # Renomear colunas para português
                        column_names = {
                            'date': 'Data',
                            'current_price': 'Preço',
                            'total_score': 'Score Total',
                            'technical_score': 'Score Técnico',
                            'fundamental_score': 'Score Fundamental',
                            'rsi': 'RSI',
                            'macd': 'MACD',
                            'pe_ratio': 'P/E',
                            'roe': 'ROE (%)'
                        }

                        display_df = display_df.rename(columns=column_names)
                        display_df = display_df.sort_values('Data', ascending=False)

                        st.dataframe(display_df, use_container_width=True, hide_index=True)

                    elif not history_df.empty:
                        st.info(f"Apenas 1 registro de histórico para {symbol}. Execute 'Atualizar Dados' em dias diferentes para ver evolução.")
                    else:
                        st.info(f"Sem histórico para {symbol}. Execute 'Atualizar Dados' para começar a registrar.")

    else:
        st.info("Sua watchlist está vazia. Adicione ações acima para acompanhar sua evolução ao longo do tempo.")

# Footer
st.divider()
st.caption("💡 Dados fornecidos por Yahoo Finance. Esta aplicação é apenas para fins educacionais.")
st.caption("⚠️ Não constitui aconselhamento financeiro. Consulte sempre um profissional qualificado.")
