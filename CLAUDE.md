# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sistema multi-agente de análise de mercado financeiro que utiliza **6 agentes especializados** trabalhando em paralelo para fornecer análises abrangentes de ações. O sistema combina análise técnica, fundamental, sentimento, macroeconómica, risco e setorial numa recomendação final ponderada.

**Stack Tecnológica**: Python, Streamlit, yfinance, pandas, numpy, plotly, Alpha Vantage API (opcional)

## Development Commands

### Setup
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual (Windows)
venv\Scripts\activate

# Ativar ambiente virtual (Linux/Mac)
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar API Alpha Vantage (opcional)
# 1. Copiar .env.example para .env
cp multi_agent_finance/.env.example multi_agent_finance/.env
# 2. Editar .env e adicionar a chave da Alpha Vantage
# Obter chave gratuita em: https://www.alphavantage.co/support/#api-key
```

### Running
```bash
# Executar a aplicação Streamlit
streamlit run app.py

# A aplicação abrirá em http://localhost:8501
```

### Testing
```bash
# Testes não implementados ainda
# Futuro: pytest tests/

# Para testar modo demo rápido
python multi_agent_finance/demo.py

# Para análise de ação específica
python multi_agent_finance/demo.py --symbol MSFT

# Para comparar múltiplas ações
python multi_agent_finance/demo.py --compare AAPL,MSFT,GOOGL
```

### Linting
```bash
# Linting não configurado ainda
# Futuro: flake8 multi_agent_finance/ app.py
# Futuro: black multi_agent_finance/ app.py
```

## Architecture

### Project Structure

```
claude_projects/
├── app.py                           # Ponto de entrada - Interface Streamlit
├── multi_agent_finance/             # Sistema multi-agente principal
│   ├── agents/                      # 6 agentes especializados
│   │   ├── base_agent.py            # Classe base para todos os agentes
│   │   ├── technical_agent.py       # Análise técnica (RSI, MACD, etc)
│   │   ├── fundamental_agent.py     # Análise fundamental (P/E, ROE, etc)
│   │   ├── sentiment_agent.py       # Análise de sentimento (notícias, social)
│   │   ├── macro_agent.py           # Análise macroeconómica (juros, inflação)
│   │   ├── risk_agent.py            # Análise de risco (volatilidade, VaR)
│   │   └── sector_agent.py          # Análise setorial (peers, competição)
│   ├── orchestrator/                # Orquestrador dos agentes
│   │   └── orchestrator.py          # Combina insights com pesos ajustáveis
│   ├── utils/                       # Utilitários
│   │   ├── data_fetcher.py          # Busca dados (multi-fonte com fallback)
│   │   └── alpha_vantage_helper.py  # Helper para Alpha Vantage API
│   ├── demo.py                      # Script CLI para testes rápidos
│   └── README.md                    # Documentação do sistema multi-agente
├── src/                             # (Vazio - estrutura antiga removida)
├── data/                            # Cache de dados (não versionado)
├── config/                          # Configurações
├── tests/                           # Testes unitários (futuro)
└── requirements.txt                 # Dependências Python
```

### Arquitetura Multi-Agente

O sistema implementa uma **arquitetura multi-agente** onde 6 especialistas independentes analisam diferentes aspectos de um ativo:

```
┌─────────────────────────────────────────────┐
│          AgentOrchestrator                  │
│   (Combina insights com pesos ajustáveis)   │
└─────────────────────────────────────────────┘
                    ▲
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼────────┐    ┌────────▼────────┐
│ Technical      │    │ Fundamental     │
│ Agent          │    │ Agent           │
└────────────────┘    └─────────────────┘
        │                       │
┌───────▼────────┐    ┌────────▼────────┐
│ Macro Agent    │    │ Sentiment Agent │
└────────────────┘    └─────────────────┘
        │                       │
