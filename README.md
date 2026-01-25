# 🤖 Sistema Multi-Agente de Análise Financeira

Sistema avançado de análise de investimentos que utiliza **6 agentes especializados** trabalhando em paralelo para fornecer análises abrangentes de ações e ETFs.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-red)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-Educational-green)](LICENSE)

## 📋 Visão Geral

Este sistema implementa uma **arquitetura multi-agente** onde diferentes "especialistas" analisam aspectos distintos de um ativo financeiro, combinando seus insights numa recomendação final ponderada e ajustável.

### 🎯 Agentes Especializados

| Agente | Foco | Principais Métricas |
|--------|------|---------------------|
| 📈 **Técnico** | Análise técnica clássica | RSI, MACD, Médias Móveis, Bollinger Bands, Volume |
| 📊 **Fundamental** | Saúde financeira | P/E, P/B, ROE, ROA, Margens, Crescimento, Dividendos |
| 💬 **Sentimento** | Percepção de mercado | Notícias, Social Media, Ratings, Insider Trading |
| 🌍 **Macroeconómico** | Contexto económico | Juros, Inflação, PIB, Emprego, Regime de Mercado |
| ⚠️ **Risco** | Perfil de risco | Volatilidade, Sharpe Ratio, Drawdown, VaR, Beta |
| 🏢 **Setorial** | Análise competitiva | Comparação Peers, Market Share, Tendências Setor |

## 🚀 Quick Start

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Instalação

1. **Clone ou baixe este repositório**

```bash
git clone <seu-repositorio>
cd claude_projects
```

2. **Crie um ambiente virtual (recomendado)**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Instale as dependências**

```bash
pip install -r requirements.txt
```

4. **Configure a API Alpha Vantage (opcional mas recomendado)**

```bash
# Copiar ficheiro de exemplo
cp multi_agent_finance/.env.example multi_agent_finance/.env

# Editar .env e adicionar sua chave
# ALPHA_VANTAGE_KEY=sua_chave_aqui
```

