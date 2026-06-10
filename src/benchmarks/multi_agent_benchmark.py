import json
from src.database.security_db import SecurityDB
from src.benchmarks.benchmark_runner import BenchmarkRunner
from src.benchmarks.benchmark_report import BenchmarkReport

class MultiAgentBenchmark:
    """Orchestrator for running and reporting TD-2.7 benchmarks."""
    
    def __init__(self, security_db: SecurityDB | None = None, network_analyzer=None):
        self.db = security_db or SecurityDB()
        self.runner = BenchmarkRunner(self.db)
        self.analyzer = network_analyzer

    def execute_full_suite(self) -> dict:
        raw_results = self.runner.run_full_benchmark()
        report_engine = BenchmarkReport(raw_results, self.analyzer)
        report = report_engine.generate_report()
        return report

    def print_report(self, report: dict):
        print("\n" + "="*40)
        print("MULTI-AGENT BENCHMARK REPORT")
        print("="*40)
        print(json.dumps(report, indent=2))
        print("="*40 + "\n")
