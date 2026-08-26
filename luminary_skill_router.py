"""
luminary_skill_router.py
========================
Skill Selection Engine for Luminary AI.

Inspired by:
- ReAct (Reason + Act) agent pattern [github.com/ysymyth/ReAct]
- Reflexion self-critique loop [github.com/noahshinn/reflexion]
- Agentic skill composition
- Chain-of-thought planning

For every task, this router:
1. Classifies the task into a domain
2. Selects the exact skills relevant
3. Returns platform specs, quality checklists, reference frameworks,
   copywriting frameworks, and the dual-AI collaboration plan.
"""

import re

# ─── Platform Specs ─────────────────────────────────────────────────────────────
PLATFORM_SPECS = {
    "pinterest": {
        "dimensions": "1000x1500 px (2:3 vertical)",
        "aspect_ratio": "2:3",
        "resolution": (1000, 1500),
        "format": "JPEG or PNG",
        "file_size": "max 20MB",
        "title_chars": 100,
        "description_chars": 500,
        "hook_style": "Search-intent driven — front-load keywords in title",
        "cta": "Save, Learn More, Shop Now",
        "seo_note": "Pinterest is a SEARCH ENGINE. Use keywords in title, description, alt text.",
        "caption_formula": "[Keyword-rich title]. [Descriptive body with related keywords]. [Soft CTA].",
        "content_types": ["Infographics", "Step-by-step guides", "Inspirational quotes", "Product shots", "Lifestyle imagery", "How-to visuals"],
        "color_strategy": "Bold, high-contrast images perform best. Warm tones outperform cool tones.",
        "hashtags": "Optional — max 5 relevant hashtags",
        "best_time": "Evenings and weekends perform best",
    },
    "instagram": {
        "dimensions": "1080x1080 px (1:1 square) or 1080x1350 px (4:5 portrait)",
        "aspect_ratio": "1:1 or 4:5",
        "resolution": (1080, 1080),
        "format": "JPEG or PNG",
        "file_size": "max 8MB",
        "caption_chars": 2200,
        "hook_style": "Emotional hook in first line — curiosity, benefit, or bold statement",
        "cta": "Comment, Save, Share, DM us, Link in bio",
        "seo_note": "Instagram uses hashtags and keyword captions for discoverability. First line = hook.",
        "caption_formula": "[Bold hook]. [Value/story body]. [CTA]. [Hashtags on new lines].",
        "content_types": ["Lifestyle shots", "Product flat lays", "Behind the scenes", "Quotes", "Carousels", "Reels covers"],
        "color_strategy": "Cohesive feed aesthetic. Consistent color palette across posts.",
        "hashtags": "5-15 targeted hashtags recommended",
        "best_time": "9-11am and 6-9pm local time, Tuesday-Friday",
    },
    "instagram_story": {
        "dimensions": "1080x1920 px (9:16 vertical)",
        "aspect_ratio": "9:16",
        "resolution": (1080, 1920),
        "hook_style": "Immediate visual impact — 3 seconds to capture attention",
        "cta": "Swipe Up, Poll, Quiz, DM",
        "content_types": ["Poll stickers", "Countdown", "Quick tip", "Product reveal", "Behind scenes"],
    },
    "instagram_reel": {
        "dimensions": "1080x1920 px (9:16 vertical)",
        "aspect_ratio": "9:16",
        "resolution": (1080, 1920),
        "hook_style": "0-3 seconds visual hook — no intro, straight into the value",
        "cta": "Follow, Save, Share",
    },
    "linkedin": {
        "dimensions": "1200x627 px (landscape) or 1200x1200 px (square)",
        "aspect_ratio": "1.91:1",
        "resolution": (1200, 627),
        "caption_chars": 3000,
        "hook_style": "Professional insight or contrarian statement. Data-driven.",
        "cta": "Like, Comment with your opinion, Share, Follow",
        "seo_note": "LinkedIn prioritises dwell time. Carousels and documents get highest reach.",
        "hashtags": "3-5 professional hashtags",
    },
    "facebook": {
        "dimensions": "1200x630 px",
        "aspect_ratio": "1.91:1",
        "resolution": (1200, 630),
        "caption_chars": 63206,
        "hook_style": "Community-oriented, emotional, story-based",
        "cta": "Like, Share, Comment, Shop Now",
        "hashtags": "2-5 hashtags",
    },
    "youtube_thumbnail": {
        "dimensions": "1280x720 px (16:9)",
        "aspect_ratio": "16:9",
        "resolution": (1280, 720),
        "hook_style": "Large readable text, expressive face/reaction, high contrast",
        "content_types": ["Text + image combo", "Face + text", "Before/After"],
    },
    "twitter": {
        "dimensions": "1200x675 px",
        "aspect_ratio": "16:9",
        "resolution": (1200, 675),
        "caption_chars": 280,
        "hook_style": "Punchy, opinionated, shareable first sentence",
        "hashtags": "1-2 hashtags",
    },
}

