from streamlit.elements import arrow
import sqlite3
from datetime import datetime

class SecurityDB:
    def __init__(self):
        self.conn = sqlite3.connect(
            "data/security.db",
            check_same_thread=False
        )
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.initialise_metrics()
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
            reputation REAL DEFAULT 0.0,
            decay_score REAL DEFAULT 1.0
        )
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics(
            metric_name TEXT PRIMARY KEY,
            metric_value INTEGER
        )
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS sources(
            source_name TEXT PRIMARY KEY,
            reputation REAL DEFAULT 0.5,
            accepted_count INTEGER DEFAULT 0,
            conflict_count INTEGER DEFAULT 0,
            quarantined_count INTEGER DEFAULT 0
        )""")
        self.conn.commit()
    
    def add_sources(self, source_name):
        self.cursor.execute("""
        INSERT OR IGNORE INTO sources(source_name,reputation)VALUES (?,?)""",(source_name,0.5))
        self.conn.commit()

    def get_source_reputation(self, source_name):
        self.cursor.execute("""
            SELECT reputation FROM sources 
            WHERE source_name = ?""",(source_name,))
        row = self.cursor.fetchone()
        if row:
            return row[0]
        return 0.5

    def update_source_reputation(self,source_name,status):
        self.add_sources(source_name)
        self.cursor.execute("""
        SELECT reputation,accepted_count,conflict_count,quarantined_count FROM sources WHERE source_name = ?
        """,(source_name,))
        row = self.cursor.fetchone()
        reputation = row[0]
        accepted = row[1]
        conflict = row[2]
        quarantined = row[3]
        if status == "accepted":
            reputation += 0.05
            accepted += 1
        elif status == "conflict":
            reputation -= 0.03
            conflict += 1
        elif status == "quarantined":
            reputation -= 0.10
            quarantined += 1
        reputation = max(0.0,min(1.0,reputation))

        self.cursor.execute("""
        UPDATE sources
        SET reputation = ?,accepted_count = ?,conflict_count = ?,quarantined_count = ?
        WHERE source_name = ?
        """,(reputation,accepted,conflict,quarantined,source_name))
        self.conn.commit()
    def get_all_sources(self):
        self.cursor.execute("""
        SELECT *
        FROM sources
        ORDER BY reputation DESC
        """)
        return self.cursor.fetchall()
    
    def initialise_metrics(self):
        metrics = ["accepted","conflict","quarantined","attack_attempts"]
        for metric in  metrics:
            self.cursor.execute("""
            INSERT OR IGNORE INTO metrics(
            metric_name, metric_value)
            VALUES(?,?)""",(metric,0))
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
        decay_score=1.0
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
            reputation,
            decay_score
        )
        VALUES (?,?,?,?,?,?,?,?,?,?)
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
            reputation,
            decay_score
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
        
    def calculate_decay(self,timestamp):
        created_time = datetime.fromisoformat(timestamp)
        age_days = (datetime.now() - created_time).days
        decay = max(0.3,1 - (age_days * 0.01))
        return decay
    def update_reputation(self, memory_id):
        self.cursor.execute("""
        SELECT
        trust_score,
        access_count,
        timestamp
        FROM memories
        WHERE memory_id = ?
        """,(memory_id,))
        row = self.cursor.fetchone()
        if not row:
            return
        trust_score = row[0]
        access_count = row[1]
        timestamp = row[2]
        decay_score = self.calculate_decay(timestamp)
        reputation = min(1.0,(trust_score * 0.5)+(decay_score * 0.3)+(min(access_count * 0.01,0.2)))
        self.cursor.execute("""
        UPDATE memories
        SET
        reputation = ?,
        decay_score = ?
        WHERE memory_id = ?
        """,(reputation,decay_score,memory_id))
        self.conn.commit()

    def get_memory(self,memory_id):
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
        decay_score
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
    def increment_metric(self, metric_name):
        self.cursor.execute("""
            UPDATE metrics
            SET metric_value =
            metric_value + 1
            WHERE metric_name = ?
            """,(metric_name,))
        self.conn.commit()
    def get_metric(self,metric_name):
        self.cursor.execute("""
        SELECT metric_value
        FROM metrics
        WHERE metric_name = ?
        """,
        (metric_name,)
        )
        row = self.cursor.fetchone()
        if row:
            return row[0]
        return 0
    def get_all_metrics(self):
        self.cursor.execute("""
        SELECT *
        FROM metrics""")
        return self.cursor.fetchall()