# 🌐 Guia da Aplicação Web

## 🚀 Como Executar

### 1. Instalar Dependências

```bash
cd multi_agent_finance
pip install -r requirements.txt
```

### 2. Executar a Aplicação

```bash
streamlit run app.py
```

A aplicação abrirá automaticamente no navegador em `http://localhost:8501`

## 📱 Funcionalidades

### 🔍 Análise Individual de Ação

**Como usar:**
1. Digite o símbolo da ação (ex: AAPL, MSFT, GOOGL)
2. Selecione o período de análise
3. Clique em "Analisar"

**O que você verá:**
- ✅ **Recomendação Final**: COMPRA FORTE, COMPRA, MANTER, VENDA, ou VENDA FORTE
- 📊 **4 Tabs com informações:**
  - **Resumo**: Pontuação geral, confiança, raciocínio combinado
  - **Preços**: Gráfico candlestick com médias móveis (SMA 50/200) e volume
  - **Fundamentals**: Métricas financeiras (P/E, ROE, margens, etc.)
  - **Agentes**: Análises detalhadas de cada um dos 6 agentes

### 📊 Comparação de Ações

**Como usar:**
1. Digite múltiplos símbolos separados por vírgula (ex: AAPL,MSFT,GOOGL,NVDA)
2. Selecione o período
3. Clique em "Comparar"

**O que você verá:**
- 🏆 **Ranking**: Gráfico de barras com scores de todas as ações
- 📋 **Tabela comparativa**: Recomendação, score e confiança de cada ação
- 📥 **Download CSV**: Exportar resultados para análise externa

## ⚙️ Configurações (Sidebar)

### 📊 Perfis de Investimento

Escolha um perfil pré-configurado que ajusta automaticamente os pesos dos agentes:

#### **Conservador**
- Foco em **risco** e **fundamentals**
- Ideal para: Investidores que priorizam segurança e dividendos
- Pesos:
  - Técnico: 0.5
  - Fundamental: 1.5 ⬆️
  - Sentimento: 0.3
  - Macro: 1.2 ⬆️
  - Risco: 1.8 ⬆️⬆️
  - Setorial: 1.0

#### **Moderado** (Padrão)
- Equilíbrio entre todas as análises
- Ideal para: Maioria dos investidores
- Pesos balanceados em torno de 1.0

#### **Agressivo**
- Foco em **técnica** e **sentimento**
- Ideal para: Growth investing, momentum
- Pesos:
  - Técnico: 2.0 ⬆️⬆️
  - Fundamental: 0.8
  - Sentimento: 1.5 ⬆️
  - Macro: 0.7
  - Risco: 0.5 ⬇️
  - Setorial: 0.8

#### **Day Trader**
- Máximo foco em **técnica** e **sentimento de curto prazo**
- Ideal para: Trading de curto prazo
- Pesos:
  - Técnico: 2.5 ⬆️⬆️⬆️
  - Fundamental: 0.3 ⬇️⬇️
  - Sentimento: 1.8 ⬆️⬆️
  - Macro: 0.5 ⬇️
  - Risco: 0.4 ⬇️
  - Setorial: 0.3 ⬇️

#### **Personalizado**
- Ajuste fino manual de cada agente
- Use os sliders para definir pesos de 0.0 a 3.0

### 📅 Período de Análise

Escolha quanto histórico usar:
- **1mo**: Muito recente, foco em tendências de curtíssimo prazo
- **3mo**: Tendências de curto prazo
- **6mo**: Equilíbrio entre curto e médio prazo
- **1y** (Recomendado): Visão completa do ano
- **2y**: Tendências de longo prazo
- **5y**: Perspectiva de muito longo prazo

## 📊 Entendendo os Resultados

### Cores da Recomendação

- 🟢 **Verde** (COMPRA FORTE / COMPRA): Score positivo, outlook bullish
- 🟡 **Amarelo** (MANTER): Score neutro, aguardar melhor ponto
- 🔴 **Vermelho** (VENDA / VENDA FORTE): Score negativo, outlook bearish

### Score Combinado

- **-100 a -60**: Muito bearish - Considere vender
- **-60 a -30**: Bearish - Cautela
- **-30 a +30**: Neutro - Manter posição ou aguardar
- **+30 a +60**: Bullish - Bom momento para comprar
- **+60 a +100**: Muito bullish - Excelente oportunidade

### Nível de Confiança

- **> 80%**: Alta confiança - Consenso forte entre agentes
- **50-80%**: Confiança moderada - Alguns agentes divergem
- **< 50%**: Baixa confiança - Muita divergência ou dados insuficientes

⚠️ **Atenção**: Baixa confiança pode indicar:
- Momento de transição/incerteza no mercado
- Dados insuficientes (ex: IPO recente)
- Sinais contraditórios (ex: bons fundamentals mas má técnica)

## 🤖 Os 6 Agentes

