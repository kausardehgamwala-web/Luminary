"""
luminary_agency_orchestrator.py
=================================
Universal Creative Agency Orchestrator for Luminary V14

This module implements the full agency-quality creative production pipeline:

  Understand → Plan → Research → Select Workflow → Select Template
  → Generate → Compose → Render → QC → Revise → QC Again → Deliver

The Creative Director is the CENTRAL COORDINATOR. No AI model independently
decides how to produce final work. All creative decisions route through this layer.

Philosophy:
  - "Generated" does NOT mean "Finished."
  - Would a professional marketing agency confidently deliver this to a paying client?
  - If NO → improve it. If YES → QC then deliver.

NO external dependencies — pure Python stdlib only.
"""

import re
import json
from typing import Optional, Dict, Any, List, Tuple


# ── Creative Production Brief Schema ─────────────────────────────────────────
class CreativeProductionBrief:
    """Structured brief the Creative Director produces before any generation starts."""

    def __init__(self):
        # Task Understanding
        self.task_type: str = "text"           # image | text | carousel | presentation | document | social
        self.deliverable: str = ""              # "Instagram Story", "Product Ad", etc.
        self.purpose: str = ""                  # "Drive product awareness", "Generate leads"
        self.target_audience: str = ""          # "25-35 urban professionals"

        # Platform & Technical
        self.platform: str = "general"
        self.dimensions: Tuple[int, int] = (1080, 1080)
        self.format: str = "JPEG"
        self.aspect_ratio: str = "1:1"

        # Brand Context
        self.brand_name: str = ""
        self.brand_colors: List[str] = []
        self.brand_tone: str = "professional"
        self.brand_fonts: List[str] = []

        # Creative Direction
        self.visual_style: str = ""
        self.composition_notes: str = ""
        self.typography_direction: str = ""
        self.color_palette: str = ""
        self.mood: str = ""
        self.lighting: str = ""

        # Content Requirements
        self.headline: str = ""
        self.subheadline: str = ""
        self.body_copy: str = ""
        self.cta: str = ""
        self.required_elements: List[str] = []
        self.excluded_elements: List[str] = []

        # Template
        self.template_id: Optional[str] = None
        self.template_category: str = ""
        self.template_zones: List[Dict] = []

        # Quality Standard
        self.quality_level: str = "agency"     # standard | agency | luxury_premium
        self.qc_requirements: List[str] = []

        # AI Coordination
        self.image_ai_instructions: str = ""   # Exact production brief for Image AI
        self.text_ai_instructions: str = ""    # Exact production brief for Text AI
        self.needs_image: bool = False
        self.needs_text: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__


# ── Platform Specifications ────────────────────────────────────────────────────
PLATFORM_COMPOSITION = {
    "instagram": {
        "primary_dims": (1080, 1080),
        "story_dims": (1080, 1920),
        "safe_zone_pct": 0.1,
        "headline_max_chars": 60,
        "body_max_chars": 150,
        "cta_placement": "lower-third",
        "visual_weight": "70% image, 30% text",
    },
    "pinterest": {
        "primary_dims": (1000, 1500),
        "safe_zone_pct": 0.08,
        "headline_max_chars": 80,
        "body_max_chars": 200,
        "cta_placement": "bottom",
        "visual_weight": "60% image, 40% text",
    },
    "facebook": {
        "primary_dims": (1200, 628),
        "safe_zone_pct": 0.1,
        "headline_max_chars": 90,
        "body_max_chars": 250,
        "cta_placement": "right or bottom",
        "visual_weight": "50% image, 50% text",
    },
    "linkedin": {
        "primary_dims": (1200, 627),
        "safe_zone_pct": 0.1,
        "headline_max_chars": 150,
        "body_max_chars": 600,
        "cta_placement": "bottom",
        "visual_weight": "40% image, 60% text",
    },
    "presentation": {
        "primary_dims": (1280, 720),
        "safe_zone_pct": 0.08,
        "headline_max_chars": 60,
        "body_max_chars": 300,
        "slides_typical": 10,
        "visual_weight": "balanced",
    },
    "product_ad": {
        "primary_dims": (1080, 1080),
        "safe_zone_pct": 0.12,
        "headline_max_chars": 50,
        "body_max_chars": 100,
        "cta_placement": "bottom-center",
        "visual_weight": "80% product, 20% text",
    },
}

