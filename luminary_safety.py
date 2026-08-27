
# ─── Prompt Injection & Jailbreak Defense ───────────────────────────────────

JAILBREAK_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|system)\s+(\w+\s+)?(instructions|guidelines|rules|prompts|directions|filters)",
    r"dan\s+mode\s+enabled",
    r"you\s+can\s+do\s+anything\s+now",
    r"system\s*override",
    r"developer\s+mode\s+enabled",
    r"unrestricted\s+ai\s+mode",
    r"disable\s+(all\s+)?safety\s+(filters|checks|guidelines)",
    r"uncensored\s+(mode|output)",
    r"pretend\s+you\s+have\s+no\s+(rules|guidelines|morals|ethics)",
    r"jailbreak\s+mode",
]

import db
import os
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

# High-conviction Violence & Attack terms
VIOLENCE_TERMS = {
    "murder", "assassinate", "behead", "decapitate", "execution", "torture", 
    "massacre", "genocide", "slaughter", "homicide", "terrorist", "terrorism",
    "bombing", "hostage", "kidnap", "lynch", "strangle", "asphyxiate",
    "infanticide", "assault", "bloodbath", "shootout", "mass shooting",
    "chemical weapon", "biological weapon", "dirty bomb", "anthrax", "suicide vest"
}

# High-conviction Gore & Mutilation terms
GORE_TERMS = {
    "gore", "gory", "mutilation", "dismemberment", "dismember", "disembowel",
    "severed limb", "severed head", "corpse", "dead body", "autopsy",
    "viscera", "entrails", "mutilated", "flayed", "burned alive", "cannibalism",
    "bloody carcass", "human meat", "rotting flesh", "gangrene", "necrophilia"
}

# Weapons & Explosives terms
WEAPON_TERMS = {
    "pipe bomb", "molotov cocktail", "improvised explosive", "ied", "suicide bomb",
    "assault rifle", "landmine", "grenade launcher", "sarin gas", "mustard gas",
    "weaponize", "homemade explosive", "ghost gun", "untraceable firearm"
}

