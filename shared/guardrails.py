"""Nexus guardrails (spec section 4).

Single home for every security control so servers, resources and the orchestrator
reuse the same logic:

  1. sanitize_free_text()        - length limit, HTML stripping, injection detection
  2. mask_identifier()           - last-4 masking of account/policy/portfolio numbers
  3. minimize_account_fields() / minimize_portfolio_fields()  - scoped field visibility
  4. redact_for_logging()        - PII-safe structured logging (data minimisation)
  5. filter_output()             - validate drafts against grounded context

This module must not import from logging_config (logging_config imports it).
"""
from __future__ import annotations

import html
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Iterable

from .errors import AccessDeniedError, InjectionDetectedError

# ---------------------------------------------------------------------------
# 1. Input sanitisation / prompt-injection defence
# ---------------------------------------------------------------------------

DEFAULT_MAX_LENGTH = 2000

# regular expression constants 
# to check any html tag '<>'
_TAG_RE = re.compile(r"<[^>]*>")
# to find <script> or <style> tag
_SCRIPT_STYLE_RE = re.compile(r"<(script|style)\b.*?>.*?</\1\s*>", re.IGNORECASE | re.DOTALL)

_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f​-‏‪-‮⁠﻿]")
_WS_RE = re.compile(r"[ \t]+")

# Regex signatures of common injection phrasing. Extend as new attacks are found.
INJECTION_PATTERNS: tuple[tuple[str, re.Pattern], ...] = tuple(
    (name, re.compile(rx, re.IGNORECASE))
    for name, rx in (
        ("ignore_instructions",
         r"\b(ignore|disregard|forget|override|bypass)\b.{0,30}\b(previous|prior|above|earlier|all|any|your|system)\b.{0,30}\b(instruction|prompt|rule|guideline|polic|constraint)"),
        ("role_override", r"\b(you are now|act as|pretend to be|from now on you)\b"),
        ("system_prompt_probe", r"\b(reveal|show|print|repeat|output)\b.{0,30}\b(system prompt|hidden prompt|your instructions)"),
        ("fake_role_marker", r"^\s*(system|assistant|developer)\s*:", ),
        ("special_tokens", r"(<\|[a-z_]+\|>|\[/?INST\]|<<SYS>>|###\s*(system|instruction))"),
        ("tool_abuse", r"\b(call|invoke|run|execute)\b.{0,20}\b(tool|function|command)\b.{0,40}\b(without|skip|disable)\b"),
        ("disable_guardrails", r"\b(disable|turn off|skip|ignore)\b.{0,20}\b(guardrail|safety|escalation|compliance|validation|audit)"),
        ("exfiltration", r"\b(send|email|post|forward|leak)\b.{0,40}\b(to|at)\b.{0,40}(https?://|@[\w.-]+\.\w+)"),
        ("jailbreak", r"\b(jailbreak|DAN mode|developer mode|do anything now)\b"),
    )
)
# fake_role_marker must be matched per line
_MULTILINE_PATTERNS = {"fake_role_marker"}


def scan_for_injection(text: str) -> list[str]:
    """Return the names of injection signatures found in text (empty list = clean)."""
    hits = []
    for name, rx in INJECTION_PATTERNS:
        flags_text = text
        if name in _MULTILINE_PATTERNS:
            if re.search(rx.pattern, flags_text, re.IGNORECASE | re.MULTILINE):
                hits.append(name)
        elif rx.search(flags_text):
            hits.append(name)
    return hits


