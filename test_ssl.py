"""
Script de teste para verificar se o problema de SSL foi resolvido
"""

import sys
sys.path.insert(0, 'C:\\Users\\Paulo Assenção\\claude_projects')

from src.data_collector import DataCollector

print("Testando coleta de dados sem curl_cffi...")
print("=" * 50)

collector = DataCollector()

# Testar busca de uma ação
print("\nTestando AAPL...")
data = collector.get_stock_data("AAPL", period="5d")

if data is not None and not data.empty:
    print("[SUCESSO] Dados obtidos com sucesso!")
    print(f"Número de registros: {len(data)}")
    print(f"Último preço: ${data['Close'].iloc[-1]:.2f}")
    print("\nPrimeiros registros:")
    print(data.head())
else:
    print("[ERRO] Falha ao obter dados")

print("\n" + "=" * 50)
print("Teste concluído!")
