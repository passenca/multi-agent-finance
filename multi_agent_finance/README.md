# 🤖 Sistema Multi-Agente de Análise Financeira

Sistema avançado de análise de investimentos que utiliza **6 agentes especializados** trabalhando em paralelo para fornecer análises abrangentes de ações e ETFs.

## 📋 Visão Geral

Este sistema implementa uma arquitetura multi-agente onde diferentes "especialistas" analisam aspectos distintos de um ativo financeiro, combinando seus insights numa recomendação final ponderada.

### 🎯 Agentes Especializados

1. **📈 Agente Técnico** - Análise técnica clássica
   - RSI (Relative Strength Index)
   - MACD (Moving Average Convergence Divergence)
   - Médias Móveis (SMA 50/200, EMA 20)
   - Bollinger Bands
   - Análise de volume

2. **📊 Agente Fundamental** - Saúde financeira da empresa
   - Valuation (P/E, P/B, PEG Ratio)
   - Rentabilidade (ROE, ROA, margens)
   - Crescimento (receita, lucros)
   - Saúde financeira (dívida, liquidez)
   - Dividendos

3. **💬 Agente de Sentimento** - Percepção do mercado
   - Análise de notícias financeiras
   - Sentimento em redes sociais
   - Ratings de analistas
   - Insider trading (compras/vendas de executivos)

4. **🌍 Agente Macroeconómico** - Contexto económico
   - Taxas de juro (Fed, BCE)
   - Inflação
   - Crescimento do PIB
   - Emprego
   - Regime de mercado (risk-on/risk-off)

5. **⚠️ Agente de Risco** - Perfil de risco
   - Volatilidade
   - Sharpe Ratio e Sortino Ratio
   - Maximum Drawdown
   - Value at Risk (VaR)
   - Beta vs mercado

6. **🏢 Agente Setorial** - Análise competitiva
   - Comparação com peers
   - Posição de mercado
   - Tendências do setor
   - Performance relativa

## 🏗️ Arquitetura

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

### Como Funciona

1. **Coleta de Dados**: O `DataFetcher` busca dados históricos, fundamentals e outras informações via yfinance
2. **Análise Paralela**: Cada agente analisa os dados de forma independente
3. **Scoring**: Cada agente gera um score de -100 (muito bearish) a +100 (muito bullish)
4. **Combinação**: O orquestrador combina os scores usando pesos configuráveis
5. **Recomendação**: Sistema gera recomendação final: COMPRA FORTE, COMPRA, MANTER, VENDA, VENDA FORTE

## 🚀 Quick Start

### Instalação

```bash
# Clone ou navegue para o diretório
cd multi_agent_finance

# Crie ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instale dependências
pip install -r requirements.txt
```

### Uso Básico

#### 1. Demo Rápido
```bash
python demo.py
```

Analisa Apple (AAPL) com configuração padrão.

#### 2. Analisar Ação Específica
```bash
python demo.py --symbol MSFT
```

#### 3. Comparar Múltiplas Ações
```bash
python demo.py --compare AAPL,MSFT,GOOGL,NVDA
```

#### 4. Modo Interativo
```bash
python demo.py --interactive
```

### Uso Programático

```python
from agents.technical_agent import TechnicalAgent
from agents.fundamental_agent import FundamentalAgent
from agents.risk_agent import RiskAgent
# ... importar outros agentes

from orchestrator.orchestrator import AgentOrchestrator
from utils.data_fetcher import DataFetcher

# 1. Buscar dados
fetcher = DataFetcher()
data = fetcher.fetch_all_data("AAPL", period="1y")

# 2. Inicializar agentes com pesos customizados
agents = [
    TechnicalAgent(weight=1.0),
    FundamentalAgent(weight=1.5),  # Peso maior = mais influência
    RiskAgent(weight=0.8),
    # ... outros agentes
]

# 3. Criar orquestrador
orchestrator = AgentOrchestrator(agents)

# 4. Executar análise
analysis = orchestrator.analyze("AAPL", data)

# 5. Ver resultados
print(f"Recomendação: {analysis['recommendation']}")
print(f"Score: {analysis['combined_score']:.2f}")
print(f"Confiança: {analysis['combined_confidence']:.1%}")
```

## 🎛️ Customização

### Ajustar Pesos dos Agentes

