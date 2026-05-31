# Empty file for conflict detector.
class ConflictDetector:
    def detect(
        self,
        new_memory,
        retrieved_memories
    ):
        new_memory = new_memory.lower()
        for memory in retrieved_memories:
            memory = memory.lower()
            if (
                "prefer" in new_memory and 
                "prefer" in memory and
                new_memory != memory
            ):
                return True
        return False