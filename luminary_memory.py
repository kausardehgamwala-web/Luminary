"""
luminary_memory.py
==================
Persistent JSON-based memory system for Luminary AI.
Stores: user preferences, brand identity, feedback history,
        interaction summaries, and research cache.

NO external dependencies — pure Python stdlib only.
"""

import json
import os
import time
from pathlib import Path
from datetime import datetime, timezone

MEMORY_DIR = Path(__file__).resolve().parent / "memory"
MEMORY_FILE = MEMORY_DIR / "luminary_memory.json"
MEMORY_TMP = MEMORY_DIR / "luminary_memory.tmp.json"

CACHE_TTL_SECONDS = 86400  # 24 hours
MAX_FEEDBACK_ENTRIES = 100
MAX_INTERACTION_SUMMARIES = 20


def _default_memory() -> dict:
    return {
        "version": 2,
        "created_at": _now(),
        "preferences": {},
        "brand": {},
        "feedback": [],
        "summaries": [],
        "research_cache": {},
    }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _now_ts() -> float:
    return time.time()


def get_memory() -> dict:
    """Load memory from disk. Creates default memory if missing or corrupted."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    if not MEMORY_FILE.exists():
        data = _default_memory()
        save_memory(data)
        return data
    try:
        raw = MEMORY_FILE.read_text(encoding="utf-8")
        return json.loads(raw)
    except Exception:
        data = _default_memory()
        save_memory(data)
        return data


def save_memory(data: dict) -> None:
    """Atomically save memory to disk (write to .tmp then rename)."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    try:
        MEMORY_TMP.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(str(MEMORY_TMP), str(MEMORY_FILE))
    except Exception as e:
        print(f"[luminary_memory] Save failed: {e}")


def update_preference(key: str, value: str) -> None:
    """Set a long-term user preference (e.g., preferred_style, tone, language)."""
    data = get_memory()
    data["preferences"][key] = value
    data["preferences"]["_updated"] = _now()
    save_memory(data)


def get_preferences() -> dict:
    """Return current user preferences dict."""
    return get_memory().get("preferences", {})


def update_brand(brand_data: dict) -> None:
    """
    Update the active brand identity.
    brand_data keys: name, primary_color, secondary_color, accent_color,
                     font, voice, logo_desc, industry, target_audience
    """
    data = get_memory()
    data["brand"].update(brand_data)
    data["brand"]["_updated"] = _now()
    save_memory(data)


def get_brand() -> dict:
    """Return the active brand identity."""
    return get_memory().get("brand", {})


def log_feedback(output_type: str, rating: str, context: str) -> None:
    """
    Record user feedback.
    rating: 'positive' or 'negative'
    """
    data = get_memory()
    entry = {
        "output_type": output_type,
        "rating": rating,
        "context": context[:300],
        "timestamp": _now(),
    }
    data["feedback"].append(entry)
    # Keep only last N entries
    data["feedback"] = data["feedback"][-MAX_FEEDBACK_ENTRIES:]
    save_memory(data)


def get_feedback_summary() -> str:
    """
    Return a concise string summarizing positive/negative patterns
    for injection into AI prompts.
    """
    data = get_memory()
    feedback = data.get("feedback", [])
    if not feedback:
        return ""

    pos = [f for f in feedback if f.get("rating") == "positive"]
    neg = [f for f in feedback if f.get("rating") == "negative"]

    lines = []
    if pos:
        pos_contexts = list({f["context"][:60] for f in pos[-5:]})
        lines.append(f"User has approved: {'; '.join(pos_contexts)}")
    if neg:
        neg_contexts = list({f["context"][:60] for f in neg[-5:]})
        lines.append(f"User has disliked: {'; '.join(neg_contexts)}")

    return "\n".join(lines) if lines else ""


def log_interaction(task: str, output_summary: str) -> None:
    """Add a summary of a completed interaction (task + what was produced)."""
    data = get_memory()
    entry = {
        "task": task[:150],
        "output_summary": output_summary[:200],
        "timestamp": _now(),
    }
    data["summaries"].append(entry)
    data["summaries"] = data["summaries"][-MAX_INTERACTION_SUMMARIES:]
    save_memory(data)


def get_recent_interactions() -> str:
    """Return formatted string of recent tasks for context injection."""
    data = get_memory()
    summaries = data.get("summaries", [])
    if not summaries:
        return ""
    lines = ["Recent work history:"]
    for s in summaries[-5:]:
        ts = s.get("timestamp", "")[:10]
        lines.append(f"  [{ts}] {s.get('task', '')} → {s.get('output_summary', '')}")
    return "\n".join(lines)


def cache_research(query: str, result: str) -> None:
    """Store a web search result with timestamp."""
    data = get_memory()
    data["research_cache"][query.lower().strip()] = {
        "result": result[:4000],
        "timestamp": _now_ts(),
    }
    # Prune cache if too large (keep newest 50)
    cache = data["research_cache"]
    if len(cache) > 50:
        sorted_keys = sorted(cache.keys(), key=lambda k: cache[k]["timestamp"])
        for old_key in sorted_keys[:len(cache) - 50]:
            del cache[old_key]
    save_memory(data)


def get_cached_research(query: str) -> str:
    """Return cached result if fresh (< 24 hours). Otherwise None."""
    data = get_memory()
    entry = data.get("research_cache", {}).get(query.lower().strip())
    if not entry:
        return None
    age = _now_ts() - entry.get("timestamp", 0)
    if age > CACHE_TTL_SECONDS:
        return None
    return entry.get("result", "")


def get_memory_context() -> str:
    """
    Build a comprehensive memory context string for AI prompt injection.
    Includes: active brand, preferences, recent feedback patterns.
    Max ~2000 chars.
    """
    parts = []

    brand = get_brand()
    if brand:
        brand_lines = ["Active Brand Identity:"]
        for key in ["name", "primary_color", "secondary_color", "font", "voice",
                    "industry", "target_audience", "logo_desc"]:
            if brand.get(key):
                brand_lines.append(f"  {key}: {brand[key]}")
        parts.append("\n".join(brand_lines))

    prefs = get_preferences()
    if prefs:
        pref_lines = ["User Preferences:"]
        for key, val in prefs.items():
            if not key.startswith("_"):
                pref_lines.append(f"  {key}: {val}")
        parts.append("\n".join(pref_lines))

    feedback = get_feedback_summary()
    if feedback:
        parts.append(f"Feedback History:\n{feedback}")

    recent = get_recent_interactions()
    if recent:
        parts.append(recent)

    ctx = "\n\n".join(parts)
    return ctx[:2000] if ctx else ""