┌───────▼────────┐    ┌────────▼────────┐
│ Risk Agent     │    │ Sector Agent    │
└────────────────┘    └─────────────────┘
```

### Fluxo de Dados

1. **Coleta de Dados** (data_fetcher.py):
   - **Multi-fonte com fallback automático**:
     - 1º Yahoo Finance (yfinance) - fonte primária
     - 2º Alpha Vantage API - fallback se Yahoo falhar
     - 3º Modo Demo - dados simulados (último recurso)
   - Dados históricos de preços
   - Informações fundamentais (balanços, P/E, ROE, etc)
   - Cache de 6 horas para reduzir chamadas à API

2. **Análise Paralela por Agentes**:

   **📈 Technical Agent** (technical_agent.py):
   - RSI (Relative Strength Index)
   - MACD (Moving Average Convergence Divergence)
   - Médias Móveis (SMA 50/200, EMA 20)
   - Bollinger Bands
   - Volume analysis
   - Score: -100 (muito bearish) a +100 (muito bullish)

   **📊 Fundamental Agent** (fundamental_agent.py):
   - Valuation: P/E Ratio, P/B Ratio, PEG Ratio
   - Rentabilidade: ROE, ROA, margens de lucro
   - Crescimento: receita, lucros YoY
   - Saúde financeira: dívida, liquidez, free cash flow
   - Dividendos: dividend yield, payout ratio

   **💬 Sentiment Agent** (sentiment_agent.py):
   - Análise de notícias financeiras
   - Sentimento em redes sociais
   - Ratings de analistas
   - Insider trading (compras/vendas de executivos)

   **🌍 Macro Agent** (macro_agent.py):
   - Taxas de juro (Fed, BCE)
   - Inflação e expectativas
   - Crescimento do PIB
   - Indicadores de emprego
   - Regime de mercado (risk-on/risk-off)

   **⚠️ Risk Agent** (risk_agent.py):
   - Volatilidade histórica e implícita
   - Sharpe Ratio e Sortino Ratio
   - Maximum Drawdown
   - Value at Risk (VaR)
   - Beta vs mercado

   **🏢 Sector Agent** (sector_agent.py):
   - Comparação com peers do setor
   - Market share e posição competitiva
   - Tendências setoriais
   - Performance relativa

3. **Orquestração** (orchestrator.py):
   - Cada agente gera um `AgentInsight` com:
     - `score`: -100 a +100
     - `confidence`: 0 a 1
     - `reasoning`: explicação textual
   - Orquestrador combina scores usando **pesos configuráveis**
   - Gera recomendação final: COMPRA FORTE / COMPRA / MANTER / VENDA / VENDA FORTE

4. **Visualização** (app.py):
   - **2 páginas principais**:
     - 🔍 Análise Individual: análise profunda de uma ação
     - 📊 Comparação de Ações: comparar múltiplas ações lado a lado
   - **Perfis de investimento pré-definidos**:
     - Conservador (foco em risco e fundamentals)
     - Moderado (balanceado)
     - Agressivo (foco em técnica e momentum)
     - Day Trader (técnica e sentimento)
     - Personalizado (ajuste manual de pesos)
   - Gráficos interativos com Plotly
   - Insights detalhados de cada agente

### Key Design Patterns

**Multi-Agent Architecture**:
- Cada agente é autónomo e especializado numa área
- Agentes não comunicam entre si (paralelos)
- Orquestrador central combina insights

**Separation of Concerns**:
- `BaseAgent`: Interface comum para todos os agentes
- `DataFetcher`: Apenas responsável por buscar dados
- `AgentOrchestrator`: Apenas responsável por combinar análises
- Cada agente: Apenas responsável pela sua área de especialização

**Configurabilidade e Extensibilidade**:
```python
# Pesos ajustáveis por perfil de investidor
agents = [
    TechnicalAgent(weight=1.0),      # Peso padrão
    FundamentalAgent(weight=1.5),    # Peso maior = mais influência
    SentimentAgent(weight=0.8),
    MacroAgent(weight=0.9),
    RiskAgent(weight=1.0),
    SectorAgent(weight=1.0)
]

# Fácil adicionar novos agentes
class CustomAgent(BaseAgent):
    def analyze(self, symbol, data):
        # Sua lógica aqui
        return AgentInsight(...)
```

**Fallback Strategy**:
- Prioridade: Yahoo Finance → Alpha Vantage → Demo Mode
- Evita falhas totais se uma API estiver indisponível
- Rate limiting configurável (3s delay entre chamadas)

### Important Dependencies

- **streamlit**: Framework para interface web. Escolhido por simplicidade e ideal para dashboards.
- **yfinance**: API gratuita do Yahoo Finance. Fonte primária de dados.
- **pandas**: Manipulação de dados tabulares. Essencial para séries temporais.
- **numpy**: Computação numérica. Usado para cálculos estatísticos.
- **plotly**: Gráficos interativos. Preferível ao matplotlib para web.
- **requests**: Para chamadas HTTP (Alpha Vantage API).
- **python-dotenv**: Gestão de variáveis de ambiente (.env files).

**Nota sobre Alpha Vantage**:
- API opcional (fallback se Yahoo Finance falhar)
- Gratuita com limite de 25 chamadas/dia (plano compact)
- Configurar via `.env` ou Streamlit Cloud Secrets

## Development Notes

### Convenções de Código

- **Idioma**: Comentários e docstrings em português, código em inglês
- **Type Hints**: Usar quando possível para melhor documentação
- **Docstrings**: Seguir formato Google/NumPy style
- **Agentes**: Todos herdam de `BaseAgent` e implementam `analyze()`

### Limitações Conhecidas

1. **Rate Limiting APIs**:
   - Yahoo Finance: limites não documentados mas existem
   - Alpha Vantage: 25 chamadas/dia (plano gratuito compact)
   - Solução: delay de 3s entre chamadas, cache de 6h

2. **Modo Demo**:
   - Dados simulados quando APIs falham
   - Útil para testes mas não reflete mercado real

3. **Sem Persistência**:
   - Cache apenas em memória (st.session_state)
   - Dados perdidos ao reiniciar aplicação
   - Futuro: SQLite ou Redis

4. **Agentes Limitados**:
   - Sentiment Agent: sem integração real com notícias (NewsAPI)
   - Macro Agent: dados macroeconómicos simulados (sem FRED API)
   - Futuro: integrar APIs reais

5. **Sem Backtesting**:
   - Sistema não testa estratégias historicamente
   - Futuro: implementar engine de backtesting

### Configuração de APIs

**Alpha Vantage (opcional mas recomendado):**

1. Obter chave gratuita: https://www.alphavantage.co/support/#api-key
2. **Ambiente local**:
   - Copiar `multi_agent_finance/.env.example` para `multi_agent_finance/.env`
   - Adicionar: `ALPHA_VANTAGE_KEY=sua_chave_aqui`
3. **Streamlit Cloud**:
   - Settings → Secrets
   - Adicionar: `ALPHA_VANTAGE_KEY = "sua_chave_aqui"`

O sistema detecta automaticamente a chave em ambos os ambientes.

### Próximos Passos Recomendados

#### Curto Prazo
1. ✅ Atualizar documentação (CLAUDE.md, README)
2. ⏳ Adicionar testes unitários básicos
3. ⏳ Implementar logging estruturado
4. ⏳ Persistência de cache em SQLite

#### Médio Prazo
1. Integrar NewsAPI para sentiment real
2. Integrar FRED API para dados macro reais
3. Adicionar sistema de alertas (email, Telegram)
4. Backtesting de estratégias

#### Longo Prazo
1. Machine Learning para otimizar pesos dos agentes
2. Análise de opções e derivativos
3. Portfolio optimization
4. Suporte para criptomoedas

### Debugging

**Para debug na interface Streamlit:**
```python
st.write("Debug:", variable)
st.json(data_dict)  # Para dicionários
```

**Para testar agentes individualmente:**
```python
from multi_agent_finance.agents.technical_agent import TechnicalAgent
from multi_agent_finance.utils.data_fetcher import DataFetcher

