"""Anthropic Claude client for structured extraction.

Primary consumer: Bucket 02 (firm profile) per-org content harvester.
Secondary consumer: Bucket 03 (publications) PDF/HTML body extraction.
Tertiary consumer: Bucket 01 (social) — the production extraction path
the Flyway POC standardizes on (the deterministic offline matcher stays
as the CI/test backend).

CONTRACT:

  1. Token via creds.get_anthropic_token() — never module-level. The
     2026-06-11 Flyway POC ran with the env-shadowed key as a
     standin-extractor workaround; production must use the vault handle.

  2. Structured extraction only — every call passes a JSON Schema for the
     expected output and the client validates the response against it
     before returning. Free-form text generation is out of scope for
     Phase 9 ingestion (it's the Wildlife911 LLM pill's job, not this
     module's).

  3. Source URLs MUST be passed in the prompt and MUST appear inline in
     the extracted record's `sources` field. The §22 audit trail requires
     every claim cite its source.

  4. Quote, do not paraphrase, for mission statements and similar
     identity-statement content. The prompt enforces this; the client
     also adds a defensive check that mission_statement, if present,
     appears verbatim in the source body. If not, the extraction is
     rejected.

  5. Cost tracking — every call returns input_tokens, output_tokens,
     and estimated_usd. Bucket pipelines aggregate these for the
     run-summary artifact.

  6. Default model: Claude Haiku 4.5 (cheap structured extraction). The
     production extractor in Bucket 02 may upgrade to Sonnet for
     complex multi-page extractions; the upgrade is per-call, not
     global.

THIS MODULE IS A SCAFFOLD. Engineer fills in the API plumbing.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Optional

from . import creds


DEFAULT_MODEL = "claude-haiku-4-5"
SONNET_MODEL = "claude-sonnet-4-5"

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"

# Field-name hints that signal "this value must be a verbatim quote, not a
# paraphrase" — enforced against the source body (contract point 4).
QUOTE_FIELD_HINTS = ("mission_statement", "quote", "verbatim")

# Rough est. for Haiku 4.5 (update as Anthropic pricing changes). Surface
# in PR descriptions, not in logs that might be persisted.
HAIKU_INPUT_USD_PER_1M = 0.25
HAIKU_OUTPUT_USD_PER_1M = 1.25
SONNET_INPUT_USD_PER_1M = 3.00
SONNET_OUTPUT_USD_PER_1M = 15.00


@dataclass
class ExtractionResult:
    """Standard envelope for every structured-extraction call."""

    record: dict  # validated against the schema the caller provided
    sources: list[str]  # URLs cited by the model
    input_tokens: int
    output_tokens: int
    estimated_usd: float
    model: str
    raw_response_id: Optional[str] = None  # Anthropic message id
    notes: list[str] = None  # validation warnings, not failures

    def __post_init__(self):
        if self.notes is None:
            self.notes = []


def extract_structured(
    *,
    system_prompt: str,
    user_content: str,
    output_schema: dict,
    source_urls: list[str],
    model: str = DEFAULT_MODEL,
    max_output_tokens: int = 4096,
    reject_on_quote_mismatch: bool = True,
) -> ExtractionResult:
    """Extract structured data matching output_schema from user_content.

    Args:
        system_prompt: the role-and-rules system message. Should include
            the Phase 9 discipline ("quote do not paraphrase," "cite every
            claim," "leave fields null when source doesn't say").
        user_content: the source text to extract from. Pre-fetched and
            validated by fetch.fetch().
        output_schema: JSON Schema the model output must match.
        source_urls: list of URLs the user_content was derived from.
            Embedded into the prompt so the model can cite them.
        model: claude model id. Defaults to Haiku 4.5 for cost.
        max_output_tokens: per-call cap.

    Returns ExtractionResult on success; raises ExtractionError on
    schema validation failure or API error.

    TODO[engineer]: implement against api.anthropic.com /v1/messages.
    Use creds.get_anthropic_token() for auth. Recommended decomposition:

    1. Build the message with tool_use forcing the output_schema.
    2. Call api.anthropic.com /v1/messages.
    3. Parse the tool_use response; extract the structured object.
    4. Validate against output_schema using jsonschema library.
    5. Defensive check: every value in the response that looks like a
       direct quote (e.g., field named 'mission_statement', 'quote',
       'verbatim_*') must appear as a substring of user_content. If
       not, append a note and consider rejecting per caller policy.
    6. Compute estimated_usd from token counts and model pricing.
    7. Return ExtractionResult.
    """
    if not source_urls:
        raise ValueError(
            "extract_structured requires at least one source_url. "
            "Phase 9 records MUST carry source attribution."
        )
    if not isinstance(output_schema, dict) or "type" not in output_schema:
        raise ValueError("output_schema must be a JSON Schema dict")

    token = creds.get_anthropic_token()

    sources_block = "\n".join(f"- {u}" for u in source_urls)
    user_msg = (
        f"{user_content}\n\n---\nSOURCE URLS (cite the relevant ones in the "
        f"record's `sources` field; quote identity statements verbatim):\n{sources_block}"
    )
    body = {
        "model": model,
        "max_tokens": max_output_tokens,
        "system": system_prompt,
        "tools": [{
            "name": "emit_record",
            "description": "Emit the structured record extracted from the source content.",
            "input_schema": output_schema,
        }],
        # Force the tool so the model cannot return free-form prose.
        "tool_choice": {"type": "tool", "name": "emit_record"},
        "messages": [{"role": "user", "content": user_msg}],
    }

    payload = _call_messages(body, token)

    record = None
    for block in payload.get("content", []):
        if block.get("type") == "tool_use" and block.get("name") == "emit_record":
            record = block.get("input")
            break
    if record is None:
        raise ExtractionError("Model returned no emit_record tool_use block.")

    _validate_schema(record, output_schema)

    notes: list[str] = []
    mismatches = _quote_discipline_check(record, user_content)
    if mismatches:
        detail = f"verbatim-quote fields not found in source body: {mismatches}"
        if reject_on_quote_mismatch:
            raise ExtractionError(
                f"Quote discipline failed — {detail}. Identity-statement fields "
                f"(mission_statement/quote/verbatim_*) must be quoted verbatim, "
                f"not paraphrased."
            )
        notes.append(detail)

    usage = payload.get("usage", {})
    in_tok = int(usage.get("input_tokens", 0))
    out_tok = int(usage.get("output_tokens", 0))
    sources = record.get("sources")
    if not isinstance(sources, list):
        sources = list(source_urls)
    return ExtractionResult(
        record=record,
        sources=sources,
        input_tokens=in_tok,
        output_tokens=out_tok,
        estimated_usd=_estimate_usd(model, in_tok, out_tok),
        model=model,
        raw_response_id=payload.get("id"),
        notes=notes,
    )


def _call_messages(body: dict, token: str) -> dict:
    """POST to the Anthropic Messages API. Raises ExtractionError on
    API/network failure. Isolated so tests can stub it without network."""
    req = urllib.request.Request(
        ANTHROPIC_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "x-api-key": token,
            "anthropic-version": ANTHROPIC_VERSION,
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:400]
        raise ExtractionError(f"Anthropic API error (HTTP {exc.code}): {detail}") from None
    except urllib.error.URLError as exc:
        raise ExtractionError(f"Anthropic network error: {exc.reason}") from None


def _validate_schema(record: Any, schema: dict) -> None:
    """Validate record against schema. The forced tool_use input_schema
    already constrains the shape server-side; this is belt-and-suspenders.
    jsonschema is used if installed, else a minimal required-keys check (so
    the module has no hard dependency and imports cleanly in CI)."""
    if not isinstance(record, dict):
        raise ExtractionError("Extracted record is not a JSON object.")
    try:
        import jsonschema  # type: ignore
    except ImportError:
        for key in schema.get("required", []):
            if key not in record:
                raise ExtractionError(f"Extracted record missing required field {key!r}.")
        return
    try:
        jsonschema.validate(record, schema)
    except jsonschema.ValidationError as exc:  # type: ignore[attr-defined]
        raise ExtractionError(f"Extracted record failed schema validation: {exc.message}") from None


def _quote_discipline_check(record: Any, source: str) -> list[str]:
    """Return paths of string leaves whose field name implies a verbatim
    quote but whose value is not a substring of the source body."""
    src = source or ""
    bad: list[str] = []

    def walk(obj: Any, path: str = "") -> None:
        if isinstance(obj, dict):
            for key, val in obj.items():
                walk(val, f"{path}.{key}" if path else key)
        elif isinstance(obj, list):
            for i, val in enumerate(obj):
                walk(val, f"{path}[{i}]")
        elif isinstance(obj, str) and obj.strip():
            leaf = path.split(".")[-1].lower()
            if any(hint in leaf for hint in QUOTE_FIELD_HINTS) and obj.strip() not in src:
                bad.append(path)

    walk(record)
    return bad


def _estimate_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    if model.startswith("claude-sonnet") or model == SONNET_MODEL:
        in_rate, out_rate = SONNET_INPUT_USD_PER_1M, SONNET_OUTPUT_USD_PER_1M
    else:
        in_rate, out_rate = HAIKU_INPUT_USD_PER_1M, HAIKU_OUTPUT_USD_PER_1M
    return round(input_tokens / 1e6 * in_rate + output_tokens / 1e6 * out_rate, 6)


class ExtractionError(RuntimeError):
    """Raised on API failures or schema-validation failures."""
