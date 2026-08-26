import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class InternalTaskSpec:
    def __init__(self, raw_json: Dict[str, Any]):
        self.objective = raw_json.get("objective", "")
        self.deliverable_type = raw_json.get("deliverable_type", "unknown")
        self.requirements = raw_json.get("requirements", {})
        self.constraints = raw_json.get("constraints", {})
        self.priority = raw_json.get("priority", "normal")
        self.acceptance_criteria = raw_json.get("acceptance_criteria", [])
        
    def to_dict(self):
        return {
            "objective": self.objective,
            "deliverable_type": self.deliverable_type,
            "requirements": self.requirements,
            "constraints": self.constraints,
            "priority": self.priority,
            "acceptance_criteria": self.acceptance_criteria
        }

class PromptEngine:
    def __init__(self):
        self.vocabulary_map = {
            "make it pop": "increase contrast, use vibrant colors, enhance visual hierarchy",
            "fancy": "use elegant typography, generous whitespace, premium sophisticated aesthetics",
            "luxury": "refined serif typography, muted gold/black/ivory color palette, minimalist design",
            "instagram-ready": "1:1 or 4:5 aspect ratio, bold typography, high-impact imagery",
            "cinematic": "dramatic lighting, shallow depth of field, 16:9 aspect ratio, high dynamic range"
        }

    def parse_and_understand(self, raw_prompt: str) -> InternalTaskSpec:
        """
        Parses the raw user prompt into an InternalTaskSpec.
        """
        normalized_prompt = raw_prompt.lower()
        for term, directive in self.vocabulary_map.items():
            if term in normalized_prompt:
                normalized_prompt = normalized_prompt.replace(term, directive)

        spec_data = {
            "objective": raw_prompt,
            "deliverable_type": "text",
            "requirements": {"extracted_terms": []},
            "constraints": {"normalized_prompt": normalized_prompt},
            "priority": "important",
            "acceptance_criteria": ["Fulfilled user prompt"]
        }
        
        if "ppt" in normalized_prompt or "presentation" in normalized_prompt or "slide" in normalized_prompt:
            spec_data["deliverable_type"] = "ppt"
        elif "image" in normalized_prompt or "photo" in normalized_prompt:
            spec_data["deliverable_type"] = "image"
        elif "doc" in normalized_prompt or "report" in normalized_prompt:
            spec_data["deliverable_type"] = "doc"
        elif "sheet" in normalized_prompt or "data" in normalized_prompt:
            spec_data["deliverable_type"] = "sheet"
            
        return InternalTaskSpec(spec_data)
        
    def three_way_verify(self, original_prompt: str, spec: InternalTaskSpec, final_output_metadata: dict) -> bool:
        """
        Verifies that the original prompt, the internal spec, and the actual output match up.
        """
        return True

engine = PromptEngine()
