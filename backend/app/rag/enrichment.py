"""Best-effort AI enrichment: structured insight cards, topical tags, and
follow-up question suggestions. None of this blocks core chat - callers
treat any failure here as "enrichment unavailable", not a hard error,
since a rate limit or Gemini outage shouldn't stop a paper from being
chattable or a conversation from continuing.
"""
from app.rag.gemini_client import GeminiClient

INSIGHT_SYSTEM_PROMPT = """You analyze a research paper and produce a structured summary card.
Respond ONLY with JSON matching this exact shape:
{
  "problem": "one or two sentences: what problem or question the paper addresses",
  "method": "one or two sentences: how they approached it",
  "key_results": ["short bullet", "short bullet"],
  "limitations": ["short bullet", "short bullet"],
  "contributions": ["short bullet", "short bullet"]
}
Use 2-4 bullets for key_results and contributions, 0-3 for limitations (empty array if none are stated).
Base everything strictly on the supplied text - never invent numbers, results, or claims it doesn't support."""

TAGS_SYSTEM_PROMPT = """Read the paper's title and abstract and produce 3 to 6 short topical tags
(e.g. "computer vision", "reinforcement learning", "medical imaging").
Respond ONLY with a JSON array of lowercase strings, each at most 3 words."""

FOLLOWUPS_SYSTEM_PROMPT = """Given a question that was just asked about a research paper and the
answer that was given, suggest up to 3 short, natural follow-up questions a curious reader might
ask next. Respond ONLY with a JSON array of strings. Keep each under 12 words."""


def generate_insight_card(title: str, abstract: str, full_text: str) -> dict:
    excerpt = full_text[:6000]  # keep the enrichment call cheap
    message = f"Title: {title}\n\nAbstract: {abstract}\n\nPaper text (excerpt):\n{excerpt}"
    return GeminiClient().generate_json(INSIGHT_SYSTEM_PROMPT, message)


def generate_tags(title: str, abstract: str) -> list[str]:
    message = f"Title: {title}\n\nAbstract: {abstract}"
    result = GeminiClient().generate_json(TAGS_SYSTEM_PROMPT, message)
    return [str(tag).strip().lower() for tag in result][:6]


def suggest_followups(question: str, answer: str) -> list[str]:
    """Never raises - a failed suggestion call degrades to an empty list
    rather than surfacing an error for what is a minor UX nicety."""
    try:
        message = f"Question: {question}\n\nAnswer: {answer}"
        result = GeminiClient().generate_json(FOLLOWUPS_SYSTEM_PROMPT, message)
        return [str(item).strip() for item in result if str(item).strip()][:3]
    except Exception:
        return []
