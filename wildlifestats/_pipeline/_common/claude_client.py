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
from dataclasses import dataclass
from typing import Any, Optional


DEFAULT_MODEL = "claude-haiku-4-5"
SONNET_MODEL = "claude-sonnet-4-5"

# Rough est. for Haiku 4.5 (update as Anthropic pricing changes). Surface
# in PR descriptions, not in logs that might be persisted.
HAIKU_INPUT_USD_PER_1M = 0.25
HAIKU_OUTPUT_USD_PER_1M = 1.25


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

    raise NotImplementedError(
        "wildlifestats._pipeline._common.claude_client.extract_structured() "
        "is a Phase 9 scaffold."
    )


class ExtractionError(RuntimeError):
    """Raised on API failures or schema-validation failures."""
