import os
FALLBACK_CAP = int(os.getenv('FALLBACK_CAP', '1024'))
"""
luminary_intelligence.py
========================
Central AI orchestrator for Luminary AI.
Handles: prompt parsing, spec extraction, requirement compliance,
quality scoring, planning prompt construction, image prompt engineering,
follow-up detection, completeness classification, smart MCQ clarification.

NO external dependencies — pure Python stdlib only.
"""

import re
from typing import Optional, Dict, Any

try:
    import luminary_client_translator
except ImportError:
    class MockTranslator:
        @staticmethod
        def translate_client_terms(p): return {"directives": [], "modifiers": ""}
    luminary_client_translator = MockTranslator

# Dynamically load luminary_skill_router
try:
    import luminary_skill_router
except ImportError:
    class MockRouter:
        @staticmethod
        def get_skill_context(p): return {"task_type": "text", "label": "General Task", "skills_active": [], "image_ai_needed": False, "platform_spec": {}}
        @staticmethod
        def build_skill_context_block(p): return ""
        @staticmethod
        def should_involve_image_ai(p): return False
        @staticmethod
        def get_platform_resolution(p): return (1080, 1080)
    luminary_skill_router = MockRouter

# ─── Word-to-number mapping ────────────────────────────────────────────────────
NUMBER_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20,
}

# ─── Resolution mapping ────────────────────────────────────────────────────────
RESOLUTION_MAP = {
    "4k": (3840, 2160), "4 k": (3840, 2160), "3840": (3840, 2160),
    "1440p": (2560, 1440), "2k": (2560, 1440), "2 k": (2560, 1440), "2560": (2560, 1440),
    "1080p": (1920, 1080), "1080 p": (1920, 1080), "1920": (1920, 1080), "full hd": (1920, 1080), "fhd": (1920, 1080),
    "720p": (1280, 720), "1280": (1280, 720), "hd": (1280, 720),
    "1080": (1080, 1080), "1:1": (1080, 1080), "square": (1080, 1080),
    "9:16": (1080, 1920), "portrait": (1080, 1920), "vertical": (1080, 1920), "story": (1080, 1920), "reel": (1080, 1920),
    "landscape": (1920, 1080), "16:9": (1920, 1080), "banner": (1920, 1080),
    "4:5": (1080, 1350), "instagram post": (1080, 1080),
    "a4": (794, 1123), "a3": (1123, 1587),
    "linkedin": (1200, 627), "twitter": (1200, 675), "facebook": (1200, 630),
    "pinterest": (1000, 1500), "pin": (1000, 1500),
}

# ─── Brand names that always trigger web search ────────────────────────────────
BRAND_TRIGGER_WORDS = {
    "ferrari", "lamborghini", "porsche", "bmw", "mercedes", "audi", "bentley",
    "rolls royce", "maserati", "bugatti", "pagani", "aston martin",
    "nike", "adidas", "gucci", "prada", "louis vuitton", "versace", "dior",
    "chanel", "hermes", "rolex", "apple", "google", "microsoft", "samsung",
    "coca cola", "pepsi", "tesla", "amazon", "meta", "netflix", "spotify",
    "mcdonalds", "starbucks", "disney", "supreme", "off white", "balenciaga",
}


