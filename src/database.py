"""
Módulo de Gerenciamento de Banco de Dados
Responsável por armazenar histórico da watchlist e dados de análise
"""

import sqlite3
import pandas as pd
from datetime import datetime, date
from typing import List, Optional, Dict
import os


class DatabaseManager:
    """Gerencia o banco de dados SQLite para histórico de ações"""

    def __init__(self, db_path: str = "watchlist_history.db"):
        """
        Inicializa o gerenciador de banco de dados

        Args:
            db_path: Caminho para o arquivo do banco de dados
        """
        self.db_path = db_path
        self._create_tables()

    def _get_connection(self):
        """Cria conexão com o banco de dados"""
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        """Cria as tabelas necessárias se não existirem"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Tabela de watchlist (símbolos que o usuário está acompanhando)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS watchlist (
                symbol TEXT PRIMARY KEY,
                added_date DATE NOT NULL,
                name TEXT
            )
        """)

        # Tabela de histórico de dados
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                date DATE NOT NULL,
                timestamp DATETIME NOT NULL,

                -- Dados de preço
                current_price REAL,
                open_price REAL,
                high_price REAL,
                low_price REAL,
                volume INTEGER,

                -- Scores
                total_score REAL,
                technical_score REAL,
                fundamental_score REAL,

                -- Indicadores técnicos
                rsi REAL,
                macd REAL,
                macd_signal REAL,
                sma_20 REAL,
                sma_50 REAL,
                ema_20 REAL,
                bb_upper REAL,
                bb_lower REAL,
                stoch_k REAL,
                atr REAL,

                -- Métricas fundamentais
                pe_ratio REAL,
                pb_ratio REAL,
                dividend_yield REAL,
                roe REAL,
                profit_margin REAL,
                revenue_growth REAL,
                earnings_growth REAL,
                market_cap REAL,
                target_price REAL,

                -- Constraint: apenas um registro por dia por símbolo
                UNIQUE(symbol, date)
            )
        """)

        # Índice para buscar por símbolo
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_symbol_date
            ON stock_history(symbol, date DESC)
        """)

        conn.commit()
        conn.close()

    def add_to_watchlist(self, symbol: str, name: str = None):
        """
        Adiciona uma ação à watchlist

        Args:
            symbol: Símbolo da ação
            name: Nome da empresa (opcional)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT OR IGNORE INTO watchlist (symbol, added_date, name) VALUES (?, ?, ?)",
                (symbol, date.today(), name)
            )
            conn.commit()
        finally:
            conn.close()

    def remove_from_watchlist(self, symbol: str):
        """Remove uma ação da watchlist"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM watchlist WHERE symbol = ?", (symbol,))
            conn.commit()
        finally:
            conn.close()

    def get_watchlist(self) -> List[str]:
        """Retorna lista de símbolos na watchlist"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT symbol FROM watchlist ORDER BY added_date DESC")
            symbols = [row[0] for row in cursor.fetchall()]
            return symbols
        finally:
            conn.close()

    def save_stock_data(self, symbol: str, data: Dict):
        """
        Salva ou atualiza dados de uma ação para o dia atual
        Se já existir registro para hoje, substitui com os dados mais recentes

        Args:
            symbol: Símbolo da ação
            data: Dicionário com os dados a salvar
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        today = date.today()
        now = datetime.now()

        try:
            # Preparar dados
            values = (
                symbol,
                today,
                now,
                data.get('current_price'),
                data.get('open_price'),
                data.get('high_price'),
                data.get('low_price'),
                data.get('volume'),
                data.get('total_score'),
                data.get('technical_score'),
                data.get('fundamental_score'),
                data.get('rsi'),
                data.get('macd'),
                data.get('macd_signal'),
                data.get('sma_20'),
                data.get('sma_50'),
                data.get('ema_20'),
                data.get('bb_upper'),
                data.get('bb_lower'),
                data.get('stoch_k'),
                data.get('atr'),
                data.get('pe_ratio'),
                data.get('pb_ratio'),
                data.get('dividend_yield'),
                data.get('roe'),
                data.get('profit_margin'),
                data.get('revenue_growth'),
                data.get('earnings_growth'),
                data.get('market_cap'),
                data.get('target_price')
            )

            # INSERT OR REPLACE: se já existe para hoje, substitui
            cursor.execute("""
                INSERT OR REPLACE INTO stock_history (
                    symbol, date, timestamp,
                    current_price, open_price, high_price, low_price, volume,
                    total_score, technical_score, fundamental_score,
                    rsi, macd, macd_signal, sma_20, sma_50, ema_20,
                    bb_upper, bb_lower, stoch_k, atr,
                    pe_ratio, pb_ratio, dividend_yield, roe, profit_margin,
                    revenue_growth, earnings_growth, market_cap, target_price
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, values)

            conn.commit()
        finally:
            conn.close()

    def get_stock_history(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """
        Recupera histórico de uma ação

        Args:
            symbol: Símbolo da ação
            days: Número de dias de histórico (padrão: 30)

        Returns:
            DataFrame com histórico
        """
        conn = self._get_connection()

        try:
            query = """
                SELECT * FROM stock_history
                WHERE symbol = ?
                ORDER BY date DESC
                LIMIT ?
            """
            df = pd.read_sql_query(query, conn, params=(symbol, days))

            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')  # Ordenar do mais antigo ao mais recente

            return df
        finally:
            conn.close()

    def get_all_watchlist_history(self, days: int = 30) -> pd.DataFrame:
        """
        Recupera histórico de todas as ações na watchlist

        Args:
            days: Número de dias de histórico

        Returns:
            DataFrame com histórico de todas as ações
        """
        watchlist = self.get_watchlist()

        if not watchlist:
            return pd.DataFrame()

        conn = self._get_connection()

        try:
            placeholders = ','.join('?' * len(watchlist))
            query = f"""
                SELECT * FROM stock_history
                WHERE symbol IN ({placeholders})
                AND date >= date('now', '-{days} days')
                ORDER BY symbol, date DESC
            """
            df = pd.read_sql_query(query, conn, params=watchlist)

            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])

            return df
        finally:
            conn.close()

    def get_latest_data(self, symbol: str) -> Optional[Dict]:
        """
        Retorna os dados mais recentes de uma ação

        Args:
            symbol: Símbolo da ação

        Returns:
            Dicionário com os dados ou None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM stock_history
                WHERE symbol = ?
                ORDER BY date DESC, timestamp DESC
                LIMIT 1
            """, (symbol,))

            row = cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
        finally:
            conn.close()

    def clear_old_data(self, days_to_keep: int = 365):
        """
        Remove dados antigos do histórico

        Args:
            days_to_keep: Número de dias de histórico para manter
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                DELETE FROM stock_history
                WHERE date < date('now', '-' || ? || ' days')
            """, (days_to_keep,))
            conn.commit()

            deleted = cursor.rowcount
            return deleted
        finally:
            conn.close()

    def get_statistics(self) -> Dict:
        """Retorna estatísticas do banco de dados"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM stock_history")
            total_records = cursor.fetchone()[0]

            # Contar símbolos únicos
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM stock_history")
            unique_symbols = cursor.fetchone()[0]

            # Data mais antiga
            cursor.execute("SELECT MIN(date) FROM stock_history")
            oldest_date = cursor.fetchone()[0]

            # Data mais recente
            cursor.execute("SELECT MAX(date) FROM stock_history")
            newest_date = cursor.fetchone()[0]

            # Tamanho da watchlist
            cursor.execute("SELECT COUNT(*) FROM watchlist")
            watchlist_size = cursor.fetchone()[0]

            return {
                'total_records': total_records,
                'unique_symbols': unique_symbols,
                'oldest_date': oldest_date,
                'newest_date': newest_date,
                'watchlist_size': watchlist_size
            }
        finally:
            conn.close()
