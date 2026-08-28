"""
luminary_canva.py
=================
Implements Canva integration logic for Luminary AI.
Simulates Canva agent API calls (create_design, edit_design, get_brand_templates)
and generates professional design handoff links to Canva.

NO external dependencies — pure Python stdlib only.
"""

import time
import random
from typing import Optional, List, Dict

# Mock Canva templates database
MOCK_TEMPLATES = [
    {"id": "tmpl_auto_001", "name": "Ferrari SF90 Social Promo", "aspect": "square", "platform": "Instagram", "category": "Automotive"},
    {"id": "tmpl_auto_002", "name": "Lamborghini Brand Showcase", "aspect": "landscape", "platform": "Website", "category": "Automotive"},
    {"id": "tmpl_lux_001", "name": "Minimalist Watch Launch", "aspect": "portrait", "platform": "Pinterest", "category": "Luxury"},
    {"id": "tmpl_lux_002", "name": "Premium Editorial Poster", "aspect": "portrait", "platform": "Pinterest", "category": "Luxury"},
    {"id": "tmpl_corp_001", "name": "Corporate Slide Pitch", "aspect": "widescreen", "platform": "Presentation", "category": "Corporate"},
    {"id": "tmpl_corp_002", "name": "Data Analytics Spreadsheet View", "aspect": "square", "platform": "Instagram", "category": "Corporate"},
]

# Stored designs database in-memory
_designs_db = {}


def get_canva_templates(keyword: str) -> List[Dict]:
    """Finds matching templates from the Canva catalog."""
    kw = keyword.lower()
    matches = []
    for t in MOCK_TEMPLATES:
        if kw in t["name"].lower() or kw in t["category"].lower() or kw in t["platform"].lower():
            matches.append(t)
    return matches or MOCK_TEMPLATES[:3]


def create_canva_design(name: str, width: int, height: int, template_id: Optional[str] = None) -> Dict:
    """
    Creates a new design draft.
    Simulates Canva API design creation.
    """
    design_id = f"canva_ds_{int(time.time())}_{random.randint(1000, 9999)}"
    
    # Resolve template details if provided
    template_name = "Blank Template"
    if template_id:
        for t in MOCK_TEMPLATES:
            if t["id"] == template_id:
                template_name = t["name"]
                break

    design_data = {
        "design_id": design_id,
        "name": name,
        "width": width,
        "height": height,
        "template_id": template_id,
        "template_name": template_name,
        "created_at": time.time(),
        "elements": [
            {"type": "background", "color": "#FFFFFF"},
            {"type": "heading", "text": name, "font": "Montserrat", "size": 32, "x": 100, "y": 100}
        ],
        "edit_url": f"https://www.canva.com/design/{design_id}/edit?utm_source=luminary_ai&handoff=true"
    }
    
    _designs_db[design_id] = design_data
    return design_data


def edit_canva_design(design_id: str, edit_instructions: str) -> Dict:
    """
    Simulates layout manipulation, element positioning, and text updates on an active design.
    """
    design = _designs_db.get(design_id)
    if not design:
        # Create a new fallback design if design ID doesn't exist
        design = create_canva_design("Revised Canva Draft", 1080, 1080)
        design_id = design["design_id"]

    # Append the edit instruction to the design log
    if "edits" not in design:
        design["edits"] = []
    design["edits"].append({
        "timestamp": time.time(),
        "instruction": edit_instructions
    })

    # Apply mock element movements/color changes
    inst_lower = edit_instructions.lower()
    if "dark" in inst_lower:
        design["elements"][0]["color"] = "#121212"
    if "larger" in inst_lower or "bigger" in inst_lower:
        for el in design["elements"]:
            if el["type"] == "heading":
                el["size"] = int(el["size"] * 1.5)
    if "move" in inst_lower:
        for el in design["elements"]:
            if el["type"] == "heading":
                el["x"] = int(el["x"] - 50) if "left" in inst_lower else int(el["x"] + 50)

    design["updated_at"] = time.time()
    _designs_db[design_id] = design
    return design


def get_canva_handoff_link(design_id: str) -> str:
    """Returns the direct link for design handoff, letting the user edit in Canva."""
    design = _designs_db.get(design_id)
    if design:
        return design["edit_url"]
    return f"https://www.canva.com/design/draft/edit?utm_source=luminary_ai"