# ─── Copywriting Frameworks ──────────────────────────────────────────────────────
COPYWRITING_FRAMEWORKS = {
    "AIDA": {
        "name": "AIDA — Attention, Interest, Desire, Action",
        "use_for": "Ads, landing pages, email campaigns, product launches",
        "structure": [
            "ATTENTION: Grab with a bold headline or visual hook",
            "INTEREST: Build curiosity with relevant context or a surprising fact",
            "DESIRE: Show the benefit, the transformation, the dream outcome",
            "ACTION: Clear, single CTA — one action only",
        ],
    },
    "PAS": {
        "name": "PAS — Problem, Agitate, Solution",
        "use_for": "Pain-point marketing, SaaS, consulting, services",
        "structure": [
            "PROBLEM: Name the pain clearly — make them feel seen",
            "AGITATE: Amplify the pain — consequences of not solving it",
            "SOLUTION: Present your offer as the inevitable answer",
        ],
    },
    "HERO": {
        "name": "HERO — Hook, Empathy, Result, Offer",
        "use_for": "Social media, short-form content, DTC brands",
        "structure": [
            "HOOK: Pattern interrupt in first 3 seconds/words",
            "EMPATHY: Show you understand the audience's world",
            "RESULT: Demonstrate or describe the outcome they want",
            "OFFER: Present the next step — low friction",
        ],
    },
    "FAB": {
        "name": "FAB — Feature, Advantage, Benefit",
        "use_for": "Product descriptions, sales copy, pitch decks",
        "structure": [
            "FEATURE: What it is / what it does",
            "ADVANTAGE: Why it's better than alternatives",
            "BENEFIT: What it means for the customer's life",
        ],
    },
    "SCQA": {
        "name": "SCQA — Situation, Complication, Question, Answer (McKinsey Pyramid)",
        "use_for": "Executive presentations, consulting reports, business proposals",
        "structure": [
            "SITUATION: Establish shared context (the world as it is)",
            "COMPLICATION: What changed or went wrong — the tension",
            "QUESTION: What does this force us to ask/solve?",
            "ANSWER: Your recommendation — lead with the answer, support with data",
        ],
    },
    "STORYBRAND": {
        "name": "StoryBrand — Character, Problem, Guide, Plan, CTA, Avoid Failure, Success",
        "use_for": "Brand messaging, website copy, brand strategy",
        "structure": [
            "CHARACTER: The customer is the hero (not your brand)",
            "PROBLEM: External problem they face + internal feeling + philosophical stakes",
            "GUIDE: Your brand is the mentor (Yoda, not Luke)",
            "PLAN: Simple 3-step plan that makes it easy to trust you",
            "CTA: Direct call to action",
            "AVOID FAILURE: What happens if they don't act",
            "SUCCESS: Paint the dream outcome",
        ],
    },
}