# ── Deliverable Type Detection ─────────────────────────────────────────────────
DELIVERABLE_KEYWORDS = {
    "instagram_story":    ["instagram story", "ig story", "story post", "reels", "9:16"],
    "instagram_post":     ["instagram post", "instagram graphic", "ig post", "instagram ad"],
    "pinterest":          ["pinterest", "pin", "pinterest post"],
    "linkedin":           ["linkedin post", "linkedin graphic", "linkedin ad"],
    "facebook_ad":        ["facebook ad", "fb ad", "facebook post", "meta ad"],
    "product_ad":         ["product ad", "product advertisement", "product campaign", "product creative"],
    "luxury_ad":          ["luxury", "luxury ad", "premium ad", "luxury brand", "perfume", "fragrance"],
    "automotive_ad":      ["car ad", "automotive", "vehicle ad", "auto campaign"],
    "social_carousel":    ["carousel", "swipe", "multi-slide post", "carousel post"],
    "email_header":       ["email header", "email banner", "email template", "newsletter header"],
    "presentation":       ["presentation", "slide deck", "ppt", "powerpoint", "slides", "deck"],
    "document":           ["document", "doc", "report", "proposal", "brief"],
    "brand_identity":     ["brand identity", "brand kit", "logo", "brand guidelines", "branding"],
    "website_creative":   ["website", "landing page", "web design", "homepage"],
}


# ── Creative Director Core Functions ─────────────────────────────────────────

def detect_deliverable_type(prompt: str) -> str:
    """Identifies the exact deliverable the client needs using unified prompt engine."""
    import luminary_prompt_engine
    spec = luminary_prompt_engine.engine.parse_and_understand(prompt)
    dtype = spec.deliverable_type
    
    # Map to agency template key
    type_map = {
        "presentation": "presentation",
        "document": "document",
        "spreadsheet": "document",
        "product_ad": "product_ad",
        "image": "product_ad",
        "website": "website_creative",
        "social_carousel": "presentation",
        "instagram_post": "product_ad",
        "pinterest_post": "product_ad",
        "email": "text_content",
        "copywriting": "text_content"
    }
    return type_map.get(dtype, "text_content")