### 📈 Agente Técnico
**O que analisa:**
- RSI (sobrecompra/sobrevenda)
- MACD (momentum)
- Médias móveis (tendência)
- Bollinger Bands (volatilidade)
- Volume (confirmação)

**Quando é mais útil:**
- Trading de curto/médio prazo
- Identificar pontos de entrada/saída
- Confirmar tendências

### 📊 Agente Fundamental
**O que analisa:**
- Valuation (P/E, P/B, PEG)
- Rentabilidade (ROE, ROA, margens)
- Crescimento (receita, lucros)
- Saúde financeira (dívida, liquidez)
- Dividendos

**Quando é mais útil:**
- Investimento de longo prazo
- Value investing
- Identificar empresas subvalorizadas

### 💬 Agente de Sentimento
**O que analisa:**
- Notícias financeiras
- Sentimento em redes sociais
- Ratings de analistas
- Insider trading

**Quando é mais útil:**
- Antecipar movimentos de curto prazo
- Identificar mudanças de percepção
- Confirmar narrativas de mercado

**Nota:** Atualmente usa dados limitados; em produção integraria APIs de notícias e social media.

### 🌍 Agente Macroeconómico
**O que analisa:**
- Taxas de juro (Fed, BCE)
- Inflação
- Crescimento do PIB
- Emprego
- Regime de mercado (VIX, yield curve)

**Quando é mais útil:**
- Entender contexto macro
- Identificar regime de mercado (risk-on/risk-off)
- Antecipar impacto de políticas monetárias

**Nota:** Atualmente usa dados placeholder; em produção usaria FRED API.

### ⚠️ Agente de Risco
**O que analisa:**
- Volatilidade histórica
- Sharpe Ratio (retorno ajustado ao risco)
- Maximum Drawdown (pior queda)
- Value at Risk (VaR)
- Beta vs mercado

**Quando é mais útil:**
- Gestão de risco de portfólio
- Identificar ativos defensivos vs agressivos
- Avaliar se risco justifica retorno esperado

### 🏢 Agente Setorial
**O que analisa:**
- Comparação com peers
- Posição de mercado
- Tendências do setor
- Performance relativa

**Quando é mais útil:**
- Escolher melhor ação dentro de um setor
- Identificar líderes vs retardatários
- Avaliar vento de cauda/contra do setor

## 💡 Dicas de Uso

### Para Investimento de Longo Prazo
1. Use perfil **Conservador** ou **Moderado**
2. Analise período de **1y** ou **2y**
3. Foque em fundamentals e risco
4. Procure empresas com:
   - Alto score fundamental
   - Baixo risco (alta confiança do Agente de Risco)
   - Boa posição setorial

### Para Trading de Médio Prazo
1. Use perfil **Moderado** ou **Agressivo**
2. Analise período de **6mo** ou **1y**
3. Equilibre técnica e fundamentals
4. Procure:
   - Sinais técnicos alinhados com fundamentals
   - Momentum positivo
   - Sentimento melhorando

### Para Trading de Curto Prazo
1. Use perfil **Day Trader**
2. Analise período de **1mo** ou **3mo**
3. Máximo peso em técnica
4. Procure:
   - Breakouts técnicos
   - Volume confirmando
   - Sentimento positivo

### Para Comparar Setores
1. Use a página de **Comparação**
2. Compare líderes de diferentes setores
3. Identifique setores com momentum
4. Exemplo: `AAPL,JPM,XOM,JNJ,NVDA` (Tech, Finance, Energy, Healthcare, Semiconductors)

## 🔍 Troubleshooting

### "Dados insuficientes"
- Empresa pode ser muito recente (IPO)
- Símbolo pode estar incorreto
- Tente outro período

### Confiança muito baixa
- Normal em momentos de alta volatilidade
- Agentes divergem = sinal de cautela
- Considere aguardar mais dados

### Aplicação lenta
- Cache de 1 hora reduz chamadas repetidas
- Comparar muitas ações pode demorar
- Considere analisar em lotes menores

## 📱 Atalhos de Teclado

- **Ctrl+R** ou **F5**: Recarregar página
- **Ctrl+Shift+R**: Limpar cache e recarregar
- **Ctrl+Click** nos gráficos: Resetar zoom

## 🔄 Atualizações Futuras Planejadas

- [ ] Adicionar watchlist persistente
- [ ] Sistema de alertas por email
- [ ] Integração com APIs de notícias reais
- [ ] Backtesting de recomendações
- [ ] Análise de portfólio completo
- [ ] Exportar relatórios em PDF
- [ ] Modo dark theme

## 📞 Feedback

Encontrou um bug ou tem sugestão?
- Abra uma issue no projeto
- Descreva o que esperava vs o que aconteceu
- Inclua símbolo da ação e configurações usadas

---

**Bom investimento! 📈**

*Lembre-se: Este sistema é educacional. Sempre faça sua própria pesquisa (DYOR) e consulte profissionais certificados.*
