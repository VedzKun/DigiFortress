import sqlite3
import threading
import time

class DatabaseService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path="data/security.db"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseService, cls).__new__(cls)
                cls._instance._init_db(db_path)
            return cls._instance

    def _init_db(self, db_path):
        self.db_lock = threading.Lock()
        # check_same_thread=False allows sharing connection across ThreadPoolExecutor workers
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        # Enable WAL mode for better concurrency
        with self.db_lock:
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.commit()

    def execute_write(self, query, params=(), max_retries=5):
        """Executes a write operation with a thread-safe lock and retry logic."""
        retries = 0
        while retries < max_retries:
            try:
                with self.db_lock:
                    cursor = self.conn.cursor()
                    cursor.execute(query, params)
                    self.conn.commit()
                    # Return lastrowid if needed
                    return cursor.lastrowid
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e).lower():
                    retries += 1
                    time.sleep(0.1 * retries)  # Exponential backoff
                else:
                    raise e
            except Exception as e:
                with self.db_lock:
                    self.conn.rollback()
                raise e
        
        raise sqlite3.OperationalError(f"Database locked after {max_retries} retries for query: {query}")

    def execute_read(self, query, params=(), fetchall=True, max_retries=5):
        """Executes a read operation with retry logic."""
        retries = 0
        while retries < max_retries:
            try:
                with self.db_lock:
                    cursor = self.conn.cursor()
                    cursor.execute(query, params)
                    if fetchall:
                        return cursor.fetchall()
                    else:
                        return cursor.fetchone()
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e).lower():
                    retries += 1
                    time.sleep(0.1 * retries)
                else:
                    raise e
        raise sqlite3.OperationalError(f"Database locked after {max_retries} retries for query: {query}")

    def close(self):
        with self.db_lock:
            if self.conn:
                self.conn.close()
                self.conn = None