def select_template_for_brief(deliverable: str, style_hint: str = "") -> Dict[str, Any]:
    """
    Selects the most suitable template structure for the deliverable.
    Returns a template specification with zones for intelligent composition.
    """
    TEMPLATE_SPECS = {
        "product_ad": {
            "id": "PROD-AD-001",
            "name": "Premium Product Advertisement",
            "category": "advertising",
            "dimensions": (1080, 1080),
            "zones": [
                {"name": "product_image", "type": "image", "position": "center", "size": "70%", "guidance": "Hero product shot, centered, dramatic lighting"},
                {"name": "headline", "type": "text", "position": "upper-third", "max_chars": 50, "font": "bold, large (48-72pt)", "alignment": "center"},
                {"name": "subline", "type": "text", "position": "below-headline", "max_chars": 80, "font": "regular (24-32pt)", "alignment": "center"},
                {"name": "cta", "type": "button", "position": "lower-third", "max_chars": 20, "guidance": "High contrast button, brand color"},
            ],
            "negative_space": "top 15% and bottom 20%",
            "visual_hierarchy": "Product → Headline → Subline → CTA",
        },
        "luxury_ad": {
            "id": "LUX-AD-001",
            "name": "Luxury Brand Advertisement",
            "category": "luxury_advertising",
            "dimensions": (1080, 1080),
            "zones": [
                {"name": "hero_product", "type": "image", "position": "center-right", "size": "60%", "guidance": "Studio hero shot with premium lighting, negative space on left"},
                {"name": "brand_name", "type": "text", "position": "upper-left", "max_chars": 20, "font": "serif, elegant (24-36pt)", "alignment": "left"},
                {"name": "headline", "type": "text", "position": "left-center", "max_chars": 40, "font": "bold serif (56-80pt)", "alignment": "left"},
                {"name": "tagline", "type": "text", "position": "below-headline", "max_chars": 60, "font": "light italic (18-24pt)", "alignment": "left"},
                {"name": "cta", "type": "text-link", "position": "lower-left", "max_chars": 15, "guidance": "Understated, uppercase text-link"},
            ],
            "negative_space": "generous — minimum 40% empty space",
            "visual_hierarchy": "Brand → Hero Image → Headline → Tagline → CTA",
        },
        "instagram_story": {
            "id": "IG-STORY-001",
            "name": "Instagram Story Creative",
            "category": "social_story",
            "dimensions": (1080, 1920),
            "zones": [
                {"name": "background", "type": "image", "position": "full-bleed", "guidance": "Full-bleed hero image or gradient background"},
                {"name": "headline", "type": "text", "position": "center", "max_chars": 40, "font": "bold (64-80pt)", "alignment": "center"},
                {"name": "subtext", "type": "text", "position": "below-headline", "max_chars": 80, "font": "regular (28-36pt)", "alignment": "center"},
                {"name": "cta", "type": "button", "position": "lower-third", "max_chars": 20, "guidance": "Pill-shaped CTA button, high contrast"},
                {"name": "safe_top", "type": "margin", "position": "top", "size": "15%", "guidance": "Keep clear — Instagram UI sits here"},
                {"name": "safe_bottom", "type": "margin", "position": "bottom", "size": "25%", "guidance": "Keep clear — swipe-up area"},
            ],
            "negative_space": "15% top, 25% bottom for UI safe zones",
            "visual_hierarchy": "Impact → Headline → CTA",
        },
        "instagram_post": {
            "id": "IG-POST-001",
            "name": "Instagram Feed Post",
            "category": "social_feed",
            "dimensions": (1080, 1080),
            "zones": [
                {"name": "visual", "type": "image", "position": "full or upper-60%", "guidance": "Eye-catching hero image or lifestyle"},
                {"name": "headline", "type": "text", "position": "center or lower-40%", "max_chars": 60, "font": "bold (40-56pt)"},
                {"name": "caption_teaser", "type": "text", "position": "bottom", "max_chars": 100, "font": "light (20-28pt)"},
            ],
            "visual_hierarchy": "Visual → Headline → Caption",
        },
        "automotive_ad": {
            "id": "AUTO-AD-001",
            "name": "Automotive Campaign Creative",
            "category": "automotive_advertising",
            "dimensions": (1920, 1080),
            "zones": [
                {"name": "vehicle", "type": "image", "position": "center-right 60%", "guidance": "Low-angle hero shot, dramatic environment"},
                {"name": "brand_logo", "type": "image", "position": "upper-left", "guidance": "Brand logo, clean on background"},
                {"name": "headline", "type": "text", "position": "left-third", "max_chars": 40, "font": "bold (64-96pt)", "alignment": "left"},
                {"name": "spec_line", "type": "text", "position": "below-headline", "max_chars": 80, "font": "light (24pt)", "alignment": "left"},
                {"name": "cta", "type": "button", "position": "lower-left", "max_chars": 20},
            ],
            "visual_hierarchy": "Vehicle → Headline → Specs → Brand → CTA",
        },
        "presentation": {
            "id": "PRES-001",
            "name": "Professional Presentation Deck",
            "category": "presentation",
            "dimensions": (1280, 720),
            "zones": [
                {"name": "title", "type": "text", "position": "upper-center", "max_chars": 60, "font": "bold (40-48pt)"},
                {"name": "body", "type": "text", "position": "center", "max_chars": 300, "font": "regular (20-24pt)"},
                {"name": "visual_placeholder", "type": "image", "position": "right-half or center", "guidance": "Supporting visual or chart"},
                {"name": "speaker_notes", "type": "text", "position": "hidden", "max_chars": 200},
            ],
            "visual_hierarchy": "Title → Visual → Body → Notes",
        },
        "social_carousel": {
            "id": "CAR-001",
            "name": "Social Media Carousel",
            "category": "social_carousel",
            "dimensions": (1080, 1080),
            "slides": 5,
            "zones": [
                {"name": "slide_visual", "type": "image", "position": "full or upper-60%"},
                {"name": "slide_headline", "type": "text", "position": "center-lower", "max_chars": 50, "font": "bold (40pt)"},
                {"name": "slide_body", "type": "text", "position": "lower-third", "max_chars": 120, "font": "regular (22pt)"},
                {"name": "slide_number", "type": "text", "position": "upper-right", "guidance": "01/05 style"},
            ],
            "consistency_rule": "All slides must share identical typography, color system, and spacing",
        },
        "text_content": {
            "id": "TEXT-001",
            "name": "Premium Marketing Copy",
            "category": "copywriting",
            "zones": [
                {"name": "headline", "type": "text", "max_chars": 80},
                {"name": "body", "type": "text", "max_chars": 500},
                {"name": "cta", "type": "text", "max_chars": 30},
            ],
        },
    }
    return TEMPLATE_SPECS.get(deliverable, TEMPLATE_SPECS["text_content"])


