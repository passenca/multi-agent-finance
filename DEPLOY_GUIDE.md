# Guia de Deploy - Streamlit Community Cloud

## Passo a Passo para Deploy

### 1. Criar Repositório no GitHub

1. Vai a https://github.com/new
2. Cria um novo repositório:
   - **Nome**: `multi-agent-finance` (ou outro à tua escolha)
   - **Descrição**: "Sistema Multi-Agente de Análise Financeira"
   - **Visibilidade**: Público ou Privado (ambos funcionam)
   - **NÃO** inicializes com README, .gitignore ou LICENSE (já temos estes ficheiros)

3. Copia o URL do repositório que aparece (algo como `https://github.com/passenca/multi-agent-finance.git`)

### 2. Fazer Push do Código para o GitHub

No terminal, executa os seguintes comandos (substitui URL_DO_TEU_REPO pelo URL copiado):

```bash
cd "C:\Users\Paulo Assenção\claude_projects"
git remote add origin URL_DO_TEU_REPO
git branch -M main
git push -u origin main
```

**Exemplo:**
```bash
git remote add origin https://github.com/passenca/multi-agent-finance.git
git branch -M main
git push -u origin main
```

### 3. Configurar Streamlit Community Cloud

#### 3.1 Criar Conta
1. Vai a https://share.streamlit.io/
2. Clica em "Sign up" ou "Continue with GitHub"
3. Autoriza o Streamlit a aceder ao teu GitHub

#### 3.2 Criar Nova App
1. Clica em "New app"
2. Preenche:
   - **Repository**: `passenca/multi-agent-finance` (ou o nome que escolheste)
   - **Branch**: `main`
   - **Main file path**: `multi_agent_finance/app.py`
   - **App URL (opcional)**: deixa em branco ou escolhe um nome personalizado

3. Clica em "Advanced settings..."

#### 3.3 Configurar Secrets (API Keys)
Na secção "Secrets", adiciona:

```toml
# Configuração de API Keys
ALPHA_VANTAGE_KEY = "MJC6PXKHCM96FE4V"
```

**IMPORTANTE**: Esta é a tua chave privada! Nunca faças commit dela no código.

#### 3.4 Python Version
Certifica-te que está selecionado Python 3.9 ou superior.

4. Clica em "Deploy!"

### 4. Aguardar Deploy

- O deploy demora ~2-5 minutos
- Podes acompanhar os logs em tempo real
- Se houver erros, aparecerão nos logs

### 5. Testar a Aplicação

Quando o deploy terminar:
1. A aplicação abre automaticamente
2. URL será algo como: `https://passenca-multi-agent-finance.streamlit.app`
3. Testa analisar uma ação (ex: AAPL)
4. Verifica se os dados reais estão a funcionar

## Troubleshooting

### Erro: "No module named 'dotenv'"
**Solução**: Verifica se `python-dotenv` está no `requirements.txt`

### Erro: "File not found: app.py"
**Solução**: Certifica-te que o caminho é `multi_agent_finance/app.py`

### Erro: "ALPHA_VANTAGE_KEY not found"
**Solução**: Verifica se adicionaste a chave nos Secrets do Streamlit Cloud

### App muito lenta ou crashando
**Solução**:
- Streamlit Cloud tem limite de 1GB RAM
- Reduz o número de símbolos analisados simultaneamente
- Verifica se o cache está a funcionar

## Atualizações Futuras

Para fazer updates na aplicação:

```bash
# Fazer mudanças no código
git add .
git commit -m "Descricao da mudanca"
git push

# O Streamlit Cloud faz deploy automático!
```

## URLs Úteis

- **Streamlit Cloud Dashboard**: https://share.streamlit.io/
- **Documentação**: https://docs.streamlit.io/streamlit-community-cloud
- **Alpha Vantage**: https://www.alphavantage.co/

## Notas Importantes

1. **Secrets nunca vão para o Git** - O `.gitignore` protege o ficheiro `.env`
2. **Deploy automático** - Cada push para `main` faz novo deploy
3. **Logs disponíveis** - Podes ver logs em tempo real no dashboard do Streamlit
4. **Limite de recursos** - 1GB RAM, apps adormecem após inatividade
5. **Wake up time** - ~30s para acordar se estiver dormindo

## Suporte

Se tiveres problemas:
1. Verifica os logs no Streamlit Cloud
2. Verifica o GitHub Actions (se configurado)
3. Contacta suporte: support@streamlit.io
