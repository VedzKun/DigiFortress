from datetime import datetime

class BurstDetector:
    def detect_burst(self, timestamps):
        if len(timestamps) < 5:
            return False
        timestamps = sorted(timestamps)
        first = datetime.fromisoformat(timestamps[0])
        last = datetime.fromisoformat(timestamps[-1])
        delta = (last-first).total_seconds()
        return delta <= 60
        
        