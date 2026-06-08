# DigiFortress System Architecture Design

This document details the software architecture, core math formulas, and database schema for DigiFortress.

---

## 🏗️ Technical Stack & Frameworks

- **Vector Memory DB**: [ChromaDB](https://www.trychroma.com/) (Persistent Local Client)
- **Embedding Vectorizer**: [HuggingFace Sentence Transformers](https://huggingface.co/sentence-transformers) (`all-MiniLM-L6-v2`, 384-dimensional dense vectors)
- **Orchestration LLM**: Local [Ollama](https://ollama.com/) Client (running `qwen2.5:3b`)
- **Web UI & Visualization**: Streamlit, Plotly, Pandas
- **Relational Auditing DB**: SQLite3

---

## 🧮 Core Algorithms & Mathematical Formulas

### 1. Active Trust Score
When a new memory is proposed, it is evaluated by the [Validator](file:///c:/Users/HP/DigiFortress/src/defenses/validator.py) using a combination of static rules, LLM analysis, and historical source reputation:

$$\text{Trust Score} = (S_{\text{rule}} \times 0.3) + (S_{\text{llm}} \times 0.5) + (R_{\text{source}} \times 0.2)$$

Where:
- $S_{\text{rule}}$: Rule-based static check score (0.0 to 1.0)
- $S_{\text{llm}}$: LLM-based prompt/trust evaluation score (0.0 to 1.0)
- $R_{\text{source}}$: Source reputation from the SQLite tracking database (0.0 to 1.0)

**Threshold Rule**: If $\text{Trust Score} < 0.4$, the memory is automatically classified as `quarantined` and blocked from active storage.

---

### 2. Risk Assessment Engine
The [RiskEngine](file:///c:/Users/HP/DigiFortress/src/security/risk_engine.py) calculates the dynamic risk score of every memory submission event:

$$\text{Risk Score} = \max\left(0, \min\left(100, 100 - (T \times 50) - (R_{\text{source}} \times 30) + \Delta_{\text{status}}\right)\right)$$

Where:
- $T$: Computed Trust Score (0.0 to 1.0)
- $R_{\text{source}}$: Source Reputation (0.0 to 1.0)
- $\Delta_{\text{status}}$: Status penalty offset:
  - $+15$ if status is `conflict` (logical contradiction detected)
  - $+25$ if status is `quarantined` (low trust score)
  - $0$ otherwise

#### Risk Levels
- **CRITICAL**: $\text{Risk Score} \ge 75$
- **HIGH**: $75 > \text{Risk Score} \ge 50$
- **MODERATE**: $50 > \text{Risk Score} \ge 25$
- **LOW**: $\text{Risk Score} < 25$

---

### 3. Source Reputation Updates
Source reputation is dynamically adjusted with every submission:
- **Accepted Memory**: Reputation increases by $+0.05$ (max $1.0$)
- **Conflict Memory**: Reputation decreases by $-0.03$ (min $0.0$)
- **Quarantined Memory**: Reputation decreases by $-0.10$ (min $0.0$)

---

### 4. Memory Decay & Reputation
Memories in long-term storage decay over time, but build reputation based on access frequency:

$$\text{Decay Score} = \max\left(0.3, 1 - (\text{Age in Days} \times 0.01)\right)$$

$$\text{Memory Reputation} = \min\left(1.0, (T \times 0.5) + (\text{Decay Score} \times 0.3) + \min(\text{Accesses} \times 0.01, 0.2)\right)$$

---

### 5. Counterfactual Audit Divergence & Influence Score
The [CounterfactualAuditor](file:///c:/Users/HP/DigiFortress/src/security/counterfactual_auditor.py) and [InfluenceEngine](file:///c:/Users/HP/DigiFortress/src/security/influence_engine.py) evaluate the downstream influence of retrieved memories on LLM responses:

$$\text{Embedding Divergence } (D) = 1 - \text{CosineSimilarity}(E_{\text{normal}}, E_{\text{counterfactual}})$$

$$\text{Base Influence Score} = D + \text{DriftOffset} + (S_{\text{risk}} \times 0.3)$$

$$\text{Influence Score} = \min(\text{Base Influence Score}, 1.0)$$

Where:
- $E_{\text{normal}}$: Embedding vector of the response generated with retrieved memories.
- $E_{\text{counterfactual}}$: Embedding vector of the response generated without memories (empty context).
- $\text{DriftOffset}$: $+0.4$ if the classification of the normal response differs from the counterfactual response (judgment drift), $0$ otherwise.
- $S_{\text{risk}}$: Session risk score from the `SessionRiskEngine` (0.1 to 1.0).

#### LLM Audit Fallback Upgrade
If $\text{Influence Score} < 0.35$ and $D > 0.10$, the secondary [LLMAuditor](file:///c:/Users/HP/DigiFortress/src/security/llm_auditor.py) is triggered. If it determines retrieved context successfully manipulated the response (`INFLUENCED` verdict), the score is elevated:

$$\text{Influence Score} = \max(\text{Influence Score}, 0.80)$$

#### Influence Threat Levels
- **CRITICAL**: $\text{Influence Score} \ge 0.8$
- **HIGH**: $0.8 > \text{Influence Score} \ge 0.5$
- **MEDIUM**: $0.5 > \text{Influence Score} \ge 0.3$
- **LOW**: $\text{Influence Score} < 0.3$

---

### 6. Session Risk & Burst Detection
The [SessionRiskEngine](file:///c:/Users/HP/DigiFortress/src/security/session_risk_engine.py) tracks session-specific interaction patterns and anomalies:

#### Session Activity Risk Score
$$\text{Session Risk } (S_{\text{risk}}) = 
\begin{cases} 
1.0 & \text{if } W \ge 10 \\
0.75 & \text{if } 10 > W > 7 \\
0.5 & \text{if } 7 > W > 5 \\
0.25 & \text{if } 5 > W > 3 \\
0.1 & \text{otherwise} 
\end{cases}$$

Where $W$ is the total write (remember) operations in the active session.

#### Burst Anomaly Penalty
If the [BurstDetector](file:///c:/Users/HP/DigiFortress/src/security/burst_detector.py) flags a high-frequency write rate (defined as 5 or more writes within 60 seconds), a penalty is applied to the active session risk:

$$S_{\text{risk}} = \min(S_{\text{risk}} + 0.3, 1.0)$$

---

## 🗄️ SQLite Database Schema (`security.db`)

All metadata, source reputations, session activity logs, and security audit logs are managed inside `data/security.db`.

```mermaid
erDiagram
    memories {
        text memory_id PK
        text content
        real trust_score
        text status
        text source
        text timestamp
        integer access_count
        text last_accessed
        real reputation
        real decay_score
    }
    metrics {
        text metric_name PK
        integer metric_value
    }
    sources {
        text source_name PK
        real reputation
        integer accepted_count
        integer conflict_count
        integer quarantined_count
    }
    memory_versions {
        integer version_id PK
        text memory_group
        text content
        text timestamp
        text source
        real trust_score
    }
    security_events {
        integer event_id PK
        text event_type
        text memory_content
        text source
        text status
        real risk_score
        text risk_level
        text timestamp
    }
    session_activity {
        integer activity_id PK
        text session_id
        text timestamp
        text memory_content
    }
    counterfactual_audits {
        integer audit_id PK
        text query
        text normal_response
        text normal_judgment
        text counterfactual_response
        text counterfactual_judgment
        real divergence
        integer judgment_divergence
        text timestamp
    }
```

### Table Definitions

#### 1. `memories`
Stores the active metadata and access counters for memories stored in ChromaDB.
- `memory_id` (TEXT, Primary Key): Unique ChromaDB reference UUID.
- `content` (TEXT): The actual memory belief string.
- `trust_score` (REAL): Evaluated trust level.
- `status` (TEXT): Current state (e.g. `'accepted'`, `'conflict'`).
- `source` (TEXT): The source identifier.
- `timestamp` (TEXT): ISO format creation timestamp.
- `access_count` (INTEGER): Number of times retrieved.
- `last_accessed` (TEXT): ISO format of last access.
- `reputation` (REAL): Computed query-time reputation score.
- `decay_score` (REAL): Time-decay multiplier.

#### 2. `security_events`
The secure audit trail logs all evaluations performed by the validator.
- `event_id` (INTEGER, Primary Key AUTOINCREMENT): Auto-incremented event sequence.
- `event_type` (TEXT): Category of event (e.g., `'MEMORY_EVALUATION'`).
- `memory_content` (TEXT): Evaluated input text.
- `source` (TEXT): Creator/submitter of memory.
- `status` (TEXT): Outcome status (`'accepted'`, `'conflict'`, `'quarantined'`).
- `risk_score` (REAL): Computed risk score from `RiskEngine`.
- `risk_level` (TEXT): Qualitative risk assessment (`'LOW'`, `'MODERATE'`, `'HIGH'`, `'CRITICAL'`).
- `timestamp` (TEXT): ISO format timestamp when validation occurred.

#### 3. `sources`
Tracks reputation scores and aggregate metrics for belief sources.
- `source_name` (TEXT, Primary Key)
- `reputation` (REAL): Dynamic weight (starts at `0.5`, bounds `[0.0, 1.0]`)
- `accepted_count` (INTEGER)
- `conflict_count` (INTEGER)
- `quarantined_count` (INTEGER)

#### 4. `memory_versions`
Tracks versions of updated/replaced memory groupings.
- `version_id` (INTEGER, Primary Key AUTOINCREMENT)
- `memory_group` (TEXT)
- `content` (TEXT)
- `timestamp` (TEXT)
- `source` (TEXT)
- `trust_score` (REAL)

#### 5. `metrics`
System-wide counters (e.g., total accepted, total conflicts, total quarantined, attack attempts).
- `metric_name` (TEXT, Primary Key)
- `metric_value` (INTEGER)

#### 6. `session_activity`
Tracks user interaction and memory modification requests during active sessions to detect rate anomalies.
- `activity_id` (INTEGER, Primary Key AUTOINCREMENT)
- `session_id` (TEXT): Submitter's active session token.
- `timestamp` (TEXT): ISO format write timestamp.
- `memory_content` (TEXT): Submitted memory belief.

#### 7. `counterfactual_audits`
Logs full input/output evaluations for query influence auditing.
- `audit_id` (INTEGER, Primary Key AUTOINCREMENT)
- `query` (TEXT): The incoming user question.
- `normal_response` (TEXT): Generated response with retrieved context.
- `normal_judgment` (TEXT): Classified safety category of normal response.
- `counterfactual_response` (TEXT): Generated baseline response without long-term memories.
- `counterfactual_judgment` (TEXT): Classified safety category of counterfactual response.
- `divergence` (REAL): Cosine distance embedding score.
- `judgment_divergence` (INTEGER): Binary drift indicator (0 or 1).
- `timestamp` (TEXT): ISO format evaluation timestamp.


