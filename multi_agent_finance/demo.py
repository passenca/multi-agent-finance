"""
Demo da arquitetura multi-agente para análise financeira.

Este script demonstra como usar o sistema de agentes para analisar ações.
"""
import sys
from datetime import datetime

# Adiciona path para importar módulos locais
sys.path.insert(0, '.')

from agents.technical_agent import TechnicalAgent
from agents.fundamental_agent import FundamentalAgent
from agents.sentiment_agent import SentimentAgent
from agents.macro_agent import MacroAgent
from agents.risk_agent import RiskAgent
from agents.sector_agent import SectorAgent
from orchestrator.orchestrator import AgentOrchestrator
from utils.data_fetcher import DataFetcher


def print_separator(char="=", length=80):
    """Imprime separador visual."""
    print(char * length)


def print_header(text):
    """Imprime cabeçalho formatado."""
    print_separator()
    print(f"  {text}")
    print_separator()


def print_agent_insight(insight):
    """Imprime insight de um agente de forma formatada."""
    print(f"\n🤖 {insight.agent_name}")
    print(f"   Score: {insight.score:+.2f}/100")
    print(f"   Confiança: {insight.confidence:.0%}")
    print(f"   Análise: {insight.reasoning}")


def print_final_analysis(analysis):
    """Imprime análise final combinada."""
    print_header("📊 ANÁLISE COMBINADA")

    # Recomendação principal
    rec = analysis['recommendation']
    score = analysis['combined_score']
    confidence = analysis['combined_confidence']

    # Define cor baseada na recomendação (usando emoji)
    emoji_map = {
        'COMPRA FORTE': '🟢',
        'COMPRA': '🟢',
        'MANTER': '🟡',
        'VENDA': '🔴',
        'VENDA FORTE': '🔴',
        'INSUFFICIENT DATA': '⚪',
        'INSUFFICIENT CONFIDENCE': '⚪'
    }

    emoji = emoji_map.get(rec, '⚪')

    print(f"\n{emoji} RECOMENDAÇÃO: {rec}")
    print(f"   Score Combinado: {score:+.2f}/100")
    print(f"   Confiança: {confidence:.0%}")
    print(f"   Agentes consultados: {analysis['total_agents']}")

    print(f"\n📝 Raciocínio:")
    for line in analysis['reasoning'].split('\n'):
        print(f"   {line}")


def analyze_stock(symbol: str, period: str = "1y", custom_weights: dict = None):
    """
    Analisa uma ação usando todos os agentes.

    Args:
        symbol: Símbolo da ação
        period: Período de dados históricos
        custom_weights: Dicionário opcional com pesos customizados para cada agente
    """
    print_header(f"🔍 ANÁLISE MULTI-AGENTE: {symbol}")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 1. Busca dados
    print("📥 Buscando dados...")
    fetcher = DataFetcher()
    data = fetcher.fetch_all_data(symbol, period)

    if data['price_history'].empty:
        print(f"\n❌ Erro: Não foi possível buscar dados para {symbol}")
        return

    # 2. Inicializa agentes com pesos customizados (ou padrão)
    weights = custom_weights or {}

    agents = [
        TechnicalAgent(weight=weights.get('technical', 1.0)),
        FundamentalAgent(weight=weights.get('fundamental', 1.2)),  # Peso maior
        SentimentAgent(weight=weights.get('sentiment', 0.8)),  # Peso menor (dados limitados)
        MacroAgent(weight=weights.get('macro', 0.9)),
        RiskAgent(weight=weights.get('risk', 1.0)),
        SectorAgent(weight=weights.get('sector', 1.0))
    ]

    # 3. Cria orquestrador
    orchestrator = AgentOrchestrator(agents)

    print("\n✓ Agentes inicializados:")
    for agent in agents:
        print(f"   • {agent.name} (peso: {agent.weight})")

    # 4. Executa análise
    print_header("🔬 ANÁLISES INDIVIDUAIS")

    analysis = orchestrator.analyze(symbol, data)

    # Imprime insights individuais
    for insight_dict in analysis['individual_insights']:
        # Reconstrói o AgentInsight para usar a função de impressão
        from agents.base_agent import AgentInsight
        insight = AgentInsight(
            agent_name=insight_dict['agent_name'],
            score=insight_dict['score'],
            confidence=insight_dict['confidence'],
            reasoning=insight_dict['reasoning']
        )
        print_agent_insight(insight)

    # 5. Imprime análise combinada
    print_final_analysis(analysis)

    return analysis