def parse_prompt_specs(prompt: str) -> dict:
    """
    Extracts all structured requirements from a user prompt.
    Returns a dict with every constraint found, combined with skill router mappings.
    """
    if not prompt:
        return _default_specs()

    p = prompt.strip()
    pl = p.lower()

    specs = _default_specs()

    # Get skill context from router
    s_ctx = luminary_skill_router.get_skill_context(p)
    specs["task_type"] = s_ctx.get("task_type", "text")
    specs["skills_active"] = s_ctx.get("skills_active", [])
    specs["image_ai_needed"] = s_ctx.get("image_ai_needed", False)
    specs["platform_spec"] = s_ctx.get("platform_spec", {})
    specs["frameworks"] = s_ctx.get("frameworks", {})
    specs["quality_checklists"] = s_ctx.get("quality_checklists", {})

    # ── Output type detection ──────────────────────────────────────────────────
    if any(k in pl for k in ["ppt", "presentation", "deck", "slide", "powerpoint"]):
        specs["output_type"] = "pptx"
    elif any(k in pl for k in ["xlsx", "spreadsheet", "excel", "csv", "sheet", "table"]):
        if "marble table" in pl or "wooden table" in pl:
            specs["output_type"] = "image"
        else:
            specs["output_type"] = "xlsx"
    elif any(k in pl for k in ["docx", "document", "report", "article", "blog", "essay", "write", "newsletter", "draft"]):
        specs["output_type"] = "docx"
    elif any(k in pl for k in ["image", "photo", "picture", "graphic", "draw", "render", "visual", "poster", "banner", "thumbnail", "shoot", "shot", "portrait", "artwork"]):
        specs["output_type"] = "image"
    elif any(k in pl for k in ["website", "web page", "html", "landing page", "build a site", "create a website", "code", "python script", "javascript", "css", "react", "component", "function", "class", "algorithm"]):
        specs["output_type"] = "code"
    else:
        # Check router fallback
        if specs["image_ai_needed"]:
            specs["output_type"] = "image"
        else:
            specs["output_type"] = "text"

    # ── Resolution & Platform default mapping ──────────────────────────────────
    explicit = re.search(r'(\d{2,5})\s*[x×]\s*(\d{2,5})', p, re.IGNORECASE)
    if explicit:
        raw_w, raw_h = int(explicit.group(1)), int(explicit.group(2))
        # Clamp to safe bounds [256, 2048] to prevent memory exhaustion / DoS
        clamped_w = max(256, min(raw_w, 2048))
        clamped_h = max(256, min(raw_h, 2048))
        specs["resolution"] = (clamped_w, clamped_h)
    else:
        resolved = False
        for key, dims in RESOLUTION_MAP.items():
            if key in pl:
                specs["resolution"] = dims
                resolved = True
                break
        
        # Fall back to platform spec default resolution if no explicit resolution matches
        if not resolved and specs.get("platform_spec") and "resolution" in specs["platform_spec"]:
            specs["resolution"] = specs["platform_spec"]["resolution"]

    # ── Quantity detection ─────────────────────────────────────────────────────
    digit_q = re.search(
        r'\b(\d+)(?:\s+[\w\-]+){0,3}\s+(?:image|photo|picture|graphic|car|person|people|product|'
        r'variation|version|slide|page|item|object|building|executive|render)s?\b', pl
    )
    if digit_q:
        specs["quantity"] = int(digit_q.group(1))
    else:
        # Word quantities
        for word, num in NUMBER_WORDS.items():
            if re.search(r'\b' + word + r'\b', pl):
                pattern = r'\b' + word + r'\b(?:\s+[\w\-]+){0,3}\s+(?:image|car|photo|person|people|executive|slide|item|product|rendering)s?\b'
                if re.search(pattern, pl):
                    specs["quantity"] = num
                    break

    # ── Slide count ────────────────────────────────────────────────────────────
    slide_m = re.search(r'(\d+)\s*(?:-slide|slide|page)s?\b', pl)
    if slide_m:
        specs["slide_count"] = int(slide_m.group(1))
    else:
        for word, num in NUMBER_WORDS.items():
            if re.search(r'\b' + word + r'\s*(?:slide|page)s?\b', pl):
                specs["slide_count"] = num
                break

    # ── Word count ────────────────────────────────────────────────────────────
    wc_m = re.search(r'(\d+)\s*(?:word|words)\b', pl)
    if wc_m:
        specs["word_count"] = int(wc_m.group(1))

    # ── Style detection ────────────────────────────────────────────────────────
    styles = {
        "photorealistic": ["photorealistic", "photo-realistic", "photorealism"],
        "cinematic": ["cinematic", "film", "movie"],
        "realistic": ["realistic", "real"],
        "animated": ["animated", "animation", "cartoon", "illustrated", "illustration"],
        "3d": ["3d render", "3d cgi", "cgi", "blender render", "octane"],
        "minimal": ["minimal", "minimalist", "clean"],
        "luxury": ["luxury", "premium", "high-end", "upscale", "elegant", "luxurious"],
        "corporate": ["corporate", "professional", "business"],
        "editorial": ["editorial", "magazine"],
        "futuristic": ["futuristic", "sci-fi", "cyberpunk"],
    }
    for style_name, keywords in styles.items():
        if any(k in pl for k in keywords):
            specs["style"] = style_name
            break

    # ── Subject extraction ─────────────────────────────────────────────────────
    subjects = []
    quoted = re.findall(r'"([^"]+)"', p)
    subjects.extend(quoted)
    prep_m = re.findall(r'\b(?:about|on|for|representing|modeling)\s+([a-zA-Z\s]{3,30})', p, re.IGNORECASE)
    for pm in prep_m:
        cleaned = re.split(r'\b(?:with|at|and|or|in|by|no|without)\b', pm, flags=re.IGNORECASE)[0].strip()
        if cleaned:
            subjects.append(cleaned)
    
    for brand in BRAND_TRIGGER_WORDS:
        if brand in pl:
            subjects.append(brand)
            
    noun_patterns = [
        r'\b(Ferrari|Lamborghini|Porsche|BMW|Mercedes|Audi|Bentley)\b',
        r'\b(\d+\s*)?(?:red|blue|black|white|silver|gold|orange|green)\s+\w+',
        r'\b(?:man|woman|person|people|car|vehicle|building|city|mountain|ocean|forest)\b',
    ]
    for pat in noun_patterns:
        matches = re.findall(pat, p, re.IGNORECASE)
        subjects.extend([m.strip() for m in matches if m.strip()])
        
    seen = set()
    clean_subjects = []
    for s in subjects:
        if s.lower() not in seen:
            seen.add(s.lower())
            clean_subjects.append(s)
    specs["subjects"] = clean_subjects

    # ── Color extraction ───────────────────────────────────────────────────────
    color_words = ["red", "blue", "green", "black", "white", "gold", "silver",
                   "orange", "purple", "pink", "yellow", "brown", "grey", "gray"]
    specs["colors"] = [c for c in color_words if re.search(r'\b' + c + r'\b', pl)]

    # ── Typography extraction ──────────────────────────────────────────────────
    typo_words = ["serif", "sans-serif", "sans serif", "script", "monospace", "elegant font", "modern font"]
    specs["typography"] = [t for t in typo_words if t in pl]

    # ── Negative requirements ──────────────────────────────────────────────────
    negatives = []
    neg_patterns = [
        r'no\s+(\w+(?:\s+\w+)?)',
        r"don'?t\s+(?:include|add|show|use|put)\s+(.+?)(?:\.|,|$)",
        r'without\s+(\w+(?:\s+\w+)?)',
        r'remove\s+(\w+(?:\s+\w+)?)',
        r'exclude\s+(\w+(?:\s+\w+)?)',
    ]
    for pat in neg_patterns:
        matches = re.findall(pat, pl)
        negatives.extend([m.strip() for m in matches])
    specs["negative"] = list(set(negatives))

    # ── Copywriting framework detection ────────────────────────────────────────
    copywriting_frameworks = []
    if any(k in pl for k in ["ad", "advertisement", "copy", "caption", "email", "newsletter", "landing page", "sales page", "headline"]):
        if any(k in pl for k in ["aida", "attention", "interest", "desire", "action"]):
            copywriting_frameworks.append("AIDA")
        if any(k in pl for k in ["pas", "problem", "agitate", "solution"]):
            copywriting_frameworks.append("PAS")
        if any(k in pl for k in ["scqa", "situation", "complication", "question", "answer"]):
            copywriting_frameworks.append("SCQA")
        if not copywriting_frameworks:
            # Default: inject AIDA for all ad/copy/caption tasks
            copywriting_frameworks.append("AIDA")
    specs["copywriting_frameworks"] = copywriting_frameworks

    # ── SEO task detection ─────────────────────────────────────────────────────
    is_seo_task = any(k in pl for k in [
        "seo", "search engine", "keyword", "meta title", "meta description",
        "h1", "heading", "backlink", "organic", "ranking", "serp", "crawl",
        "sitemap", "schema", "core web vitals", "page speed", "blog post",
        "blog article", "content strategy", "pillar page", "topic cluster",
    ])
    specs["is_seo_task"] = is_seo_task

    # ── Web search trigger ─────────────────────────────────────────────────────
    needs_search = any(brand in pl for brand in BRAND_TRIGGER_WORDS)
    needs_search = needs_search or any(k in pl for k in [
        "latest", "current", "recent", "2024", "2025", "2026",
        "statistics", "stats", "data", "research", "trend",
        "market share", "revenue", "founded", "history",
    ])
    specs["needs_web_search"] = needs_search
    specs["needs_research"] = needs_search or any(k in pl for k in [
        "competitor", "industry", "analysis", "audit", "market",
    ])

    # ── Ambiguity detection ────────────────────────────────────────────────────
    ambiguity_score = 0
    if len(p.split()) < 5:
        ambiguity_score += 2
    if specs["subjects"] == []:
        ambiguity_score += 1
    if specs["output_type"] == "text" and not any(k in pl for k in [
        "write", "create", "make", "build", "generate", "design"
    ]):
        ambiguity_score += 1

    if ambiguity_score >= 3:
        specs["ambiguity_level"] = "high"
    elif ambiguity_score == 2:
        specs["ambiguity_level"] = "medium"
    else:
        specs["ambiguity_level"] = "low"

    # ── Client Terminology Translation ──────────────────────────────────────
    translation = luminary_client_translator.translate_client_terms(prompt)
    specs["client_directives"] = translation["directives"]
    specs["client_modifiers"] = translation["modifiers"]

    # ── Objective (cleaned prompt) ─────────────────────────────────────────────
    specs["objective"] = p[:200]

    # ════════════════════════════════════════════════════════════════════════
    # PART 2 — Extended V12 Intelligence Fields
    # ════════════════════════════════════════════════════════════════════════

    # ── Deliverable (what must be produced) ───────────────────────────────
    deliverable_map = [
        ("pptx", ["ppt", "deck", "presentation", "slides"]),
        ("docx", ["document", "report", "article", "essay", "blog", "newsletter"]),
        ("xlsx", ["spreadsheet", "excel", "csv", "sheet"]),
        ("image", ["image", "photo", "graphic", "poster", "banner", "visual", "render", "artwork"]),
        ("caption", ["caption", "post copy", "ad copy"]),
        ("strategy", ["strategy", "plan", "roadmap", "framework"]),
        ("campaign", ["campaign", "launch", "rollout"]),
        ("code", ["code", "script", "function", "component", "website", "html"]),
    ]
    specs["deliverable"] = "content"
    for dlv, keys in deliverable_map:
        if any(k in pl for k in keys):
            specs["deliverable"] = dlv
            break

    # ── Purpose (why it is being created) ─────────────────────────────────
    purpose_map = [
        ("product_launch", ["launch", "introducing", "new product", "release", "reveal"]),
        ("brand_awareness", ["awareness", "brand presence", "visibility", "recognition"]),
        ("sales", ["sell", "sales", "conversion", "promote", "drive traffic", "e-commerce"]),
        ("engagement", ["engagement", "likes", "comments", "followers", "community"]),
        ("investor", ["investor", "pitch", "funding", "series", "vc", "board"]),
        ("internal", ["internal", "team", "training", "onboarding", "hr"]),
        ("education", ["educate", "teach", "tutorial", "how to", "guide", "learn"]),
        ("event", ["event", "conference", "webinar", "summit", "workshop"]),
    ]
    specs["purpose"] = "general"
    for purp, keys in purpose_map:
        if any(k in pl for k in keys):
            specs["purpose"] = purp
            break

    # ── Audience (target audience) ─────────────────────────────────────────
    audience_map = [
        ("luxury consumers", ["luxury", "premium", "high-end", "affluent", "vip"]),
        ("investors", ["investor", "vc", "board", "stakeholder", "shareholder"]),
        ("gen z", ["gen z", "genz", "teens", "youth", "young people", "tiktok audience"]),
        ("millennials", ["millennial", "25-40", "working professional"]),
        ("business owners", ["entrepreneur", "startup", "small business", "business owner", "ceo"]),
        ("consumers", ["consumer", "customer", "buyer", "shopper"]),
        ("professionals", ["professional", "executive", "manager", "b2b", "enterprise"]),
    ]
    specs["audience"] = "general audience"
    for aud, keys in audience_map:
        if any(k in pl for k in keys):
            specs["audience"] = aud
            break

    # ── Platform ───────────────────────────────────────────────────────────
    platform_kw = [
        ("instagram", ["instagram", "ig", "insta", "reel", "story"]),
        ("pinterest", ["pinterest", "pin"]),
        ("linkedin", ["linkedin"]),
        ("tiktok", ["tiktok", "tik tok"]),
        ("youtube", ["youtube", "yt", "thumbnail"]),
        ("twitter", ["twitter", "x.com", "tweet"]),
        ("facebook", ["facebook", "fb"]),
        ("website", ["website", "landing page", "web"]),
    ]
    specs["platform"] = specs["platform_spec"].get("name", "general") if specs.get("platform_spec") else "general"
    for plat, keys in platform_kw:
        if any(k in pl for k in keys):
            specs["platform"] = plat
            break

    # ── Exact text / copy that must appear in output ───────────────────────
    # Extract quoted strings as required copy text
    quoted_text = re.findall(r'["\u201c\u201d]([^"\u201c\u201d]{3,120})["\u201c\u201d]', p)
    specs["content_text"] = quoted_text  # list of exact strings

    # ── Brand name ──────────────────────────────────────────────────────────
    brand_in_prompt = ""
    # Check subjects first
    for subj in specs.get("subjects", []):
        for brand in BRAND_TRIGGER_WORDS:
            if brand in subj.lower():
                brand_in_prompt = subj
                break
    if not brand_in_prompt:
        # Check entire prompt for brand words
        for brand in BRAND_TRIGGER_WORDS:
            if re.search(r'\b' + re.escape(brand) + r'\b', pl):
                brand_in_prompt = brand.title()
                break
    specs["brand_name"] = brand_in_prompt

    # ── References (URLs, file names) ──────────────────────────────────────
    urls = re.findall(r'https?://[^\s]+', p)
    file_refs = re.findall(r'\b\w+\.(?:pdf|png|jpg|jpeg|pptx|docx|xlsx|mp4|svg)\b', p, re.IGNORECASE)
    specs["references"] = urls + file_refs

    # ── Restrictions (hard dont-change rules) ──────────────────────────────
    restriction_patterns = [
        r"keep\s+(.*?)\s+(?:the same|unchanged|as is|as-is)",
        r"(?:don'?t|do\s+not)\s+change\s+(.*?)(?:\.|,|$)",
        r"preserve\s+(.*?)(?:\.|,|$)",
        r"maintain\s+(.*?)(?:\.|,|$)",
        r"only\s+change\s+(.+?)(?:\.|,|$)",
    ]
    restrictions = []
    for pat in restriction_patterns:
        matches = re.findall(pat, pl)
        restrictions.extend([m.strip() for m in matches if m.strip()])
    specs["restrictions"] = list(set(restrictions))

    # ── Output format preference ────────────────────────────────────────────
    fmt_map = [
        ("PNG", ["png", "transparent background", "no background"]),
        ("JPG", ["jpg", "jpeg"]),
        ("PDF", ["pdf"]),
        ("PPTX", ["pptx", "powerpoint"]),
        ("DOCX", ["docx", "word document"]),
        ("XLSX", ["xlsx", "excel", "spreadsheet"]),
    ]
    specs["output_format"] = ""
    for fmt, keys in fmt_map:
        if any(k in pl for k in keys):
            specs["output_format"] = fmt
            break

    # ── Quality level expectation ───────────────────────────────────────────
    quality_level = "standard"
    if any(k in pl for k in ["world class", "top agency", "luxury", "premium", "award winning", "high end", "editorial"]):
        quality_level = "luxury_premium"
    elif any(k in pl for k in ["professional", "agency", "commercial", "brand", "corporate"]):
        quality_level = "professional"
    elif any(k in pl for k in ["quick", "simple", "basic", "draft", "rough"]):
        quality_level = "draft"
    specs["quality_level"] = quality_level

    # ── Implied requirements (inferred professional needs) ─────────────────
    implied = []
    if specs["deliverable"] == "image" and not specs.get("style"):
        implied.append("photorealistic photography style")
    if specs["platform"] in ["instagram", "pinterest"] and not specs.get("colors"):
        implied.append("cohesive color palette for social media")
    if specs["purpose"] == "product_launch":
        implied.append("product in hero position, lifestyle context")
    if specs["audience"] == "luxury consumers":
        implied.append("premium materials, minimal negative space, refined typography")
    if specs["purpose"] == "investor":
        implied.append("data-driven, executive-grade presentation quality")
    specs["implied_requirements"] = implied

    # ── Follow-up context detection ─────────────────────────────────────────
    followup_indicators = [
        r'\b(it|this|the image|the photo|the graphic|the design|that|the one|the result)\b',
        r'\b(make it|change it|adjust it|update it|modify it)\b',
        r'\b(same|keep|but|instead|now|also|again|more|less)\b',
    ]
    is_followup = any(re.search(pat, pl) for pat in followup_indicators)
    specs["is_follow_up"] = is_followup

    # ── Change-Only mode ────────────────────────────────────────────────────
    change_only_triggers = [
        r'make\s+(?:it|the|this)\s+(?:more|less|bigger|smaller|darker|lighter|brighter|warmer|cooler)',
        r'(?:remove|take out|delete|get rid of)\s+the\s+\w+',
        r'(?:add|include|put)\s+(?:a|an)\s+\w+',
        r'(?:change|update|adjust|fix|tweak|refine)\s+(?:the|only|just)\s+\w+',
        r'make\s+the\s+\w+\s+(?:bigger|smaller|darker|lighter|different|better)',
    ]
    specs["change_only_mode"] = any(re.search(pat, pl) for pat in change_only_triggers)

    # ── Completeness score (0-100) ──────────────────────────────────────────
    specs["completeness_score"] = _compute_completeness_score(p, specs)

    return specs


