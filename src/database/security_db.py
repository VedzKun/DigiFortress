# Empty file for security database.
from src import memory
from src import memory
import sqlite3

class SecurityDB:

    def __init__(self):
        self.conn = sqlite3.connect(
            "data/security.db"
        )
        self.cursor = self.conn.cursor()
        self.create_tables()
    def create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
        memory_id TEXT PRIMARY KEY,
        content TEXT,
        trust_score REAL,
        status TEXT,
        source TEXT,
        timestamp TEXT)""")
        self.conn.commit()

    def add_memory(self, memory_id, content, trust_score, status, source, timestamp):
        self.cursor.execute("""
        INSERT INTO memories VALUES (?,?,?,?,?,?)""", (memory_id, content, trust_score, status, source, timestamp))
        self.conn.commit()