def compare_stocks(symbols: list, period: str = "1y"):
    """
    Compara múltiplas ações lado a lado.

    Args:
        symbols: Lista de símbolos para comparar
        period: Período de dados históricos
    """
    print_header(f"📊 COMPARAÇÃO DE AÇÕES")

    results = []

    for symbol in symbols:
        print(f"\n🔍 Analisando {symbol}...")
        analysis = analyze_stock(symbol, period)
        if analysis:
            results.append({
                'symbol': symbol,
                'score': analysis['combined_score'],
                'recommendation': analysis['recommendation'],
                'confidence': analysis['combined_confidence']
            })

    # Ranking
    print_header("🏆 RANKING COMPARATIVO")
    results.sort(key=lambda x: x['score'], reverse=True)

    print(f"\n{'Rank':<6} {'Símbolo':<10} {'Score':<12} {'Recomendação':<20} {'Confiança':<12}")
    print("-" * 70)

    for i, result in enumerate(results, 1):
        print(f"{i:<6} {result['symbol']:<10} {result['score']:+8.2f}    "
              f"{result['recommendation']:<20} {result['confidence']:>8.0%}")


def interactive_demo():
    """Demo interativo."""
    print_header("🤖 SISTEMA MULTI-AGENTE DE ANÁLISE FINANCEIRA")

    print("\nEste sistema usa 6 agentes especializados para análise completa:")
    print("  1. 📈 Agente Técnico - RSI, MACD, médias móveis, Bollinger Bands")
    print("  2. 📊 Agente Fundamental - P/E, ROE, crescimento, dividendos")
    print("  3. 💬 Agente de Sentimento - Notícias, social media, analyst ratings")
    print("  4. 🌍 Agente Macroeconómico - Taxas, inflação, PIB, regime de mercado")
    print("  5. ⚠️  Agente de Risco - Volatilidade, Sharpe, VaR, drawdowns")
    print("  6. 🏢 Agente Setorial - Comparação com peers, market share")

    print("\n" + "=" * 80)

    while True:
        print("\n\nOpções:")
        print("  1. Analisar uma ação")
        print("  2. Comparar múltiplas ações")
        print("  3. Analisar top 5 tech stocks")
        print("  4. Sair")

        choice = input("\nEscolha uma opção (1-4): ").strip()

        if choice == '1':
            symbol = input("Digite o símbolo da ação (ex: AAPL): ").strip().upper()
            if symbol:
                analyze_stock(symbol)
        elif choice == '2':
            symbols_input = input("Digite os símbolos separados por vírgula (ex: AAPL,MSFT,GOOGL): ").strip()
            symbols = [s.strip().upper() for s in symbols_input.split(',') if s.strip()]
            if symbols:
                compare_stocks(symbols)
        elif choice == '3':
            tech_stocks = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META']
            compare_stocks(tech_stocks)
        elif choice == '4':
            print("\n👋 Até breve!")
            break
        else:
            print("❌ Opção inválida")


def quick_demo():
    """Demo rápido com exemplo pré-definido."""
    print_header("🚀 DEMO RÁPIDO")

    # Analisa Apple
    print("\n📱 Analisando Apple (AAPL)...\n")
    analyze_stock("AAPL", period="1y")

    print("\n\n" + "=" * 80)
    print("✅ Demo concluído!")
    print("\nPara análise interativa, execute: python demo.py --interactive")
    print("Para comparar ações, execute: python demo.py --compare AAPL,MSFT,GOOGL")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Demo do sistema multi-agente de análise financeira")
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Modo interativo')
    parser.add_argument('--compare', '-c', type=str,
                       help='Compara múltiplas ações (ex: AAPL,MSFT,GOOGL)')
    parser.add_argument('--symbol', '-s', type=str,
                       help='Analisa uma ação específica')
    parser.add_argument('--period', '-p', type=str, default='1y',
                       help='Período de dados (ex: 1y, 6mo, 2y)')

    args = parser.parse_args()

    if args.interactive:
        interactive_demo()
    elif args.compare:
        symbols = [s.strip().upper() for s in args.compare.split(',')]
        compare_stocks(symbols, args.period)
    elif args.symbol:
        analyze_stock(args.symbol.upper(), args.period)
    else:
        # Demo rápido padrão
        quick_demo()
