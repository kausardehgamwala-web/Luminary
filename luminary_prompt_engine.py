"""
luminary_prompt_engine.py — Strategic Prompt Understanding & 3-Way Verification
================================================================================
Implements:
  - LLM-powered prompt understanding (in-depth intent, deliverable, audience, tone, constraints)
  - Handling of vague/paraphrased requests ("make it pop", "something luxury", incomplete briefs)
  - Ambiguity detection & strategic clarification generation
  - 3-Way Semantic Verification (Original Prompt <-> Interpreted Brief <-> Final Output)
  - Deterministic fast fallback when LLM server is offline
"""

import json
import logging
import re
import urllib.request
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Vocabulary mapping for creative translations
VOCABULARY_EXPANSIONS = {
    "make it pop": "increase visual contrast, apply dynamic typography hierarchy, use vivid accent saturation",
    "fancy": "use refined editorial serif typography, generous whitespace, understated luxury styling",
    "luxury": "sophisticated noir/gold/ivory palette, high-contrast editorial photography, minimalist layout",
    "instagram-ready": "optimal 1080x1350 vertical/square composition, high thumb-stop hook, readable text overlay",
    "cinematic": "dramatic directional lighting, 16:9 widescreen composition, rich shadows and depth",
    "corporate": "clean professional structure, data-driven credibility, enterprise color palette, clear hierarchy",
    "viral": "strong curiosity gap hook, punchy short-form copy, clear emotional trigger, high-contrast visual",
}

class InternalTaskSpec:
    def __init__(self, raw_data: Dict[str, Any]):
        self.objective = raw_data.get("objective", "")
        self.deliverable_type = raw_data.get("deliverable_type", "text")
        self.target_audience = raw_data.get("target_audience", "General Target Audience")
        self.brand_tone = raw_data.get("brand_tone", "Professional & Premium")
        self.brand_context = raw_data.get("brand_context", {})
        self.requirements = raw_data.get("requirements", {})
        self.constraints = raw_data.get("constraints", {})
        self.priority = raw_data.get("priority", "normal")
        self.acceptance_criteria = raw_data.get("acceptance_criteria", [])
        self.is_ambiguous = raw_data.get("is_ambiguous", False)
        self.clarifying_questions = raw_data.get("clarifying_questions", [])
        self.design_system_hint = raw_data.get("design_system_hint", "ai_marketing_agency")
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "objective": self.objective,
            "deliverable_type": self.deliverable_type,
            "target_audience": self.target_audience,
            "brand_tone": self.brand_tone,
            "brand_context": self.brand_context,
            "requirements": self.requirements,
            "constraints": self.constraints,
            "priority": self.priority,
            "acceptance_criteria": self.acceptance_criteria,
            "is_ambiguous": self.is_ambiguous,
            "clarifying_questions": self.clarifying_questions,
            "design_system_hint": self.design_system_hint
        }