# ─── Design Quality Checklists ──────────────────────────────────────────────────
DESIGN_QUALITY_CHECKLISTS = {
    "visual": [
        "Visual hierarchy: Is there a clear primary focal point?",
        "Alignment: Are all elements aligned to an underlying grid?",
        "Contrast: Is text readable against background? (WCAG AA minimum 4.5:1)",
        "Spacing: Is there purposeful negative space? (Avoid cramping)",
        "Typography: Max 2 fonts. Consistent heading/body sizes.",
        "Color: Max 3 colors. Brand-consistent. No random color mixing.",
        "Composition: Rule of thirds applied? Leading lines? Framing?",
        "Balance: Symmetrical or intentional asymmetrical balance?",
        "Depth: Foreground/midground/background separation?",
        "CTA: Is there one clear call-to-action? Is it visually prominent?",
    ],
    "image_qa": [
        "COUNT: Exactly the requested number of subjects/objects?",
        "TEXT: Any text readable, correct, no spelling errors?",
        "LOGO/BRAND: Correct brand colors, no distorted logos?",
        "ANATOMY: Hands, faces, bodies anatomically correct?",
        "PERSPECTIVE: Does perspective make physical sense?",
        "LIGHTING: Consistent light direction across the scene?",
        "SHADOWS: Shadows match light direction and intensity?",
        "MATERIALS: Surfaces look like real materials (metal, glass, leather)?",
        "COMPOSITION: Does it communicate the idea within 2 seconds?",
        "QUALITY: Would a professional marketing agency deliver this?",
    ],
    "presentation": [
        "STORY: Problem → Insight → Solution → Market → Evidence → CTA?",
        "SLIDE STRUCTURE: Title + 3-5 bullets max per slide?",
        "DATA VIZ: Charts used for data? No data in paragraph form?",
        "TYPOGRAPHY: Slide titles large (36-48pt), body readable (18-24pt)?",
        "ALIGNMENT: Consistent margins? Elements align to grid?",
        "BRAND: Consistent colors, fonts, logo placement?",
        "IMAGES: Professional images, not stock clipart?",
        "NOTES: Speaker notes present for each slide?",
        "FLOW: Does each slide lead logically to the next?",
        "DELIVERY: Would a McKinsey consultant present this without changes?",
    ],
    "document": [
        "HIERARCHY: H1 → H2 → H3 → Body properly structured?",
        "EXECUTIVE SUMMARY: First page summarises key points?",
        "PAGE BREAKS: Sections start on new pages?",
        "TABLES: Data in tables, not lists?",
        "MARGINS: Consistent margins (2.54cm standard)?",
        "NUMBERING: Page numbers present?",
        "FONTS: Max 2 fonts, consistent heading sizes?",
        "REFERENCES: Sources cited where needed?",
        "FOOTERS: Company/client name and date in footer?",
        "PROOFREADING: Spelling, grammar, consistency checked?",
    ],
    "spreadsheet": [
        "STRUCTURE: Input area / Calculation area / Output area separated?",
        "HEADERS: Bold, frozen header row?",
        "FORMATS: Numbers formatted correctly (currency, %, 2dp)?",
        "FORMULAS: SUM/AVERAGE/IF formulas used (no hardcoded totals)?",
        "VALIDATION: Data validation on input cells?",
        "CHART: At least one chart visualising key data?",
        "SUMMARY: Summary dashboard or totals section?",
        "FILTERS: AutoFilter on data tables?",
        "COLORS: Consistent color coding (blue=input, green=calculated)?",
        "CLEAN: No empty rows/columns breaking table structure?",
    ],
}

# ─── Presentation Story Structures ──────────────────────────────────────────────
PRESENTATION_STRUCTURES = {
    "pitch_deck": [
        "Slide 1: Cover — Company name, tagline, logo",
        "Slide 2: Problem — The pain point (make it visceral)",
        "Slide 3: Solution — Your product/service (show, don't just tell)",
        "Slide 4: Market Size — TAM/SAM/SOM with sources",
        "Slide 5: Product — Features + demo/screenshots",
        "Slide 6: Business Model — How you make money",
        "Slide 7: Traction — Revenue, users, partnerships, growth",
        "Slide 8: Competition — 2x2 matrix, your differentiators",
        "Slide 9: Team — Key people, credentials, relevant experience",
        "Slide 10: Financials — 3-year projections, key metrics",
        "Slide 11: Ask — How much, what it's used for, milestones",
    ],
    "marketing_deck": [
        "Slide 1: Executive Summary — Key findings and recommendations",
        "Slide 2: Market Overview — Industry size, trends, landscape",
        "Slide 3: Target Audience — ICP, personas, psychographics",
        "Slide 4: Competitive Analysis — Positioning map, gaps",
        "Slide 5: Strategy — Channels, messaging, positioning",
        "Slide 6: Campaign Creative — Visual direction, copy direction",
        "Slide 7: KPIs & Metrics — How we measure success",
        "Slide 8: Budget & Timeline — Investment breakdown, milestones",
        "Slide 9: Next Steps — Action items with owners and dates",
    ],
    "business_proposal": [
        "Slide 1: Cover Page",
        "Slide 2: About Us — Credibility brief",
        "Slide 3: Understanding Your Challenge — Restate the brief",
        "Slide 4: Our Approach — Methodology, process",
        "Slide 5: Deliverables — Exactly what they get",
        "Slide 6: Timeline — Phases and milestones",
        "Slide 7: Investment — Pricing, packages",
        "Slide 8: Case Studies — Proof of past results",
        "Slide 9: Team — Who does the work",
        "Slide 10: Next Steps — Clear action required from client",
    ],
}

