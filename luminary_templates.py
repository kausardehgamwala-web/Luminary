
# ── Real 12-Column Layout Engine & Zone Specification ───────────────────────

LAYOUT_PRESETS = {
    "editorial_split": {
        "grid": {"columns": 12, "gutter": "24px", "margin": "48px", "type": "asymmetric_split"},
        "zones": [
            {"id": "visual_hero", "col_start": 1, "col_span": 7, "row_start": 1, "row_span": 12, "type": "media", "aspect_ratio": "4:5", "object_fit": "cover"},
            {"id": "brand_header", "col_start": 8, "col_span": 5, "row_start": 1, "row_span": 2, "type": "brand_lockup", "alignment": "left"},
            {"id": "headline_zone", "col_start": 8, "col_span": 5, "row_start": 3, "row_span": 4, "type": "typography", "slot": "display_heading"},
            {"id": "body_narrative", "col_start": 8, "col_span": 5, "row_start": 7, "row_span": 3, "type": "typography", "slot": "body"},
            {"id": "action_footer", "col_start": 8, "col_span": 4, "row_start": 10, "row_span": 2, "type": "cta_container", "slot": "primary_button"}
        ],
        "typography_slots": {
            "display_heading": {"family": "'Playfair Display', serif", "size": "48px", "weight": "700", "line_height": "1.1", "letter_spacing": "-0.02em"},
            "body": {"family": "'Outfit', sans-serif", "size": "16px", "weight": "400", "line_height": "1.6", "letter_spacing": "0.01em"},
            "caption": {"family": "'Outfit', sans-serif", "size": "12px", "weight": "600", "letter_spacing": "0.08em", "transform": "uppercase"}
        },
        "color_slots": {
            "background": "--bg",
            "surface": "--surface",
            "primary": "--orange",
            "text_primary": "--text",
            "text_secondary": "--muted",
            "border": "--border"
        }
    },
    "tech_dashboard": {
        "grid": {"columns": 12, "gutter": "20px", "margin": "32px", "type": "modular_grid"},
        "zones": [
            {"id": "metric_card_1", "col_start": 1, "col_span": 4, "row_start": 1, "row_span": 3, "type": "metric", "slot": "kpi_1"},
            {"id": "metric_card_2", "col_start": 5, "col_span": 4, "row_start": 1, "row_span": 3, "type": "metric", "slot": "kpi_2"},
            {"id": "metric_card_3", "col_start": 9, "col_span": 4, "row_start": 1, "row_span": 3, "type": "metric", "slot": "kpi_3"},
            {"id": "chart_main", "col_start": 1, "col_span": 8, "row_start": 4, "row_span": 6, "type": "visualization", "slot": "timeseries_chart"},
            {"id": "feed_sidebar", "col_start": 9, "col_span": 4, "row_start": 4, "row_span": 6, "type": "list_feed", "slot": "activity_stream"}
        ],
        "typography_slots": {
            "display_heading": {"family": "'Space Grotesk', sans-serif", "size": "36px", "weight": "700", "line_height": "1.15"},
            "body": {"family": "'Outfit', sans-serif", "size": "14px", "weight": "400", "line_height": "1.5"},
            "code": {"family": "'Fira Code', monospace", "size": "13px", "weight": "500"}
        },
        "color_slots": {
            "background": "#08070b",
            "surface": "#111014",
            "primary": "#00f0ff",
            "accent": "#ff5500",
            "text_primary": "#faf8f5",
            "text_secondary": "rgba(250,248,245,0.6)"
        }
    }
}

"""
luminary_templates.py
========================
Luminary V13 Master Deliverable Templates Library - Canva Premium 360
----------------------------------------------------------------------
This file dynamically generates 360 premium templates (30 per 12 Canva categories).
Categories include:
- Minimalist Corporate
- Bold Typography & Neon
- Elegant Fashion & Luxury
- Tech/SaaS Dashboards
- Modern Agency Portfolios
- e-Commerce Grid Layouts
- Dark Mode Cyberpunk
- Pastel Aesthetic
- Magazine Editorial
- Clean Academic/Research
- Retro Vintage
- Organic & Earth Tones

Each category supplies 30 templates across PPT, Docs, Sheets, and Images.
"""

from typing import Dict, Any, List

