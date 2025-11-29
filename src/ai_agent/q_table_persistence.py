"""
🧠 Q-Table Persistence System
Saves and loads Q-Learning agent's Q-table to/from PostgreSQL for continuous learning.
"""

import json
import pickle
import base64
from datetime import datetime
from typing import Dict, Tuple, Optional
import psycopg2
import os
import logging

logger = logging.getLogger(__name__)


class QTablePersistence:
    """Persist Q-table to PostgreSQL for continuous learning across restarts."""
    
    def __init__(self):
        self.db_config = {
            'host': os.getenv('POSTGRES_HOST', 'postgres'),
            'port': int(os.getenv('POSTGRES_PORT', 5432)),
            'database': os.getenv('POSTGRES_DB', 'cyber_mirage'),
            'user': os.getenv('POSTGRES_USER', 'cybermirage'),
            'password': os.getenv('POSTGRES_PASSWORD', 'ChangeThisToSecurePassword123!')
        }
        self._init_table()
    
    def _init_table(self):
        """Initialize Q-table storage table in PostgreSQL."""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            # Create table for Q-table snapshots
            cur.execute("""
                CREATE TABLE IF NOT EXISTS q_table_snapshots (
                    id SERIAL PRIMARY KEY,
                    version INTEGER NOT NULL,
                    q_table_data BYTEA NOT NULL,
                    state_count INTEGER,
                    total_updates INTEGER,
                    avg_reward DOUBLE PRECISION,
                    epsilon DOUBLE PRECISION,
                    created_at TIMESTAMP DEFAULT NOW(),
                    notes TEXT
                )
            """)
            
            # Create table for Q-table metadata
            cur.execute("""
                CREATE TABLE IF NOT EXISTS q_table_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            conn.commit()
            cur.close()
            conn.close()
            logger.info("✅ Q-table persistence table initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Q-table persistence: {e}")
    
    def save_q_table(self, q_table: Dict, epsilon: float, metadata: Dict = None) -> bool:
        """Save Q-table snapshot to database."""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            # Serialize Q-table (pickle + base64 for PostgreSQL)
            q_table_bytes = pickle.dumps(q_table)
            
            # Calculate statistics
            state_count = len(q_table)
            total_updates = metadata.get('decision_count', 0) if metadata else 0
            avg_reward = metadata.get('avg_reward', 0.0) if metadata else 0.0
            
            # Get current version
            cur.execute("SELECT MAX(version) FROM q_table_snapshots")
            max_version = cur.fetchone()[0]
            new_version = (max_version or 0) + 1
            
            # Insert snapshot
            cur.execute("""
                INSERT INTO q_table_snapshots 
                (version, q_table_data, state_count, total_updates, avg_reward, epsilon, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                new_version,
                q_table_bytes,
                state_count,
                total_updates,
                avg_reward,
                epsilon,
                f"Auto-save at {datetime.now().isoformat()}"
            ))
            
            # Update metadata
            cur.execute("""
                INSERT INTO q_table_metadata (key, value, updated_at)
                VALUES ('latest_version', %s, NOW())
                ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()
            """, (str(new_version),))
            
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"✅ Saved Q-table version {new_version} ({state_count} states, ε={epsilon:.3f})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save Q-table: {e}")
            return False
    
    def load_q_table(self, version: Optional[int] = None) -> Tuple[Dict, float]:
        """Load Q-table from database. Returns (q_table, epsilon)."""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            if version is None:
                # Load latest version
                cur.execute("""
                    SELECT q_table_data, epsilon
                    FROM q_table_snapshots
                    ORDER BY version DESC
                    LIMIT 1
                """)
            else:
                # Load specific version
                cur.execute("""
                    SELECT q_table_data, epsilon
                    FROM q_table_snapshots
                    WHERE version = %s
                """, (version,))
            
            row = cur.fetchone()
            cur.close()
            conn.close()
            
            if row:
                q_table = pickle.loads(bytes(row[0]))
                epsilon = float(row[1])
                logger.info(f"✅ Loaded Q-table ({len(q_table)} states, ε={epsilon:.3f})")
                return q_table, epsilon
            else:
                logger.warning("No Q-table found in database, starting fresh")
                return {}, 0.35  # Default epsilon
                
        except Exception as e:
            logger.error(f"Failed to load Q-table: {e}")
            return {}, 0.35
    
    def get_q_table_history(self, limit: int = 10) -> list:
        """Get Q-table version history."""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT version, state_count, total_updates, avg_reward, epsilon, created_at
                FROM q_table_snapshots
                ORDER BY version DESC
                LIMIT %s
            """, (limit,))
            
            history = []
            for row in cur.fetchall():
                history.append({
                    'version': row[0],
                    'state_count': row[1],
                    'total_updates': row[2],
                    'avg_reward': float(row[3]) if row[3] else 0.0,
                    'epsilon': float(row[4]),
                    'created_at': row[5].isoformat()
                })
            
            cur.close()
            conn.close()
            return history
            
        except Exception as e:
            logger.error(f"Failed to get Q-table history: {e}")
            return []
    
    def cleanup_old_versions(self, keep_last: int = 5):
        """Delete old Q-table versions to save space."""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            cur.execute("""
                DELETE FROM q_table_snapshots
                WHERE version NOT IN (
                    SELECT version FROM q_table_snapshots
                    ORDER BY version DESC
                    LIMIT %s
                )
            """, (keep_last,))
            
            deleted = cur.rowcount
            conn.commit()
            cur.close()
            conn.close()
            
            if deleted > 0:
                logger.info(f"🧹 Cleaned up {deleted} old Q-table versions")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to cleanup Q-table versions: {e}")
            return 0


# Integration with DeceptionAgent
def integrate_persistence_with_agent():
    """Example of how to integrate persistence with the DeceptionAgent."""
    from ai_agent.deception_agent import DeceptionAgent
    
    # Initialize agent
    agent = DeceptionAgent()
    persistence = QTablePersistence()
    
    # Load existing Q-table if available
    q_table, epsilon = persistence.load_q_table()
    agent.q_table = q_table
    agent.epsilon = epsilon
    
    # ... agent makes decisions ...
    
    # Periodically save Q-table (e.g., every 100 decisions)
    if agent.decision_count % 100 == 0:
        metadata = {
            'decision_count': agent.decision_count,
            'avg_reward': 5.0  # Calculate from recent rewards
        }
        persistence.save_q_table(agent.q_table, agent.epsilon, metadata)
    
    return agent


if __name__ == "__main__":
    # Test persistence
    persistence = QTablePersistence()
    
    # Create dummy Q-table
    from ai_agent.deception_agent import ActionType, DeceptionState
    
    dummy_q_table = {
        ('SSH', 5, 0, 1, 60, 'auth', 0.5): {
            ActionType.MAINTAIN: 2.5,
            ActionType.INJECT_DELAY: 3.0,
            ActionType.SWAP_SERVICE_BANNER: 1.5,
            ActionType.PRESENT_LURE: 4.2,
            ActionType.DROP_SESSION: 1.0
        }
    }
    
    # Save
    persistence.save_q_table(dummy_q_table, epsilon=0.25, metadata={'decision_count': 150, 'avg_reward': 3.5})
    
    # Load
    loaded_q_table, loaded_epsilon = persistence.load_q_table()
    print(f"Loaded {len(loaded_q_table)} states with epsilon={loaded_epsilon}")
    
    # History
    history = persistence.get_q_table_history()
    print(f"\nQ-Table History ({len(history)} versions):")
    for h in history:
        print(f"  v{h['version']}: {h['state_count']} states, ε={h['epsilon']:.3f}, avg_reward={h['avg_reward']:.2f}")
