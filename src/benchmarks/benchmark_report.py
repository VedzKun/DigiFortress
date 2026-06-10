class BenchmarkReport:
    def __init__(self, raw_results: dict, network_analyzer=None):
        self.raw_results = raw_results
        self.analyzer = network_analyzer

    def generate_report(self) -> dict:
        total = self.raw_results.get("total_attacks", 1)
        if total == 0: total = 1

        detected = self.raw_results.get("detected", 0)
        blocked = self.raw_results.get("blocked", 0)
        contained = self.raw_results.get("contained", 0)
        compromised = self.raw_results.get("compromised", 0)

        propagation_percent = (compromised / total) * 100
        compromise_percent = (compromised / total) * 100
        containment_percent = (contained / total) * 100

        # Formula: 100 - Propagation % - Compromise % + Containment %
        resilience_score = 100 - propagation_percent - compromise_percent + containment_percent
        # Ensure it stays within logical bounds for display
        resilience_score = max(0.0, min(100.0, resilience_score))

        target_counts = self.raw_results.get("target_counts", {})
        most_targeted = max(target_counts, key=target_counts.get) if target_counts else "None"

        report = {
            "attacks": total,
            "detected": detected,
            "blocked": blocked,
            "contained": contained,
            "compromised": compromised,
            "resilience_score": round(resilience_score, 1),
            "most_targeted_agent": most_targeted,
        }

        # If network analyzer available, enrich report
        if self.analyzer:
            critical_agents = self.analyzer.find_critical_agents()
            report["top_risk_agent"] = critical_agents[0][0] if critical_agents else "None"
        else:
            report["top_risk_agent"] = "None"

        return report