# ─── Domain → Skill Map ─────────────────────────────────────────────────────────
SKILL_MAP = {
    "pinterest_post": {
        "label": "Pinterest Marketing Creative",
        "skills": [
            "brand_research", "product_research", "automotive_photography",
            "graphic_design", "pinterest_seo", "social_copywriting",
            "image_generation", "image_qa", "platform_spec_pinterest",
        ],
        "frameworks": ["AIDA", "HERO"],
        "platform": "pinterest",
        "image_ai_needed": True,
        "text_ai_role": "Write title, description, SEO caption, hashtags, and CTA",
        "image_ai_role": "Generate 1000x1500 (2:3) hero image matching Pinterest best practices",
        "quality_checklist": ["image_qa", "visual"],
        "next_steps": [
            "Repurpose this as an Instagram post (1080x1080)",
            "Create a second Pinterest variation with different angle",
            "Create a Story version (1080x1920)",
        ],
    },
    "instagram_post": {
        "label": "Instagram Marketing Creative",
        "skills": [
            "brand_research", "graphic_design", "instagram_strategy",
            "social_copywriting", "hashtag_research", "image_generation", "image_qa",
        ],
        "frameworks": ["HERO", "PAS"],
        "platform": "instagram",
        "image_ai_needed": True,
        "text_ai_role": "Write caption hook, body copy, CTA, hashtags (platform-native)",
        "image_ai_role": "Generate 1080x1080 or 1080x1350 image optimised for Instagram feed",
        "quality_checklist": ["image_qa", "visual"],
        "next_steps": [
            "Create a Story version (1080x1920)",
            "Create a carousel (3-5 slides)",
            "Repurpose for Pinterest (1000x1500)",
        ],
    },
    "social_carousel": {
        "label": "Social Carousel / Multi-Image Post",
        "skills": [
            "graphic_design", "social_copywriting", "storytelling",
            "image_generation", "image_qa",
        ],
        "frameworks": ["HERO", "AIDA"],
        "image_ai_needed": True,
        "text_ai_role": "Write slide-by-slide copy, hook slide, CTA slide",
        "image_ai_role": "Generate each carousel slide at correct dimensions",
        "quality_checklist": ["image_qa", "visual"],
    },
    "presentation": {
        "label": "Professional Presentation / Deck",
        "skills": [
            "business_strategy", "market_research", "storytelling",
            "presentation_design", "data_visualization", "branding",
        ],
        "frameworks": ["SCQA"],
        "image_ai_needed": False,
        "text_ai_role": "Full slide content with structured hierarchy, data, speaker notes",
        "image_ai_role": "Generate supporting hero images for key slides if requested",
        "quality_checklist": ["presentation"],
        "structures": "pitch_deck / marketing_deck / business_proposal",
    },
    "pitch_deck": {
        "label": "Startup Pitch Deck",
        "skills": [
            "business_strategy", "market_research", "financial_modeling",
            "storytelling", "presentation_design", "data_visualization",
        ],
        "frameworks": ["SCQA", "STORYBRAND"],
        "image_ai_needed": False,
        "text_ai_role": "Full 10-slide pitch deck following YC/a16z investor standards",
        "quality_checklist": ["presentation"],
    },
    "document": {
        "label": "Professional Document / Report",
        "skills": [
            "writing", "information_architecture", "professional_formatting",
            "document_design", "seo_writing",
        ],
        "frameworks": ["SCQA"],
        "image_ai_needed": False,
        "text_ai_role": "Full structured document with executive summary, H1/H2/H3, tables, references",
        "quality_checklist": ["document"],
    },
    "spreadsheet": {
        "label": "Professional Spreadsheet / Excel",
        "skills": [
            "data_analysis", "financial_modeling", "spreadsheet_design",
            "data_visualization",
        ],
        "frameworks": [],
        "image_ai_needed": False,
        "text_ai_role": "Structured spreadsheet with formulas, headers, formatting, summary",
        "quality_checklist": ["spreadsheet"],
    },
    "website": {
        "label": "Website / Landing Page",
        "skills": [
            "ux_design", "ui_design", "responsive_design", "frontend_dev",
            "seo", "performance", "accessibility", "branding",
        ],
        "frameworks": ["STORYBRAND", "AIDA"],
        "image_ai_needed": True,
        "text_ai_role": "Full page copy: hero, features, social proof, pricing, CTA — per StoryBrand",
        "image_ai_role": "Generate hero images, product shots, section backgrounds",
        "quality_checklist": ["visual"],
        "page_structure": "Hero → Story → Product → Social Proof → Benefits → CTA → Footer",
    },
    "ad_creative": {
        "label": "Advertisement Creative",
        "skills": [
            "brand_research", "graphic_design", "ad_copywriting",
            "image_generation", "image_qa", "platform_spec",
        ],
        "frameworks": ["AIDA", "PAS", "FAB"],
        "image_ai_needed": True,
        "text_ai_role": "Headline, subheadline, body copy, CTA — AIDA/PAS driven",
        "image_ai_role": "Generate high-impact ad visual at required dimensions",
        "quality_checklist": ["image_qa", "visual"],
    },
    "email": {
        "label": "Email Campaign",
        "skills": [
            "email_copywriting", "storytelling", "segmentation",
        ],
        "frameworks": ["AIDA", "PAS"],
        "image_ai_needed": False,
        "text_ai_role": "Subject line, preview text, hero copy, body, CTA — AIDA driven",
        "quality_checklist": [],
    },
    "image": {
        "label": "Image Generation",
        "skills": [
            "image_generation", "photography_art_direction", "image_qa",
        ],
        "frameworks": [],
        "image_ai_needed": True,
        "text_ai_role": "Enrich and structure the image prompt with pro photography terms",
        "image_ai_role": "Generate at exact resolution, quantity, style specified",
        "quality_checklist": ["image_qa"],
    },
    "brand_identity": {
        "label": "Brand Identity",
        "skills": [
            "brand_strategy", "typography", "color_theory",
            "logo_design", "brand_guidelines",
        ],
        "frameworks": ["STORYBRAND"],
        "image_ai_needed": True,
        "text_ai_role": "Brand story, values, voice, color rationale, typography choices",
        "image_ai_role": "Generate logo concepts, mood boards, brand application visuals",
        "quality_checklist": ["visual"],
    },
    "text": {
        "label": "Text / Chat Response",
        "skills": ["writing", "research", "reasoning"],
        "frameworks": [],
        "image_ai_needed": False,
        "text_ai_role": "Direct, high-quality text response",
        "quality_checklist": [],
    },
}