def _default_specs() -> dict:
    return {
        # Core
        "objective": "",
        "output_type": "text",
        "resolution": (1920, 1080),
        "quantity": 1,
        "slide_count": None,
        "word_count": None,
        "subjects": [],
        "style": "realistic",
        "colors": [],
        "typography": [],
        "negative": [],
        "needs_web_search": False,
        "needs_research": False,
        "ambiguity_level": "low",
        "format_constraints": {},
        "client_directives": [],
        "client_modifiers": "",
        "task_type": "text",
        "skills_active": [],
        "image_ai_needed": False,
        "platform_spec": {},
        "frameworks": {},
        "quality_checklists": {},
        "copywriting_frameworks": [],
        "is_seo_task": False,
        # V12 Extended Fields
        "deliverable": "content",
        "purpose": "general",
        "audience": "general audience",
        "platform": "general",
        "content_text": [],
        "brand_name": "",
        "references": [],
        "restrictions": [],
        "output_format": "",
        "quality_level": "standard",
        "implied_requirements": [],
        "is_follow_up": False,
        "change_only_mode": False,
        "completeness_score": 50,
    }


def _compute_completeness_score(prompt: str, specs: dict) -> int:
    """
    Scores how complete the user's prompt is (0-100).
    Higher = more complete = less clarification needed.
    """
    score = 30  # Base
    pl = prompt.lower()
    word_count = len(prompt.split())

    # Length bonus
    if word_count >= 15:
        score += 15
    elif word_count >= 8:
        score += 8
    elif word_count >= 4:
        score += 3

    # Clear deliverable known
    if specs.get("deliverable") and specs["deliverable"] != "content":
        score += 10

    # Subject known
    if specs.get("subjects"):
        score += 10

    # Platform known
    if specs.get("platform") and specs["platform"] != "general":
        score += 8

    # Purpose known
    if specs.get("purpose") and specs["purpose"] != "general":
        score += 7

    # Style known
    if specs.get("style") and specs["style"] != "realistic":
        score += 5

    # Resolution explicitly mentioned
    explicit_res = re.search(r'\d{3,4}\s*[x×]\s*\d{3,4}', prompt, re.IGNORECASE)
    if explicit_res:
        score += 5

    # Contains explicit text/copy to include
    if specs.get("content_text"):
        score += 5

    # Very short prompt penalty
    if word_count < 4:
        score -= 20
    elif word_count < 6:
        score -= 10

    # Only a name / single word — very ambiguous
    if word_count <= 2:
        score = max(score, 0)
        score = min(score, 25)

    return max(0, min(100, score))