def build_image_ai_instructions(brief: CreativeProductionBrief) -> str:
    """
    Generates EXACT, specific production instructions for the Image AI.
    No vague requests. Every instruction specifies WHAT, HOW, WHERE, WHY, dimensions, style, and WHAT NOT TO DO.
    """
    dims = f"{brief.dimensions[0]}x{brief.dimensions[1]}"

    # Build zone-specific composition instruction
    zone_instructions = []
    for zone in brief.template_zones:
        if zone.get("type") == "image":
            zone_instructions.append(
                f"Image composition: {zone.get('guidance', 'hero subject centered')}, "
                f"positioned at {zone.get('position', 'center')}, "
                f"occupying approximately {zone.get('size', '60%')} of the frame"
            )

    negative = (
        "no visible text overlaid on image, no watermarks, no amateur composition, "
        "no flat shadowless lighting, no cluttered backgrounds, no distorted proportions, "
        "no generic stock photo appearance"
    )
    if brief.excluded_elements:
        negative += ", " + ", ".join(brief.excluded_elements)

    instruction = (
        f"CREATIVE BRIEF FOR IMAGE AI:\n"
        f"DELIVERABLE: {brief.deliverable} for {brief.platform} platform\n"
        f"EXACT DIMENSIONS: {dims} pixels\n"
        f"PURPOSE: {brief.purpose}\n"
        f"TARGET AUDIENCE: {brief.target_audience}\n"
        f"VISUAL STYLE: {brief.visual_style}\n"
        f"MOOD: {brief.mood}\n"
        f"LIGHTING: {brief.lighting}\n"
        f"COLOR PALETTE: {brief.color_palette}\n"
        f"COMPOSITION REQUIREMENTS: {', '.join(zone_instructions) if zone_instructions else brief.composition_notes}\n"
        f"BRAND CONTEXT: {brief.brand_name} — {brief.brand_tone} tone\n"
        f"REQUIRED VISUAL ELEMENTS: {', '.join(brief.required_elements)}\n"
        f"NEGATIVE CONSTRAINTS: {negative}\n"
        f"QUALITY STANDARD: {brief.quality_level.upper()} — output must look like a professional "
        f"commercial photograph or premium advertising visual, not like a generated image."
    )
    return instruction


def build_text_ai_instructions(brief: CreativeProductionBrief) -> str:
    """
    Generates EXACT, specific production instructions for the Text AI.
    Specifies character limits, tone, hierarchy, and content structure mapped to template zones.
    """
    zone_specs = []
    for zone in brief.template_zones:
        if zone.get("type") == "text":
            zone_specs.append(
                f"  - {zone['name'].upper()}: max {zone.get('max_chars', 100)} characters, "
                f"{zone.get('font', 'professional')}, "
                f"aligned {zone.get('alignment', 'center')}"
            )

    instruction = (
        f"CREATIVE BRIEF FOR TEXT AI:\n"
        f"DELIVERABLE: {brief.deliverable} copy for {brief.platform}\n"
        f"PURPOSE: {brief.purpose}\n"
        f"TARGET AUDIENCE: {brief.target_audience}\n"
        f"BRAND TONE: {brief.brand_tone}\n"
        f"BRAND NAME: {brief.brand_name}\n"
        f"\nCONTENT STRUCTURE (map exactly to these zones):\n"
        + "\n".join(zone_specs) +
        f"\n\nREQUIRED CTA: {brief.cta}\n"
        f"QUALITY STANDARD: {brief.quality_level.upper()} — copy must be sharp, purposeful, and "
        f"sound like it was written by a senior copywriter, not generated by an AI.\n"
        f"DO NOT: use generic phrases, filler words, meaningless superlatives, or placeholder copy."
    )
    return instruction


