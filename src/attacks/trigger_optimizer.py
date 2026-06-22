"""
AgentPoison — Trigger Optimizer
================================
Black-box greedy beam search that crafts a trigger phrase
whose embedding maps to a unique cluster far from the
centroid of benign memories (Chen et al., NeurIPS 2024).

No model gradients are required; we approximate projected
gradient descent by iteratively substituting tokens with
candidates from a naturalness-constrained vocabulary pool
and scoring each candidate by cluster separation.
"""

from __future__ import annotations

import math
import random
from typing import List, Tuple

from src.embeddings.embedder import Embedder


# ---------------------------------------------------------------------------
# Default vocabulary pool — common English words that blend into normal prose
# and do not trigger rule-based security filters.
# ---------------------------------------------------------------------------
_DEFAULT_VOCAB: List[str] = [
    "review", "monitor", "process", "verify", "schedule",
    "confirm", "update", "authorize", "validate", "complete",
    "initiate", "submit", "approve", "document", "record",
    "assess", "evaluate", "coordinate", "align", "integrate",
    "synchronize", "consolidate", "finalize", "archive", "deploy",
    "configure", "establish", "maintain", "optimize", "generate",
    "quarterly", "internal", "standard", "routine", "regular",
    "compliance", "protocol", "workflow", "procedure", "framework",
    "checkpoint", "milestone", "directive", "mandate", "guideline",
    "systematic", "automated", "structured", "centralized", "dedicated",
    "primary", "secondary", "critical", "essential", "mandatory",
]

# Sentence template skeletons into which the trigger token(s) are woven.
_TRIGGER_TEMPLATES: List[str] = [
    "The {trigger} procedure requires immediate attention from the designated team.",
    "All {trigger} requests must be logged and forwarded to the compliance office.",
    "Standard {trigger} protocols are enforced across all operational divisions.",
    "A {trigger} directive has been issued for all active system configurations.",
    "Please ensure the {trigger} workflow is completed before end of business.",
]


