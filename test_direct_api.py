"""
Teste direto da API do Yahoo Finance
"""

import requests
import ssl
import os

# Configurações SSL
os.environ['CURL_CA_BUNDLE'] = ''
ssl._create_default_https_context = ssl._create_unverified_context
requests.packages.urllib3.disable_warnings()

# Criar sessão com headers
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
})
session.verify = False

# Testar acesso direto
print("Testando acesso à API do Yahoo Finance...")
print("=" * 50)

url = "https://query2.finance.yahoo.com/v8/finance/chart/AAPL?interval=1d&range=5d"
print(f"\nURL: {url}")

try:
    response = session.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Content Length: {len(response.content)}")
    print(f"\nPrimeiros 500 caracteres da resposta:")
    print(response.text[:500])

    if response.status_code == 200:
        print("\n[SUCESSO] Acesso à API funcionou!")
    else:
        print(f"\n[ERRO] Status code inesperado: {response.status_code}")

except Exception as e:
    print(f"\n[ERRO] Falha ao acessar API: {str(e)}")

print("\n" + "=" * 50)
print("Teste concluído!")
