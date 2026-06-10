from src.graph.agent_network_graph import AgentNetworkGraph
from src.graph.trust_network import TrustNetwork
from src.graph.influence_tracker import InfluenceTracker
from src.graph.network_analyzer import NetworkAnalyzer

class DashboardService:
    def __init__(self, security_db):
        self.db = security_db

    def get_summary(self):
        analytics = self.db.get_memory_analytics()
        total_trust = 0
        count = 0
        for row in analytics:
            trust = row[1]
            total_trust += trust
            count += 1
        avg_trust = (total_trust / count) if count > 0 else 0.0

        metrics = self.db.get_metrics()
        accepted = metrics.get("accepted", 0)
        conflict = metrics.get("conflict", 0)
        quarantined = metrics.get("quarantined", 0)
        attack_attempts = metrics.get("attack_attempts", 0)
        auth_success = metrics.get("auth_success", 0)
        auth_failed = metrics.get("auth_failed", 0)
        spoof_attempts = metrics.get("spoof_attempts", 0)
        unknown_agents = metrics.get("unknown_agents", 0)
        cross_agent_conflicts = metrics.get("cross_agent_conflicts", 0)
        resolved_conflicts = metrics.get("resolved_conflicts", 0)
        unresolved_conflicts = metrics.get("unresolved_conflicts", 0)
        poisoning_attempts = metrics.get("poisoning_attempts", 0)
        successful_containments = metrics.get("successful_containments", 0)
        compromised_agents = metrics.get("compromised_agents", 0)

        events = self.db.get_security_events()
        total_risk = sum(event[5] for event in events)
        avg_risk = (total_risk / len(events)) if events else 0.0

        red_team_res = self.db.get_red_team_res()
        if red_team_res:
            security_score = red_team_res[0][6]
        else:
            if attack_attempts > 0:
                security_score = min(100.0, ((conflict + quarantined) / attack_attempts) * 100.0)
            else:
                security_score = 100.0

        top_threats = self.db.get_source_reputations()[:5]
        recent_events = events[:5]

        result = {
            "accepted": accepted,
            "conflict": conflict,
            "quarantined": quarantined,
            "avg_trust": round(avg_trust, 2),
            "avg_risk": round(avg_risk, 2),
            "security_score": round(security_score, 2),
            "top_threat_sources": top_threats,
            "recent_events": recent_events,
            "auth_success": auth_success,
            "auth_failed": auth_failed,
            "spoof_attempts": spoof_attempts,
            "unknown_agents": unknown_agents,
            "cross_agent_conflicts": cross_agent_conflicts,
            "resolved_conflicts": resolved_conflicts,
            "unresolved_conflicts": unresolved_conflicts,
            "poisoning_attempts": poisoning_attempts,
            "successful_containments": successful_containments,
            "compromised_agents": compromised_agents
        }

        # TD-2.6 Graph Metrics
        graph = AgentNetworkGraph(self.db)
        graph.load_graph()
        trust_net = TrustNetwork(graph)
        influence = InfluenceTracker(graph)
        analyzer = NetworkAnalyzer(graph)
        
        most_trusted = trust_net.get_most_trusted_agents()
        least_trusted = trust_net.get_least_trusted_agents()
        most_influential = influence.get_top_influencers()
        critical_agents = analyzer.find_critical_agents()
        
        result["network_trust_score"] = round(trust_net.calculate_network_trust(), 2)
        result["most_trusted_agent"] = most_trusted[0][0] if most_trusted else "None"
        result["least_trusted_agent"] = least_trusted[0][0] if least_trusted else "None"
        result["most_influential_agent"] = most_influential[0][0] if most_influential else "None"
        result["most_critical_agent"] = critical_agents[0][0] if critical_agents else "None"
        result["total_connections"] = metrics.get("total_connections", 0)

        # TD-2.7 Benchmark metrics
        bm_total = metrics.get("benchmark_attacks_run", 0)
        bm_detected = metrics.get("benchmark_detected", 0)
        bm_blocked = metrics.get("benchmark_blocked", 0)
        bm_contained = metrics.get("benchmark_contained", 0)
        bm_compromised = metrics.get("compromised_agents", 0) 
        
        if bm_total > 0:
            bm_det_rate = (bm_detected / bm_total) * 100
            bm_cont_rate = (bm_contained / bm_total) * 100
            bm_prop_rate = (bm_compromised / bm_total) * 100
            resilience_score = max(0.0, min(100.0, 100 - bm_prop_rate - (bm_compromised/bm_total)*100 + bm_cont_rate))
        else:
            bm_det_rate = bm_cont_rate = bm_prop_rate = 0.0
            resilience_score = 100.0
            
        result["network_resilience_score"] = round(resilience_score, 1)
        result["attack_detection_rate"] = round(bm_det_rate, 1)
        result["containment_rate"] = round(bm_cont_rate, 1)
        result["propagation_rate"] = round(bm_prop_rate, 1)

        return result