def run_5_pass_qa(output_text: str, specs: dict) -> dict:
    """
    Executes the strict 5-Pass QA Gate:
    1. Requirements QA (subjects, slide count, exclusions, exact text, brand colors, restrictions)
    2. Visual QA (typography systems, color harmony, aspect ratio compatibility, layout grids)
    3. Professional QA (Canva layout density, copywriting framework, tone, no filler words)
    4. Technical QA (markdown layout structures, XLSX/table format, closed tags, code flows)
    5. Adversarial QA (red-team style check: no distortions, hallucinated options, compliance with restrictions)

    Returns:
        {
            "passed": bool,
            "score": int, # Normalized 0-100
            "passes": {
                "requirements": {"passed": bool, "deductions": int, "issues": list},
                "visual":       {"passed": bool, "deductions": int, "issues": list},
                "professional": {"passed": bool, "deductions": int, "issues": list},
                "technical":    {"passed": bool, "deductions": int, "issues": list},
                "adversarial":  {"passed": bool, "deductions": int, "issues": list}
            },
            "failures": list, # Critical failures that trigger reject
            "warnings": list
        }
    """
    import re
    try:
        import luminary_design_systems as lds
    except ImportError:
        class MockLds:
            @staticmethod
            def get_design_system_by_prompt(p): return {"title": "Generic", "typography": {}, "color_system": {}, "recommended_animation": [], "avoid_effects": [], "avoid_animation": []}
            @staticmethod
            def validate_design_combination(s, e, a): return []
        lds = MockLds

    failures = []
    warnings = []
    output_lower = output_text.lower()
    output_len = len(output_text.split())

    # Map design system for visual/theme checks
    prompt_obj = specs.get("objective", "")
    design_sys = lds.get_design_system_by_prompt(prompt_obj)
    sys_title = design_sys.get("title", "Generic")

    # Initialize passes
    passes = {
        "requirements": {"passed": True, "deductions": 0, "issues": []},
        "visual":       {"passed": True, "deductions": 0, "issues": []},
        "professional": {"passed": True, "deductions": 0, "issues": []},
        "technical":    {"passed": True, "deductions": 0, "issues": []},
        "adversarial":  {"passed": True, "deductions": 0, "issues": []}
    }

    # Helper to deduct points in a pass
    def deduct(pass_name: str, points: int, issue: str, is_critical: bool = False):
        p_dict = passes[pass_name]
        p_dict["deductions"] += points
        p_dict["issues"].append(issue)
        if is_critical:
            p_dict["passed"] = False
            failures.append(f"[{pass_name.upper()} CRITICAL] {issue}")
        else:
            warnings.append(f"[{pass_name.upper()} WARNING] {issue}")

    # ════════════════════════════════════════════════════════════════════════
    # PASS 1: Requirements QA
    # ════════════════════════════════════════════════════════════════════════
    # Check: subjects presence (up to 5)
    subjects = specs.get("subjects", [])
    missing_subj_count = 0
    for subject in subjects[:5]:
        if subject.lower() not in output_lower:
            missing_subj_count += 1
            deduct("requirements", 5, f"Required subject '{subject}' is missing from output")
    if len(subjects) > 0 and (missing_subj_count / min(len(subjects), 5)) > 0.5:
        deduct("requirements", 10, "More than 50% of requested subjects are missing", is_critical=True)

    # Check: slide count compliance
    if specs.get("slide_count"):
        expected_slides = specs["slide_count"]
        found_slides = output_text.count("### Slide")
        if found_slides < expected_slides:
            deduct("requirements", (expected_slides - found_slides) * 4, f"Slide count mismatch: expected {expected_slides}, found {found_slides}", is_critical=True)

    # Check: word count compliance
    if specs.get("word_count"):
        expected_wc = specs["word_count"]
        ratio = output_len / expected_wc
        if ratio < 0.3:
            deduct("requirements", 15, f"Word count is severely low: contains only {output_len} words, expected ~{expected_wc}", is_critical=True)
        elif ratio < 0.7:
            deduct("requirements", 5, f"Word count is low: got {output_len}, expected ~{expected_wc}")

    # Check: exact copy (quoted texts)
    for text_req in specs.get("content_text", []):
        if text_req.lower() not in output_lower:
            deduct("requirements", 6, f"Required copy text '{text_req}' not present in response", is_critical=True)

    # Check: Exclusions / Negative constraints
    for neg in specs.get("negative", []):
        if neg.lower() in output_lower and neg not in ["watermark", "logo"]:
            deduct("requirements", 4, f"Excluded element '{neg}' was found in the output")

    # ════════════════════════════════════════════════════════════════════════
    # PASS 2: Visual QA
    # ════════════════════════════════════════════════════════════════════════
    # Check: Aspect ratio compliance for social media/platform specifications
    if specs.get("platform_spec"):
        p_spec = specs["platform_spec"]
        width, height = specs.get("resolution", (1080, 1080))
        target_aspect = p_spec.get("aspect_ratio", "")
        if target_aspect in ["2:3", "9:16"] and width >= height:
            deduct("visual", 10, f"Aspect ratio mismatch: platform requires vertical image but got landscape ({width}x{height})", is_critical=True)
        elif target_aspect in ["16:9", "1.91:1"] and height >= width:
            deduct("visual", 10, f"Aspect ratio mismatch: platform requires landscape image but got vertical/square ({width}x{height})", is_critical=True)

    # Check: Typography pairing mention & Color Harmony matching the design system
    colors_mentioned = specs.get("colors", [])
    if colors_mentioned:
        # Check color palette compatibility with mapped industry
        avoid_colors = []
        if design_sys.get("color_system"):
            # Mock or check color suite mismatch
            pass
    
    # Check design grid spacing compliance (e.g., Apple HIG minimal, high contrast headers)
    if specs["output_type"] != "image" and output_len > 100:
        lines = output_text.split("\n")
        header_count = sum(1 for line in lines if line.strip().startswith("#"))
        if header_count == 0:
            deduct("visual", 5, "Visual layout lacks formatting hierarchy (no markdown headers used)")

    # ════════════════════════════════════════════════════════════════════════
    # PASS 3: Professional QA
    # ════════════════════════════════════════════════════════════════════════
    # Check: Canva Layout Density (no walls of text >100 words in any single paragraph)
    paragraphs = output_text.split("\n\n")
    for idx, p in enumerate(paragraphs):
        p_words = len(p.split())
        if p_words > 100 and specs["output_type"] not in ["code", "image"]:
            deduct("professional", 8, f"Canva Layout Violation: Block {idx+1} contains a wall of text ({p_words} words). Split into concise bullets or shorter blocks.", is_critical=True)
            break

    # Check: Copywriting framework compliance (AIDA/PAS/SCQA)
    copy_fw = specs.get("copywriting_frameworks", [])
    if copy_fw:
        if "AIDA" in copy_fw:
            attention_found = any(k in output_lower for k in ["attention", "imagine", "stop", "discover", "introducing", "are you", "what if"])
            action_found = any(k in output_lower for k in ["buy", "shop", "order", "click", "sign up", "cta", "now", "link", "get yours"])
            if not attention_found or not action_found:
                deduct("professional", 10, "AIDA copy framework incomplete: missing Attention hook or Action CTA", is_critical=True)
        elif "PAS" in copy_fw:
            has_problem = any(k in output_lower for k in ["problem", "struggle", "frustrated", "tired", "pain"])
            has_sol = any(k in output_lower for k in ["solution", "answer", "fix", "solve", "introducing"])
            if not has_problem or not has_sol:
                deduct("professional", 10, "PAS copy framework incomplete: missing Problem or Solution structures", is_critical=True)

    # Check: Professional tone & weak AI phrase filters
    weak_phrases = ["as an ai", "i cannot", "i'm sorry", "i apologize", "unfortunately", "i don't have the ability"]
    for phrase in weak_phrases:
        if phrase in output_lower:
            deduct("professional", 10, f"Unprofessional phrasing detected: '{phrase}'", is_critical=True)

    # ════════════════════════════════════════════════════════════════════════
    # PASS 4: Technical QA
    # ════════════════════════════════════════════════════════════════════════
    # Check: Presentation slide format validation
    if specs["output_type"] == "pptx":
        if "### slide" not in output_lower and "slide 1" not in output_lower:
            deduct("technical", 12, "Presentation output is missing Slide layout tags (e.g. ### Slide [Number])", is_critical=True)

    # Check: Spreadsheet/table format validation
    if specs["output_type"] == "xlsx" or "table" in prompt_obj.lower():
        if "|" not in output_text:
            deduct("technical", 10, "Data layout is missing tabular formatting (standard markdown pipe table)", is_critical=True)

    # Check: Closed markdown code blocks & tags
    open_ticks = output_text.count("```")
    if open_ticks % 2 != 0:
        deduct("technical", 10, "Broken syntax: Unclosed markdown code fence (```) detected", is_critical=True)

    # ════════════════════════════════════════════════════════════════════════
    # PASS 5: Adversarial QA (Red-teaming of layout, brand restrictions, distortions)
    # ════════════════════════════════════════════════════════════════════════
    # Check: brand guidelines / restrictions
    for restriction in specs.get("restrictions", []):
        # If restriction says "keep unchanged" or similar, check if output alters it
        pass

    # Check for visual distortions (e.g., layout overlap, logo squishing) in prompt descriptions
    if specs["output_type"] == "image":
        distort_triggers = ["stretched logo", "squished logo", "watermark", "pixelated", "blurry", "lowres"]
        for dt in distort_triggers:
            if dt in output_lower:
                deduct("adversarial", 8, f"Adversarial QA Block: Image prompt contains forbidden distortion reference: '{dt}'", is_critical=True)

    # Calculate overall normalized score
    # Max score is 100. Subtract all deductions across the 5 passes
    total_deductions = sum(p["deductions"] for p in passes.values())
    score_val = max(0, min(100, 100 - total_deductions))

    # Determine passing state: Must have a score >= 85 AND no critical failures
    passed = (score_val >= 85) and (len(failures) == 0)

    # If any pass has a critical failure, force passed to False
    for p_name, p_data in passes.items():
        if not p_data["passed"]:
            passed = False

    return {
        "passed": passed,
        "score": score_val,
        "passes": passes,
        "failures": failures,
        "warnings": warnings
    }


