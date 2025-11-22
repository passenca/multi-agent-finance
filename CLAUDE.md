# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Aplicação de análise de mercado financeiro que realiza análise técnica e fundamental de ações do S&P 500 e NASDAQ. O sistema identifica e ranqueia ações com maior potencial de crescimento nos próximos 5 anos, utilizando uma interface web interativa construída com Streamlit.

**Stack Tecnológica**: Python, Streamlit, yfinance, pandas, pandas-ta

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
```

### Linting
```bash
# Linting não configurado ainda
# Futuro: flake8 src/ app.py
# Futuro: black src/ app.py
```

## Architecture

### Project Structure

```
claude_projects/
├── app.py                      # Ponto de entrada - Interface Streamlit
├── src/                        # Módulos do sistema
│   ├── data_collector.py       # Busca dados do Yahoo Finance
│   ├── technical_analysis.py   # Calcula indicadores técnicos
│   ├── fundamental_analysis.py # Avalia métricas fundamentais
│   └── scoring.py              # Combina análises e ranqueia ações
├── data/                       # Cache de dados (não versionado)
├── config/                     # Configurações
└── tests/                      # Testes unitários (futuro)
```

### Fluxo de Dados

1. **Coleta** (data_collector.py):
   - Busca lista de ações do S&P 500/NASDAQ
   - Obtém dados históricos via yfinance API
   - Coleta informações fundamentais das empresas

2. **Análise Técnica** (technical_analysis.py):
   - Calcula indicadores: RSI, MACD, SMA, EMA, Bollinger Bands, Stochastic, ATR
   - Gera sinais de compra/venda
   - Calcula força da tendência (0-100)

3. **Análise Fundamental** (fundamental_analysis.py):
   - Avalia P/E Ratio, P/B Ratio, ROE, Margem de Lucro, Dividend Yield
   - Analisa crescimento de receita e lucros
   - Pontua cada métrica individualmente

4. **Pontuação Combinada** (scoring.py):
   - Combina análises técnica (40%) e fundamental (60%)
   - Gera recomendação: COMPRA FORTE/COMPRA/MANTER/VENDA/VENDA FORTE
   - Ranqueia ações por pontuação final

5. **Visualização** (app.py):
   - Interface web com 4 tabs: Dashboard, Análise Técnica, Análise Fundamental, Watchlist
   - Gráficos interativos com plotly
   - Filtros e configurações na sidebar

### Key Design Patterns

**Separation of Concerns**: Cada módulo tem uma responsabilidade específica:
- `DataCollector`: Apenas coleta de dados
- `TechnicalAnalyzer`: Apenas cálculos técnicos
- `FundamentalAnalyzer`: Apenas avaliação fundamental
- `ScoringSystem`: Orquestra as análises e gera ranking

**Configurabilidade**: Os pesos da análise técnica vs fundamental são ajustáveis no ScoringSystem:
```python
ScoringSystem(technical_weight=0.4, fundamental_weight=0.6)
```

**Caching Potencial**: O sistema está preparado para adicionar cache de dados para reduzir chamadas à API do Yahoo Finance.

### Important Dependencies

- **streamlit**: Framework para criar a interface web. Escolhido por ser Python puro e ideal para dashboards de dados.
- **yfinance**: Busca dados financeiros do Yahoo Finance. API gratuita e abrangente.
- **pandas**: Manipulação de dados tabulares. Essencial para séries temporais financeiras.
- **pandas-ta**: Biblioteca de análise técnica. Complementa ou substitui TA-Lib se houver problemas de instalação.
- **plotly**: Gráficos interativos. Preferível ao matplotlib para dashboards web.
- **sqlalchemy**: Preparado para persistência futura (ainda não implementado).

**Nota sobre TA-Lib**: Pode ser problemática de instalar em Windows. Se houver problemas, usar apenas pandas-ta.

## Development Notes

### Convenções de Código

- **Idioma**: Comentários e docstrings em português, código em inglês
- **Type Hints**: Usar quando possível para melhor documentação
- **Docstrings**: Seguir formato Google/NumPy style

### Limitações Conhecidas

1. **Rate Limiting**: Yahoo Finance tem limites de requisições. Adicionar `time.sleep()` entre chamadas.
2. **Dados Limitados**: Símbolos no `data_collector.py` são uma amostra. Expandir conforme necessário.
3. **Sem Persistência**: Dados não são salvos. Cada execução busca tudo novamente. Futuro: adicionar SQLite.
4. **Sem Autenticação**: Aplicação é local. Se hospedar online, adicionar autenticação.

### Próximos Passos Recomendados

1. Implementar cache em SQLite para reduzir chamadas à API
2. Adicionar testes unitários para módulos de análise
3. Implementar watchlist persistente
4. Adicionar sistema de alertas por email
5. Criar scheduler para atualização automática diária
6. Implementar backtesting de estratégias

### Debugging

Para debug, adicionar prints ou usar o Streamlit's `st.write()` para visualizar DataFrames:
```python
st.write("Debug:", df)
```

Para testar módulos individualmente sem Streamlit:
```python
from src.data_collector import DataCollector
collector = DataCollector()
data = collector.get_stock_data("AAPL", period="1y")
print(data.head())
```
