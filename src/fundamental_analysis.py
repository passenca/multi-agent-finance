"""
Módulo de Análise Fundamental
Avalia a saúde financeira e o valor intrínseco das empresas
"""

import pandas as pd
from typing import Dict, Optional


class FundamentalAnalyzer:
    """Classe para realizar análise fundamental de ações"""

    def __init__(self):
        """Inicializa o analisador fundamental"""
        # Valores de referência para comparação
        self.good_pe_ratio = 15
        self.good_pb_ratio = 3
        self.good_roe = 0.15  # 15%
        self.good_profit_margin = 0.10  # 10%
        self.good_dividend_yield = 0.02  # 2%

    def evaluate_pe_ratio(self, pe_ratio: Optional[float]) -> Dict[str, any]:
        """
        Avalia o P/E Ratio (Price to Earnings)

        Args:
            pe_ratio: Relação Preço/Lucro

        Returns:
            Dicionário com pontuação e análise
        """
        if pe_ratio is None or pe_ratio <= 0:
            return {
                'score': 0,
                'status': 'N/A',
                'description': 'Dados não disponíveis'
            }

        if pe_ratio < 10:
            score = 100
            status = 'Excelente'
            description = 'Ação potencialmente subvalorizada'
        elif pe_ratio < 15:
            score = 80
            status = 'Bom'
            description = 'Avaliação razoável'
        elif pe_ratio < 25:
            score = 60
            status = 'Moderado'
            description = 'Avaliação dentro da média'
        elif pe_ratio < 40:
            score = 40
            status = 'Alto'
            description = 'Ação pode estar sobrevalorizada'
        else:
            score = 20
            status = 'Muito Alto'
            description = 'Ação potencialmente cara'

        return {
            'score': score,
            'status': status,
            'description': description,
            'value': pe_ratio
        }

    def evaluate_pb_ratio(self, pb_ratio: Optional[float]) -> Dict[str, any]:
        """
        Avalia o P/B Ratio (Price to Book)

        Args:
            pb_ratio: Relação Preço/Valor Contábil

        Returns:
            Dicionário com pontuação e análise
        """
        if pb_ratio is None or pb_ratio <= 0:
            return {
                'score': 0,
                'status': 'N/A',
                'description': 'Dados não disponíveis'
            }

        if pb_ratio < 1:
            score = 100
            status = 'Excelente'
            description = 'Negociando abaixo do valor contábil'
        elif pb_ratio < 2:
            score = 80
            status = 'Bom'
            description = 'Avaliação atrativa'
        elif pb_ratio < 3:
            score = 60
            status = 'Moderado'
            description = 'Avaliação razoável'
        elif pb_ratio < 5:
            score = 40
            status = 'Alto'
            description = 'Prêmio elevado sobre valor contábil'
        else:
            score = 20
            status = 'Muito Alto'
            description = 'Prêmio muito alto'

        return {
            'score': score,
            'status': status,
            'description': description,
            'value': pb_ratio
        }

    def evaluate_roe(self, roe: Optional[float]) -> Dict[str, any]:
        """
        Avalia o ROE (Return on Equity)

        Args:
            roe: Retorno sobre Patrimônio Líquido

        Returns:
            Dicionário com pontuação e análise
        """
        if roe is None:
            return {
                'score': 0,
                'status': 'N/A',
                'description': 'Dados não disponíveis'
            }

        roe_percent = roe * 100

        if roe > 0.20:  # 20%
            score = 100
            status = 'Excelente'
            description = 'Retorno sobre capital muito bom'
        elif roe > 0.15:  # 15%
            score = 80
            status = 'Bom'
            description = 'Retorno sobre capital saudável'
        elif roe > 0.10:  # 10%
            score = 60
            status = 'Moderado'
            description = 'Retorno sobre capital aceitável'
        elif roe > 0:
            score = 40
            status = 'Fraco'
            description = 'Retorno sobre capital baixo'
        else:
            score = 0
            status = 'Negativo'
            description = 'Empresa não é rentável'

        return {
            'score': score,
            'status': status,
            'description': description,
            'value': roe_percent
        }

    def evaluate_profit_margin(self, margin: Optional[float]) -> Dict[str, any]:
        """
        Avalia a Margem de Lucro

        Args:
            margin: Margem de lucro

        Returns:
            Dicionário com pontuação e análise
        """
        if margin is None:
            return {
                'score': 0,
                'status': 'N/A',
                'description': 'Dados não disponíveis'
            }

        margin_percent = margin * 100

        if margin > 0.20:  # 20%
            score = 100
            status = 'Excelente'
            description = 'Margem de lucro muito alta'
        elif margin > 0.15:  # 15%
            score = 80
            status = 'Bom'
            description = 'Margem de lucro saudável'
        elif margin > 0.10:  # 10%
            score = 60
            status = 'Moderado'
            description = 'Margem de lucro aceitável'
        elif margin > 0:
            score = 40
            status = 'Fraco'
            description = 'Margem de lucro baixa'
        else:
            score = 0
            status = 'Negativo'
            description = 'Empresa opera com prejuízo'

        return {
            'score': score,
            'status': status,
            'description': description,
            'value': margin_percent
        }

    def evaluate_dividend_yield(self, dividend_yield: Optional[float]) -> Dict[str, any]:
        """
        Avalia o Dividend Yield

        Args:
            dividend_yield: Taxa de dividendos

        Returns:
            Dicionário com pontuação e análise
        """
        if dividend_yield is None or dividend_yield == 0:
            return {
                'score': 50,
                'status': 'N/A',
                'description': 'Não paga dividendos'
            }

        dividend_percent = dividend_yield * 100

        if dividend_yield > 0.05:  # 5%
            score = 100
            status = 'Excelente'
            description = 'Dividend yield muito atrativo'
        elif dividend_yield > 0.03:  # 3%
            score = 80
            status = 'Bom'
            description = 'Dividend yield atrativo'
        elif dividend_yield > 0.02:  # 2%
            score = 60
            status = 'Moderado'
            description = 'Dividend yield razoável'
        else:
            score = 40
            status = 'Baixo'
            description = 'Dividend yield baixo'

        return {
            'score': score,
            'status': status,
            'description': description,
            'value': dividend_percent
        }

    def evaluate_growth(self, revenue_growth: Optional[float], earnings_growth: Optional[float]) -> Dict[str, any]:
        """
        Avalia o crescimento da empresa

        Args:
            revenue_growth: Crescimento de receita
            earnings_growth: Crescimento de lucros

        Returns:
            Dicionário com pontuação e análise
        """
        if revenue_growth is None and earnings_growth is None:
            return {
                'score': 0,
                'status': 'N/A',
                'description': 'Dados não disponíveis'
            }

        # Usar o melhor dos dois ou a média se ambos disponíveis
        if revenue_growth is not None and earnings_growth is not None:
            growth = (revenue_growth + earnings_growth) / 2
        elif revenue_growth is not None:
            growth = revenue_growth
        else:
            growth = earnings_growth

        growth_percent = growth * 100

        if growth > 0.25:  # 25%
            score = 100
            status = 'Excelente'
            description = 'Crescimento muito forte'
        elif growth > 0.15:  # 15%
            score = 80
            status = 'Bom'
            description = 'Crescimento saudável'
        elif growth > 0.05:  # 5%
            score = 60
            status = 'Moderado'
            description = 'Crescimento moderado'
        elif growth > 0:
            score = 40
            status = 'Fraco'
            description = 'Crescimento lento'
        else:
            score = 20
            status = 'Negativo'
            description = 'Empresa em declínio'

        return {
            'score': score,
            'status': status,
            'description': description,
            'value': growth_percent
        }

    def analyze_stock(self, stock_info: Dict) -> Dict[str, any]:
        """
        Realiza análise fundamental completa de uma ação

        Args:
            stock_info: Dicionário com informações fundamentais

        Returns:
            Dicionário com análise completa
        """
        analysis = {
            'symbol': stock_info.get('symbol', 'N/A'),
            'name': stock_info.get('name', 'N/A'),
            'sector': stock_info.get('sector', 'N/A'),
            'pe_analysis': self.evaluate_pe_ratio(stock_info.get('peRatio')),
            'pb_analysis': self.evaluate_pb_ratio(stock_info.get('priceToBook')),
            'roe_analysis': self.evaluate_roe(stock_info.get('returnOnEquity')),
            'margin_analysis': self.evaluate_profit_margin(stock_info.get('profitMargins')),
            'dividend_analysis': self.evaluate_dividend_yield(stock_info.get('dividendYield')),
            'growth_analysis': self.evaluate_growth(
                stock_info.get('revenueGrowth'),
                stock_info.get('earningsGrowth')
            )
        }

        # Calcular pontuação geral
        scores = [
            analysis['pe_analysis']['score'],
            analysis['pb_analysis']['score'],
            analysis['roe_analysis']['score'],
            analysis['margin_analysis']['score'],
            analysis['dividend_analysis']['score'],
            analysis['growth_analysis']['score']
        ]

        analysis['overall_score'] = sum(scores) / len(scores)

        # Classificação geral
        if analysis['overall_score'] >= 80:
            analysis['overall_rating'] = 'Excelente'
        elif analysis['overall_score'] >= 60:
            analysis['overall_rating'] = 'Bom'
        elif analysis['overall_score'] >= 40:
            analysis['overall_rating'] = 'Moderado'
        else:
            analysis['overall_rating'] = 'Fraco'

        return analysis

    def compare_to_sector(self, stock_info: Dict, sector_avg: Dict) -> Dict[str, str]:
        """
        Compara a ação com a média do setor

        Args:
            stock_info: Informações da ação
            sector_avg: Médias do setor

        Returns:
            Dicionário com comparações
        """
        comparisons = {}

        # Comparar P/E
        if stock_info.get('peRatio') and sector_avg.get('pe'):
            if stock_info['peRatio'] < sector_avg['pe']:
                comparisons['PE'] = 'Abaixo da média do setor (positivo)'
            else:
                comparisons['PE'] = 'Acima da média do setor'

        # Comparar ROE
        if stock_info.get('returnOnEquity') and sector_avg.get('roe'):
            if stock_info['returnOnEquity'] > sector_avg['roe']:
                comparisons['ROE'] = 'Acima da média do setor (positivo)'
            else:
                comparisons['ROE'] = 'Abaixo da média do setor'

        return comparisons