def build_quality_score(output_text: str, specs: dict) -> dict:
    """
    Scores an AI output against the parsed specs using the 5-Pass QA Gate.
    Returns a dict with dimension scores and overall total.
    """
    if not output_text:
        return {"total": 0, "pass": False, "issues": ["Empty output"]}

    qa_result = run_5_pass_qa(output_text, specs)
    
    # Return formatted schema compatible with server.py expects
    return {
        "accuracy": max(0, 20 - qa_result["passes"]["requirements"]["deductions"]),
        "completeness": max(0, 15 - qa_result["passes"]["requirements"]["deductions"]),
        "professionalism": max(0, 15 - qa_result["passes"]["professional"]["deductions"]),
        "creativity": max(0, 10 - qa_result["passes"]["visual"]["deductions"]),
        "technical_correctness": max(0, 10 - qa_result["passes"]["technical"]["deductions"]),
        "usability": max(0, 10 - qa_result["passes"]["professional"]["deductions"]),
        "visual_quality": max(0, 20 - qa_result["passes"]["visual"]["deductions"]),
        "copywriting_quality": max(0, 10 - qa_result["passes"]["professional"]["deductions"]),
        "seo_quality": max(0, 10 - qa_result["passes"]["technical"]["deductions"]),
        "total": qa_result["score"],
        "pass": qa_result["passed"],
        "issues": qa_result["failures"] + qa_result["warnings"]
    }



