# analytics.py
import sqlite3
from datetime import datetime
from typing import Dict, List
import pandas as pd
from pathlib import Path

class AnalyticsTracker:
    """Track and analyze prompt performance"""

    def __init__(self, db_path: str = "./data/performance.db"):
        self.db_path = db_path
        # Ensure the directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                query TEXT NOT NULL,
                technique_id TEXT NOT NULL,
                technique_name TEXT NOT NULL,
                provider TEXT NOT NULL,
                response TEXT,
                user_rating INTEGER,
                tokens_used INTEGER,
                input_tokens INTEGER,
                output_tokens INTEGER,
                response_time_ms INTEGER,
                metadata TEXT
            )
        """)

        conn.commit()
        conn.close()

    def log_interaction(self, query: str, technique_id: str, technique_name: str,
                       provider: str, response: str, tokens: Dict,
                       response_time: int, rating: int = None):
        """Log a single interaction"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO interactions
            (timestamp, query, technique_id, technique_name, provider, response,
             user_rating, tokens_used, input_tokens, output_tokens, response_time_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            query, technique_id, technique_name, provider, response,
            rating, tokens.get('tokens', 0), tokens.get('input_tokens', 0),
            tokens.get('output_tokens', 0), response_time
        ))

        conn.commit()
        conn.close()

    def get_technique_stats(self) -> pd.DataFrame:
        """Get statistics by technique"""
        conn = sqlite3.connect(self.db_path)

        df = pd.read_sql_query("""
            SELECT
                technique_name,
                COUNT(*) as uses,
                AVG(user_rating) as avg_rating,
                AVG(tokens_used) as avg_tokens,
                AVG(response_time_ms) as avg_response_time
            FROM interactions
            WHERE user_rating IS NOT NULL
            GROUP BY technique_name
            ORDER BY uses DESC
        """, conn)

        conn.close()
        return df

    def get_provider_comparison(self) -> pd.DataFrame:
        """Compare providers"""
        conn = sqlite3.connect(self.db_path)

        df = pd.read_sql_query("""
            SELECT
                provider,
                COUNT(*) as uses,
                AVG(user_rating) as avg_rating,
                AVG(tokens_used) as avg_tokens,
                AVG(response_time_ms) as avg_response_time
            FROM interactions
            WHERE user_rating IS NOT NULL
            GROUP BY provider
        """, conn)

        conn.close()
        return df

    def get_recent_history(self, limit: int = 20) -> pd.DataFrame:
        """Get recent interactions"""
        conn = sqlite3.connect(self.db_path)

        df = pd.read_sql_query(f"""
            SELECT timestamp, query, technique_name, provider, user_rating, tokens_used
            FROM interactions
            ORDER BY timestamp DESC
            LIMIT {limit}
        """, conn)

        conn.close()
        return df