# ─── Task Classifier ─────────────────────────────────────────────────────────────
def classify_task(prompt: str) -> str:
    """Returns the task domain key from SKILL_MAP."""
    pl = prompt.lower()

    # Social platform detection first
    is_pinterest = any(k in pl for k in ["pinterest", "pin", "pinterest post"])
    is_instagram = any(k in pl for k in ["instagram", "ig post", "insta"])
    is_story = any(k in pl for k in ["story", "reel", "tiktok"])
    is_carousel = any(k in pl for k in ["carousel", "multi-slide", "swipe"])
    is_ad = any(k in pl for k in ["ad creative", "advertisement", "sponsored", "paid ad", "banner ad", "google ad", "facebook ad"])
    is_email = any(k in pl for k in ["email", "newsletter", "campaign email"])

    # Document types
    is_pitch = any(k in pl for k in ["pitch deck", "investor deck", "fundraising deck"])
    is_ppt = any(k in pl for k in ["ppt", "presentation", "deck", "slide", "powerpoint"])
    is_doc = any(k in pl for k in ["report", "document", "article", "blog", "essay", "proposal", "docx"])
    is_sheet = any(k in pl for k in ["spreadsheet", "excel", "xlsx", "sheet", "csv", "table"])
    is_website = any(k in pl for k in ["website", "landing page", "web page", "webflow", "html"])
    is_brand = any(k in pl for k in ["brand identity", "brand guide", "brand kit", "logo", "brand color"])
    is_image = any(k in pl for k in ["image", "photo", "picture", "graphic", "render", "poster", "visual", "draw", "generate", "create an image", "shot"])

    # Priority order (most specific first)
    if is_pinterest and is_image:
        return "pinterest_post"
    if is_instagram and is_story:
        return "instagram_post"
    if is_instagram and is_carousel:
        return "social_carousel"
    if is_instagram:
        return "instagram_post"
    if is_carousel:
        return "social_carousel"
    if is_ad:
        return "ad_creative"
    if is_email:
        return "email"
    if is_pitch:
        return "pitch_deck"
    if is_ppt:
        return "presentation"
    if is_doc:
        return "document"
    if is_sheet:
        return "spreadsheet"
    if is_website:
        return "website"
    if is_brand:
        return "brand_identity"
    if is_image:
        return "image"
    return "text"


def get_skill_context(prompt: str) -> dict:
    """
    Main entry point. Returns full routing context for a task.
    Uses ReAct-style: Reason about task → Select skills → Build action plan.
    """
    task_key = classify_task(prompt)
    route = SKILL_MAP.get(task_key, SKILL_MAP["text"])

    # Get platform spec if applicable
    platform = route.get("platform")
    platform_spec = PLATFORM_SPECS.get(platform, {}) if platform else {}

    # Get copywriting frameworks
    fw_details = {fw: COPYWRITING_FRAMEWORKS[fw] for fw in route.get("frameworks", []) if fw in COPYWRITING_FRAMEWORKS}

    # Get quality checklists
    checklists = {}
    for ck in route.get("quality_checklist", []):
        if ck in DESIGN_QUALITY_CHECKLISTS:
            checklists[ck] = DESIGN_QUALITY_CHECKLISTS[ck]

    return {
        "task_type": task_key,
        "label": route.get("label", "General Task"),
        "skills_active": route.get("skills", []),
        "image_ai_needed": route.get("image_ai_needed", False),
        "text_ai_role": route.get("text_ai_role", ""),
        "image_ai_role": route.get("image_ai_role", ""),
        "platform_spec": platform_spec,
        "frameworks": fw_details,
        "quality_checklists": checklists,
        "next_steps": route.get("next_steps", []),
        "page_structure": route.get("page_structure", ""),
        "structures": route.get("structures", ""),
    }


