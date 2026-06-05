from src.redteam.attack_library import AttackLibrary
from datetime import datetime

class RedTeamEngine:
    def __init__(self, agent):
        self.agent = agent
        self.library = AttackLibrary()

    def run(self):
        attacks = self.library.get_attacks()
        total = 0 
        blocked = 0
        missed = 0
        print("RED TEAM TEST")
        for category, memories in attacks.items():
            print(f"Category: {category}")
            for attack in memories:
                total += 1
                result = self.agent.remember(attack, source="red_team")
                status = result['status']
                print(f"{attack} --> {status}")
                if status in ["quarantined", "conflict"]:
                    blocked += 1
                else:
                    missed += 1
        
        detection_rate = (blocked / total) * 100 if total > 0 else 0.0
        security_score = (blocked / total) * 100 if total > 0 else 0.0
        self.agent.security_db.save_red_team_res(timestamp=str(datetime.now()), total_attacks=total, blocked=blocked, missed=missed, detection_rate=detection_rate, security_score=security_score)
        print("RED TEAM REPORT")
        print(f"TOTAL ATTACKS: {total}")
        print(f"BLOCKED: {blocked}")
        print(f"MISSED: {missed}")
        print(f"DETECTION RATE: {detection_rate}%")
        print(f"SECURITY SCORE: {security_score}%")
        return {
            "total": total,
            "blocked": blocked,
            "missed": missed,
            "security_score": security_score
        }

        
        