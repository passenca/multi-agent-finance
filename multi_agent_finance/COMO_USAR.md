# 🚀 Como Usar o Sistema Multi-Agente

## ✅ Passo 1: Verificar Instalação

A instalação está quase concluída. Aguarde até ver a mensagem "Successfully installed".

## 🌐 Passo 2: Executar a Aplicação Web

Abre o terminal (PowerShell ou CMD) e executa:

```bash
cd "C:\Users\Paulo Assenção\claude_projects\multi_agent_finance"
streamlit run app.py
```

A aplicação abrirá automaticamente no navegador em: **http://localhost:8501**

## 📖 Passo 3: Usar a Interface

### 🔍 Análise Individual
1. Digite um símbolo de ação (ex: **AAPL**, **MSFT**, **GOOGL**)
2. Clique em "🔍 Analisar"
3. Vê os resultados em 4 tabs:
   - **Resumo**: Recomendação geral
   - **Preços**: Gráficos interativos
   - **Fundamentals**: Métricas financeiras
   - **Agentes**: Análise detalhada

### 📊 Comparação de Ações
1. Vai para a aba "📊 Comparação de Ações"
2. Digite vários símbolos separados por vírgula (ex: **AAPL,MSFT,GOOGL**)
3. Clique em "📊 Comparar"
4. Vê o ranking e download o CSV

### ⚙️ Ajustar Configurações (Sidebar)
- **Perfis**: Conservador, Moderado, Agressivo, Day Trader
- **Pesos** personalizados de cada agente
- **Período**: 1mo, 3mo, 6mo, 1y, 2y, 5y

## 💡 Exemplos Práticos

### Exemplo 1: Análise Rápida da Apple
```
1. Símbolo: AAPL
2. Período: 1y
3. Perfil: Moderado
4. Analisar ✓
```

### Exemplo 2: Comparar Big Tech
```
1. Símbolos: AAPL,MSFT,GOOGL,AMZN,META
2. Período: 6mo
3. Comparar ✓
4. Ver ranking
```

### Exemplo 3: Análise Conservadora
```
1. Perfil: Conservador (na sidebar)
2. Símbolo: JNJ (Johnson & Johnson)
3. Período: 2y
4. Verificar agente de Risco
```

## 🛠️ Troubleshooting

### Problema: "streamlit: command not found"
**Solução**: A instalação ainda não terminou. Aguarda mais um momento.

### Problema: "Dados insuficientes"
**Solução**:
- Verifica se o símbolo está correto
- Usa símbolos de grandes empresas (AAPL, MSFT, etc.)
- Experimenta outro período (ex: 1y)

### Problema: Aplicação muito lenta
**Solução**:
- É normal na primeira busca de dados
- Cache armazena dados por 1 hora
- Compara menos ações de cada vez (máx 5-6)

## 📚 Guias Adicionais

- **README.md**: Documentação completa do sistema
- **WEB_APP_GUIDE.md**: Guia detalhado da interface web
- **demo.py**: Versão linha de comando (alternativa)

## ⚠️ Lembretes Importantes

1. Este sistema é **educacional**
2. NÃO constitui aconselhamento financeiro
3. Sempre faz a tua própria pesquisa (DYOR)
4. Consulta profissionais certificados para decisões de investimento

---

**Pronto para começar? Execute:**
```bash
streamlit run app.py
```

Boa análise! 📈