def orchestrate_task(
    prompt: str,
    specs: Dict[str, Any] = None,
    history: List[Dict] = None,
    brand_context: str = "",
    memory_context: str = "",
) -> CreativeProductionBrief:
    """
    MASTER ORCHESTRATION FUNCTION — The Creative Director's primary decision-making layer.

    Produces a full CreativeProductionBrief that coordinates all AI models.
    This is called BEFORE any generation starts.

    Flow: Understand → Classify → Select Template → Analyze → Build Instructions
    """
    brief = CreativeProductionBrief()
    if specs is None:
        specs = {}
    lowered = prompt.lower()

    # ── Step 1: Understand the Task ───────────────────────────────────────────
    deliverable = detect_deliverable_type(prompt)
    brief.deliverable = deliverable.replace("_", " ").title()
    brief.purpose = specs.get("campaign_goal", _infer_purpose(prompt))
    brief.target_audience = specs.get("target_audience", _infer_audience(prompt))

    # ── Step 2: Determine Task Type ───────────────────────────────────────────
    image_deliverables = {"product_ad", "luxury_ad", "instagram_story", "instagram_post",
                          "automotive_ad", "pinterest", "facebook_ad", "email_header", "brand_identity"}
    needs_image_deliverables = {"product_ad", "luxury_ad", "instagram_story", "instagram_post",
                                "automotive_ad", "pinterest", "social_carousel"}

    if deliverable in image_deliverables:
        brief.task_type = "image"
        brief.needs_image = True
        brief.needs_text = deliverable not in {"brand_identity"}
    elif deliverable == "presentation":
        brief.task_type = "presentation"
        brief.needs_image = True
        brief.needs_text = True
    elif deliverable == "social_carousel":
        brief.task_type = "carousel"
        brief.needs_image = True
        brief.needs_text = True
    else:
        brief.task_type = "text"
        brief.needs_image = False
        brief.needs_text = True

    # ── Step 3: Brand Context ─────────────────────────────────────────────────
    brief.brand_name = specs.get("brand_name", _extract_brand_name(prompt))
    brief.brand_tone = _infer_brand_tone(prompt, specs)
    brief.brand_colors = specs.get("colors", [])

    # ── Step 4: Platform & Dimensions ─────────────────────────────────────────
    platform = specs.get("platform", "general")
    brief.platform = platform

    # Map deliverable to correct dimensions
    platform_map = {
        "instagram": (1080, 1080),
        "instagram_story": (1080, 1920),
        "pinterest": (1000, 1500),
        "facebook": (1200, 628),
        "linkedin": (1200, 627),
        "presentation": (1280, 720),
    }
    if specs.get("resolution"):
        brief.dimensions = tuple(specs["resolution"])
    else:
        brief.dimensions = platform_map.get(deliverable, platform_map.get(platform, (1080, 1080)))

    # ── Step 5: Select Template ────────────────────────────────────────────────
    style_hint = specs.get("style", "")
    template = select_template_for_brief(deliverable, style_hint)
    brief.template_id = template.get("id")
    brief.template_category = template.get("category", "")
    brief.template_zones = template.get("zones", [])

    # ── Step 6: Creative Direction ─────────────────────────────────────────────
    brief.visual_style = _build_visual_style(prompt, specs, deliverable)
    brief.mood = specs.get("mood", _infer_mood(prompt, deliverable))
    brief.lighting = _select_lighting(deliverable, brief.mood)
    brief.color_palette = _build_color_palette(brief.brand_colors, deliverable, brief.mood)
    brief.composition_notes = template.get("visual_hierarchy", "")

    # ── Step 7: Content Requirements ──────────────────────────────────────────
    brief.cta = specs.get("cta", _infer_cta(prompt, deliverable))
    brief.required_elements = _infer_required_elements(prompt, deliverable)
    brief.excluded_elements = ["watermarks", "visible AI artifacts", "amateur design elements"]

    # ── Step 8: Quality Level ─────────────────────────────────────────────────
    premium_keywords = ["luxury", "premium", "agency", "high-end", "world class", "elite", "award"]
    if any(kw in lowered for kw in premium_keywords) or specs.get("quality_level") == "luxury_premium":
        brief.quality_level = "luxury_premium"
    elif any(kw in lowered for kw in ["professional", "commercial", "campaign", "brand"]):
        brief.quality_level = "agency"
    else:
        brief.quality_level = "standard"

    # ── Step 9: Build AI-Specific Instructions ────────────────────────────────
    if brief.needs_image:
        brief.image_ai_instructions = build_image_ai_instructions(brief)
    if brief.needs_text:
        brief.text_ai_instructions = build_text_ai_instructions(brief)

    # ── Step 10: QC Requirements ──────────────────────────────────────────────
    brief.qc_requirements = _build_qc_checklist(deliverable, brief.quality_level)

    print(f"[CD Orchestrator] Brief created: deliverable='{brief.deliverable}' | "
          f"task_type='{brief.task_type}' | template='{brief.template_id}' | "
          f"quality='{brief.quality_level}' | dims={brief.dimensions}")

    return brief


