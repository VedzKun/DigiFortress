from datetime import datetime
from src.database.database_service import DatabaseService

class SecurityDB:
    def __init__(self):
        self.db_service = DatabaseService()
        self.create_tables()
        self.initialise_metrics()

    def create_tables(self):
        self.db_service.execute_write("""
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
        self.db_service.execute_write("""
        CREATE TABLE IF NOT EXISTS metrics(
            metric_name TEXT PRIMARY KEY,
            metric_value INTEGER
        )
        """)
        self.db_service.execute_write("""
        CREATE TABLE IF NOT EXISTS sources(
            source_name TEXT PRIMARY KEY,
            reputation REAL DEFAULT 0.5,
            accepted_count INTEGER DEFAULT 0,
            conflict_count INTEGER DEFAULT 0,
            quarantined_count INTEGER DEFAULT 0
        )""")
        self.db_service.execute_write("""
        CREATE TABLE IF NOT EXISTS memory_versions(
        version_id INTEGER PRIMARY KEY AUTOINCREMENT,
        memory_group TEXT,
        content TEXT,
        timestamp TEXT,
        source TEXT,
        trust_score REAL)
        """)
        self.db_service.execute_write("""
        CREATE TABLE IF NOT EXISTS security_events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT,
        memory_content TEXT,
        source TEXT,
        status TEXT,
        risk_score REAL,
        risk_level TEXT,
        timestamp TEXT)""")
        self.db_service.execute_write("""
        CREATE TABLE IF NOT EXISTS red_team_results(
        test_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        total_attacks INTEGER,
        blocked INTEGER,
        missed INTEGER,
        detection_rate REAL,
        security_score REAL)""")
        self.db_service.execute_write("DROP TABLE IF EXISTS session_activity")
        self.db_service.execute_write("""
        CREATE TABLE IF NOT EXISTS session_activity(
        activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        timestamp TEXT,
        memory_content TEXT)""")
        self.db_service.execute_write("""
        CREATE TABLE IF NOT EXISTS counterfactual_audits(
        audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT,
        normal_response TEXT,
        normal_judgment TEXT,
        counterfactual_response TEXT,
        counterfactual_judgment TEXT,
        divergence REAL,
        judgment_divergence INTEGER,
        timestamp TEXT)""")
        self.db_service.execute_write("""
        CREATE TABLE IF NOT EXISTS agent_registry(
        agent_id TEXT PRIMARY KEY,
        agent_name TEXT,
        agent_type TEXT,
        reputation REAL DEFAULT 0.5,
        created_at TEXT)""")
        self.db_service.execute_write("""
        CREATE TABLE IF NOT EXISTS agent_reputation(
        agent_id TEXT PRIMARY KEY,
        reputation REAL DEFAULT 0.5,
        accepted_count INTEGER DEFAULT 0,
        conflict_count INTEGER DEFAULT 0,
        quarantine_count INTEGER DEFAULT 0,
        last_updated TEXT)""")
        self.db_service.execute_write("""
        CREATE TABLE IF NOT EXISTS agent_credentials(
        agent_id TEXT PRIMARY KEY,
        secret_key TEXT,
        created_at TEXT)""")
        self.db_service.execute_write("""
        CREATE TABLE IF NOT EXISTS cross_agent_events(
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        claim_a TEXT,
        claim_b TEXT,
        winner TEXT,
        timestamp TEXT)""")
        self.db_service.execute_write("""
        CREATE TABLE IF NOT EXISTS agent_poison_events(
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        attacker_agent TEXT,
        target_agent TEXT,
        attack_type TEXT,
        status TEXT,
        timestamp TEXT)""")
        self.db_service.execute_write("""
        CREATE TABLE IF NOT EXISTS agent_propagation_events(
        source_agent TEXT,
        target_agent TEXT,
        attack_depth INTEGER,
        timestamp TEXT)""")
        self.db_service.execute_write("""
        CREATE TABLE IF NOT EXISTS agent_network_edges(
        source_agent TEXT,
        target_agent TEXT,
        trust_score REAL,
        message_count INTEGER,
        timestamp TEXT,
        PRIMARY KEY (source_agent, target_agent))""")
        self.db_service.execute_write("""
        CREATE TABLE IF NOT EXISTS policies(
        policy_id TEXT PRIMARY KEY,
        name TEXT,
        description TEXT,
        action_type TEXT,
        created_at TEXT)""")
        self.db_service.execute_write("""
        CREATE TABLE IF NOT EXISTS policy_events(
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        policy_id TEXT,
        content TEXT,
        action_taken TEXT,
        timestamp TEXT)""")
        self.db_service.execute_write("""
        CREATE TABLE IF NOT EXISTS agentpoison_sessions(
        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
        trigger_phrase TEXT,
        malicious_action TEXT,
        n_poison INTEGER,
        retrieval_asr REAL,
        e2e_asr REAL,
        benign_degradation REAL,
        timestamp TEXT)""")

    def session_logger(self, session_id, memory_content, timestamp):
        self.db_service.execute_write("""
        INSERT INTO session_activity(session_id,timestamp,memory_content)
        VALUES(?,?,?)""", (session_id,timestamp,memory_content))
    
    def get_recent_write_count(self, session_id):
        result = self.db_service.execute_read("""
        SELECT COUNT(*) FROM session_activity WHERE session_id = ?""",(session_id,), fetchall=False)
        return result[0] if result else 0
    
    def get_session_summary(self, session_id):
        result = self.db_service.execute_read("""
        SELECT COUNT(*) FROM session_activity WHERE session_id = ?""",(session_id,), fetchall=False)
        return result

    def get_session_write_count(self, session_id):
        result = self.db_service.execute_read("""SELECT COUNT(*) FROM session_activity
        WHERE session_id = ?""",(session_id,), fetchall=False)
        return result[0] if result else 0

    def get_session_timestamps(self, session_id):
        rows = self.db_service.execute_read("""
        SELECT timestamp FROM session_activity WHERE session_id = ? ORDER BY timestamp DESC LIMIT 5""", (session_id,))
        return [row[0] for row in rows]

    def get_session_memory_count(self, session_id):
        result = self.db_service.execute_read("""
        SELECT COUNT(*) FROM session_activity WHERE session_id = ?""", (session_id,), fetchall=False)
        return result[0] if result else 0

    def save_read_team_res(self, timestamp, total_attacks, blocked, missed, detection_rate, security_score):
        self.db_service.execute_write("""
        INSERT INTO red_team_results(
        timestamp, total_attacks, blocked, missed, detection_rate, security_score)
        VALUES(?,?,?,?,?,?)""",(timestamp, total_attacks,blocked,missed,detection_rate,security_score))

    def get_red_team_res(self):
        return self.db_service.execute_read("""
        SELECT * FROM red_team_results ORDER BY test_id DESC""")

    def get_source_reputations(self):
        return self.db_service.execute_read("""
        SELECT
            source_name,
            reputation
        FROM sources
        ORDER BY reputation ASC
        """)

    def get_metrics(self):
        rows = self.db_service.execute_read("SELECT metric_name, metric_value FROM metrics")
        return {row[0]: row[1] for row in rows}

    def log_security_event(self,event_type, memory_content, source, status, risk_score, risk_level, timestamp):
        self.db_service.execute_write("""
        INSERT INTO security_events(
        event_type, memory_content, source, status, risk_score, risk_level, timestamp)
        VALUES (?,?,?,?,?,?,?)""",(event_type, memory_content, source, status, risk_score, risk_level, timestamp))
    
    def get_security_events(self):
        return self.db_service.execute_read("""
        SELECT * FROM security_events
        ORDER BY event_id DESC""")

    def add_memory_version(self, memory_group, content, timestamp, source, trust_score):
        self.db_service.execute_write("""
        INSERT INTO memory_versions(
        memory_group, content, timestamp, source, trust_score) 
        VALUES (?,?,?,?,?)
        """, (memory_group, content, timestamp, source, trust_score))

    def get_memory_versions(self, memory_group):
        return self.db_service.execute_read("""
        SELECT * FROM memory_versions
        WHERE memory_group = ?
        ORDER BY version_id
        """,(memory_group,))

    def add_sources(self, source_name):
        self.db_service.execute_write("""
        INSERT OR IGNORE INTO sources(source_name,reputation)VALUES (?,?)""",(source_name,0.5))

    def get_source_reputation(self, source_name):
        row = self.db_service.execute_read("""
            SELECT reputation FROM sources 
            WHERE source_name = ?""",(source_name,), fetchall=False)
        if row:
            return row[0]
        return 0.5

    def update_source_reputation(self,source_name,status):
        self.add_sources(source_name)
        row = self.db_service.execute_read("""
        SELECT reputation,accepted_count,conflict_count,quarantined_count FROM sources WHERE source_name = ?
        """,(source_name,), fetchall=False)
        if not row: return
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

        self.db_service.execute_write("""
        UPDATE sources
        SET reputation = ?,accepted_count = ?,conflict_count = ?,quarantined_count = ?
        WHERE source_name = ?
        """,(reputation,accepted,conflict,quarantined,source_name))

    def get_all_sources(self):
        return self.db_service.execute_read("""
        SELECT *
        FROM sources
        ORDER BY reputation DESC
        """)
    
    def initialise_metrics(self):
        metrics = ["accepted","conflict","quarantined","attack_attempts", "auth_success", "auth_failed", "spoof_attempts", "unknown_agents",
                   "cross_agent_conflicts", "resolved_conflicts", "unresolved_conflicts", 
                   "poisoning_attempts", "successful_containments", "compromised_agents",
                   "total_connections", "benchmark_attacks_run", "benchmark_detected", "benchmark_blocked", "benchmark_contained",
                   "agentpoison_runs", "agentpoison_poison_injected"]
        for metric in  metrics:
            self.db_service.execute_write("""
            INSERT OR IGNORE INTO metrics(
            metric_name, metric_value)
            VALUES(?,?)""",(metric,0))
        
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
        self.db_service.execute_write("""
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

    def update_access(
        self,
        memory_id
    ):
        self.db_service.execute_write("""
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
        self.update_reputation(memory_id)
        
    def calculate_decay(self,timestamp):
        created_time = datetime.fromisoformat(timestamp)
        age_days = (datetime.now() - created_time).days
        decay = max(0.3,1 - (age_days * 0.01))
        return decay

    def update_reputation(self, memory_id):
        row = self.db_service.execute_read("""
        SELECT
        trust_score,
        access_count,
        timestamp
        FROM memories
        WHERE memory_id = ?
        """,(memory_id,), fetchall=False)
        if not row:
            return
        trust_score = row[0]
        access_count = row[1]
        timestamp = row[2]
        decay_score = self.calculate_decay(timestamp)
        reputation = min(1.0,(trust_score * 0.5)+(decay_score * 0.3)+(min(access_count * 0.01,0.2)))
        self.db_service.execute_write("""
        UPDATE memories
        SET
        reputation = ?,
        decay_score = ?
        WHERE memory_id = ?
        """,(reputation,decay_score,memory_id))

    def get_memory(self,memory_id):
        return self.db_service.execute_read("""
        SELECT *
        FROM memories
        WHERE memory_id = ?
        """,
        (memory_id,), fetchall=False
        )

    def get_all_memories(self):
        return self.db_service.execute_read("""
        SELECT *
        FROM memories
        """)

    def get_accepted_memories(self):
        return self.db_service.execute_read("""
        SELECT *
        FROM memories
        WHERE status = 'accepted'
        """)

    def get_memories_by_reputation(self):
        return self.db_service.execute_read("""
        SELECT *
        FROM memories
        WHERE status = 'accepted'
        ORDER BY reputation DESC
        """)

    def get_memory_analytics(self):
        return self.db_service.execute_read("""
        SELECT
        content,
        trust_score,
        access_count,
        reputation,
        decay_score,
        last_accessed
        FROM memories
        ORDER BY reputation DESC
        """)

    def delete_memory(
        self,
        memory_id
    ):
        self.db_service.execute_write("""
        DELETE FROM memories
        WHERE memory_id = ?
        """,
        (memory_id,)
        )

    def close(self):
        pass

    def increment_metric(self, metric_name):
        self.db_service.execute_write("""
            UPDATE metrics
            SET metric_value =
            metric_value + 1
            WHERE metric_name = ?
            """,(metric_name,))

    def get_metric(self,metric_name):
        row = self.db_service.execute_read("""
        SELECT metric_value
        FROM metrics
        WHERE metric_name = ?
        """,
        (metric_name,), fetchall=False
        )
        if row:
            return row[0]
        return 0

    def get_all_metrics(self):
        return self.db_service.execute_read("""
        SELECT *
        FROM metrics""")

    def insert_counterfactual(self, query, normal_response, normal_judgment, counterfactual_response, counterfactual_judgment, divergence, judgment_divergence):
        timestamp = str(datetime.now())
        self.db_service.execute_write("""
        INSERT INTO counterfactual_audits(
        query, normal_response, normal_judgment, counterfactual_response, counterfactual_judgment, divergence, judgment_divergence, timestamp)
        VALUES (?,?,?,?,?,?,?,?)
        """, (query, normal_response, normal_judgment, counterfactual_response, counterfactual_judgment, divergence, int(judgment_divergence), timestamp))

    # ── Agent Registry ────────────────────────────────────────────────────────

    def register_agent(self, agent_id, agent_name, agent_type):
        """Insert a new agent with default reputation 0.50."""
        created_at = str(datetime.now())
        self.db_service.execute_write("""
        INSERT OR IGNORE INTO agent_registry(agent_id, agent_name, agent_type, reputation, created_at)
        VALUES (?, ?, ?, ?, ?)""", (agent_id, agent_name, agent_type, 0.5, created_at))
        self.db_service.execute_write("""
        INSERT OR IGNORE INTO agent_reputation(agent_id, reputation, last_updated)
        VALUES (?, ?, ?)""", (agent_id, 0.5, created_at))

    def get_agent(self, agent_id):
        """Return a single agent row by ID."""
        return self.db_service.execute_read("""
        SELECT agent_id, agent_name, agent_type, reputation, created_at
        FROM agent_registry WHERE agent_id = ?""", (agent_id,), fetchall=False)

    def get_all_agents(self):
        """Return all registered agents ordered by reputation descending."""
        return self.db_service.execute_read("""
        SELECT agent_id, agent_name, agent_type, reputation, created_at
        FROM agent_registry ORDER BY reputation DESC""")

    def update_agent(self, agent_id, agent_name=None, agent_type=None):
        """Update mutable fields on an agent record."""
        if agent_name is not None:
            self.db_service.execute_write("""
            UPDATE agent_registry SET agent_name = ? WHERE agent_id = ?""",
            (agent_name, agent_id))
        if agent_type is not None:
            self.db_service.execute_write("""
            UPDATE agent_registry SET agent_type = ? WHERE agent_id = ?""",
            (agent_type, agent_id))

    def delete_agent(self, agent_id):
        """Remove an agent and its reputation record."""
        self.db_service.execute_write(
            "DELETE FROM agent_registry WHERE agent_id = ?", (agent_id,))
        self.db_service.execute_write(
            "DELETE FROM agent_reputation WHERE agent_id = ?", (agent_id,))
        self.delete_agent_credentials(agent_id)

    # ── Agent Credentials ─────────────────────────────────────────────────────

    def add_agent_credentials(self, agent_id, secret_key):
        created_at = str(datetime.now())
        self.db_service.execute_write("""
        INSERT OR IGNORE INTO agent_credentials(agent_id, secret_key, created_at)
        VALUES (?, ?, ?)""", (agent_id, secret_key, created_at))

    def get_agent_secret(self, agent_id):
        row = self.db_service.execute_read("""
        SELECT secret_key FROM agent_credentials WHERE agent_id = ?""", (agent_id,), fetchall=False)
        if row:
            return row[0]
        return None

    def delete_agent_credentials(self, agent_id):
        self.db_service.execute_write(
            "DELETE FROM agent_credentials WHERE agent_id = ?", (agent_id,))

    # ── Agent Reputation ──────────────────────────────────────────────────────

    def get_agent_reputation(self, agent_id):
        """Return (reputation, accepted, conflict, quarantine, last_updated) or None."""
        return self.db_service.execute_read("""
        SELECT reputation, accepted_count, conflict_count, quarantine_count, last_updated
        FROM agent_reputation WHERE agent_id = ?""", (agent_id,), fetchall=False)

    def update_agent_reputation(self, agent_id, event_type):
        """
        Apply a reputation delta based on event_type:
          accepted          → +0.05
          conflict          → -0.10
          quarantine        → -0.15
          security_incident → -0.25
        Clamped to [0.00, 1.00]. Syncs reputation to agent_registry as well.
        """
        DELTAS = {
            "accepted":           +0.05,
            "conflict":           -0.10,
            "quarantine":         -0.15,
            "security_incident":  -0.25,
        }
        row = self.get_agent_reputation(agent_id)
        if row is None:
            return
        reputation, accepted, conflict, quarantine, _ = row
        delta = DELTAS.get(event_type, 0.0)
        reputation = max(0.0, min(1.0, reputation + delta))
        last_updated = str(datetime.now())
        if event_type == "accepted":
            accepted += 1
        elif event_type == "conflict":
            conflict += 1
        elif event_type in ("quarantine", "security_incident"):
            quarantine += 1
        self.db_service.execute_write("""
        UPDATE agent_reputation
        SET reputation = ?, accepted_count = ?, conflict_count = ?,
            quarantine_count = ?, last_updated = ?
        WHERE agent_id = ?""",
        (reputation, accepted, conflict, quarantine, last_updated, agent_id))
        self.db_service.execute_write("""
        UPDATE agent_registry SET reputation = ? WHERE agent_id = ?""",
        (reputation, agent_id))

    def get_all_agent_reputations(self):
        """Return all agent reputation rows joined with agent names."""
        return self.db_service.execute_read("""
        SELECT r.agent_id, a.agent_name, a.agent_type,
               r.reputation, r.accepted_count, r.conflict_count,
               r.quarantine_count, r.last_updated
        FROM agent_reputation r
        JOIN agent_registry a ON r.agent_id = a.agent_id
        ORDER BY r.reputation DESC""")

    # ── Cross-Agent & Poisoning Events ───────────────────────────────────────

    def log_cross_agent_event(self, claim_a, claim_b, winner, timestamp):
        self.db_service.execute_write("""
        INSERT INTO cross_agent_events(claim_a, claim_b, winner, timestamp)
        VALUES (?, ?, ?, ?)""", (claim_a, claim_b, winner, timestamp))

    def log_agent_poison_event(self, attacker_agent, target_agent, attack_type, status, timestamp):
        self.db_service.execute_write("""
        INSERT INTO agent_poison_events(attacker_agent, target_agent, attack_type, status, timestamp)
        VALUES (?, ?, ?, ?, ?)""", (attacker_agent, target_agent, attack_type, status, timestamp))

    def log_agent_propagation_event(self, source_agent, target_agent, attack_depth, timestamp):
        self.db_service.execute_write("""
        INSERT INTO agent_propagation_events(source_agent, target_agent, attack_depth, timestamp)
        VALUES (?, ?, ?, ?)""", (source_agent, target_agent, attack_depth, timestamp))

    def get_agent_poison_events(self):
        return self.db_service.execute_read("""
        SELECT * FROM agent_poison_events ORDER BY event_id DESC""")

    # ── Agent Trust Network Graph ────────────────────────────────────────────

    def add_network_edge(self, source_agent, target_agent, trust_score, timestamp):
        self.db_service.execute_write("""
        INSERT INTO agent_network_edges(source_agent, target_agent, trust_score, message_count, timestamp)
        VALUES (?, ?, ?, 1, ?)
        ON CONFLICT(source_agent, target_agent) DO UPDATE SET
            message_count = message_count + 1,
            trust_score = ?,
            timestamp = ?
        """, (source_agent, target_agent, trust_score, timestamp, trust_score, timestamp))

    def get_network_edges(self):
        return self.db_service.execute_read("""
        SELECT * FROM agent_network_edges""")

    # ── Enterprise Policy Engine ──────────────────────────────────────────────

    def add_policy(self, policy_id, name, description, action_type):
        created_at = str(datetime.now())
        self.db_service.execute_write("""
        INSERT OR IGNORE INTO policies(policy_id, name, description, action_type, created_at)
        VALUES (?, ?, ?, ?, ?)""", (policy_id, name, description, action_type, created_at))

    def get_all_policies(self):
        return self.db_service.execute_read("""
        SELECT policy_id, name, description, action_type, created_at
        FROM policies ORDER BY created_at ASC""")

    def delete_policy(self, policy_id):
        self.db_service.execute_write("""
        DELETE FROM policies WHERE policy_id = ?""", (policy_id,))

    def log_policy_event(self, policy_id, content, action_taken, timestamp):
        self.db_service.execute_write("""
        INSERT INTO policy_events(policy_id, content, action_taken, timestamp)
        VALUES (?, ?, ?, ?)""", (policy_id, content, action_taken, timestamp))

    def get_policy_events(self):
        return self.db_service.execute_read("""
        SELECT * FROM policy_events ORDER BY event_id DESC""")

    # ── AgentPoison Sessions ──────────────────────────────────────────────────

    def log_agentpoison_session(
        self,
        trigger: str,
        malicious_action: str,
        n_poison: int,
        retrieval_asr: float,
        e2e_asr: float,
        benign_degradation: float,
    ) -> None:
        """Persist the results of one AgentPoison attack run."""
        timestamp = str(datetime.now())
        self.db_service.execute_write("""
        INSERT INTO agentpoison_sessions(
            trigger_phrase, malicious_action, n_poison,
            retrieval_asr, e2e_asr, benign_degradation, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (trigger, malicious_action, n_poison, retrieval_asr, e2e_asr, benign_degradation, timestamp))

    def get_agentpoison_sessions(self) -> list:
        """Return all logged AgentPoison sessions, newest first."""
        return self.db_service.execute_read("""
        SELECT session_id, trigger_phrase, malicious_action, n_poison,
               retrieval_asr, e2e_asr, benign_degradation, timestamp
        FROM agentpoison_sessions
        ORDER BY session_id DESC""")