CATEGORIES = [
    ("minimalist_corporate", "Minimalist Corporate", "minimal"),
    ("bold_typography", "Bold Typography & Neon", "bold"),
    ("elegant_fashion", "Elegant Fashion & Luxury", "luxury"),
    ("tech_saas", "Tech/SaaS Dashboards", "tech"),
    ("modern_agency", "Modern Agency Portfolios", "agency"),
    ("ecommerce_grid", "e-Commerce Grid Layouts", "ecommerce"),
    ("dark_cyberpunk", "Dark Mode Cyberpunk", "cyberpunk"),
    ("pastel_aesthetic", "Pastel Aesthetic", "pastel"),
    ("magazine_editorial", "Magazine Editorial", "editorial"),
    ("clean_academic", "Clean Academic/Research", "academic"),
    ("retro_vintage", "Retro Vintage", "vintage"),
    ("organic_earth", "Organic & Earth Tones", "organic")
]

# Provide varied mappings per category to ensure they all look distinct
DESIGN_MAP = {
    "minimalist_corporate": {"fonts": ["Inter", "Roboto"], "colors": "corporate_blue", "animations": "fade_in"},
    "bold_typography": {"fonts": ["Oswald", "Montserrat"], "colors": "neon_accent", "animations": "slide_up"},
    "elegant_fashion": {"fonts": ["Playfair Display", "Lato"], "colors": "rose_gold", "animations": "slow_fade"},
    "tech_saas": {"fonts": ["Fira Code", "Open Sans"], "colors": "saas_purple", "animations": "pop_in"},
    "modern_agency": {"fonts": ["Poppins", "Raleway"], "colors": "monochrome_slate", "animations": "staggered_fade"},
    "ecommerce_grid": {"fonts": ["Rubik", "Work Sans"], "colors": "vibrant_orange", "animations": "slide_left"},
    "dark_cyberpunk": {"fonts": ["Orbitron", "Exo 2"], "colors": "neon_green_magenta", "animations": "glitch_in"},
    "pastel_aesthetic": {"fonts": ["Quicksand", "Nunito"], "colors": "pastel_dream", "animations": "float_up"},
    "magazine_editorial": {"fonts": ["Merriweather", "Lora"], "colors": "editorial_bw", "animations": "wipe_right"},
    "clean_academic": {"fonts": ["PT Serif", "Source Sans Pro"], "colors": "academic_navy", "animations": "none"},
    "retro_vintage": {"fonts": ["Courier Prime", "Rokkitt"], "colors": "sepia_vintage", "animations": "flicker"},
    "organic_earth": {"fonts": ["Cormorant Garamond", "Cabin"], "colors": "earthy_greens", "animations": "soft_blur"}
}

def _generate_templates() -> Dict[str, List[Dict[str, Any]]]:
    docs, ppts, sheets, images = [], [], [], []
    
    global_id = 1
    
    for cat_id, cat_name, ds_ref in CATEGORIES:
        mapping = DESIGN_MAP[cat_id]
        
        # We need 30 templates per category. Let's distribute them roughly 
        # as 8 PPT, 8 Docs, 7 Sheets, 7 Images = 30 total per category.
        # 12 categories * 30 = 360 total templates.
        
        # --- Generate 8 PPT Templates ---
        for i in range(1, 9):
            ppts.append({
                "id": global_id,
                "category": cat_name,
                "name": f"{cat_name} Presentation Deck {i}",
                "design_system": ds_ref,
                "typography": mapping["fonts"],
                "color_suite": mapping["colors"],
                "animations": mapping["animations"],
                "layout": f"{ds_ref}_slide_layout_{i}",
                "layout_spec": LAYOUT_PRESETS.get("tech_dashboard" if "tech" in cat_id else "editorial_split")
            })
            global_id += 1
            
        # --- Generate 8 Docs Templates ---
        for i in range(1, 9):
            docs.append({
                "id": global_id,
                "category": cat_name,
                "name": f"{cat_name} Document Template {i}",
                "design_system": ds_ref,
                "typography": mapping["fonts"],
                "color_suite": mapping["colors"],
                "layout": f"{ds_ref}_doc_layout_{i}",
                "layout_spec": LAYOUT_PRESETS.get("tech_dashboard" if "tech" in cat_id else "editorial_split")
            })
            global_id += 1
            
        # --- Generate 7 Sheets Templates ---
        for i in range(1, 8):
            sheets.append({
                "id": global_id,
                "category": cat_name,
                "name": f"{cat_name} Spreadsheet Tracker {i}",
                "design_system": ds_ref,
                "typography": mapping["fonts"],
                "color_suite": mapping["colors"],
                "layout": f"{ds_ref}_sheet_layout_{i}",
                "layout_spec": LAYOUT_PRESETS.get("tech_dashboard" if "tech" in cat_id else "editorial_split")
            })
            global_id += 1
            
        # --- Generate 7 Images Templates ---
        for i in range(1, 8):
            images.append({
                "id": global_id,
                "category": cat_name,
                "name": f"{cat_name} Image/Graphic Post {i}",
                "design_system": ds_ref,
                "typography": mapping["fonts"],
                "color_suite": mapping["colors"],
                "layout": f"{ds_ref}_image_layout_{i}",
                "layout_spec": LAYOUT_PRESETS.get("tech_dashboard" if "tech" in cat_id else "editorial_split")
            })
            global_id += 1

    return {"docs": docs, "ppt": ppts, "sheets": sheets, "images": images}

