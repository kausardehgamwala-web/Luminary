"""
luminary_safety.py
==================
Core safety engine for Luminary AI.
Implements a multi-layered, non-bypassable content validation gate.
Pure Python standard library only.
"""

import re
import base64

# Dataclass for safety results
class SafetyResult:
    def __init__(self, safe: bool, category: str = "none", severity: str = "none", reason: str = "", safe_alternative: str = ""):
        self.safe = safe
        self.category = category
        self.severity = severity
        self.reason = reason
        self.safe_alternative = safe_alternative

    def to_dict(self):
        return {
            "safe": self.safe,
            "category": self.category,
            "severity": self.severity,
            "reason": self.reason,
            "safe_alternative": self.safe_alternative
        }

# ─── Prohibited Word Lists ───

# High-conviction explicit/sexual terms (exact or substring)
SEXUAL_TERMS = {
    "nude", "nudity", "naked", "porn", "pornography", "nsfw", "xxx", "hentai", 
    "erotic", "orgasm", "penis", "vagina", "genitalia", "genital", "stripper", 
    "fetish", "erotica", "topless", "undressed", "nakedness", "intercourse",
    "clitoris", "testicles", "semen", "ejaculate", "masturbate", "coitus",
    "anal sex", "oral sex", "vulva", "slut", "whore", "escort girl", "prostitute"
}

# Ambiguous terms that are flag-worthy only when combined with minor/youth context or other sexualizing terms
AMBIGUOUS_SEXUAL = {
    "sensual", "sexy", "seductive", "lingerie", "underwear", "panties", "bikini",
    "swimsuit", "swimwear", "topless", "cleavage", "bare", "naked", "exposed", "bedroom",
    "latex", "leather outfit"
}

MINOR_TERMS = {
    "child", "minor", "teen", "teenager", "under 18", "schoolgirl", "schoolboy", 
    "lolita", "youth", "kid", "kids", "girl", "boy", "toddler", "baby"
}

DANGEROUS_TERMS = {
    "system32", "steal passwords", "keylogger", "ransomware", "trojan", "malware", 
    "ddos attack", "exfiltrate data", "delete windows", "format c", "exploit payload",
    "bomb", "weapon", "explosive", "terrorism"
}

PROFANITY_TERMS = {
    "fuck", "shit", "bitch", "asshole", "cunt", "motherfucker", "bastard", 
    "pussy", "dick", "cock", "crap", "wanker", "prick", "bollocks"
}

HATE_TERMS = {
    "nigger", "kike", "chink", "faggot", "dyke", "retard", "spic", "tranny",
    "dehumanize", "hateful", "supremacy", "neo-nazi", "propaganda"
}

# Leetspeak translation table
LEET_MAP = str.maketrans("4310578", "aeiosbt")

def _normalize_text(text: str) -> str:
    """Normalizes text by converting to lowercase, removing punctuation, and translating leetspeak."""
    if not text:
        return ""
    text_lower = text.lower()
    
    # Strip spacing tricks (e.g. "n u d e" -> "nude")
    # We do this by checking words that have spaces between every single letter.
    spaced_words = re.findall(r'\b(?:[a-z]\s+){2,}[a-z]\b', text_lower)
    for sw in spaced_words:
        cleaned_sw = sw.replace(" ", "")
        text_lower = text_lower.replace(sw, cleaned_sw)

    # Translate leetspeak
    text_leet = text_lower.translate(LEET_MAP)
    
    # Remove common punctuation/non-alphanumeric
    normalized = re.sub(r'[^a-z0-9\s]', '', text_leet)
    return normalized

def _check_base64(text: str) -> str:
    """Checks if the text contains base64 encoded strings and decodes them for inspection."""
    # Look for common base64 format strings (length >= 16)
    candidates = re.findall(r'[a-zA-Z0-9+/=]{16,}', text)
    decoded_chunks = []
    for c in candidates:
        try:
            decoded = base64.b64decode(c).decode("utf-8", errors="ignore")
            if len(decoded) > 5 and any(word in decoded.lower() for word in SEXUAL_TERMS):
                decoded_chunks.append(decoded)
        except Exception:
            pass
    return " ".join(decoded_chunks)