def run_creative_qc(output: str, brief: CreativeProductionBrief, pass_num: int = 1) -> Dict[str, Any]:
    """
    Creative Director Quality Control Check.
    
    Evaluates the output against the production brief.
    Returns a QC report with pass/fail status and specific failure descriptions.
    """
    failures = []
    warnings = []
    score = 100

    lowered_output = output.lower()

    # ── Visual & Composition Checks ───────────────────────────────────────────
    if brief.task_type in ["text", "presentation", "carousel"]:
        # Headline present?
        if brief.cta and brief.cta.lower() not in lowered_output:
            warnings.append(f"CTA '{brief.cta}' may be missing or phrased differently from brief")
            score -= 5

        # Check for generic AI phrases that indicate low-quality output
        generic_phrases = [
            "as an ai", "i cannot", "i don't have the ability",
            "here is your", "here's your", "i hope this helps",
            "feel free to", "please note that", "let me know if"
        ]
        for phrase in generic_phrases:
            if phrase in lowered_output:
                failures.append(f"Generic AI phrase detected: '{phrase}' — output sounds AI-generated, not agency-quality")
                score -= 15
                break

        # Check length for brevity (for ad copy)
        if brief.deliverable in ["Product Ad", "Luxury Ad", "Instagram Story"]:
            # Ad copy should not be excessively long
            word_count = len(output.split())
            if word_count > 500 and brief.task_type == "text":
                warnings.append(f"Output is {word_count} words — ad copy should be concise and punchy")
                score -= 5

        # Check for placeholder text
        placeholder_patterns = ["lorem ipsum", "[insert", "[your brand", "[product name", "xyz brand"]
        for ph in placeholder_patterns:
            if ph in lowered_output:
                failures.append(f"Placeholder text detected: '{ph}' — replace with actual content")
                score -= 20

        # Check for brand name presence (if specified)
        if brief.brand_name and brief.brand_name.lower() not in lowered_output:
            if brief.quality_level in ["agency", "luxury_premium"]:
                warnings.append(f"Brand name '{brief.brand_name}' not found in output")
                score -= 5

    # ── Technical Checks ──────────────────────────────────────────────────────
    if brief.task_type == "image":
        # For full image outputs (markdown image links), check they exist
        img_links = re.findall(r'!\[.*?\]\((https?://[^\)]+)\)', output)
        if not img_links:
            # Check if this is a text-only copywriting output (valid for the text generation phase)
            word_count = len(output.split())

            # Always check for quality issues in copy regardless of length
            generic_phrases = [
                "as an ai", "i cannot", "i don't have the ability",
                "here is your", "here's your", "i hope this helps",
                "feel free to", "please note that", "let me know if"
            ]
            for phrase in generic_phrases:
                if phrase in lowered_output:
                    failures.append(f"Generic AI phrase detected: '{phrase}' — copy sounds AI-generated, not agency-quality")
                    score -= 15
                    break

            # Check for placeholder text (always a hard failure)
            placeholder_patterns = ["lorem ipsum", "[insert", "[your brand", "[product name", "xyz brand"]
            for ph in placeholder_patterns:
                if ph in lowered_output:
                    failures.append(f"Placeholder text detected: '{ph}' — replace with actual content")
                    score -= 20

            # Only flag as "too short" if genuinely empty or near-empty (real ad copy can be just 5-10 words)
            if word_count < 5:
                failures.append("Output is empty or too short to be a usable deliverable")
                score -= 30

    # ── QC Requirement Checks ─────────────────────────────────────────────────
    # These are brief-specific requirements
    for req in brief.qc_requirements[:5]:  # Check top 5
        if "cta" in req.lower() and not any(cta_w in lowered_output for cta_w in ["click", "shop", "discover", "learn", "get", "start", "buy", "order", "book"]):
            warnings.append(f"QC requirement may not be met: {req}")
            score -= 3

    # ── Score Calibration ─────────────────────────────────────────────────────
    score = max(0, min(100, score))
    passed = len(failures) == 0 and score >= 70

    print(f"[CD QC Pass {pass_num}] score={score}/100 | passed={passed} | "
          f"failures={len(failures)} | warnings={len(warnings)}")

    return {
        "passed": passed,
        "score": score,
        "failures": failures,
        "warnings": warnings,
        "pass_num": pass_num,
    }


def build_revision_prompt(original_prompt: str, output: str, qc_report: Dict) -> str:
    """
    Builds a specific, actionable revision prompt based on QC failures.
    The Creative Director tells the AI exactly what to fix, not just 'make it better'.
    """
    failure_list = "\n".join(f"  - {f}" for f in qc_report["failures"])
    warning_list = "\n".join(f"  - {w}" for w in qc_report["warnings"])

    revision_prompt = (
        f"### CREATIVE DIRECTOR — REVISION INSTRUCTION (Pass {qc_report['pass_num'] + 1})\n\n"
        f"Your previous output failed quality control with a score of {qc_report['score']}/100.\n\n"
        f"CRITICAL FAILURES TO FIX:\n{failure_list or '  None'}\n\n"
        f"IMPROVEMENTS REQUIRED:\n{warning_list or '  None'}\n\n"
        f"PREVIOUS OUTPUT:\n{output}\n\n"
        f"REVISION REQUIREMENTS:\n"
        f"  1. Fix ALL listed failures — they are non-negotiable\n"
        f"  2. Eliminate any AI-sounding phrases — write like a senior agency copywriter\n"
        f"  3. Ensure the output is production-ready, not a draft\n"
        f"  4. Do NOT add meta-commentary about the revision — just output the improved content\n\n"
        f"ORIGINAL CLIENT REQUEST: {original_prompt}\n\n"
        f"### REVISED OUTPUT:"
    )
    return revision_prompt