def build_skill_context_block(prompt: str) -> str:
    """
    Returns a formatted string to inject into the AI system context.
    This is the ReAct 'Reason' output — the AI's pre-flight skill plan.
    """
    ctx = get_skill_context(prompt)
    lines = []

    lines.append(f"\n### SKILL ROUTER: Task classified as [{ctx['label'].upper()}]")
    lines.append(f"Active skills: {', '.join(ctx['skills_active'])}")
    lines.append(f"Dual-AI: TEXT AI = {ctx['text_ai_role']}")
    if ctx["image_ai_needed"]:
        lines.append(f"          IMAGE AI = {ctx['image_ai_role']}")
    else:
        lines.append("          IMAGE AI = Not required for this task")

    if ctx["platform_spec"]:
        ps = ctx["platform_spec"]
        lines.append(f"\nPLATFORM SPEC:")
        lines.append(f"  Dimensions: {ps.get('dimensions', 'N/A')}")
        lines.append(f"  Hook style: {ps.get('hook_style', 'N/A')}")
        lines.append(f"  Caption formula: {ps.get('caption_formula', 'N/A')}")
        lines.append(f"  CTA options: {ps.get('cta', 'N/A')}")
        lines.append(f"  SEO note: {ps.get('seo_note', 'N/A')}")

    if ctx["frameworks"]:
        lines.append(f"\nCOPYWRITING FRAMEWORKS:")
        for fw_key, fw in ctx["frameworks"].items():
            lines.append(f"  [{fw_key}] {fw['name']}")
            for step in fw["structure"]:
                lines.append(f"    - {step}")

    if ctx["quality_checklists"]:
        lines.append(f"\nQUALITY CHECKLIST (self-validate before delivery):")
        for ck_key, items in ctx["quality_checklists"].items():
            for item in items:
                lines.append(f"  ✓ {item}")

    if ctx["next_steps"]:
        lines.append(f"\nSUGGESTED NEXT STEPS (offer after delivery):")
        for ns in ctx["next_steps"]:
            lines.append(f"  → {ns}")

    return "\n".join(lines)


def should_involve_image_ai(prompt: str) -> bool:
    """Returns True if this task requires the Image AI to collaborate."""
    ctx = get_skill_context(prompt)
    return ctx.get("image_ai_needed", False)


def get_platform_resolution(platform: str) -> tuple:
    """Returns (width, height) for a given platform."""
    spec = PLATFORM_SPECS.get(platform.lower(), {})
    return spec.get("resolution", (1080, 1080))