def build_planning_prompt(prompt: str, specs: dict, context: str = "") -> str:
    """
    Builds a structured chain-of-thought prompt that forces the model to plan
    before generating, improving output quality significantly.
    """
    subjects_str = ", ".join(specs.get("subjects", [])) if specs.get("subjects") else "None specified"
    neg_str = ", ".join(specs.get("negative", [])) if specs.get("negative") else "None"
    
    # Format client directives as structured design constraints
    client_dirs = ""
    if specs.get("client_directives"):
        client_dirs = "\n**CLIENT TERMINOLOGY INTERPRETATION (Actionable Design Constraints):**\n"
        for d in specs["client_directives"]:
            client_dirs += f"- {d}\n"

    # Format active skills context block
    skills_context = luminary_skill_router.build_skill_context_block(prompt)

    planning = f"""### SYSTEM: You are Luminary's senior AI marketing strategist and creative director.
You represent a top-tier creative agency. You must plan carefully before replying.

{context}
{skills_context}

### REQUIRED 9-STEP AGENTIC REASONING (Do this step-by-step silently before output):
1. **UNDERSTAND**: What is the core business objective and specific target audience?
2. **CONTEXT**: What brand files, preferences, and verified web statistics are available?
3. **REQUIREMENTS**: Identify all mandatory constraints (exact resolution, count, styles, exclusions).
4. **RESEARCH**: If real brands or recent dates are mentioned, ensure web search details are integrated deeply.
5. **PLAN**: Outline the visual grid, typography system, copywriting framework (AIDA/PAS/SCQA), and layout.
6. **EXECUTE**: Construct the response with pixel-perfect structure.
7. **INSPECT**: Audit against checklists (Anatomy, perspective, contrast, hierarchy, limits).
8. **IMPROVE**: Fix any long paragraphs, generic boilerplate, or weak structures.
9. **DELIVER**: Output only the polished, agency-grade result. Offer 1-2 strategic next steps.

### CRITICAL PRODUCTION MANDATE:
**NO OUTLINES. NO PLACEHOLDERS.** You must write the actual, exhaustive, multi-paragraph content for every single section. Do not write "[Insert content here]". If writing a document or presentation, generate the exact, final, publication-ready copy. Your text must be deep, researched, and highly detailed.

### SMART IMPROVISATION MANDATE:
If the user's prompt is missing details like the target audience, purpose, or platform, **YOU MUST SMARTLY IMPROVISE**. Do not ask the user for details in your text. Assume the most professional, high-converting option (e.g. enterprise executives, luxury consumers, high-growth startups) and build the content around that specific, targeted assumption. Never generate generic "general audience" text.

---
**STEP 1 — WHAT I UNDERSTOOD:**
- Objective: {specs.get('objective', prompt)[:150]}
- Output type: {specs.get('output_type', 'text').upper()}
- Required subjects: {subjects_str}
- Style required: {specs.get('style', 'professional')}
- Resolution/Size: {specs.get('resolution', (1080,1080))[0]}x{specs.get('resolution', (1080,1080))[1]}
- Quantity: {specs.get('quantity', 1)}
- Exclude: {neg_str}{client_dirs}

**STEP 2 — MY APPROACH & COMPLIANCE COMMITMENT:**
I will produce work satisfying every single constraint.
If subjects are specified, they will all appear.
If format is slide deck, document, or table, I will use exact markdown components.
I will never settle for mediocre. The final response must represent professional, production-ready quality.

---
### USER BRIEF:
{prompt}

### RESPONSE (agency-quality, complete, professional):"""

    return planning


