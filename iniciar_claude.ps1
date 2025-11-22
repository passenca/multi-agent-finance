# Script para iniciar Claude Code no projeto
# Uso: .\iniciar_claude.ps1

# Navegar para o diretório do projeto
Set-Location "C:\Users\Paulo Assenção\claude_projects"

# Mostrar mensagem
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Iniciando Claude Code..." -ForegroundColor Green
Write-Host "Projeto: Análise Financeira" -ForegroundColor Yellow
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dica: Digite isso ao começar:" -ForegroundColor Magenta
Write-Host "  'Ler RETOMAR_SESSAO.md para contexto'" -ForegroundColor White
Write-Host ""

# Lançar Claude Code
claude
