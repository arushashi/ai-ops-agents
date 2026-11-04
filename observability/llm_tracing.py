"""OpenTelemetry instrumentation for LLM calls.

Records one span per call with model, latency, token usage and errors, using the
OpenTelemetry GenAI semantic-convention attribute names. Prompt/response text is
NOT recorded by default (privacy and cost).

Run this file directly to see spans printed to the console.
"""
import time

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

tracer = trace.get_tracer("ai-ops-agents")


def setup_console_exporter() -> None:
    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)


def traced_completion(client, model: str, system: str, user: str, max_tokens: int = 500):
    """Call the Anthropic Messages API inside a span."""
    with tracer.start_as_current_span("gen_ai.chat") as span:
        span.set_attribute("gen_ai.system", "anthropic")
        span.set_attribute("gen_ai.request.model", model)
        span.set_attribute("gen_ai.request.max_tokens", max_tokens)
        start = time.perf_counter()
        try:
            resp = client.messages.create(
                model=model, max_tokens=max_tokens, system=system,
                messages=[{"role": "user", "content": user}],
            )
        except Exception as exc:
            span.record_exception(exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(exc)))
            raise
        span.set_attribute("gen_ai.usage.input_tokens", resp.usage.input_tokens)
        span.set_attribute("gen_ai.usage.output_tokens", resp.usage.output_tokens)
        span.set_attribute("gen_ai.response.stop_reason", str(resp.stop_reason))
        span.set_attribute("app.llm.latency_ms", (time.perf_counter() - start) * 1000)
        return resp


if __name__ == "__main__":
    import anthropic

    setup_console_exporter()
    r = traced_completion(anthropic.Anthropic(), "claude-sonnet-5-5",
                          "Answer in one sentence.", "What is an error budget?", 100)
    print(r.content[0].text)
