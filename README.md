# 📈 Análise de Mercado Financeiro

Aplicação web para acompanhar a evolução dos mercados financeiros, realizando análise fundamental e técnica das ações do S&P 500 e NASDAQ, identificando ações com maior potencial de crescimento nos próximos 5 anos.

## 🎯 Funcionalidades

- **Análise Técnica**: RSI, MACD, Médias Móveis, Bandas de Bollinger, Estocástico, ATR
- **Análise Fundamental**: P/E Ratio, P/B Ratio, ROE, Margem de Lucro, Dividend Yield, Crescimento
- **Sistema de Pontuação**: Combina análises técnica e fundamental para ranquear ações
- **Dashboard Interativo**: Interface web amigável construída com Streamlit
- **Watchlist**: Acompanhe suas ações favoritas
- **Atualizações Diárias**: Mantenha-se atualizado com os últimos dados do mercado

## 🚀 Como Começar

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Instalação

1. **Clone ou baixe este repositório**

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

**Nota sobre TA-Lib**: A biblioteca `ta-lib` pode requerer instalação manual em alguns sistemas:

**Windows:**
```bash
# Baixe o arquivo wheel apropriado de:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
pip install TA_Lib‑0.4.XX‑cpXX‑cpXX‑win_amd64.whl
```

**Linux:**
```bash
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
pip install ta-lib
```

**Mac:**
```bash
brew install ta-lib
pip install ta-lib
```

Se encontrar problemas com TA-Lib, você pode comentar a linha correspondente no `requirements.txt` e usar apenas `pandas-ta`.

### Executar a Aplicação

```bash
streamlit run app.py
```

A aplicação será aberta automaticamente no seu navegador em `http://localhost:8501`

## 📖 Como Usar

1. **Selecione o Índice**: Escolha entre S&P 500, NASDAQ ou ambos na barra lateral
2. **Configure o Período**: Selecione o período de análise (1 mês a 5 anos)
3. **Ajuste Filtros**: Defina pontuação mínima e filtros de análise
4. **Atualize Dados**: Clique em "Atualizar Dados" para buscar as informações mais recentes
5. **Analise Resultados**: Visualize as ações ranqueadas e explore os detalhes

### Abas da Aplicação

- **Dashboard Principal**: Visão geral com métricas e top ações
- **Análise Técnica**: Indicadores técnicos detalhados e gráficos
- **Análise Fundamental**: Métricas fundamentais e saúde financeira
- **Watchlist**: Suas ações em observação

## 📊 Indicadores Implementados

### Análise Técnica

- **Médias Móveis**: SMA (20, 50, 200) e EMA (12, 26)
- **RSI**: Índice de Força Relativa
- **MACD**: Convergência/Divergência de Médias Móveis
- **Bandas de Bollinger**: Volatilidade e níveis de preço
- **Estocástico**: Momentum de preço
- **ATR**: Average True Range (volatilidade)

### Análise Fundamental

- **P/E Ratio**: Relação Preço/Lucro
- **P/B Ratio**: Relação Preço/Valor Contábil
- **ROE**: Retorno sobre Patrimônio Líquido
- **Margem de Lucro**: Rentabilidade
- **Dividend Yield**: Taxa de dividendos
- **Crescimento**: Crescimento de receita e lucros

## 🔧 Estrutura do Projeto

```
claude_projects/
│
├── app.py                      # Aplicação principal Streamlit
├── requirements.txt            # Dependências Python
├── README.md                   # Este arquivo
├── CLAUDE.md                   # Documentação para Claude Code
├── .gitignore                  # Arquivos a ignorar no Git
│
├── src/                        # Código fonte
│   ├── __init__.py
│   ├── data_collector.py       # Coleta de dados financeiros
│   ├── technical_analysis.py   # Análise técnica
│   ├── fundamental_analysis.py # Análise fundamental
│   └── scoring.py              # Sistema de pontuação
│
├── data/                       # Dados locais (cache)
├── config/                     # Configurações
└── tests/                      # Testes (futuro)
```

## ⚙️ Personalização

### Ajustar Pesos da Análise

No arquivo `src/scoring.py`, você pode ajustar os pesos da análise técnica vs fundamental:

```python
scoring = ScoringSystem(
    technical_weight=0.4,    # 40% técnica
    fundamental_weight=0.6   # 60% fundamental
)
```

### Adicionar Mais Ações

No arquivo `src/data_collector.py`, expanda as listas `SP500_SYMBOLS` e `NASDAQ_SYMBOLS` com mais símbolos.

## ⚠️ Avisos Importantes

- **Não é aconselhamento financeiro**: Esta aplicação é apenas para fins educacionais
- **Consulte profissionais**: Sempre consulte um consultor financeiro qualificado
- **Dados podem estar desatualizados**: Verifique sempre em fontes oficiais
- **Uso de APIs gratuitas**: Os dados vêm do Yahoo Finance (yfinance) que tem limitações

## 🐛 Solução de Problemas

### Erro ao instalar TA-Lib
Se tiver problemas com TA-Lib, você pode remover essa dependência e usar apenas pandas-ta, que oferece funcionalidades similares.

### Erro "Rate limit exceeded"
O Yahoo Finance tem limites de requisições. Adicione pausas entre as requisições ou use a aplicação com menos frequência.

### Dados não aparecem
Verifique sua conexão com a internet e tente novamente após alguns minutos.

## 🔮 Próximas Funcionalidades

- [ ] Persistência de dados em banco de dados SQLite
- [ ] Alertas por email para oportunidades de compra
- [ ] Backtesting de estratégias
- [ ] Análise de correlação entre ações
- [ ] Exportar relatórios em PDF
- [ ] Integração com mais fontes de dados
- [ ] Machine Learning para previsões

## 📝 Licença

Este projeto é de código aberto e está disponível para uso educacional.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir novas funcionalidades
- Melhorar a documentação
- Submeter pull requests

## 📧 Contato

Para dúvidas ou sugestões, abra uma issue no repositório.

---

**Disclaimer**: Esta ferramenta não constitui aconselhamento de investimento. Invista por sua própria conta e risco.