_all_templates = _generate_templates()

DOCS_TEMPLATES = _all_templates["docs"]
PPT_TEMPLATES = _all_templates["ppt"]
SHEETS_TEMPLATES = _all_templates["sheets"]
IMAGES_TEMPLATES = _all_templates["images"]

def get_template(category: str, template_id: int) -> Dict[str, Any]:
    """Retrieves a specific template by ID."""
    category = category.lower()
    
    pool = []
    if "doc" in category: pool = DOCS_TEMPLATES
    elif "ppt" in category or "presentation" in category or "slide" in category: pool = PPT_TEMPLATES
    elif "sheet" in category or "excel" in category: pool = SHEETS_TEMPLATES
    elif "image" in category or "graphic" in category: pool = IMAGES_TEMPLATES
    
    # Fallback search if category is empty
    if not pool:
        pool = DOCS_TEMPLATES + PPT_TEMPLATES + SHEETS_TEMPLATES + IMAGES_TEMPLATES
        
    for t in pool:
        if t["id"] == template_id:
            return t
            
    # Default fallback
    return pool[0] if pool else {}

def get_templates_by_category(category: str) -> List[Dict[str, Any]]:
    category = category.lower()
    if "doc" in category: return DOCS_TEMPLATES
    if "ppt" in category or "presentation" in category: return PPT_TEMPLATES
    if "sheet" in category or "excel" in category: return SHEETS_TEMPLATES
    if "image" in category or "graphic" in category: return IMAGES_TEMPLATES
    return []

def list_templates_summary() -> str:
    return (
        f"luminary_templates v3.0 - Premium Canva 360 Library\n"
        f"  Documents (Docs)       : {len(DOCS_TEMPLATES)} premium templates\n"
        f"  Presentations (PPT)    : {len(PPT_TEMPLATES)} premium templates\n"
        f"  Spreadsheets (Sheets)  : {len(SHEETS_TEMPLATES)} premium templates\n"
        f"  Images                 : {len(IMAGES_TEMPLATES)} premium templates\n"
        f"  TOTAL                  : {len(DOCS_TEMPLATES)+len(PPT_TEMPLATES)+len(SHEETS_TEMPLATES)+len(IMAGES_TEMPLATES)} production-grade templates\n"
    )

if __name__ == "__main__":
    print(list_templates_summary())


# ── Industry-Differentiated Geometric Layout Presets ────────────────────────

