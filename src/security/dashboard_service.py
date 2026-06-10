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

        return {
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
            "unknown_agents": unknown_agents
        }
