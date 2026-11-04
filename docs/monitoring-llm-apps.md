# Monitoring LLM, RAG and vector-search applications

A RAG request has several stages; each can fail or degrade independently.

```
user query -> embed query -> vector search (pgvector) -> build prompt -> LLM -> response
```

## What to measure

| Layer | Signals | Why it matters |
|---|---|---|
| Whole request | Success rate, p50/p95/p99 latency, time to first token | User experience and SLOs |
| Embedding | Latency, error rate, throttling (429) | First stage, blocks everything |
| Vector search | Query latency, rows scanned, index used?, recall on a test set | Slow or wrong retrieval ruins answers |
| LLM call | Latency, input/output tokens, stop reason, error/429/overloaded rate | Cost and capacity |
| Cost | Tokens x price per service/team/feature | Budgets and anomaly alerts |
| Quality | Groundedness, "no answer" rate, thumbs-down rate, eval-set score | Silent failures: the app is up but wrong |
| Safety | Guardrail triggers, prompt-injection detections | Security |

## Suggested SLOs
- 99% of requests succeed.
- 95% of requests complete in under N seconds.
- Retrieval hit rate on a fixed evaluation set stays above a baseline (checked daily).

## pgvector health queries

```sql
-- Is the vector index being used? (look for "Index Scan using ..." not "Seq Scan")
EXPLAIN (ANALYZE, BUFFERS)
SELECT id FROM documents ORDER BY embedding <=> '[0.1,0.2,...]' LIMIT 5;

-- Table and index size
SELECT pg_size_pretty(pg_total_relation_size('documents')) AS total,
       pg_size_pretty(pg_relation_size('documents_embedding_idx')) AS index;

-- Slowest statements (needs pg_stat_statements)
SELECT calls, round(mean_exec_time::numeric,1) AS mean_ms, left(query,80)
FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;
```

Tuning knobs: HNSW `ef_search` (recall vs speed) or IVFFlat `probes`; keep `maintenance_work_mem`
adequate when building indexes; vacuum/analyze after bulk loads.

## Alert ideas
- LLM error or 429 rate above 2% for 5 minutes
- p95 latency above SLO for 10 minutes
- Tokens per request jumping 2x (prompt bloat, runaway context)
- Daily spend above forecast
- Retrieval returning zero results unusually often
- Eval score drops after a deploy or model change

## Tracing
Use one trace per user request with child spans for embed, search, prompt build and LLM
call (see `observability/llm_tracing.py`). Record token counts as span attributes. Do not
store raw prompts or responses unless you have a retention and privacy policy for them.