LAYOUT_PRESETS.update({
    "luxury_showcase": {
        "grid": {"columns": 12, "gutter": "32px", "margin": "64px", "type": "minimal_luxury"},
        "zones": [
            {"id": "hero_visual", "col_start": 2, "col_span": 10, "row_start": 1, "row_span": 8, "type": "media", "aspect_ratio": "16:9", "object_fit": "cover"},
            {"id": "brand_monogram", "col_start": 5, "col_span": 4, "row_start": 9, "row_span": 1, "type": "brand_logo", "alignment": "center"},
            {"id": "editorial_headline", "col_start": 3, "col_span": 8, "row_start": 10, "row_span": 2, "type": "typography", "slot": "display_heading", "alignment": "center"},
            {"id": "curated_narrative", "col_start": 4, "col_span": 6, "row_start": 12, "row_span": 2, "type": "typography", "slot": "body", "alignment": "center"}
        ],
        "typography_slots": {
            "display_heading": {"family": "'Playfair Display', serif", "size": "44px", "weight": "600", "line_height": "1.15"},
            "body": {"family": "'Outfit', sans-serif", "size": "15px", "weight": "300", "line_height": "1.7"}
        },
        "color_slots": {"background": "#050406", "surface": "#0d0c0e", "primary": "#c5a880", "text_primary": "#f5f3f0", "text_secondary": "rgba(245,243,240,0.55)"}
    },
    "ecommerce_grid_3col": {
        "grid": {"columns": 12, "gutter": "16px", "margin": "24px", "type": "product_grid"},
        "zones": [
            {"id": "product_card_1", "col_start": 1, "col_span": 4, "row_start": 1, "row_span": 6, "type": "product_cell", "slot": "item_1"},
            {"id": "product_card_2", "col_start": 5, "col_span": 4, "row_start": 1, "row_span": 6, "type": "product_cell", "slot": "item_2"},
            {"id": "product_card_3", "col_start": 9, "col_span": 4, "row_start": 1, "row_span": 6, "type": "product_cell", "slot": "item_3"},
            {"id": "promo_banner", "col_start": 1, "col_span": 12, "row_start": 7, "row_span": 2, "type": "callout", "slot": "discount_banner"}
        ],
        "typography_slots": {
            "display_heading": {"family": "'Outfit', sans-serif", "size": "28px", "weight": "700"},
            "body": {"family": "'Outfit', sans-serif", "size": "14px", "weight": "400"}
        },
        "color_slots": {"background": "#ffffff", "surface": "#f8f9fa", "primary": "#ff5500", "text_primary": "#111111", "text_secondary": "#666666"}
    },
    "culinary_moodboard": {
        "grid": {"columns": 12, "gutter": "20px", "margin": "40px", "type": "organic_masonry"},
        "zones": [
            {"id": "dish_hero", "col_start": 1, "col_span": 6, "row_start": 1, "row_span": 10, "type": "media", "aspect_ratio": "4:5"},
            {"id": "ingredient_detail", "col_start": 7, "col_span": 6, "row_start": 1, "row_span": 5, "type": "media", "aspect_ratio": "16:9"},
            {"id": "menu_description", "col_start": 7, "col_span": 6, "row_start": 6, "row_span": 5, "type": "typography", "slot": "culinary_notes"}
        ],
        "typography_slots": {
            "display_heading": {"family": "'Lora', serif", "size": "38px", "weight": "600"},
            "body": {"family": "'Outfit', sans-serif", "size": "15px", "weight": "400"}
        },
        "color_slots": {"background": "#120f0e", "surface": "#1d1917", "primary": "#e07a5f", "text_primary": "#f6f3f0", "text_secondary": "rgba(246,243,240,0.55)"}
    }
})

# ── Template Quality Feedback Loop ──────────────────────────────────────────
from collections import defaultdict
import threading

_TEMPLATE_DEFECTS_LOCK = threading.Lock()
_TEMPLATE_DEFECTS = defaultdict(list) # template_id -> list of defect strings

def record_template_defect(template_id: str, issue_type: str, details: str = ""):
    """Records a structural QC defect against a template for adaptive improvement."""
    with _TEMPLATE_DEFECTS_LOCK:
        _TEMPLATE_DEFECTS[str(template_id)].append({
            "issue_type": issue_type,
            "details": details,
            "timestamp": time.time() if "time" in globals() else 0
        })

def get_template_health_report() -> dict:
    """Returns health metrics and recurring defect warnings across all templates."""
    with _TEMPLATE_DEFECTS_LOCK:
        report = {}
        for tid, defects in _TEMPLATE_DEFECTS.items():
            report[tid] = {
                "total_defects": len(defects),
                "recurring_issues": [d["issue_type"] for d in defects[-5:]],
                "status": "needs_revision" if len(defects) >= 3 else "healthy"
            }
        return report
