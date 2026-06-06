import chromadb
import sqlite3
import os

def clear_chroma():
    try:
        client = chromadb.PersistentClient(path="data/chroma_db")
        collection = client.get_or_create_collection(name="agent_memory")
        results = collection.get()
        ids = results['ids']
        if ids:
            collection.delete(ids=ids)
            print(f"Deleted {len(ids)} documents from Chroma DB.")
        else:
            print("Chroma DB is already empty.")
    except Exception as e:
        print(f"Failed to clear Chroma DB: {e}")

def clear_sqlite():
    try:
        conn = sqlite3.connect("data/security.db")
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall() if row[0] != 'sqlite_sequence']
        
        for table in tables:
            cursor.execute(f"DELETE FROM {table};")
            print(f"Cleared table: {table}")
            
        conn.commit()
        conn.close()
        print("SQLite database cleared successfully.")
    except Exception as e:
        print(f"Failed to clear SQLite DB: {e}")

if __name__ == "__main__":
    clear_chroma()
    clear_sqlite()