# Buscar dados
fetcher = DataFetcher()
data = fetcher.fetch_all_data("AAPL", period="1y")

# Testar agente
agent = TechnicalAgent()
insight = agent.analyze("AAPL", data)
print(f"Score: {insight.score}")
print(f"Reasoning: {insight.reasoning}")
```

**Para testar via CLI:**
```bash
# Demo rápido (AAPL)
python multi_agent_finance/demo.py

# Ação específica
python multi_agent_finance/demo.py --symbol TSLA

# Comparação
python multi_agent_finance/demo.py --compare AAPL,MSFT,GOOGL,NVDA

# Modo interativo
python multi_agent_finance/demo.py --interactive
```

### Estrutura de Dados

**AgentInsight** (retornado por cada agente):
```python
@dataclass
class AgentInsight:
    agent_name: str           # Nome do agente
    score: float              # -100 a +100
    confidence: float         # 0 a 1
    reasoning: str            # Explicação textual
    metrics: Dict[str, Any]   # Métricas específicas do agente
```

**Análise Final** (retornada pelo orquestrador):
```python
{
    'symbol': 'AAPL',
    'combined_score': 45.2,           # Score ponderado final
    'combined_confidence': 0.75,      # Confiança média
    'recommendation': 'COMPRA',       # Recomendação textual
    'agent_insights': [...]           # Lista de AgentInsights
}
```

## Common Tasks

### Adicionar um Novo Agente

1. Criar ficheiro em `multi_agent_finance/agents/new_agent.py`
2. Herdar de `BaseAgent`
3. Implementar método `analyze()`
4. Adicionar ao orquestrador em `app.py`

```python
from agents.base_agent import BaseAgent, AgentInsight

class NewAgent(BaseAgent):
    def __init__(self, weight=1.0):
        super().__init__(name="New Analyst", weight=weight)

    def analyze(self, symbol, data):
        # Sua lógica aqui
        score = 0  # Calcular score -100 a +100
        confidence = 0.5  # Calcular confiança 0 a 1
        reasoning = "Sua explicação"

        return AgentInsight(
            agent_name=self.name,
            score=score,
            confidence=confidence,
            reasoning=reasoning,
            metrics={}
        )
```

### Ajustar Pesos dos Agentes

Editar em `app.py` nos perfis pré-definidos ou permitir ajuste via sidebar.

### Adicionar Nova Fonte de Dados

Editar `multi_agent_finance/utils/data_fetcher.py` e adicionar método de fallback.

## Deployment

### Streamlit Cloud

A aplicação está preparada para deploy no Streamlit Cloud:

1. `app.py` na raiz do repositório ✅
2. `requirements.txt` na raiz ✅
3. Secrets configurados via dashboard (ALPHA_VANTAGE_KEY)
4. `sys.path` configurado para importar `multi_agent_finance/`

### Local

```bash
streamlit run app.py
```

## Avisos Importantes

⚠️ **DISCLAIMER**:
- Este sistema é para fins **educacionais e informativos** apenas
- **NÃO** constitui aconselhamento financeiro
- Sempre faça sua própria pesquisa (DYOR)
- Investimentos envolvem risco de perda de capital
- Consulte profissionais certificados para decisões de investimento
