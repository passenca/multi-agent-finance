# Histórico da Sessão - Criação da Aplicação de Análise Financeira

**Data:** 2 de Novembro de 2025
**Projeto:** Analisador de Ações S&P 500 e NASDAQ

---

## 📋 Resumo do Projeto

Criamos uma aplicação web completa para análise de ações usando:
- **Interface:** Streamlit (Python)
- **Dados:** Yahoo Finance via yahooquery
- **Análise Técnica:** 7 indicadores (RSI, MACD, SMA, EMA, Bollinger Bands, Stochastic, ATR)
- **Análise Fundamental:** 9 métricas (P/E, P/B, ROE, Margins, etc.)
- **Sistema de Scoring:** 40% técnica + 60% fundamental

---

## 🛠️ O Que Foi Criado

### Estrutura de Arquivos:
```
claude_projects/
├── src/
│   ├── data_collector.py         # Coleta de dados do Yahoo Finance
│   ├── technical_analysis.py     # Indicadores técnicos
│   ├── fundamental_analysis.py   # Métricas fundamentais
│   └── scoring.py                # Sistema de pontuação
├── app.py                        # Interface Streamlit (arquivo principal)
├── requirements.txt              # Dependências do projeto
├── test_ssl.py                   # Script de teste
├── test_direct_api.py            # Teste de API direto
├── .streamlit/config.toml        # Configurações Streamlit
├── CLAUDE.md                     # Documentação técnica
└── README.md                     # Guia do usuário
```

---

## 🐛 Problemas Encontrados e Soluções

### Problema 1: Erro de Cache do Streamlit
**Erro:** `Cannot hash argument 'progress_callback' (of type builtins.function)`

**Causa:** Streamlit não conseguia fazer cache de funções com callbacks

**Solução:**
- Removido decorator `@st.cache_data` da função `fetch_and_analyze_stocks()`
- Mudado de callback para passar widgets diretamente (`progress_bar`, `status_text`)
- Arquivo modificado: `app.py` (linhas 58-116)

### Problema 2: SSL Certificate com Caracteres Especiais (PRINCIPAL)
**Erro:** `Failed to perform, curl: (77) error setting certificate verify locations`

**Causa:** Character "ç" em "Paulo Assenção" quebrava o path do certificado SSL no yfinance

**Tentativas que NÃO funcionaram:**
1. Configurar variáveis SSL (`CURL_CA_BUNDLE=''`, etc.)
2. Modificar contexto SSL com `ssl._create_unverified_context`
3. Desinstalar curl_cffi
4. Downgrade yfinance 0.2.66 → 0.2.37 → 0.2.28

**Solução que FUNCIONOU:**
- Migração completa de **yfinance** para **yahooquery**
- yahooquery respeita o parâmetro `verify=False` corretamente
- Arquivo reescrito: `src/data_collector.py` (274 linhas)

**Teste confirmado:**
```
Testando AAPL...
[SUCESSO] Dados obtidos com sucesso!
Número de registros: 4
Último preço: $270.37
```

### Problema 3: Incompatibilidade NumPy
**Erro:** `ImportError: Numba needs NumPy 2.2 or less. Got NumPy 2.3.`

**Causa:** pandas-ta usa Numba que não suporta NumPy 2.3+

**Solução:**
```bash
pip install "numpy<2.3"
```
- NumPy downgraded: 2.3.4 → 2.2.6
- Adicionado constraint em requirements.txt: `numpy<2.3`

### Problema 4: Configuração Streamlit Obsoleta
**Aviso:** `"general.email" is not a valid config option`

**Solução:**
- Removido seção `[general]` de `.streamlit/config.toml`
- Mantido apenas `[browser]` e `[server]`

---

## 📦 Dependências Instaladas

```txt
streamlit              # Interface web
yahooquery            # Dados financeiros (substitui yfinance)
pandas                # Manipulação de dados
numpy<2.3            # Computação numérica (versão restrita)
pandas-ta            # Indicadores técnicos
plotly               # Gráficos interativos
matplotlib           # Visualizações
sqlalchemy           # Base de dados (futuro)
python-dotenv        # Variáveis de ambiente
requests             # HTTP requests
```

---

## 🚀 Como Executar a Aplicação

### Passo 1: Ativar ambiente virtual
```bash
cd "C:\Users\Paulo Assenção\claude_projects"
venv\Scripts\activate
```

### Passo 2: Executar Streamlit
```bash
streamlit run app.py
```

### Passo 3: Acessar no navegador
```
http://localhost:8503
```

---

## 📊 Funcionalidades da Aplicação

### Dashboard Principal
- Seletor de índice (S&P 500, NASDAQ, Ambos)
- Botão "Atualizar Dados"
- Top 10 ações ranqueadas por score

### Aba 1: Dashboard
- Tabela com scores totais
- Colunas: Símbolo, Nome, Score Total, Score Técnico, Score Fundamental
- Ordenado por Score Total (decrescente)

### Aba 2: Análise Técnica
- Indicadores individuais para cada ação:
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - SMA/EMA (Médias Móveis)
  - Bollinger Bands
  - Stochastic Oscillator
  - ATR (Average True Range)
- Sinais de compra/venda

