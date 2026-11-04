# Guardrails for operations agents

1. **Start read-only.** Let the agent query logs, metrics and docs. Add write
   actions one at a time, only for low-risk operations.
2. **Least privilege.** Give the agent its own identity with the minimum role;
   never reuse a human's admin credentials.
3. **Human approval for risky actions.** Anything destructive, costly or
   customer-visible needs an explicit approval step.
4. **Treat retrieved text as untrusted.** Logs, tickets and web pages can contain
   instructions aimed at the model (prompt injection). Wrap them as data and never
   let them expand the agent's permissions.
5. **Allow-list tools and arguments.** Validate every argument before executing.
6. **Redact secrets and personal data** before sending text to a model.
7. **Limits.** Cap steps, tokens, runtime and spend per task; add a kill switch.
8. **Audit trail.** Log each prompt hash, tool call, result and who approved it.
9. **Evaluate before trusting.** Keep a set of past incidents with known answers
   and track accuracy before expanding what the agent may do.