def run_agency_workflow(
    prompt: str,
    brief: CreativeProductionBrief,
    generate_fn,
    max_revisions: int = 2,
) -> Tuple[str, Dict]:
    """
    Master iterative agency workflow loop.
    
    Generate → QC → If failed: Revise → QC → Accept or flag.
    
    Args:
        prompt: original user prompt
        brief: CreativeProductionBrief from orchestrate_task()
        generate_fn: callable(prompt) -> str (the actual generation function)
        max_revisions: maximum revision cycles before accepting best result
    
    Returns:
        (final_output: str, qc_report: Dict)
    """
    current_prompt = prompt
    best_output = ""
    best_score = 0
    final_qc = {}

    for attempt in range(1, max_revisions + 2):  # +2 for initial + max_revisions
        print(f"[Agency Workflow] Attempt {attempt}/{max_revisions + 1}")

        output = generate_fn(current_prompt)

        if not output:
            print(f"[Agency Workflow] Empty output on attempt {attempt}")
            continue

        qc_report = run_creative_qc(output, brief, pass_num=attempt)

        if qc_report["score"] > best_score:
            best_score = qc_report["score"]
            best_output = output
            final_qc = qc_report

        if qc_report["passed"]:
            print(f"[Agency Workflow] QC PASSED on attempt {attempt} with score {qc_report['score']}/100")
            return best_output, final_qc

        if attempt <= max_revisions:
            print(f"[Agency Workflow] QC failed (score {qc_report['score']}). Building revision prompt...")
            current_prompt = build_revision_prompt(prompt, output, qc_report)
        else:
            print(f"[Agency Workflow] Max revisions reached. Delivering best result (score {best_score}/100)")

    return best_output, final_qc


# ── Private Helper Functions ──────────────────────────────────────────────────

def _infer_purpose(prompt: str) -> str:
    lowered = prompt.lower()
    if any(kw in lowered for kw in ["launch", "new product", "announce"]):
        return "Product launch awareness and drive initial sales"
    if any(kw in lowered for kw in ["sale", "discount", "offer", "promo"]):
        return "Drive immediate conversion and sales"
    if any(kw in lowered for kw in ["awareness", "brand", "introduce"]):
        return "Increase brand awareness and audience reach"
    if any(kw in lowered for kw in ["engagement", "social", "instagram", "linkedin"]):
        return "Drive social media engagement and community growth"
    return "Communicate key marketing message effectively"


def _infer_audience(prompt: str) -> str:
    lowered = prompt.lower()
    if any(kw in lowered for kw in ["luxury", "premium", "exclusive", "high-end"]):
        return "Affluent consumers, 28-50, premium lifestyle orientation"
    if any(kw in lowered for kw in ["b2b", "business", "enterprise", "corporate"]):
        return "Business decision-makers, C-suite and senior managers"
    if any(kw in lowered for kw in ["youth", "gen z", "teen", "young"]):
        return "Young adults, 18-28, digitally native, trend-conscious"
    return "General target audience aligned with brand positioning"


def _extract_brand_name(prompt: str) -> str:
    # Look for capitalized words that could be brand names
    matches = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b', prompt)
    common_words = {"Create", "Make", "Generate", "Design", "Build", "Show", "Write",
                    "An", "The", "For", "With", "And", "Or", "But", "Campaign", "Ad",
                    "Image", "Post", "Story", "Reel", "Video", "Product", "Brand"}
    filtered = [m for m in matches if m not in common_words and len(m) > 2]
    return filtered[0] if filtered else ""


def _infer_brand_tone(prompt: str, specs: Dict) -> str:
    tone = specs.get("brand_tone", "").lower()
    if tone:
        return tone
    lowered = prompt.lower()
    if any(kw in lowered for kw in ["luxury", "premium", "exclusive", "sophisticat"]):
        return "sophisticated, aspirational, understated elegance"
    if any(kw in lowered for kw in ["fun", "playful", "energetic", "bold"]):
        return "energetic, vibrant, youthful"
    if any(kw in lowered for kw in ["professional", "corporate", "b2b", "enterprise"]):
        return "authoritative, trustworthy, professional"
    return "professional and engaging"


def _infer_mood(prompt: str, deliverable: str) -> str:
    lowered = prompt.lower()
    if any(kw in lowered for kw in ["luxury", "premium", "fragrance", "perfume"]):
        return "opulent, sensual, refined"
    if any(kw in lowered for kw in ["car", "automotive", "speed", "performance"]):
        return "powerful, dynamic, aspirational"
    if any(kw in lowered for kw in ["food", "restaurant", "fresh"]):
        return "warm, appetizing, inviting"
    if any(kw in lowered for kw in ["tech", "app", "software", "saas"]):
        return "clean, innovative, trustworthy"
    return "professional and compelling"


def _select_lighting(deliverable: str, mood: str) -> str:
    lighting_map = {
        "luxury_ad": "controlled three-point studio lighting, key light at 45°, subtle warm fill, crisp rim light",
        "product_ad": "professional studio lighting, soft diffused key light, clean background separation",
        "automotive_ad": "dramatic large-area soft lighting from both sides, directional rim light defining body contours",
        "instagram_story": "natural lifestyle lighting or dramatic studio depending on product",
        "instagram_post": "bright, clean, optimized for small screen viewing",
    }
    return lighting_map.get(deliverable, "professional studio lighting, even and flattering")