def sanitize_free_text(
    text: Any,
    max_length: int = DEFAULT_MAX_LENGTH,
    on_injection: str = "raise",
) -> str:
    """Sanitise untrusted text (customer input, retrieved docs, tool output, outbound messages).

    Steps: type check -> NFKC normalise -> strip script/style/HTML -> unescape entities ->
    drop control/zero-width chars -> collapse whitespace -> length limit -> injection scan.

    on_injection:
      "raise"  - raise InjectionDetectedError (use for customer input / outbound messages)
      "redact" - replace offending lines with [REMOVED: possible prompt injection]
                 (use for retrieved documents so the pipeline can continue)
      "flag"   - return text unchanged; caller uses scan_for_injection() itself
    """
    if on_injection not in {"raise", "redact", "flag"}:
        raise ValueError("on_injection must be raise|redact|flag")
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)

    text = unicodedata.normalize("NFKC", text)
    # Scan before stripping too: tag-like tokens such as <|im_start|> vanish during HTML stripping.
    pre_hits = scan_for_injection(text[: max_length * 4])
    text = _SCRIPT_STYLE_RE.sub(" ", text)
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)
    text = _TAG_RE.sub(" ", text)  # entities may decode into tags (&lt;b&gt;)
    text = _CONTROL_RE.sub("", text)
    lines = [_WS_RE.sub(" ", ln).strip() for ln in text.splitlines()]
    text = "\n".join(ln for ln in lines if ln)
    text = text[:max_length]

    hits = sorted(set(scan_for_injection(text)) | set(pre_hits))
    if hits:
        if on_injection == "raise":
            raise InjectionDetectedError("Potential prompt injection detected", signatures=hits)
        if on_injection == "redact":
            kept = []
            for ln in text.splitlines():
                kept.append("[REMOVED: possible prompt injection]" if scan_for_injection(ln) else ln)
            text = "\n".join(kept)
    return text


# ---------------------------------------------------------------------------
# 2. Identifier masking (last four digits) - hard requirement
# ---------------------------------------------------------------------------

# Customer IDs (CUS-) are identifiers, not account numbers; spec requires masking
# account, policy and portfolio numbers.
_MASKABLE_ID_RE = re.compile(r"\b(?:ACC-\d{5}|POL-[A-Z]{2}-\d{5}|PORT-\d{5})\b")


def mask_identifier(value: str | None) -> str | None:
    """'ACC-20077' -> '****0077'; 'POL-IN-30091' -> '****0091'. Always last four digits."""
    if value is None:
        return None
    digits = re.sub(r"\D", "", str(value))
    return "****" + digits[-4:] if digits else "****"


def mask_identifiers_in_text(text: str) -> str:
    """Mask every account/policy/portfolio id embedded in free text."""
    return _MASKABLE_ID_RE.sub(lambda m: mask_identifier(m.group(0)), text)


# ---------------------------------------------------------------------------
# 3. Scoped field visibility
# ---------------------------------------------------------------------------

# caller_scope -> fields it may see. Anything not listed is dropped.
ACCOUNT_SCOPES: dict[str, frozenset[str]] = {
    "customer_facing": frozenset({"account_id", "account_type", "status", "balance", "currency", "restrictions"}),
    "agent_support": frozenset({"account_id", "account_type", "status", "balance", "currency",
                                "restrictions", "opened_date", "auto_debit_allowed"}),
    "internal_ops": frozenset({"account_id", "account_type", "status", "balance", "currency",
                               "restrictions", "opened_date", "auto_debit_allowed", "customer_id"}),
}
PORTFOLIO_SCOPES: dict[str, frozenset[str]] = {
    "customer_facing": frozenset({"portfolio_id", "portfolio_type", "total_value", "currency", "risk_profile"}),
    "agent_support": frozenset({"portfolio_id", "portfolio_type", "total_value", "currency",
                                "risk_profile", "holdings", "performance_ytd"}),
    "internal_ops": frozenset({"portfolio_id", "portfolio_type", "total_value", "currency",
                               "risk_profile", "holdings", "performance_ytd", "customer_id"}),
}
_ID_FIELDS = {"account_id", "portfolio_id", "policy_id", "account_number", "policy_number", "portfolio_number"}


def _minimize(record: dict, scope: str, scopes: dict[str, frozenset[str]]) -> dict:
    if scope not in scopes:
        raise AccessDeniedError(f"Unknown caller_scope '{scope}'", allowed=sorted(scopes))
    allowed = scopes[scope]
    out = {}
    for key, value in record.items():
        if key not in allowed:
            continue
        out[key] = mask_identifier(value) if key in _ID_FIELDS else value
    return out


def minimize_account_fields(account: dict, caller_scope: str) -> dict:
    """Filter an account record to the caller_scope's allow-list and mask identifiers."""
    return _minimize(account, caller_scope, ACCOUNT_SCOPES)