def inspect_prompt(prompt: str) -> SafetyResult:
    """
    Evaluates a user prompt or external context for safety compliance.
    Strictly blocks sexual/explicit material, minor sexualization, hate speech, and profanity.
    Allows normal fashion, fitness, and portraits.
    """
    if not prompt:
        return SafetyResult(safe=True)

    # Decode and append any hidden base64 content
    base64_decoded = _check_base64(prompt)
    full_text = prompt + " " + base64_decoded
    normalized = _normalize_text(full_text)
    words = set(normalized.split())

    # 0. Dangerous & Malicious Content Check
    found_dangerous = [t for t in DANGEROUS_TERMS if t in normalized]
    if found_dangerous:
        return SafetyResult(
            safe=False,
            category="dangerous_content",
            severity="critical",
            reason=f"Prohibited dangerous content detected: {found_dangerous[0]}",
            safe_alternative="I can't help with that request. Let's focus on something we can do together — like professional marketing copy, high-end brand visuals, or premium design campaigns."
        )

    # 1. Zero-Tolerance Explicit / Sexual Check
    # Check exact matching of critical words (this is completely safe from substring false positives)
    found_sexual = words.intersection(SEXUAL_TERMS)
    if found_sexual:
        return SafetyResult(
            safe=False,
            category="sexual_explicit",
            severity="critical",
            reason=f"Prohibited explicit content detected: {list(found_sexual)[0]}",
            safe_alternative="I can't help with that request. Let's focus on something we can do together — like professional marketing copy, high-end brand visuals, or premium design campaigns."
        )

    # Check substring matches only for specific, safe-to-match roots (prevents Scunthorpe false positives like 'semen' in 'advertisement')
    SUBSTRING_ROOTS = {"porn", "nude", "sex", "hentai", "genital"}
    for term in SUBSTRING_ROOTS:
        if term in normalized:
            # Check if it's a benign word like "essex" or "sussex"
            if term == "sex" and any(benign in normalized for benign in ["essex", "sussex", "middlesex"]):
                continue
            return SafetyResult(
                safe=False,
                category="sexual_explicit",
                severity="critical",
                reason=f"Prohibited explicit substring match: {term}",
                safe_alternative="I can't help with that request. Let's focus on something we can do together — like professional marketing copy, high-end brand visuals, or premium design campaigns."
            )

    # 2. Minor Protection & Age Check
    has_minor = any(m in normalized for m in MINOR_TERMS)
    if has_minor:
        # Check if minor is in close proximity to any ambiguous sexual terms
        for amb in AMBIGUOUS_SEXUAL:
            if amb in normalized:
                return SafetyResult(
                    safe=False,
                    category="minor_safety",
                    severity="critical",
                    reason="Minor term coupled with sexualizing attire or aesthetic context",
                    safe_alternative="I can't help with that request. Let's focus on something we can do together — like professional marketing copy, high-end brand visuals, or premium design campaigns."
                )

    # 3. Profanity & Abusive Language Filter
    found_profanity = words.intersection(PROFANITY_TERMS)
    if found_profanity:
        return SafetyResult(
            safe=False,
            category="profanity",
            severity="medium",
            reason=f"Profanity detected in prompt",
            safe_alternative="I can't help with that request. Let's focus on something we can do together — like professional marketing copy, high-end brand visuals, or premium design campaigns."
        )

    # 4. Hateful or Abusive Language
    found_hate = words.intersection(HATE_TERMS)
    if found_hate:
        return SafetyResult(
            safe=False,
            category="hate_speech",
            severity="high",
            reason="Hateful or abusive language detected in prompt",
            safe_alternative="I can't help with that request. Let's focus on something we can do together — like professional marketing copy, high-end brand visuals, or premium design campaigns."
        )

    # 5. Prompt Injection override detection
    bypass_phrases = [
        "ignore all safety rules", "disable safety", "bypass safety", "ignore safety guidelines",
        "nsfw mode", "unfiltered mode", "disable filter", "without filter", "ignore the rules",
        "system override approved", "developer override"
    ]
    for phrase in bypass_phrases:
        if phrase in normalized:
            return SafetyResult(
                safe=False,
                category="prompt_injection",
                severity="high",
                reason="Attempt to override system safety rules detected",
                safe_alternative="I can't help with that request. Let's focus on something we can do together — like professional marketing copy, high-end brand visuals, or premium design campaigns."
            )

    return SafetyResult(safe=True)