def build_creative_brief(prompt: str, specs: dict) -> dict:
    """
    Builds a structured art-direction brief that the text model creates BEFORE
    asking the image model to generate. This is the V12 creative collaboration layer.

    Returns a dict:
    {
        "campaign": str,
        "platform": str,
        "aspect_ratio": str,
        "hero": str,
        "mood": str,
        "lighting": str,
        "environment": str,
        "materials": str,
        "composition": str,
        "background": str,
        "negative_space": str,
        "marketing_objective": str,
        "exact_constraints": list,
        "color_palette": str,
        "camera_direction": str,
        "brand_context": str,
    }
    """
    pl = prompt.lower()

    # -- Hero / Subject --
    subjects = specs.get("subjects", [])
    hero = ", ".join(subjects) if subjects else prompt.strip()[:60]

    # -- Platform & Aspect Ratio --
    platform = specs.get("platform", "general")
    platform_spec = PLATFORM_SPECS.get(platform, {})
    res = specs.get("resolution", (1080, 1080))
    w, h = res
    if h > w:
        aspect_ratio = "vertical (portrait)"
    elif w > h:
        aspect_ratio = "landscape"
    else:
        aspect_ratio = "square (1:1)"
    aspect_ratio_str = f"{w}x{h} — {aspect_ratio}"

    # -- Mood derivation --
    style = specs.get("style", "realistic")
    quality_level = specs.get("quality_level", "standard")
    audience = specs.get("audience", "general audience")
    purpose = specs.get("purpose", "general")

    mood_map = {
        "luxury": "opulent, aspirational, refined, exclusive",
        "cinematic": "dramatic, epic, high-contrast, atmospheric",
        "photorealistic": "authentic, natural, true-to-life",
        "minimal": "clean, serene, focused, whisper-quiet",
        "futuristic": "sleek, technological, forward-looking, neon-edged",
        "3d": "sculptural, dimensional, hyper-detailed, rendered",
        "editorial": "sophisticated, fashion-forward, styled, conceptual",
        "corporate": "confident, professional, trustworthy, structured",
        "animated": "vibrant, energetic, playful, expressive",
        "realistic": "natural, grounded, true-to-life, believable",
    }
    mood = mood_map.get(style, "professional, high-quality, refined")
    if quality_level == "luxury_premium":
        mood += ", ultra-luxury, world-class production value"

    # -- Lighting --
    lighting_map = {
        "luxury": "dramatic studio lighting with deep shadows, rim light halo, subtle fill",
        "cinematic": "golden hour backlight, lens flare, volumetric haze, Rembrandt shadows",
        "photorealistic": "soft diffused natural light, window light from left, balanced shadows",
        "minimal": "clean flat softbox light, even exposure, no harsh shadows",
        "futuristic": "neon ambient glow, edge lighting, dramatic under-lighting",
        "3d": "HDRI environment lighting, global illumination, caustics",
        "editorial": "high-fashion strobe lighting, sharp shadows, dramatic contrast",
    }
    lighting = lighting_map.get(style, "professional studio softbox lighting, clean shadows")

    # -- Environment --
    if any(k in pl for k in ["outdoor", "street", "city", "nature", "beach", "forest", "mountain"]):
        environment = "outdoor location"
    elif any(k in pl for k in ["studio", "white background", "dark background", "seamless"]):
        environment = "professional studio setup"
    elif any(k in pl for k in ["home", "living room", "kitchen", "bedroom", "office"]):
        environment = "interior lifestyle setting"
    elif any(k in pl for k in ["abstract", "gradient", "minimal background"]):
        environment = "abstract minimal background"
    else:
        # Default by audience/purpose
        if audience == "luxury consumers" or quality_level == "luxury_premium":
            environment = "architectural interior with premium surfaces"
        elif purpose == "investor":
            environment = "clean white or gradient professional background"
        else:
            environment = "contextually appropriate environment"

    # -- Materials --
    subjects_lower = " ".join(subjects).lower()
    if any(k in subjects_lower or k in pl for k in ["perfume", "fragrance", "bottle", "glass"]):
        materials = "hand-blown glass, liquid crystal refraction, frosted surface"
    elif any(k in subjects_lower or k in pl for k in ["watch", "rolex", "timepiece"]):
        materials = "brushed titanium, sapphire crystal glass, laser-engraved metal"
    elif any(k in subjects_lower or k in pl for k in ["car", "ferrari", "lamborghini", "vehicle"]):
        materials = "gloss automotive paint, chrome trim, brushed carbon fibre, leather interior"
    elif any(k in subjects_lower or k in pl for k in ["shoe", "sneaker", "boot", "footwear"]):
        materials = "premium leather, suede, woven mesh, vulcanized rubber sole"
    elif any(k in subjects_lower or k in pl for k in ["jewelry", "ring", "necklace", "diamond"]):
        materials = "platinum setting, brilliant diamond facets, gold, gemstone"
    elif any(k in subjects_lower or k in pl for k in ["bag", "handbag", "purse"]):
        materials = "full-grain leather, brass hardware, interior suede lining"
    elif any(k in subjects_lower or k in pl for k in ["food", "cake", "coffee", "drink"]):
        materials = "fresh natural ingredients, steam, condensation, artisan preparation"
    else:
        materials = "appropriate materials for subject"

    # -- Composition --
    if platform in ["instagram", "instagram_story", "tiktok"]:
        composition = "centered hero, rule of thirds, safe zone margins for platform UI"
    elif platform == "pinterest":
        composition = "vertical flow composition, hero at top 60%, text space at bottom"
    elif platform == "linkedin":
        composition = "left-weighted, professional framing, clear focal point"
    else:
        composition = "rule of thirds, strong visual hierarchy, intentional negative space"

    # -- Background --
    colors = specs.get("colors", [])
    if colors:
        color_bg = " and ".join(colors[:2])
        background = f"{color_bg} toned background"
    elif audience == "luxury consumers" or quality_level == "luxury_premium":
        background = "deep charcoal or matte black with subtle texture, or pure white studio infinity"
    elif platform in ["instagram", "pinterest"]:
        background = "clean gradient or lifestyle-appropriate background"
    else:
        background = "neutral professional background"

    # -- Negative space --
    neg_space_map = {
        "instagram": "minimum 20% negative space at edges for platform UI",
        "pinterest": "bottom 30% reserved for title text overlay",
        "instagram_story": "top 15% and bottom 25% safe zones for UI elements",
        "linkedin": "left third with copy-space",
    }
    negative_space = neg_space_map.get(platform, "purposeful negative space for visual breathing room")

    # -- Marketing objective --
    objective_map = {
        "product_launch": "Drive immediate product awareness and desire",
        "brand_awareness": "Build brand recognition and emotional connection",
        "sales": "Convert viewers into buyers — show product value",
        "engagement": "Stop the scroll — generate saves, comments, shares",
        "investor": "Demonstrate credibility, vision, and premium positioning",
        "education": "Communicate information clearly and memorably",
    }
    marketing_objective = objective_map.get(purpose, "Create a compelling, professional visual")

    # -- Exact constraints --
    exact_constraints = []
    for neg in specs.get("negative", []):
        exact_constraints.append(f"EXCLUDE: {neg}")
    for restriction in specs.get("restrictions", []):
        exact_constraints.append(f"PRESERVE: {restriction}")
    if specs.get("quantity", 1) > 1:
        exact_constraints.append(f"COUNT: exactly {specs['quantity']} subjects")

    # -- Color palette --
    if colors:
        color_palette = ", ".join(colors) + " tones, professionally balanced"
    elif style == "luxury" or quality_level == "luxury_premium":
        color_palette = "deep black, champagne gold, crisp white — luxury editorial palette"
    elif platform == "pinterest":
        color_palette = "warm terracotta, dusty rose, sage green — high-engagement Pinterest palette"
    else:
        color_palette = "professionally curated, harmonious palette appropriate to subject"

    # -- Camera direction --
    if style in ["photorealistic", "cinematic", "editorial", "luxury"]:
        camera_direction = "Shot on Hasselblad H6D, 85mm lens, f/2.0, shallow depth of field, tack-sharp focus on hero"
    elif style == "3d":
        camera_direction = "3D render, 50mm lens equivalent, clean camera angle, subtle depth of field"
    else:
        camera_direction = "Professional photography composition, clean focus, balanced exposure"

    # -- Brand context --
    brand = specs.get("brand_name", "")
    brand_context = f"{brand} brand — match official brand colors and premium aesthetic" if brand else "No specific brand constraint"

    # -- Campaign title --
    campaign = f"{purpose.replace('_', ' ').title()} campaign for {hero[:40]}"

    return {
        "campaign": campaign,
        "platform": f"{platform} — {platform_spec.get('dimensions', aspect_ratio_str)}",
        "aspect_ratio": aspect_ratio_str,
        "hero": hero,
        "mood": mood,
        "lighting": lighting,
        "environment": environment,
        "materials": materials,
        "composition": composition,
        "background": background,
        "negative_space": negative_space,
        "marketing_objective": marketing_objective,
        "exact_constraints": exact_constraints,
        "color_palette": color_palette,
        "camera_direction": camera_direction,
        "brand_context": brand_context,
    }