### Aba 3: Análise Fundamental
- Métricas por ação:
  - P/E Ratio (Price-to-Earnings)
  - P/B Ratio (Price-to-Book)
  - ROE (Return on Equity)
  - Profit Margins
  - Dividend Yield
  - Revenue Growth
  - Earnings Growth
  - Target Price vs Current Price

### Aba 4: Watchlist
- Lista de ações para monitoramento
- Preços atuais
- Variações percentuais

---

## 🎯 Ações Disponíveis

### S&P 500 (42 símbolos):
AAPL, MSFT, GOOGL, AMZN, META, TSLA, NVDA, JPM, V, JNJ, WMT, PG, MA, HD, DIS, BAC, ADBE, NFLX, CRM, CMCSA, PFE, KO, PEP, TMO, ABBV, AVGO, COST, MRK, ACN, CSCO, NKE, DHR, TXN, LIN, UNP, NEE, BMY, PM, UPS, RTX, LOW, ORCL

### NASDAQ (24 símbolos):
AAPL, MSFT, GOOGL, AMZN, META, TSLA, NVDA, ADBE, NFLX, INTC, CSCO, CMCSA, PEP, AVGO, TXN, QCOM, COST, SBUX, INTU, AMGN, ISRG, AMD, BKNG, ADP

### Total (Ambos): 53 símbolos únicos

---

## 🔧 Comandos Úteis

### Instalar/Atualizar dependências:
```bash
pip install -r requirements.txt
```

### Testar coleta de dados:
```bash
python test_ssl.py
```

### Ver versões instaladas:
```bash
pip list
```

### Atualizar yahooquery:
```bash
pip install --upgrade yahooquery
```

### Reinstalar NumPy com versão correta:
```bash
pip install "numpy<2.3" --force-reinstall
```

---

## 📝 Notas Importantes

### Sobre SSL/Certificados:
O código em `data_collector.py` desabilita verificação SSL devido ao problema com caracteres especiais no path. Estas configurações estão nas linhas 11-19:

```python
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['SSL_CERT_FILE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['PYTHONHTTPSVERIFY'] = '0'
ssl._create_default_https_context = ssl._create_unverified_context
```

### Sobre Encoding:
O console Windows tem problemas com emojis. Por isso todos os prints usam:
- `[ERRO]` em vez de ❌
- `[AVISO]` em vez de ⚠️
- `[SUCESSO]` em vez de ✓

### Sobre yahooquery vs yfinance:
- **yahooquery** é mais moderno e respeita `verify=False`
- Usa API similar mas com métodos diferentes
- `ticker.history()` em vez de `ticker.download()`
- Acesso a dados via dicionários: `ticker.price.get(symbol)`

---

## 🔮 Melhorias Futuras Sugeridas

1. **Expandir lista de ações:**
   - Adicionar lista completa do S&P 500 (~500 símbolos)
   - Incluir NASDAQ 100 completo
   - Opção de pesquisar símbolo específico

2. **Cache de dados:**
   - Implementar cache SQLite (já preparado no código)
   - Evitar chamadas repetidas à API
   - Atualização incremental

3. **Alertas:**
   - Email quando ação atinge score alvo
   - Notificações de sinais de compra/venda
   - Mudanças significativas no ranking

4. **Exportação:**
   - Excel com dados históricos
   - PDF com relatório de análise
   - CSV para importar em outras ferramentas

5. **Gráficos avançados:**
   - Candlestick charts
   - Volume bars
   - Comparação entre ações
   - Histórico de scores

6. **Backtesting:**
   - Testar estratégias históricas
   - Performance de sinais passados
   - Otimização de parâmetros

7. **Análise de Sentimento:**
   - Integrar notícias financeiras
   - Sentiment analysis de mídia social
   - Eventos corporativos

---

## 🆘 Resolução de Problemas

### Se a aplicação não carregar:
1. Verificar se ambiente virtual está ativado
2. Reinstalar dependências: `pip install -r requirements.txt`
3. Verificar porta 8503 disponível: `netstat -ano | findstr :8503`

### Se não buscar dados:
1. Testar conexão: `python test_ssl.py`
2. Verificar yahooquery instalado: `pip show yahooquery`
3. Testar API direta: `python test_direct_api.py`

### Se aparecer erro NumPy:
1. Verificar versão: `pip show numpy`
2. Reinstalar: `pip install "numpy<2.3" --force-reinstall`

### Se caracteres aparecerem incorretos:
1. Problema de encoding do console Windows
2. Não afeta funcionalidade da aplicação web
3. Ver aplicação no browser em vez do terminal

---

## 📞 Referências

- **Streamlit Docs:** https://docs.streamlit.io
- **yahooquery Docs:** https://yahooquery.dpguthrie.com
- **pandas-ta Docs:** https://github.com/twopirllc/pandas-ta
- **Plotly Docs:** https://plotly.com/python/

---

## ✅ Status Final

**Estado:** ✓ FUNCIONANDO PERFEITAMENTE
**URL:** http://localhost:8503
**Data coleta:** ✓ Testado com AAPL
**Interface:** ✓ 4 abas operacionais
**Análises:** ✓ Técnica + Fundamental

**Projeto completo e pronto para uso diário!**

---

*Documento criado automaticamente para preservar histórico da sessão.*
*Última atualização: 2025-11-02*
