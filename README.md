# ai-ops-agents

Practical examples of using LLMs for operations, and of **monitoring LLM-based
applications** (RAG, vector search, agents).

| Path | Purpose |
|---|---|
| `agents/log_triage.py` | Read-only agent that summarises a log file, groups errors and suggests next checks |
| `observability/llm_tracing.py` | Wraps LLM calls in OpenTelemetry spans with model, latency and token usage |
| `docs/monitoring-llm-apps.md` | What to monitor in RAG / pgvector / LLM applications, with example queries |
| `docs/agent-safety.md` | Guardrails for operations agents |

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...        # never commit keys
python agents/log_triage.py sample.log
```

The triage agent is **read-only**: it never executes commands. It prints a summary and
suggested checks for a human to run.

## License

MIT
