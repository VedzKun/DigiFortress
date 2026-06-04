# DigiFortress Project Charter

## 1. Executive Summary
DigiFortress is an advanced, secure Large Language Model (LLM) agent architecture designed to address the vulnerabilities of persistent semantic memory in autonomous agents. Autonomous agents retrieving historical semantic memory are prone to prompt injections, poisoned memories, and logical contradictions. DigiFortress implements a multi-tier active validation pipeline combining rule-based checks, dynamic LLM-based verification, source-reputation metrics, and a dynamic risk calculation engine to ensure that only trusted beliefs are ingested, versioned, and recalled.

---

## 2. Core Objectives
- **Secure Semantic Persistence**: Prevent adversarial inputs and system-override attempts from entering long-term memory stores.
- **Logical Contradiction Prevention**: Detect and resolve contradictions between new statements and established historical memories.
- **Comprehensive Audit Trail**: Maintain a tamper-evident audit database tracking all memory modification events, source reliability, and risk evaluations.
- **Performant Retrievals**: Ensure reasoning layer dynamically decides when memory queries are necessary, mitigating latency and token cost.

---

## 3. Scope Statement

### In-Scope
1. **Dynamic Ingestion Defense**: Multi-weight validation (`TrustScorer`, `LLMTrustScorer`, source reputations).
2. **Conflict Resolution**: Real-time evaluation of semantic overlap utilizing local LLMs.
3. **Quarantine Mechanisms**: Safe isolation of low-trust inputs for administrative review.
4. **Adversarial Wave Simulator**: Pre-configured attack injection suites testing security boundary defenses.
5. **Interactive Console & Visual Dashboards**: Real-time KPI charts, logs, and interactive administration panels.

### Out-of-Scope
1. External Cloud Vector Databases (DigiFortress enforces local, self-hosted, offline-capable configurations).
2. Multi-user role authorization systems (RBAC is delegated to the host deployment wrapper).

---

## 4. Key Performance & Security Targets

| Metric | Target | Verification Method |
| --- | --- | --- |
| **Defense Success Rate** | $\ge 95\%$ of simulated attacks blocked | Adversarial Wave Simulator run via Web UI |
| **Trust Evaluation Latency** | $< 1.5\text{ seconds}$ | Step-by-step pipeline timers |
| **Risk Scoring Sensitivity** | Critical risk rating triggers on low reputation + high threat payload | Risk Engine calculations |
| **Data Integrity** | $0\%$ lost memories; $100\%$ version history | SQLite memory_versions logs check |

---

## 5. System Milestones

- [x] **Phase 1: Foundation (V1.0)**: Core memory storage with ChromaDB and short-term conversation context buffers.
- [x] **Phase 2: Validation Core (V2.0)**: Rule-based trust evaluation and LLM-driven conflict detectors.
- [x] **Phase 3: Source Reputation & Decay (V2.2)**: Source telemetry tracking and time-based memory decay formulas.
- [x] **Phase 4: Risk Auditing & Event Logging (V2.4)**: Real-time risk assessment scoring engine and SQL-based security event log trails.
- [ ] **Phase 5: Automated Recovery (V2.6)**: Administrative dashboard action to auto-rehab or purge quarantined nodes.

