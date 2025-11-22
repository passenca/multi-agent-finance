# 🔑 Como Obter a API Key do Alpha Vantage (GRATUITO)

## Passo a Passo Rápido

### 1. Acede ao site do Alpha Vantage
🔗 **Link direto**: https://www.alphavantage.co/support/#api-key

### 2. Preenche o formulário simples
O formulário pede apenas:
- **First Name** (Nome próprio)
- **Last Name** (Apelido)
- **Email Address** (Email)
- **Organization** (pode colocar "Personal" ou "Individual")

⚠️ **IMPORTANTE**: Usa um email válido, pois a chave é enviada para lá!

### 3. Clica em "GET FREE API KEY"
- A chave aparece IMEDIATAMENTE no ecrã
- Também recebes um email com a chave

### 4. Copia a chave
A chave tem este formato: `ABC123XYZ789EXAMPLE`
- Normalmente tem 16 caracteres alfanuméricos

### 5. Cola a chave no ficheiro `.env`
Abre o ficheiro `.env` na raiz do projeto e substitui:

```
ALPHA_VANTAGE_KEY=your_api_key_here
```

Por:

```
ALPHA_VANTAGE_KEY=ABC123XYZ789EXAMPLE
```

(Substitui `ABC123XYZ789EXAMPLE` pela tua chave real!)

## 📊 Limites da API Gratuita

✅ **Gratuito para sempre**
- 25 chamadas por DIA (suficiente para testes)
- 5 chamadas por MINUTO
- Não expira
- Sem necessidade de cartão de crédito

## 🔒 Segurança

⚠️ **NUNCA partilhes a tua chave publicamente!**
- O ficheiro `.env` está no `.gitignore` (não vai para o git)
- Nunca faças commit da chave para repositórios públicos

## ✅ Verificar se está a funcionar

Depois de configurares a chave:
1. Executa a aplicação: `streamlit run app.py`
2. Tenta analisar uma ação (ex: AAPL)
3. Verifica nas mensagens de log se aparece `[ALPHA VANTAGE]`

---

**Tempo total estimado**: 2 minutos ⏱️
