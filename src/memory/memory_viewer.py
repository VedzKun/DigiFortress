# Memory viewer for inspecting and searching memories
class MemoryViewer:
    @staticmethod
    def display(memories):
        documents = memories["documents"]
        metadatas = memories["metadatas"]

        for doc, meta in zip(documents,metadatas):
            print("\n")
            print(f"Memory: {doc}")
            print(f"Category: {meta['category']}")
            print(f"Source: {meta['source']}")
            print(f"Timestamp: {meta['timestamp']}")
        