def _build_color_palette(colors: List[str], deliverable: str, mood: str) -> str:
    if colors:
        return f"Brand colors: {', '.join(colors)}"
    if "luxury" in deliverable or "opulent" in mood:
        return "Deep black/dark navy background, warm gold/amber accents, cream/ivory typography"
    if "automotive" in deliverable:
        return "Dramatic dark background, metallic accents matching vehicle color, strong contrast"
    if "instagram" in deliverable:
        return "Vibrant, high-saturation palette optimized for feed visibility"
    return "Professional color palette with strong contrast for readability"


def _infer_cta(prompt: str, deliverable: str) -> str:
    lowered = prompt.lower()
    cta_map = {
        "product_ad": "Shop Now",
        "luxury_ad": "Discover More",
        "instagram_story": "Swipe Up",
        "instagram_post": "Learn More",
        "automotive_ad": "Configure Yours",
        "presentation": None,
        "social_carousel": "Save This",
    }
    if "book" in lowered or "appointment" in lowered:
        return "Book Now"
    if "subscribe" in lowered or "newsletter" in lowered:
        return "Subscribe"
    if "learn" in lowered or "discover" in lowered:
        return "Learn More"
    return cta_map.get(deliverable, "Get Started")


def _build_visual_style(prompt: str, specs: Dict, deliverable: str) -> str:
    """Builds a comprehensive visual style description for the deliverable."""
    style_overrides = specs.get("style", "")
    if style_overrides:
        return style_overrides

    lowered = prompt.lower()
    style_map = {
        "luxury_ad": "editorial luxury advertising — dramatic studio photography, strong negative space, premium typography, sophisticated restraint",
        "product_ad": "clean commercial product photography — controlled studio lighting, sharp product detail, white or dark seamless background",
        "automotive_ad": "dramatic automotive advertising — low-angle cinematic composition, environmental storytelling, dynamic perspective",
        "instagram_story": "full-bleed social-first visual — bold typography, high-impact composition, mobile-optimized layout",
        "instagram_post": "scroll-stopping feed aesthetic — bright, high-contrast, emotionally engaging",
        "social_carousel": "cohesive multi-frame narrative — consistent design system across all slides",
        "presentation": "clean professional slide design — generous white space, strong data visualization, executive-level polish",
    }
    if any(kw in lowered for kw in ["minimalist", "minimal", "clean", "simple"]):
        return "minimalist design — maximum negative space, restrained palette, precision typography"
    if any(kw in lowered for kw in ["bold", "vibrant", "energetic", "pop"]):
        return "bold graphic design — high contrast, vibrant color, expressive typography"
    if any(kw in lowered for kw in ["editorial", "magazine", "fashion"]):
        return "editorial fashion aesthetic — asymmetric layout, oversized typography, art-directed photography"
    return style_map.get(deliverable, "premium professional marketing design — strong hierarchy, intentional composition, brand-consistent")


def _infer_required_elements(prompt: str, deliverable: str) -> List[str]:
    elements = []
    lowered = prompt.lower()
    if "logo" in lowered:
        elements.append("brand logo")
    if "product" in lowered:
        elements.append("hero product shot")
    if "price" in lowered:
        elements.append("pricing information")
    if any(kw in lowered for kw in ["perfume", "fragrance", "bottle"]):
        elements.append("centered luxury product bottle with premium lighting")
    if any(kw in lowered for kw in ["car", "vehicle", "automotive"]):
        elements.append("full vehicle in hero position with dramatic environment")
    return elements


def _build_qc_checklist(deliverable: str, quality_level: str) -> List[str]:
    base = [
        "Output must not contain placeholder or dummy text",
        "Brand name must be present (if specified)",
        "CTA must be clear and compelling",
        "No generic AI-sounding phrases",
        "Copy must be concise and purposeful",
    ]
    if quality_level in ["agency", "luxury_premium"]:
        base += [
            "Headline must be a strong, specific benefit statement — not generic",
            "Body copy hierarchy must flow naturally from headline to CTA",
            "Every word must earn its place — eliminate all filler",
        ]
    if quality_level == "luxury_premium":
        base += [
            "Tone must feel aspirational and exclusive, never mass-market",
            "No overused superlatives (best, amazing, incredible, revolutionary)",
            "Negative space and restraint are as important as content",
        ]
    return base


def get_version() -> str:
    return "luminary_agency_orchestrator v1.0 — Universal Creative Agency Workflow"