def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute cosine similarity between two embedding vectors."""
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _cosine_distance(vec_a: List[float], vec_b: List[float]) -> float:
    return 1.0 - _cosine_similarity(vec_a, vec_b)


def _centroid(embeddings: List[List[float]]) -> List[float]:
    """Element-wise mean of a list of embedding vectors."""
    if not embeddings:
        return []
    dim = len(embeddings[0])
    result = [0.0] * dim
    for emb in embeddings:
        for i, v in enumerate(emb):
            result[i] += v
    n = len(embeddings)
    return [v / n for v in result]


class TriggerOptimizer:
    """
    Greedy beam-search trigger optimizer.

    Parameters
    ----------
    embedder : Embedder
        The sentence-transformer embedder already used by the agent.
    beam_width : int
        Number of candidate triggers to keep at each search step.
    n_steps : int
        Number of greedy substitution steps to perform.
    vocab_pool : list[str] | None
        Candidate tokens. Defaults to ``_DEFAULT_VOCAB``.
    seed : int
        Random seed for reproducibility.
    """

    def __init__(
        self,
        embedder: Embedder | None = None,
        beam_width: int = 3,
        n_steps: int = 20,
        vocab_pool: List[str] | None = None,
        seed: int = 42,
    ) -> None:
        self.embedder = embedder or Embedder()
        self.beam_width = beam_width
        self.n_steps = n_steps
        self.vocab = vocab_pool or _DEFAULT_VOCAB
        random.seed(seed)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def optimize_trigger(
        self,
        target_concept: str,
        benign_memories: List[str],
        verbose: bool = False,
    ) -> Tuple[str, float]:
        """
        Find a trigger phrase that maximises cluster separation.

        Parameters
        ----------
        target_concept : str
            The semantic domain the trigger should *appear* related to
            (e.g. ``"financial transfer"``).
        benign_memories : list[str]
            A sample of clean memory strings already in the vector store.
            Used to compute the benign centroid.
        verbose : bool
            Print progress at each step.

        Returns
        -------
        best_trigger : str
            The optimized full trigger sentence.
        best_score : float
            Final cluster-separation score (cosine distance from benign
            centroid; higher is better, theoretical max = 2.0).
        """
        # Encode benign memories and compute their centroid
        benign_embs = [self.embedder.generate_embedding(m) for m in benign_memories] if benign_memories else []
        benign_centroid = _centroid(benign_embs) if benign_embs else None

        # Precompute target concept embedding once to avoid redundant computations inside _score_token
        concept_emb = self.embedder.generate_embedding(target_concept)

        # Seed beam with random tokens from the vocab pool
        beam: List[Tuple[str, float]] = []  # (trigger_token, score)
        seed_tokens = random.sample(self.vocab, min(self.beam_width, len(self.vocab)))
        for tok in seed_tokens:
            score = self._score_token(tok, benign_centroid, concept_emb)
            beam.append((tok, score))
        beam.sort(key=lambda x: x[1], reverse=True)

        if verbose:
            print(f"[TriggerOptimizer] Seed beam: {[(t, f'{s:.3f}') for t, s in beam]}")

        # Greedy beam search
        for step in range(self.n_steps):
            candidates: List[Tuple[str, float]] = list(beam)
            for tok, _ in beam:
                # Try each vocab token as a substitution / extension
                for candidate_tok in random.sample(self.vocab, min(15, len(self.vocab))):
                    if candidate_tok == tok:
                        continue
                    new_score = self._score_token(candidate_tok, benign_centroid, concept_emb)
                    candidates.append((candidate_tok, new_score))

            # Keep best beam_width unique tokens
            seen: set = set()
            unique: List[Tuple[str, float]] = []
            for tok, score in sorted(candidates, key=lambda x: x[1], reverse=True):
                if tok not in seen:
                    seen.add(tok)
                    unique.append((tok, score))
                if len(unique) == self.beam_width:
                    break
            beam = unique

            if verbose:
                best_tok, best_s = beam[0]
                print(f"[TriggerOptimizer] Step {step+1:02d}/{self.n_steps} | best_token={best_tok!r} score={best_s:.4f}")

        best_token, best_score = beam[0]

        # Wrap the best token in a natural-looking sentence
        template = random.choice(_TRIGGER_TEMPLATES)
        best_trigger = template.format(trigger=best_token)

        if verbose:
            print(f"[TriggerOptimizer] Optimized trigger: '{best_trigger}' (score={best_score:.4f})")

        return best_trigger, best_score

    def score_trigger(self, trigger: str, benign_memories: List[str]) -> float:
        """
        Score a trigger phrase against the benign centroid.
        Returns cosine distance (higher = more separated = better for the attack).
        """
        benign_embs = [self.embedder.generate_embedding(m) for m in benign_memories]
        centroid = _centroid(benign_embs)
        trigger_emb = self.embedder.generate_embedding(trigger)
        if not centroid:
            return 0.0
        return _cosine_distance(trigger_emb, centroid)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _score_token(
        self,
        token: str,
        benign_centroid: List[float] | None,
        concept_emb: List[float],
    ) -> float:
        """
        Score a candidate trigger token.

        Combines two signals:
        - Cluster separation: cosine distance from benign centroid (high → good).
        - Concept proximity: cosine similarity to the target concept embedding.
          We want the trigger to appear *conceptually relevant* to avoid perplexity
          filters, so we add a small bonus for reasonable concept proximity.
        """
        # Embed the token inside a neutral sentence so the model sees context
        sentence = f"The {token} process is required."
        emb = self.embedder.generate_embedding(sentence)

        separation = 0.0
        if benign_centroid:
            separation = _cosine_distance(emb, benign_centroid)

        # Concept proximity bonus (small weight, keeps trigger "on topic")
        proximity = _cosine_similarity(emb, concept_emb)
        proximity_bonus = proximity * 0.15  # up-weight if close to target domain

        return separation + proximity_bonus
