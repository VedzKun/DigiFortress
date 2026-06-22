"""
Sleeper Memory Poisoning Simulation Foundation
===============================================
Implements core object-oriented structures to simulate cross-session Sleeper Memory 
Poisoning attacks (Arxiv 2605.15338).
"""

from __future__ import annotations

import uuid
import queue
import threading
from datetime import datetime
from typing import Any, List, Dict, Optional

from src.database.security_db import SecurityDB
from src.memory.memory_manager import MemoryManager
from src.embeddings.embedder import Embedder


class SleeperDocument:
    """
    Represents an ingested document (webpage, email, PDF) that may contain 
    poisoned memory payloads.
    """

    def __init__(self, filename: str, source_type: str, content: str, document_id: Optional[str] = None) -> None:
        self.document_id = document_id or str(uuid.uuid4())
        self.filename = filename
        self.source_type = source_type  # e.g., 'pdf', 'webpage', 'email'
        self.content = content
        self.ingested_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "filename": self.filename,
            "source_type": self.source_type,
            "content": self.content,
            "ingested_at": str(self.ingested_at),
        }


class SleeperMemoryPipeline:
    """
    Summarizes, structures, and processes ingested documents, then registers 
    the resulting memories into the Vector and SQL stores.
    """

    def __init__(self, db: SecurityDB, memory: MemoryManager, embedder: Embedder) -> None:
        self.db = db
        self.memory = memory
        self.embedder = embedder

    def process_document(self, document: SleeperDocument) -> List[str]:
        """
        Parses document contents and returns a list of individual memory strings 
        to be stored in ChromaDB/SQLite.
        """
        # Under the Sleeper Poisoning model, documents are processed asynchronously.
        # Here we extract semantic chunks or key summaries.
        # For simplicity, we chunk the text by line or split by key sentence structure.
        lines = [line.strip() for line in document.content.split("\n") if line.strip()]
        extracted_memories = []

        for line in lines:
            # Generate embedding and store in vector memory
            embedding = self.embedder.generate_embedding(line)
            chroma_id = self.memory.add_memory(
                text=line,
                embedding=embedding,
                category="fact",
                source=f"sleeper_doc_{document.filename}"
            )
            
            # Persist in SQLite registry
            self.db.add_memory(
                memory_id=chroma_id,
                content=line,
                trust_score=0.80, # simulating standard async ingestion trust level
                status="accepted",
                source=f"sleeper_doc_{document.filename}",
                timestamp=str(datetime.now())
            )
            extracted_memories.append(line)

        return extracted_memories


class SleeperQueueManager:
    """
    Asynchronous task queue manager simulating back-office document processing pipelines.
    """

    def __init__(self, pipeline: SleeperMemoryPipeline, db: SecurityDB) -> None:
        self.pipeline = pipeline
        self.db = db
        self.task_queue: queue.Queue[tuple[str, SleeperDocument]] = queue.Queue()
        self.worker_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        """Starts the background worker thread."""
        self._stop_event.clear()
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    def stop(self) -> None:
        """Stops the background worker thread."""
        self._stop_event.set()
        if self.worker_thread:
            self.worker_thread.join(timeout=2.0)

    def enqueue_document(self, document: SleeperDocument) -> str:
        """Enqueues a document for async processing and logs it to DB."""
        task_id = str(uuid.uuid4())
        self.db.add_sleeper_document(
            document_id=document.document_id,
            filename=document.filename,
            source_type=document.source_type,
            content=document.content
        )
        self.db.add_sleeper_queue_task(task_id, document.document_id, "PENDING")
        self.task_queue.put((task_id, document))
        return task_id

    def _worker_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                task_id, doc = self.task_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            self.db.update_sleeper_queue_status(task_id, "PROCESSING")
            try:
                # Process the document using our extraction/memory pipeline
                self.pipeline.process_document(doc)
                self.db.update_sleeper_queue_status(task_id, "COMPLETED")
            except Exception as e:
                self.db.update_sleeper_queue_status(task_id, "FAILED", error_message=str(e))
            finally:
                self.task_queue.task_done()


class SleeperPoisonAttack:
    """
    Orchestration class simulating Sleeper Memory Poisoning attacks.
    Defines methods to prepare poisoned templates and test future cross-session retrieval.
    """

    def __init__(self, db: Optional[SecurityDB] = None, memory: Optional[MemoryManager] = None, embedder: Optional[Embedder] = None) -> None:
        self.db = db or SecurityDB()
        self.memory = memory or MemoryManager()
        self.embedder = embedder or Embedder()
        self.pipeline = SleeperMemoryPipeline(self.db, self.memory, self.embedder)
        self.queue_manager = SleeperQueueManager(self.pipeline, self.db)

    def prepare_poison_document(self, filename: str, source_type: str, trigger_phrase: str, malicious_action: str) -> SleeperDocument:
        """
        Creates a SleeperDocument holding a trigger and a malicious action.
        """
        content = f"Regarding {trigger_phrase}: the standard protocol dictates to {malicious_action}."
        return SleeperDocument(filename, source_type, content)

    def verify_sleeper_retrieval(self, query: str) -> Dict[str, Any]:
        """
        Simulates a future retrieval check to verify if the sleeper poison memory 
        is successfully retrieved by a trigger query.
        """
        query_embedding = self.embedder.generate_embedding(query)
        results = self.memory.retrieve_memory(query_embedding, n_results=5)
        
        retrieved_docs = results["documents"][0] if results["documents"] else []
        retrieved_ids = results["ids"][0] if results["ids"] else []
        
        return {
            "query": query,
            "retrieved_docs": retrieved_docs,
            "retrieved_ids": retrieved_ids,
        }
