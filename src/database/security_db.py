import sqlite3
from datetime import datetime

class SecurityDB:
    def __init__(self):
        self.conn = sqlite3.connect(
            "data/security.db"
        )
        self.cursor = self.conn.cursor()
        self.create_tables()
    def create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories(
            memory_id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            trust_score REAL NOT NULL,
            status TEXT NOT NULL,
            source TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            access_count INTEGER DEFAULT 0,
            last_accessed TEXT,
            reputation REAL DEFAULT 0.0

        )
        """)
        self.conn.commit()
    def add_memory(
        self,
        memory_id,
        content,
        trust_score,
        status,
        source,
        timestamp
    ):
        reputation = trust_score
        self.cursor.execute("""
        INSERT INTO memories(
            memory_id,
            content,
            trust_score,
            status,
            source,
            timestamp,
            access_count,
            last_accessed,
            reputation

        )
        VALUES (?,?,?,?,?,?,?,?,?)
        """,
        (
            memory_id,
            content,
            trust_score,
            status,
            source,
            timestamp,
            0,
            None,
            reputation
        ))
        self.conn.commit()
    def update_access(
        self,
        memory_id
    ):
        self.cursor.execute("""
        UPDATE memories
        SET
        access_count =
        access_count + 1,
        last_accessed = ?
        WHERE memory_id = ?
        """,
        (
            str(datetime.now()),
            memory_id
        ))
        self.conn.commit()
        self.update_reputation(memory_id)
    def update_reputation(
        self,
        memory_id
    ):
        self.cursor.execute("""
        SELECT
        trust_score,
        access_count
        FROM memories
        WHERE memory_id = ?
        """,
        (memory_id,)
        )
        row = self.cursor.fetchone()
        if not row:
            return
        trust_score = row[0]
        access_count = row[1]
        reputation = min(
            1.0,
            trust_score + (access_count * 0.01)
        )
        self.cursor.execute("""
        UPDATE memories
        SET reputation = ?
        WHERE memory_id = ?
        """,
        (
            reputation,
            memory_id
        ))

        self.conn.commit()
    def get_memory(
        self,
        memory_id
    ):

        self.cursor.execute("""
        SELECT *

        FROM memories

        WHERE memory_id = ?
        """,
        (memory_id,)
        )
        return self.cursor.fetchone()
    def get_all_memories(self):
        self.cursor.execute("""
        SELECT *
        FROM memories
        """)

        return self.cursor.fetchall()

    def get_accepted_memories(self):
        self.cursor.execute("""
        SELECT *
        FROM memories
        WHERE status = 'accepted'
        """)
        return self.cursor.fetchall()
    def get_memories_by_reputation(self):
        self.cursor.execute("""
        SELECT *
        FROM memories
        WHERE status = 'accepted'
        ORDER BY reputation DESC
        """)
        return self.cursor.fetchall()

    def get_memory_analytics(self):
        self.cursor.execute("""
        SELECT
        content,
        trust_score,
        access_count,
        reputation,
        last_accessed
        FROM memories
        ORDER BY reputation DESC
        """)
        return self.cursor.fetchall()
    def delete_memory(
        self,
        memory_id
    ):
        self.cursor.execute("""
        DELETE FROM memories
        WHERE memory_id = ?
        """,
        (memory_id,)
        )
        self.conn.commit()
    def close(self):
        self.conn.close()