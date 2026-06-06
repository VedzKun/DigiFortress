# Benchmark configuration
# Change these to tune performance vs. accuracy trade-off.

# Model used by all LLM callers during benchmark runs.
# qwen2.5:3b  — fast (~45s/attack), good for 16GB RAM machines
# qwen2.5:7b  — accurate but slow (~120s/attack), use for production audits
BENCHMARK_MODEL = "qwen2.5:3b"

# Max parallel workers. Safe upper bound for 16GB RAM:
#   3b model uses ~2.2GB RAM per worker instance.
#   3 workers = ~6.6GB, leaves headroom for OS + app overhead.
# Increase to 4 only if you have a dedicated GPU with 8GB+ VRAM.
BENCHMARK_MAX_WORKERS = 3