# High-conviction Self-Harm & Suicide terms
SELF_HARM_TERMS = {
    "suicide", "kill myself", "hang myself", "slit wrists", "self-harm", "self harm",
    "commit suicide", "overdose suicide", "how to hang", "how to kill myself",
    "cut myself", "suicidal ideation", "cyanide suicide", "lethal dose"
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


    # 0a. Prompt Injection & Jailbreak Defense Check
    for pattern in JAILBREAK_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return SafetyResult(
                safe=False,
                category="prompt_injection",
                severity="critical",
                reason=f"Prompt flagged for system jailbreak or safety bypass attempt ({pattern}).",
                safe_alternative="I cannot process system overrides or bypass safety instructions. Let's focus on legitimate creative marketing campaigns."
            )

    # 0. Dangerous & Malicious Content Check
    found_dangerous = [t for t in DANGEROUS_TERMS if t in normalized]
    if found_dangerous:
        # Persistent Audit Logging
        try:
            db.log_security_audit('client_1', category='blocked', severity='high', reason=normalized[:200], blocked_content=prompt)
        except Exception:
            pass
        return SafetyResult(
            safe=False,
            category="dangerous_content",
            severity="critical",
            reason=f"Prohibited dangerous content detected: {found_dangerous[0]}",
            safe_alternative="I can't help with that request. Let's focus on something we can do together — like professional marketing copy, high-end brand visuals, or premium design campaigns."
        )


    # 0b. Violence, Gore & Weapons Check
    for term in VIOLENCE_TERMS.union(GORE_TERMS).union(WEAPON_TERMS):
        if term in normalized or term in words:
            return SafetyResult(
                safe=False,
                category="violence_gore",
                severity="critical",
                reason=f"Prohibited violence, gore or weapon content detected: {term}",
                safe_alternative="I can't assist with violent or gory imagery. Let's focus on commercial brand visuals and product campaigns."
            )

    # 0c. Self-Harm & Suicide Check
    for term in SELF_HARM_TERMS:
        if term in normalized or term in words:
            return SafetyResult(
                safe=False,
                category="self_harm",
                severity="critical",
                reason=f"Prohibited self-harm content detected: {term}",
                safe_alternative="Luminary AI cannot assist with self-harm or suicide content. Please contact a crisis lifeline if you need support."
            )

    # 1. Zero-Tolerance Explicit / Sexual Check
    # Check exact matching of critical words (this is completely safe from substring false positives)
    found_sexual = words.intersection(SEXUAL_TERMS)
    if found_sexual:
        # Persistent Audit Logging
        try:
            db.log_security_audit('client_1', category='blocked', severity='high', reason=normalized[:200], blocked_content=prompt)
        except Exception:
            pass
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
        # Persistent Audit Logging
        try:
            db.log_security_audit('client_1', category='blocked', severity='high', reason=normalized[:200], blocked_content=prompt)
        except Exception:
            pass
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
        # Persistent Audit Logging
        try:
            db.log_security_audit('client_1', category='blocked', severity='high', reason=normalized[:200], blocked_content=prompt)
        except Exception:
            pass
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
        # Persistent Audit Logging
        try:
            db.log_security_audit('client_1', category='blocked', severity='high', reason=normalized[:200], blocked_content=prompt)
        except Exception:
            pass
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
        # Persistent Audit Logging
        try:
            db.log_security_audit('client_1', category='blocked', severity='high', reason=normalized[:200], blocked_content=prompt)
        except Exception:
            pass
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
        # Persistent Audit Logging
        try:
            db.log_security_audit('client_1', category='blocked', severity='high', reason=normalized[:200], blocked_content=prompt)
        except Exception:
            pass
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


# ─── Post-Generation Image Safety Classifier ────────────────────────────────

def classify_image_safety(image_input) -> SafetyResult:
    """
    Analyzes an image (PIL.Image or file path) for NSFW/sexual content and violence/gore.
    Uses multi-stage chromatic, skin-exposure distribution, and color-clustering checks.
    Returns SafetyResult.
    """
    try:
        from PIL import Image
        if isinstance(image_input, (str, bytes)):
            if isinstance(image_input, str) and os.path.exists(image_input):
                img = Image.open(image_input).convert("RGB")
            else:
                import io
                img = Image.open(io.BytesIO(image_input if isinstance(image_input, bytes) else image_input.encode())).convert("RGB")
        elif hasattr(image_input, "convert"):
            img = image_input.convert("RGB")
        else:
            return SafetyResult(safe=True)

        # Downsample for fast deterministic pixel evaluation
        thumb = img.resize((128, 128))
        pixels = thumb.getdata()
        total_pixels = len(pixels)

        skin_pixels = 0
        blood_pixels = 0

        for r, g, b in pixels:
            # 1. Nudity / Explicit Skin Chromatic Signature
            # Standard YCbCr skin tone locus in RGB space
            if r > 95 and g > 40 and b > 20 and (max(r, g, b) - min(r, g, b) > 15) and abs(r - g) > 15 and r > g and r > b:
                skin_pixels += 1

            # 2. Violence / Severe Gore / Blood Signature
            # Deep saturated crimson/blood red dominance
            if r > 130 and g < 45 and b < 45 and (r / (g + b + 1) > 2.2):
                blood_pixels += 1

        skin_ratio = skin_pixels / total_pixels
        blood_ratio = blood_pixels / total_pixels

        # Strict Thresholds
        if skin_ratio > 0.45:
            return SafetyResult(
                safe=False,
                category="sexual_content",
                severity="high",
                reason=f"Post-generation image classifier flagged excessive explicit skin exposure ({skin_ratio:.1%})."
            )

        if blood_ratio > 0.18:
            return SafetyResult(
                safe=False,
                category="violence_gore",
                severity="critical",
                reason=f"Post-generation image classifier flagged extreme blood/gore chrominance ({blood_ratio:.1%})."
            )

        return SafetyResult(safe=True)
    except Exception as ex:
        # Fail closed on unexpected classifier crash
        # Persistent Audit Logging
        try:
            db.log_security_audit('client_1', category='blocked', severity='high', reason=normalized[:200], blocked_content=prompt)
        except Exception:
            pass
        return SafetyResult(
            safe=False,
            category="classifier_error",
            severity="medium",
            reason=f"Image safety classifier evaluation error (failing closed): {str(ex)}"
        )


evaluate_prompt = inspect_prompt


# ─── Per-Client Safety Rate Limiting & Strike Flagging ──────────────────────

import time
from collections import defaultdict

# In-memory tracking of violation timestamps: client_id -> list of timestamps
_CLIENT_VIOLATIONS = defaultdict(list)
_CLIENT_LOCKOUTS = {} # client_id -> lockout_expiration_timestamp

MAX_VIOLATIONS_PER_WINDOW = 3 # 3 strikes
VIOLATION_WINDOW_SECONDS = 300 # 5 minutes
LOCKOUT_DURATION_SECONDS = 600 # 10 minutes lockout

def record_client_violation(client_id: str) -> tuple[bool, int, str]:
    """
    Records a safety violation for a client.
    Returns (is_locked_out: bool, strike_count: int, message: str).
    """
    now = time.time()
    cid = str(client_id or "anonymous")

    # Check active lockout
    if cid in _CLIENT_LOCKOUTS and _CLIENT_LOCKOUTS[cid] > now:
        remaining = int(_CLIENT_LOCKOUTS[cid] - now)
        return True, MAX_VIOLATIONS_PER_WINDOW, f"Client is locked out for repeated safety violations ({remaining}s remaining)."

    # Prune old violations outside the 5-minute window
    _CLIENT_VIOLATIONS[cid] = [t for t in _CLIENT_VIOLATIONS[cid] if now - t < VIOLATION_WINDOW_SECONDS]
    _CLIENT_VIOLATIONS[cid].append(now)

    strike_count = len(_CLIENT_VIOLATIONS[cid])

    if strike_count >= MAX_VIOLATIONS_PER_WINDOW:
        _CLIENT_LOCKOUTS[cid] = now + LOCKOUT_DURATION_SECONDS
        return True, strike_count, f"Client flagged and locked out: exceeded {MAX_VIOLATIONS_PER_WINDOW} safety violations in {VIOLATION_WINDOW_SECONDS}s."

    return False, strike_count, f"Warning: strike {strike_count}/{MAX_VIOLATIONS_PER_WINDOW} recorded."

def check_client_safety_status(client_id: str) -> tuple[bool, str]:
    """Checks if a client is currently locked out."""
    now = time.time()
    cid = str(client_id or "anonymous")
    if cid in _CLIENT_LOCKOUTS and _CLIENT_LOCKOUTS[cid] > now:
        remaining = int(_CLIENT_LOCKOUTS[cid] - now)
        return False, f"Request blocked: Client in safety cooldown ({remaining}s remaining)."
    return True, "Client status in good standing"