def minimize_portfolio_fields(portfolio: dict, caller_scope: str) -> dict:
    """Filter a portfolio record to the caller_scope's allow-list and mask identifiers."""
    return _minimize(portfolio, caller_scope, PORTFOLIO_SCOPES)


# ---------------------------------------------------------------------------
# 4. PII redaction for logs (data minimisation)
# ---------------------------------------------------------------------------

PII_KEYS = frozenset({
    "account_id", "customer_id", "policy_id", "portfolio_id", "claim_id",
    "phone", "email", "account_number", "policy_number", "customer_name", "name", "address",
})
_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE_RE = re.compile(r"(?<!\w)\+?\d[\d\s().-]{8,}\d(?!\w)")
_REDACTED = "[REDACTED]"


def _mask_pii_value(key: str, value: Any) -> str:
    s = str(value)
    if key in {"email", "phone", "customer_name", "name", "address"}:
        return _REDACTED
    return mask_identifier(s)


def _scrub_string(s: str) -> str:
    s = _EMAIL_RE.sub(_REDACTED, s)
    s = _PHONE_RE.sub(_REDACTED, s)
    return mask_identifiers_in_text(s)


def redact_for_logging(data: Any) -> Any:
    """Return a copy safe to log.

    - dict keys in PII_KEYS are masked (ids -> last 4, email/phone/name -> [REDACTED])
    - free-text strings are scrubbed of emails, phone numbers and account/policy/portfolio ids
    - recurses through dicts, lists and tuples; never mutates the input

    Data minimisation: logs keep enough to correlate events (last four digits, call_id)
    without ever persisting full identifiers or contact details.
    """
    if isinstance(data, dict):
        return {
            k: (_mask_pii_value(str(k).lower(), v) if str(k).lower() in PII_KEYS and v is not None
                else redact_for_logging(v))
            for k, v in data.items()
        }
    if isinstance(data, (list, tuple)):
        return type(data)(redact_for_logging(v) for v in data)
    if isinstance(data, str):
        return _scrub_string(data)
    return data


# ---------------------------------------------------------------------------
# 5. Output filtering
# ---------------------------------------------------------------------------

_NUMBER_RE = re.compile(r"(?<![\w-])(?:[$£€₹]\s?)?\d[\d,]*(?:\.\d+)?%?")


@dataclass
class OutputFilterResult:
    ok: bool
    text: str                       # draft with identifiers masked
    violations: list[str] = field(default_factory=list)


def _normalise_number(tok: str) -> str:
    return re.sub(r"[^\d.]", "", tok)


def filter_output(draft: str, grounded_context: str | Iterable[str]) -> OutputFilterResult:
    """Check a draft before it reaches the customer.

    Violations:
      - unmasked_identifier : raw ACC-/POL-/PORT- id present (text is masked in the result)
      - unsupported_number  : a figure in the draft not present in the grounded context
      - injection           : draft contains injection signatures
    Facts-vs-context checking beyond numbers is done by the Validation Agent; this is the
    deterministic last line of defence.
    """
    if not isinstance(grounded_context, str):
        grounded_context = "\n".join(map(str, grounded_context))
    violations: list[str] = []

    if _MASKABLE_ID_RE.search(draft):
        violations.append("unmasked_identifier")
    masked = mask_identifiers_in_text(draft)

    context_numbers = {_normalise_number(t) for t in _NUMBER_RE.findall(grounded_context)}
    for tok in _NUMBER_RE.findall(masked):
        n = _normalise_number(tok)
        # ignore tiny numbers (list indexes, "2 business days" still checked if >= 2 digits)
        if len(n.replace(".", "")) >= 2 and n not in context_numbers and not re.fullmatch(r"\*+\d{4}", tok):
            # last-four fragments of masked ids are expected
            if re.search(r"\*{4}" + re.escape(n) + r"\b", masked):
                continue
            violations.append(f"unsupported_number:{tok.strip()}")

    if scan_for_injection(masked):
        violations.append("injection")

    return OutputFilterResult(ok=not violations, text=masked, violations=violations)
