from datetime import datetime
from src.database.security_db import SecurityDB
from src.security.consensus_engine import ConsensusEngine
from src.security.containment_engine import ContainmentEngine

class CrossAgentValidator:
    def __init__(self, security_db: SecurityDB | None = None):
        self.db = security_db or SecurityDB()
        self.consensus = ConsensusEngine()
        self.containment = ContainmentEngine(self.db)

    def detect_conflicts(self, claim_a: str, claim_b: str) -> bool:
        """
        Simple prototype conflict detection: Exact opposite matching or differing values.
        For TD-2.4, we assume claims that aren't identical on the same topic are conflicts.
        (In a full implementation, an LLM could be used here).
        """
        # Lowercase and strip
        ca = claim_a.lower().strip()
        cb = claim_b.lower().strip()
        if ca != cb:
            return True
        return False

    def validate_claims(self, claims_list: list) -> dict:
        """
        Given a list of AgentClaim objects (as dicts), detect conflicts and resolve them.
        Returns a dict with status, winning_claim, and conflict details.
        """
        if not claims_list:
            return {"status": "NO_CLAIMS", "winner": None}

        if len(claims_list) == 1:
            return {"status": "CONSENSUS", "winner": claims_list[0]}

        # Detect conflicts among claims
        has_conflict = False
        reference_claim = claims_list[0]['claim']
        
        for i in range(1, len(claims_list)):
            if self.detect_conflicts(reference_claim, claims_list[i]['claim']):
                has_conflict = True
                break

        if not has_conflict:
            return {"status": "CONSENSUS", "winner": claims_list[0]}

        # If conflict, resolve using reputation
        return self.resolve_conflict(claims_list)

    def resolve_conflict(self, claims_list: list) -> dict:
        """
        Resolves conflicts using ConsensusEngine, logs events, and handles containment.
        """
        # Fetch reputations for all involved agents
        reputations = {}
        for c in claims_list:
            agent_id = c['agent_id']
            rep_data = self.db.get_agent_reputation(agent_id)
            reputations[agent_id] = rep_data[0] if rep_data else 0.5

        winner = self.consensus.resolve_agent_conflict(claims_list, reputations)
        
        self.db.increment_metric("cross_agent_conflicts")
        
        if winner:
            self.db.increment_metric("resolved_conflicts")
            
            # Log cross agent event (just picking first two for logging)
            claim_a = claims_list[0]['claim']
            claim_b = claims_list[1]['claim']
            self.db.log_cross_agent_event(
                claim_a=claim_a,
                claim_b=claim_b,
                winner=winner['claim'],
                timestamp=str(datetime.now())
            )
            
            # The losing agents have conflicts
            for c in claims_list:
                if c['agent_id'] != winner['agent_id']:
                    # Update reputation
                    self.db.update_agent_reputation(c['agent_id'], "conflict")
                    # Check containment
                    if self.containment.check_and_quarantine(c['agent_id']):
                        print(f"Agent {c['agent_id']} quarantined due to multiple conflicts.")
            
            # Winner gets accepted
            self.db.update_agent_reputation(winner['agent_id'], "accepted")

            return {"status": "CONFLICT_RESOLVED", "winner": winner}
        else:
            self.db.increment_metric("unresolved_conflicts")
            return {"status": "UNRESOLVED", "winner": None}