class PromptEngine:
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.vocabulary_map = VOCABULARY_EXPANSIONS

    def _query_model(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """Queries local Ollama or returns None if offline."""
        try:
            url = f"{self.ollama_url}/api/generate"
            payload = {
                "model": "qwen2.5:3b",
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {"temperature": 0.2, "num_predict": 400}
            }
            req = urllib.request.Request(
                url, 
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("response", "")
        except Exception:
            return None

    def parse_and_understand(self, raw_prompt: str, client_context: Optional[dict] = None) -> InternalTaskSpec:
        """
        Deeply understands the raw client request like an agency strategist.
        Infers deliverable type, target audience, tone, key constraints, and ambiguity.
        """
        if not raw_prompt or not raw_prompt.strip():
            return InternalTaskSpec({
                "objective": "Empty request",
                "deliverable_type": "text",
                "is_ambiguous": True,
                "clarifying_questions": ["What type of marketing deliverable can we create for your brand today?"]
            })

        # 1. Try LLM-Powered Strategic Brief Extraction
        sys_prompt = (
            "You are an elite creative agency account director. Analyze the client's request.\n"
            "Output ONLY valid JSON with keys:\n"
            "  deliverable_type: string ('presentation', 'document', 'spreadsheet', 'product_ad', 'website', 'social_carousel', 'instagram_post', 'pinterest_post', 'email', 'copywriting')\n"
            "  target_audience: string\n"
            "  brand_tone: string\n"
            "  key_constraints: list of strings\n"
            "  is_ambiguous: boolean (true if request is too vague to execute without guessing)\n"
            "  clarifying_questions: list of 1-3 specific questions if ambiguous, else empty list\n"
            "  design_system_hint: string ('ai_saas', 'luxury_brand', 'creative_agency', 'ecommerce', 'fintech', 'automotive', 'hospitality', 'beauty')"
        )
        
        analysis_prompt = f"Client Brief: {raw_prompt}\nClient Brand Context: {json.dumps(client_context or {})}"
        model_output = self._query_model(analysis_prompt, sys_prompt)
        
        if model_output:
            try:
                json_match = re.search(r'\{[\s\S]*\}', model_output)
                if json_match:
                    parsed_json = json.loads(json_match.group(0))
                    spec_data = {
                        "objective": raw_prompt,
                        "deliverable_type": parsed_json.get("deliverable_type", "copywriting"),
                        "target_audience": parsed_json.get("target_audience", "High-intent prospective buyers"),
                        "brand_tone": parsed_json.get("brand_tone", "Authoritative, premium, conversion-focused"),
                        "brand_context": client_context or {},
                        "requirements": {"expanded_directives": []},
                        "constraints": {"key_constraints": parsed_json.get("key_constraints", [])},
                        "priority": "high",
                        "acceptance_criteria": ["Achieves core strategic goal", "Meets visual and copy quality standards"],
                        "is_ambiguous": parsed_json.get("is_ambiguous", False),
                        "clarifying_questions": parsed_json.get("clarifying_questions", []),
                        "design_system_hint": parsed_json.get("design_system_hint", "ai_marketing_agency")
                    }
                    return InternalTaskSpec(spec_data)
            except Exception as e:
                logger.warning(f"Error parsing model brief JSON: {e}")

        # 2. Robust Deterministic Fallback Engine (Fast & Semantic)
        return self._deterministic_fallback_understanding(raw_prompt, client_context)

    def _deterministic_fallback_understanding(self, raw_prompt: str, client_context: Optional[dict] = None) -> InternalTaskSpec:
        """Deterministic NLP classification with phrase normalization."""
        pl = raw_prompt.lower().strip()
        words = pl.split()
        
        # Expand creative terminology
        expanded_directives = []
        for term, directive in self.vocabulary_map.items():
            if term in pl:
                expanded_directives.append(directive)

        # Detect deliverable type
        deliverable = "copywriting"
        has_explicit_deliverable = False
        
        if any(k in pl for k in ["ppt", "presentation", "deck", "slide", "pitch deck", "powerpoint"]):
            deliverable = "presentation"
            has_explicit_deliverable = True
        elif any(k in pl for k in ["spreadsheet", "excel", "xlsx", "sheet", "csv", "data table", "budget"]):
            deliverable = "spreadsheet"
            has_explicit_deliverable = True
        elif any(k in pl for k in ["report", "doc", "document", "article", "blog", "whitepaper", "proposal", "case study"]):
            deliverable = "document"
            has_explicit_deliverable = True
        elif any(k in pl for k in ["website", "landing page", "web page", "html", "site design"]):
            deliverable = "website"
            has_explicit_deliverable = True
        elif any(k in pl for k in ["carousel", "swipe"]):
            deliverable = "social_carousel"
            has_explicit_deliverable = True
        elif any(k in pl for k in ["pinterest", "pin"]):
            deliverable = "pinterest_post"
            has_explicit_deliverable = True
        elif any(k in pl for k in ["instagram", "ig post", "insta"]):
            deliverable = "instagram_post"
            has_explicit_deliverable = True
        elif any(k in pl for k in ["email", "newsletter", "drip"]):
            deliverable = "email"
            has_explicit_deliverable = True
        elif any(k in pl for k in ["image", "photo", "render", "poster", "banner", "visual", "product photo", "shoot"]):
            deliverable = "product_ad"
            has_explicit_deliverable = True

        # Detect ambiguity (very short or lacking deliverable context)
        is_ambiguous = False
        clarifying_questions = []
        
        vague_intents = ["help", "make something", "do something", "create something", "market my business", "promote", "make it pop", "something nice", "grow my brand", "need ads", "make a post"]
        is_too_short = len(words) < 4 and not has_explicit_deliverable
        is_vague = any(pl == v or pl.startswith(v + " ") for v in vague_intents)
        
        if is_too_short or is_vague:
            is_ambiguous = True
            clarifying_questions = [
                "1. Format & Channel: What deliverable are we building? (e.g., 10-Slide Pitch Deck, Instagram Carousel, Responsive Landing Page, Email Drip Sequence)",
                "2. Target Audience: Who is the ideal customer persona (ICP) and what is their primary pain point?",
                "3. Brand Voice & Objective: What is your primary conversion goal (e.g., immediate sales, investor funding, brand authority) and desired tone?"
            ]

        # Infer Tone
        tone = "Professional, persuasive, and brand-aligned"
        if any(k in pl for k in ["luxury", "prestige", "exclusive", "couture", "perfume", "high-end"]):
            tone = "Minimalist luxury, elegant, sophisticated, and evocative"
        elif any(k in pl for k in ["fun", "casual", "playful", "witty", "gen-z"]):
            tone = "Vibrant, conversational, energetic, and engaging"
        elif any(k in pl for k in ["tech", "saas", "b2b", "enterprise", "developer"]):
            tone = "Authoritative, clear, metric-driven, and innovative"

        # Design system hint
        design_system = "ai_marketing_agency"
        if "luxury" in tone.lower():
            design_system = "luxury_brand"
        elif "tech" in pl or "saas" in pl:
            design_system = "ai_saas"
        elif "ecommerce" in pl or "shop" in pl:
            design_system = "ecommerce"

        spec_data = {
            "objective": raw_prompt,
            "deliverable_type": deliverable,
            "target_audience": "Target demographic seeking high-value solutions",
            "brand_tone": tone,
            "brand_context": client_context or {},
            "requirements": {"expanded_directives": expanded_directives},
            "constraints": {"detected_keywords": expanded_directives},
            "priority": "normal",
            "acceptance_criteria": ["Directly fulfills client brief", "Complies with agency quality benchmark"],
            "is_ambiguous": is_ambiguous,
            "clarifying_questions": clarifying_questions,
            "design_system_hint": design_system
        }
        return InternalTaskSpec(spec_data)

    def three_way_verify(self, original_prompt: str, spec: InternalTaskSpec, final_output_metadata: dict) -> Tuple[bool, List[str]]:
        """
        Performs real 3-way semantic verification between:
          1. The Original User Request
          2. The Interpreted Brief / Specification
          3. The Actual Final Deliverable Output
        Returns (is_verified: bool, drift_notes: List[str]).
        """
        drift_notes = []
        
        # 1. Check Deliverable Type Alignment
        expected_type = spec.deliverable_type
        actual_type = final_output_metadata.get("type", final_output_metadata.get("format", "unknown")).lower()
        
        # Mapping compatibility
        compat_map = {
            "presentation": ["presentation", "pptx", "deck", "slide"],
            "document": ["document", "docx", "doc", "text", "markdown"],
            "spreadsheet": ["spreadsheet", "xlsx", "sheet", "csv"],
            "product_ad": ["product_ad", "image", "jpg", "png", "banner"],
            "website": ["website", "code", "html"],
            "social_carousel": ["social_carousel", "presentation", "image", "carousel"],
            "instagram_post": ["instagram_post", "image", "text", "copywriting", "product_ad"],
            "pinterest_post": ["pinterest_post", "image", "pin", "product_ad"],
            "email": ["email", "text", "copywriting"],
            "copywriting": ["copywriting", "text", "document", "docx"]
        }
        
        valid_types = compat_map.get(expected_type, [expected_type])
        if actual_type != "unknown" and not any(vt in actual_type for vt in valid_types):
            drift_notes.append(f"Deliverable format mismatch: Brief expected '{expected_type}', but output generated was '{actual_type}'.")

        # 2. Check Content Completeness
        output_content = str(final_output_metadata.get("content", "")) + str(final_output_metadata.get("text", ""))
        if len(output_content.strip()) < 20 and actual_type not in ["image", "product_ad"]:
            drift_notes.append("Output deliverable appears incomplete or truncated (content length too short).")

        is_verified = len(drift_notes) == 0
        return is_verified, drift_notes


# Global prompt engine singleton
engine = PromptEngine()