```python
# Perfil conservador (foco em risco e fundamentals)
agents = [
    TechnicalAgent(weight=0.5),
    FundamentalAgent(weight=1.5),
    SentimentAgent(weight=0.3),
    MacroAgent(weight=1.0),
    RiskAgent(weight=1.8),      # Peso alto
    SectorAgent(weight=1.0)
]

# Perfil agressivo (foco em técnica e momentum)
agents = [
    TechnicalAgent(weight=2.0),   # Peso alto
    FundamentalAgent(weight=0.8),
    SentimentAgent(weight=1.5),   # Peso alto
    MacroAgent(weight=0.7),
    RiskAgent(weight=0.5),        # Peso baixo
    SectorAgent(weight=0.8)
]
```

### Desabilitar Agentes

```python
risk_agent = RiskAgent()
risk_agent.disable()  # Agente não será consultado
```

### Criar Agente Personalizado

```python
from agents.base_agent import BaseAgent, AgentInsight

class CustomAgent(BaseAgent):
    def __init__(self, weight=1.0):
        super().__init__(name="Custom Analyst", weight=weight)

    def analyze(self, symbol, data):
        # Sua lógica aqui
        score = 50  # -100 a +100
        confidence = 0.8  # 0 a 1
        reasoning = "Sua explicação"

        return AgentInsight(
            agent_name=self.name,
            score=score,
            confidence=confidence,
            reasoning=reasoning
        )

# Usar
custom = CustomAgent(weight=1.5)
orchestrator.add_agent(custom)
```

## 📊 Interpretação dos Resultados

### Scores
- **+80 a +100**: Muito bullish (COMPRA FORTE)
- **+30 a +79**: Bullish (COMPRA)
- **-29 a +29**: Neutro (MANTER)
- **-79 a -30**: Bearish (VENDA)
- **-100 a -80**: Muito bearish (VENDA FORTE)

### Confiança
- **>80%**: Alta confiança (consenso entre agentes)
- **50-80%**: Confiança moderada
- **<50%**: Baixa confiança (agentes divergentes ou dados insuficientes)

## 🔮 Próximos Passos e Melhorias

### Curto Prazo
- [ ] Adicionar cache de dados para reduzir chamadas à API
- [ ] Implementar logging estruturado
- [ ] Adicionar testes unitários
- [ ] Criar interface web com Streamlit

### Médio Prazo
- [ ] Integrar APIs de notícias (NewsAPI, Alpha Vantage)
- [ ] Adicionar análise de social media (Twitter, Reddit)
- [ ] Implementar dados macro reais (FRED API)
- [ ] Backtesting de estratégias
- [ ] Sistema de alertas (email, Telegram)

### Longo Prazo
- [ ] Machine Learning para otimizar pesos
- [ ] Análise de opções e derivativos
- [ ] Portfolio optimization
- [ ] Análise de criptomoedas
- [ ] Agente de eventos corporativos (earnings, M&A)

## ⚠️ Avisos Importantes

**DISCLAIMER**:
- Este sistema é para fins **educacionais e informativos** apenas
- **NÃO** constitui aconselhamento financeiro
- Sempre faça sua própria pesquisa (DYOR - Do Your Own Research)
- Investimentos em ações envolvem risco de perda de capital
- Performance passada não garante resultados futuros
- Consulte um consultor financeiro certificado para decisões de investimento

## 📚 Recursos e Aprendizado

### Conceitos Implementados
- **Arquitetura Multi-Agente**: Cada agente é autónomo e especializado
- **Ensemble Methods**: Combinação ponderada de múltiplos modelos
- **Separation of Concerns**: Cada módulo tem responsabilidade única
- **Extensibilidade**: Fácil adicionar novos agentes

### Leitura Recomendada
- "A Random Walk Down Wall Street" - Burton Malkiel
- "The Intelligent Investor" - Benjamin Graham
- "Technical Analysis of Financial Markets" - John Murphy
- Papers sobre sentiment analysis em finanças
- Documentação do yfinance e pandas

## 🤝 Contribuições

Contribuições são bem-vindas! Áreas de interesse:
- Novos agentes especializados
- Integração de novas fontes de dados
- Melhorias nos algoritmos de análise
- Testes e documentação
- Casos de uso interessantes

## 📄 Licença

Este projeto é de código aberto para fins educacionais.

## 📧 Contacto

Para dúvidas, sugestões ou feedback sobre este sistema multi-agente.

---

**Construído com Python, yfinance, pandas e numpy**

*"The goal of a successful trader is to make the best trades. Money is secondary." - Alexander Elder*