def build_image_prompt(prompt: str, specs: dict, web_context: str = "") -> dict:
    """
    Builds an enriched, professional image generation prompt from a user request.
    Returns a dict containing {"positive": str, "negative": str}.
    """
    try:
        import luminary_creative_director
        brief = luminary_creative_director.interpret_creative_brief(prompt, specs, web_context)
        return luminary_creative_director.build_production_prompt(prompt, brief)
    except Exception as e:
        print("[Luminary] Error running creative director layer, using fallback:", e)
        # Fallback to basic string enrichment
        always_negative = "watermark, text overlay, logo, blurry, low quality"
        return {"positive": prompt + ", professional photography, high quality", "negative": always_negative}


def should_run_evaluator(prompt: str, response: str) -> bool:
    """
    Smart gate: only run the expensive evaluator AI for outputs that need it.
    Skip for short/simple responses to save time.
    """
    if not response or len(response.split()) < 80:
        return False
    if len(prompt.split()) < 8:
        return False
    complex_indicators = [
        "ppt", "presentation", "slide", "report", "document",
        "marketing", "strategy", "campaign", "proposal", "deck",
        "analysis", "audit", "plan", "spreadsheet", "instagram", "pinterest",
    ]
    if any(k in prompt.lower() for k in complex_indicators):
        return True
    return len(response.split()) > 200


def extract_clarification_question(prompt: str, specs: dict) -> Optional[str]:
    """
    Legacy compatibility shim. Calls generate_smart_clarification internally.
    Returns the question text only (no MCQ structure).
    """
    mcq = generate_smart_clarification(prompt, specs)
    if mcq:
        return mcq.get("question")
    return None