Obter chave gratuita em: [alphavantage.co](https://www.alphavantage.co/support/#api-key)

### Executar a Aplicação

**Interface Web (Streamlit):**
```bash
streamlit run app.py
```

A aplicação abrirá automaticamente em `http://localhost:8501`

**Demo CLI (testes rápidos):**
```bash
# Análise padrão (AAPL)
python multi_agent_finance/demo.py

# Ação específica
python multi_agent_finance/demo.py --symbol MSFT

# Comparar múltiplas ações
python multi_agent_finance/demo.py --compare AAPL,MSFT,GOOGL,NVDA

# Modo interativo
python multi_agent_finance/demo.py --interactive
```

## 🏗️ Arquitetura

### Estrutura do Sistema

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

1. **Coleta de Dados Multi-Fonte**
   - 🥇 Yahoo Finance (yfinance) - fonte primária
   - 🥈 Alpha Vantage API - fallback automático
   - 🥉 Modo Demo - dados simulados (último recurso)

2. **Análise Paralela**
   - Cada agente analisa os dados de forma independente
   - Gera score de **-100** (muito bearish) a **+100** (muito bullish)
   - Calcula nível de confiança (**0** a **1**)

3. **Combinação Inteligente**
   - Orquestrador aplica pesos configuráveis a cada agente
   - Combina scores considerando confiança
   - Gera recomendação final com explicação detalhada

4. **Recomendação Final**
   - **COMPRA FORTE**: Score +80 a +100
   - **COMPRA**: Score +30 a +79
   - **MANTER**: Score -29 a +29
   - **VENDA**: Score -79 a -30
   - **VENDA FORTE**: Score -100 a -80

## 📊 Interface Web (Streamlit)

### Páginas Principais

#### 🔍 Análise Individual
Análise profunda de uma ação específica com:
- Dashboard com métricas-chave
- Insights detalhados de cada agente
- Gráficos de preço e indicadores técnicos
- Recomendação final com nível de confiança

#### 📊 Comparação de Ações
Compare múltiplas ações lado a lado:
- Scores comparativos de todos os agentes
- Gráficos de performance
- Ranking por critérios específicos

### Perfis de Investimento

Ajuste automático de pesos dos agentes conforme seu perfil:

| Perfil | Foco | Melhor Para |
|--------|------|-------------|
| **Conservador** | Risco + Fundamentals | Investidores de longo prazo |
| **Moderado** | Balanceado | Investidores equilibrados |
| **Agressivo** | Técnica + Momentum | Traders ativos |
| **Day Trader** | Técnica + Sentimento | Trading intraday |
| **Personalizado** | Ajuste manual | Total controle |

## 🎛️ Customização

### Ajustar Pesos Programaticamente

```python
from multi_agent_finance.agents.technical_agent import TechnicalAgent
from multi_agent_finance.agents.fundamental_agent import FundamentalAgent
from multi_agent_finance.orchestrator.orchestrator import AgentOrchestrator

# Perfil conservador
agents = [
    TechnicalAgent(weight=0.5),
    FundamentalAgent(weight=1.5),    # Peso maior
    RiskAgent(weight=1.8),            # Peso maior
    # ... outros agentes
]

orchestrator = AgentOrchestrator(agents)
analysis = orchestrator.analyze("AAPL", data)
```

### Criar Agente Personalizado

```python
from multi_agent_finance.agents.base_agent import BaseAgent, AgentInsight

class CustomAgent(BaseAgent):
    def __init__(self, weight=1.0):
        super().__init__(name="Custom Analyst", weight=weight)

    def analyze(self, symbol, data):
        # Sua lógica aqui
        score = 50  # -100 a +100
        confidence = 0.8  # 0 a 1
        reasoning = "Sua explicação detalhada"

        return AgentInsight(
            agent_name=self.name,
            score=score,
            confidence=confidence,
            reasoning=reasoning,
            metrics={"custom_metric": 42}
        )
```

## 📖 Interpretação dos Resultados

### Scores dos Agentes

Cada agente retorna um score entre **-100** e **+100**:
- **Positivo**: Bullish (favorável à compra)
- **Negativo**: Bearish (favorável à venda)
- **Próximo de 0**: Neutro

### Nível de Confiança

Indica a qualidade/completude dos dados:
- **> 80%**: Alta confiança (dados completos, sinais claros)
- **50-80%**: Confiança moderada
- **< 50%**: Baixa confiança (dados incompletos ou sinais divergentes)

### Recomendação Final

Combina scores ponderados de todos os agentes:
- Considera tanto o score quanto a confiança
- Agentes com peso maior têm mais influência
- Resultado é traduzido em recomendação textual

## 📁 Estrutura do Projeto

```
claude_projects/
├── app.py                           # Interface Streamlit (ponto de entrada)
├── multi_agent_finance/             # Sistema multi-agente
│   ├── agents/                      # 6 agentes especializados
│   │   ├── base_agent.py            # Classe base
│   │   ├── technical_agent.py
│   │   ├── fundamental_agent.py
│   │   ├── sentiment_agent.py
│   │   ├── macro_agent.py
│   │   ├── risk_agent.py
│   │   └── sector_agent.py
│   ├── orchestrator/
│   │   └── orchestrator.py          # Combina análises
│   ├── utils/
│   │   ├── data_fetcher.py          # Busca dados (multi-fonte)
│   │   └── alpha_vantage_helper.py  # Helper Alpha Vantage
│   ├── demo.py                      # CLI para testes
│   └── README.md                    # Documentação detalhada
├── requirements.txt                 # Dependências
├── CLAUDE.md                        # Guia para Claude Code
└── README.md                        # Este ficheiro
```

## 🔧 Tecnologias Utilizadas

- **Python 3.8+**: Linguagem principal
- **Streamlit**: Interface web interativa
- **yfinance**: Dados do Yahoo Finance
- **pandas**: Manipulação de dados
- **numpy**: Computação numérica
- **plotly**: Gráficos interativos
- **requests**: Chamadas HTTP (Alpha Vantage)
- **python-dotenv**: Gestão de variáveis de ambiente

## ⚠️ Limitações Conhecidas

1. **APIs Externas**:
   - Yahoo Finance: rate limits não documentados
   - Alpha Vantage: 25 chamadas/dia (plano gratuito)
   - Solução: cache de 6h, delays entre chamadas

2. **Agentes Simulados**:
   - Sentiment Agent: sem integração real com NewsAPI
   - Macro Agent: dados macro simulados (sem FRED API)

3. **Sem Persistência**:
   - Cache apenas em memória
   - Dados perdidos ao reiniciar

4. **Sem Backtesting**:
   - Sistema não testa estratégias historicamente

## 🔮 Roadmap

### Curto Prazo
- [ ] Adicionar testes unitários
- [ ] Implementar logging estruturado
- [ ] Persistência em SQLite
- [ ] Melhorar tratamento de erros

### Médio Prazo
- [ ] Integrar NewsAPI para sentiment real
- [ ] Integrar FRED API para dados macro
- [ ] Sistema de alertas (email/Telegram)
- [ ] Backtesting de estratégias

### Longo Prazo
- [ ] Machine Learning para otimizar pesos
- [ ] Análise de opções e derivativos
- [ ] Portfolio optimization
- [ ] Suporte para criptomoedas

## 🐛 Solução de Problemas

### Erro ao instalar dependências
```bash
# Certifique-se de estar no ambiente virtual
pip install --upgrade pip
pip install -r requirements.txt
```

### Erro "No data found" ou rate limit
- Yahoo Finance tem limites: aguarde alguns minutos
- Configure Alpha Vantage como fallback
- Em último caso, use modo demo

### Aplicação não inicia
```bash
# Verifique se Streamlit está instalado
streamlit --version

# Reinstale se necessário
pip install streamlit --upgrade
```

## 📚 Documentação Adicional

- **[CLAUDE.md](CLAUDE.md)**: Guia completo para desenvolvimento
- **[multi_agent_finance/README.md](multi_agent_finance/README.md)**: Documentação técnica detalhada
- **[DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)**: Guia para deploy no Streamlit Cloud

## ⚠️ Avisos Importantes

**DISCLAIMER**:

Este sistema é para fins **educacionais e informativos** apenas.

- ❌ **NÃO** constitui aconselhamento financeiro
- ❌ **NÃO** garante retornos ou resultados
- ✅ Sempre faça sua própria pesquisa (DYOR)
- ✅ Investimentos envolvem risco de perda de capital
- ✅ Consulte profissionais certificados para decisões de investimento
- ✅ Performance passada não garante resultados futuros

## 🤝 Contribuições

Contribuições são bem-vindas! Áreas de interesse:
- Novos agentes especializados
- Integração de novas fontes de dados
- Melhorias nos algoritmos de análise
- Testes e documentação
- Casos de uso interessantes

## 📝 Licença

Este projeto é de código aberto para fins educacionais.

## 📧 Contacto

Para dúvidas, sugestões ou feedback sobre este sistema multi-agente, abra uma issue no repositório.

---

**Construído com Python, Streamlit, yfinance e muito café ☕**

*"The goal of a successful trader is to make the best trades. Money is secondary."* - Alexander Elder