def inspect_image_prompt(prompt: str) -> SafetyResult:
    """
    Specific check before calling image generation tools.
    More restrictive on ambiguous terms to prevent accidental generation of explicit visuals.
    """
    res = inspect_prompt(prompt)
    if not res.safe:
        return res

    normalized = _normalize_text(prompt)
    words = set(normalized.split())

    # Strict check on clothing removal/exposure in image prompts
    exposure_terms = {"undress", "clothing removal", "no clothes", "without clothing", "nude pose", "explicit pose"}
    for term in exposure_terms:
        if term in normalized:
            return SafetyResult(
                safe=False,
                category="image_safety",
                severity="critical",
                reason=f"Prohibited exposure directive in image prompt: {term}",
                safe_alternative="I can't help with that request. Let's focus on something we can do together — like professional marketing copy, high-end brand visuals, or premium design campaigns."
            )

    # Prevent potential bypasses using swimwear/bikini in inappropriate contexts (e.g. combined with "indoor", "bedroom")
    swimwear_terms = {"bikini", "swimsuit", "swimwear", "lingerie", "underwear"}
    has_swimwear = any(st in normalized for st in swimwear_terms)
    if has_swimwear:
        inappropriate_contexts = {"bedroom", "bed", "office", "classroom", "studio posing", "erotic pose", "sexy pose"}
        has_bad_context = any(ctx in normalized for ctx in inappropriate_contexts)
        if has_bad_context:
            return SafetyResult(
                safe=False,
                category="image_safety",
                severity="high",
                reason="Swimwear/attire requested in an inappropriate indoor or sexually suggestive context",
                safe_alternative="I can't help with that request. Let's focus on something we can do together — like professional marketing copy, high-end brand visuals, or premium design campaigns."
            )

    return SafetyResult(safe=True)


def inspect_output(text: str) -> SafetyResult:
    """
    Post-generation check for text safety.
    If the generated model output somehow includes profanity, slurs, or sexual content, it is blocked.
    """
    if not text:
        return SafetyResult(safe=True)

    normalized = _normalize_text(text)
    words = set(normalized.split())

    # Check for direct sexual/explicit leaks
    found_sexual = words.intersection(SEXUAL_TERMS)
    if found_sexual:
        return SafetyResult(
            safe=False,
            category="output_sexual",
            severity="critical",
            reason=f"Generated output contained prohibited sexual term: {list(found_sexual)[0]}",
            safe_alternative="I can't help with that request. Let's focus on something we can do together — like professional marketing copy, high-end brand visuals, or premium design campaigns."
        )

    # Check for profanity leak
    found_profanity = words.intersection(PROFANITY_TERMS)
    if found_profanity:
        return SafetyResult(
            safe=False,
            category="output_profanity",
            severity="medium",
            reason=f"Generated output contained profanity: {list(found_profanity)[0]}",
            safe_alternative="I can't help with that request. Let's focus on something we can do together — like professional marketing copy, high-end brand visuals, or premium design campaigns."
        )

    # Check for slurs/hate
    found_hate = words.intersection(HATE_TERMS)
    if found_hate:
        return SafetyResult(
            safe=False,
            category="output_hate",
            severity="high",
            reason="Generated output contained hateful language",
            safe_alternative="I can't help with that request. Let's focus on something we can do together — like professional marketing copy, high-end brand visuals, or premium design campaigns."
        )

    return SafetyResult(safe=True)


def filter_profanity(text: str) -> str:
    """Utility to clean minor profanities in-place instead of outright blocking when appropriate."""
    if not text:
        return ""
    cleaned = text
    for word in PROFANITY_TERMS:
        # Match word bounds case-insensitively
        pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
        cleaned = pattern.sub("[clean]", cleaned)
    return cleaned