def get_platform_content_strategy(platform: str, purpose: str = "general") -> dict:
    """
    Returns a complete content strategy for a given platform and purpose.
    Used by the server to inject platform-specific intelligence into the planning prompt.
    """
    spec = PLATFORM_SPECS.get(platform.lower(), {})
    if not spec:
        return {}

    strategy = {
        "platform": platform,
        "dimensions": spec.get("dimensions", "N/A"),
        "hook_style": spec.get("hook_style", ""),
        "caption_formula": spec.get("caption_formula", ""),
        "cta": spec.get("cta", ""),
        "seo_note": spec.get("seo_note", ""),
        "hashtag_strategy": spec.get("hashtags", ""),
        "best_time": spec.get("best_time", ""),
        "content_types": spec.get("content_types", []),
        "color_strategy": spec.get("color_strategy", ""),
    }

    # Purpose-specific overlays
    if purpose == "product_launch":
        strategy["caption_formula"] = "[Product reveal hook]. [Key benefit]. [Scarcity/exclusivity cue]. [CTA]."
    elif purpose == "brand_awareness":
        strategy["caption_formula"] = "[Bold brand statement]. [Story/values]. [Community CTA]."
    elif purpose == "sales":
        strategy["caption_formula"] = "[Problem/pain point hook]. [Solution = product]. [Proof/testimonial]. [Buy CTA]."

    return strategy


def get_module_summary() -> str:
    return "luminary_skill_router v2.0 — V12 upgrade: ReAct skill routing, platform specs, creative brief builder, content strategy, dual-AI routing"