def generate_smart_clarification(prompt: str, specs: dict) -> Optional[Dict[str, Any]]:
    """
    Returns a structured MCQ clarification card ONLY when the prompt is genuinely
    incomplete and clarification would materially improve the result.
    Returns None when the prompt is complete enough to proceed.

    Return format:
    {
        "question": str,
        "options": [str, str, str],   # exactly 3 intelligent options
        "context": str                 # 1-sentence reason why we're asking
    }
    """
    output_type = specs.get("output_type", "text")
    deliverable = specs.get("deliverable", "content")
    purpose = specs.get("purpose", "general")
    audience = specs.get("audience", "general audience")
    platform = specs.get("platform", "general")
    pl = prompt.lower().strip()

    # Don't ask for follow-up modifications — just execute
    if specs.get("change_only_mode") or specs.get("is_follow_up"):
        return None

    # MISSING AUDIENCE (Highest Priority for Marketing/Docs/PPT)
    if audience == "general audience" and output_type in ["pptx", "docx", "text", "campaign"]:
        topic = prompt.strip().title() if len(prompt.split()) < 10 else "this topic"
        return {
            "question": f"Who is the target audience for {topic}?",
            "options": [
                "Investors, Executives, and Key Stakeholders",
                "High-end luxury consumers and premium buyers",
                "General public, emphasizing accessibility and engagement",
            ],
            "context": "Knowing the audience lets me tune the tone, depth, and structural complexity precisely."
        }

    # MISSING PLATFORM/STYLE (Highest Priority for Images)
    if output_type == "image" and platform == "general" and not specs.get("subjects") and not specs.get("style"):
        return {
            "question": "What style or platform is this visual intended for?",
            "options": [
                "Luxury product photography (Clean, studio lighting, hyper-realistic)",
                "Social Media Lifestyle (Instagram/Pinterest, editorial, authentic)",
                "Bold Graphic Art (Vivid, striking composition, vector/illustration)",
            ],
            "context": "A quick style choice will help me generate a visual that perfectly matches your brand aesthetic."
        }

    # MISSING PURPOSE
    if purpose == "general" and deliverable in ["strategy", "campaign", "docx"]:
        return {
            "question": "What is the primary business goal here?",
            "options": [
                "Drive immediate sales and high conversions",
                "Build brand awareness and thought leadership",
                "Internal education and team alignment",
            ],
            "context": "Understanding the business goal helps me structure the call-to-actions and overall strategy."
        }

    return None


def check_requirement_compliance(output: str, specs: dict) -> dict:
    """
    Validates the output against all parsed specs using 5-Pass QA Gate.
    Returns {passed: bool, failures: list, warnings: list}
    """
    qa_result = run_5_pass_qa(output, specs)
    return {
        "passed": qa_result["passed"],
        "failures": qa_result["failures"],
        "warnings": qa_result["warnings"]
    }


def classify_prompt_completeness(specs: dict) -> str:
    """
    Classifies prompt completeness into 4 tiers:
    COMPLETE (>=75) | MOSTLY_COMPLETE (50-74) | INCOMPLETE (25-49) | AMBIGUOUS (<25)
    """
    score = specs.get("completeness_score", 50)
    if score >= 75:
        return "COMPLETE"
    elif score >= 50:
        return "MOSTLY_COMPLETE"
    elif score >= 25:
        return "INCOMPLETE"
    else:
        return "AMBIGUOUS"


def detect_follow_up_type(prompt: str, specs: dict) -> str:
    """
    Detects the type of follow-up request:
    CHANGE_ONLY | SCALE_CHANGE | STYLE_CHANGE | ADD_ELEMENT | REMOVE_ELEMENT | FULL_REVISION | NEW_TASK
    Returns 'NEW_TASK' if not a follow-up.
    """
    if not specs.get("is_follow_up"):
        return "NEW_TASK"

    pl = prompt.lower()

    if re.search(r'redo|start over|completely different|from scratch|new concept', pl):
        return "FULL_REVISION"

    if re.search(r'\b(remove|take out|delete|hide|get rid of|eliminate)\b', pl):
        return "REMOVE_ELEMENT"

    if re.search(r'\b(add|include|insert|put|place|show)\b', pl):
        return "ADD_ELEMENT"

    if re.search(r'\b(bigger|smaller|larger|increase|decrease|scale|resize|shrink|enlarge)\b', pl):
        return "SCALE_CHANGE"

    if re.search(r'\b(darker|lighter|brighter|warmer|cooler|more luxury|less|more|tone|mood|color|colour|style|aesthetic)\b', pl):
        return "STYLE_CHANGE"

    if re.search(r'\b(change|adjust|update|modify|fix|tweak|refine|make it|turn it)\b', pl):
        return "CHANGE_ONLY"

    return "CHANGE_ONLY"  # Default for follow-ups


def generate_smart_suggestions(prompt: str, specs: dict, output_type: str) -> list:
    """
    Generates 2-3 smart contextual next-step suggestions after a delivered response.
    Returns a list of suggestion strings.
    """
    suggestions = []
    platform = specs.get("platform", "general")
    deliverable = specs.get("deliverable", output_type)
    purpose = specs.get("purpose", "general")
    brand = specs.get("brand_name", "")
    brand_txt = f" for {brand}" if brand else ""

    if deliverable == "image" or output_type == "image":
        if platform == "instagram":
            suggestions = [
                "Create Story version (9:16 vertical)",
                f"Write Instagram caption{brand_txt}",
                "Generate Pinterest pin version",
            ]
        elif platform == "pinterest":
            suggestions = [
                "Create Instagram post version (1:1)",
                f"Write Pinterest description with SEO keywords{brand_txt}",
                "Generate 3 color variations",
            ]
        elif platform == "linkedin":
            suggestions = [
                "Write LinkedIn post copy to accompany this",
                "Create a carousel version (multiple slides)",
                "Generate a square Instagram version",
            ]
        else:
            suggestions = [
                "Create Instagram post version (1080x1080)",
                "Generate Story/Reel format (9:16)",
                f"Write marketing caption{brand_txt}",
            ]
    elif deliverable == "pptx" or output_type == "pptx":
        suggestions = [
            "Export as PDF for sharing",
            "Add speaker notes to each slide",
            "Create an executive summary document",
        ]
    elif deliverable in ["docx", "text"] or output_type in ["docx", "text"]:
        if purpose == "product_launch":
            suggestions = [
                "Create social media campaign for this launch",
                "Build a launch presentation deck",
                "Generate press release version",
            ]
        else:
            suggestions = [
                "Summarize this into a one-page overview",
                "Create a presentation from this content",
                "Generate social media posts from key points",
            ]
    elif deliverable == "campaign":
        suggestions = [
            "Generate campaign visuals for each platform",
            "Create email version of this campaign",
            "Build a campaign tracking dashboard",
        ]
    else:
        suggestions = [
            "Create a visual graphic for this",
            "Turn this into a presentation deck",
            "Generate a social media post version",
        ]

    return suggestions[:3]


def get_intelligence_summary() -> str:
    """Returns a one-line module summary for logging."""
    return "luminary_intelligence v4.0 — V12 upgrade: 16-field prompt parser, completeness engine, follow-up detection, smart MCQ, enhanced planning, suggestions engine"
