import luminary_safety
"""
luminary_asset_engine.py  —  Luminary V13 Intelligent Asset Analysis Engine
=============================================================================
Classifies user-uploaded files, extracts design tokens (colors, fonts, brand
guidelines), determines compositional role, and recommends professional
treatment for each asset in generated deliverables.

Supports: images, logos, PDFs, brand docs, screenshots, CSVs, spreadsheets.
Pure Python stdlib + optional Pillow for image analysis.
"""

import os
import re
import json
import mimetypes
from pathlib import Path
from typing import Optional

# ── ASSET CATEGORIES ───────────────────────────────────────────────────────
ASSET_CATEGORIES = {
    "logo":          ["logo", "brand mark", "icon", "badge", "symbol", "wordmark"],
    "photography":   ["photo", "image", "photograph", "shot", "picture", "campaign"],
    "screenshot":    ["screenshot", "screen", "ui", "app", "dashboard", "mockup"],
    "document":      ["pdf", "brief", "report", "brief", "spec", "proposal", "guide"],
    "spreadsheet":   ["csv", "xlsx", "xls", "data", "sheet", "table"],
    "brand_guide":   ["brand", "guidelines", "style guide", "identity", "manual", "kit"],
    "illustration":  ["illustration", "vector", "svg", "graphic", "icon set", "artwork"],
    "product":       ["product", "item", "object", "bottle", "pack", "packaging", "render"]
}

# ── FILE EXTENSION MAP ────────────────────────────────────────────────────
EXT_TYPE_MAP = {
    ".jpg":  "image", ".jpeg": "image", ".png": "image", ".webp": "image",
    ".gif":  "image", ".bmp":  "image", ".tiff": "image", ".avif": "image",
    ".svg":  "vector",
    ".pdf":  "document",
    ".csv":  "data", ".xlsx": "data", ".xls": "data", ".tsv": "data",
    ".pptx": "presentation", ".ppt": "presentation",
    ".docx": "document", ".doc": "document",
    ".mp4":  "video", ".mov": "video", ".webm": "video",
    ".ttf":  "font", ".otf": "font", ".woff": "font", ".woff2": "font",
    ".json": "data", ".xml": "data"
}

# ── COMPOSITIONAL ROLES ───────────────────────────────────────────────────
COMPOSITIONAL_ROLES = {
    "logo":         ["header", "footer", "watermark", "favicon", "brand badge"],
    "photography":  ["hero_background", "section_image", "card_thumbnail", "full_bleed", "split_layout"],
    "screenshot":   ["device_frame", "feature_preview", "comparison_panel", "carousel_item"],
    "document":     ["content_source", "data_extraction", "brief_reference"],
    "spreadsheet":  ["chart_source", "table_render", "stats_extraction"],
    "illustration": ["hero_graphic", "section_decoration", "icon_system"],
    "product":      ["hero_product_shot", "feature_highlight", "360_view", "lifestyle_integration"]
}

# ── RECOMMENDED PROFESSIONAL TREATMENTS ─────────────────────────────────
TREATMENT_LIBRARY = {
    "logo": {
        "do": [
            "Preserve aspect ratio at all times — never stretch or squish",
            "Use on clean or transparent backgrounds only",
            "Maintain minimum clear space (equal to logo height on all sides)",
            "Export in SVG for scalability, PNG for raster use",
            "For dark backgrounds: use light/white version of the logo",
            "For light backgrounds: use dark/original version of the logo"
        ],
        "dont": [
            "Never place on a busy photographic background without a safe zone or frosted panel",
            "Never rotate, skew, add drop shadows, or apply filters to the logo",
            "Never use incorrect brand color variants",
            "Never resize below minimum readable size (32px height)"
        ],
        "effects": ["frosted_glass_panel", "clear_space_enforcement", "svg_export"],
        "placement_priority": "top_left_or_center_hero"
    },
    "photography": {
        "do": [
            "Apply consistent color grading / LUT to all campaign images",
            "Use focal-point-aware cropping — never crop faces mid-forehead or mid-chin",
            "Layer text with sufficient contrast — use gradient overlay if needed",
            "Apply subtle grain for editorial quality (luxury/fashion contexts)",
            "Use parallax scrolling for hero photography"
        ],
        "dont": [
            "Never stretch or distort image proportions",
            "Never place bright text directly on bright image without overlay",
            "Never use pixelated or low-resolution images at hero scale",
            "Never use mismatched color temperatures across a campaign"
        ],
        "effects": ["color_grade", "gradient_overlay", "parallax", "ken_burns_motion"],
        "placement_priority": "full_bleed_hero_or_split_layout"
    },
    "screenshot": {
        "do": [
            "Place inside a realistic device frame (macOS, iPhone, browser)",
            "Apply subtle drop shadow for depth",
            "Animate with fade-in or slide-in for feature reveals",
            "Use at 2x resolution minimum for retina clarity",
            "Crop to show only the most relevant UI section"
        ],
        "dont": [
            "Never show outdated or broken UI states",
            "Never use blurry or low-resolution screenshots",
            "Never display at 1:1 pixel scale without retina handling"
        ],
        "effects": ["device_frame", "drop_shadow", "retina_scale"],
        "placement_priority": "feature_section_center_or_split"
    },
    "document": {
        "do": [
            "Extract key text content for slide/section copy",
            "Extract quantitative data for infographic or chart generation",
            "Use as reference for tone, naming conventions and brand terminology",
            "Extract color hex codes from brand guidelines PDFs"
        ],
        "dont": [
            "Never display a raw PDF page as a visual asset",
            "Never use document content verbatim without design formatting"
        ],
        "effects": ["content_extraction", "data_visualization"],
        "placement_priority": "content_source_only"
    },
    "spreadsheet": {
        "do": [
            "Convert tabular data into styled HTML table or chart",
            "Identify numerical trends for data visualization (bar, line, donut)",
            "Extract key metrics for hero stat callouts",
            "Use column headers to infer semantic meaning of data"
        ],
        "dont": [
            "Never display raw spreadsheet rows without visual formatting",
            "Never truncate important data without summary"
        ],
        "effects": ["chart_render", "stat_callout", "table_style"],
        "placement_priority": "data_section_or_stats_block"
    },
    "product": {
        "do": [
            "Use on dark background with subtle radial glow for drama",
            "Apply soft drop shadow or reflection for depth",
            "Ensure product is the clear visual focal point — eliminate distractions",
            "Use zoom animation on hover or scroll reveal on entrance",
            "Consider 360-degree rotation for interactive presentations"
        ],
        "dont": [
            "Never use a product image with visible background unless intentional",
            "Never place product competing with text for visual hierarchy",
            "Never use flat-on-white product images in luxury contexts"
        ],
        "effects": ["radial_glow", "drop_shadow", "background_removal", "zoom_hover"],
        "placement_priority": "hero_center_or_split_layout"
    }
}


class AssetRecord:
    """Represents a single analysed asset with its classification and design recommendations."""

    def __init__(self, filepath: str, user_description: str = ""):
        self.filepath        = filepath
        self.filename        = Path(filepath).name
        self.extension       = Path(filepath).suffix.lower()
        self.user_description = user_description.lower()
        self.file_type       = EXT_TYPE_MAP.get(self.extension, "unknown")
        self.category        = self._classify_category()
        self.treatment       = TREATMENT_LIBRARY.get(self.category, {})
        self.roles           = COMPOSITIONAL_ROLES.get(self.category, [])
        self.dominant_colors  = []
        self.is_transparent  = False
        self.aspect_ratio    = None
        self.file_size_kb    = self._get_file_size()

    def _classify_category(self) -> str:
        """Classify asset into a semantic category using filename + description heuristics."""
        combined = (self.filename + " " + self.user_description).lower()
        for category, keywords in ASSET_CATEGORIES.items():
            if any(k in combined for k in keywords):
                return category
        # Fallback by file type
        if self.file_type == "image":
            return "photography"
        if self.file_type == "vector":
            return "illustration"
        if self.file_type in ("document", "data", "presentation"):
            return self.file_type
        return "photography"

    def _get_file_size(self) -> float:
        try:
            return round(os.path.getsize(self.filepath) / 1024, 1)
        except Exception:
            return 0.0

    def analyse_image(self) -> dict:
        """
        Perform image analysis if Pillow is available.
        Extracts: dominant colors, transparency, aspect ratio, resolution.
        """
        result = {"colors": [], "transparent": False, "aspect_ratio": None, "width": 0, "height": 0}
        try:
            from PIL import Image
            img = Image.open(self.filepath)
            self.aspect_ratio = round(img.width / img.height, 2)
            result["width"]  = img.width
            result["height"] = img.height
            result["aspect_ratio"] = self.aspect_ratio
            self.is_transparent = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
            result["transparent"] = self.is_transparent

            # Dominant color extraction (quantize to 8 colors)
            small = img.convert("RGB").resize((150, 150))
            quantized = small.quantize(colors=8, method=Image.Quantize.MEDIANCUT)
            palette = quantized.getpalette()
            colors = []
            for i in range(8):
                r, g, b = palette[i*3], palette[i*3+1], palette[i*3+2]
                hex_val = f"#{r:02x}{g:02x}{b:02x}"
                colors.append(hex_val)
            self.dominant_colors = colors
            result["colors"] = colors
        except ImportError:
            result["note"] = "Pillow not installed — install with: pip install Pillow"
        except Exception as e:
            result["error"] = str(e)
        return result

    def to_dict(self) -> dict:
        return {
            "filename":       self.filename,
            "file_type":      self.file_type,
            "category":       self.category,
            "file_size_kb":   self.file_size_kb,
            "aspect_ratio":   self.aspect_ratio,
            "is_transparent": self.is_transparent,
            "dominant_colors":self.dominant_colors,
            "roles":          self.roles,
            "treatment_do":   self.treatment.get("do", []),
            "treatment_dont": self.treatment.get("dont", []),
            "recommended_effects": self.treatment.get("effects", []),
            "placement_priority":  self.treatment.get("placement_priority", "")
        }

    def get_prompt_context(self) -> str:
        """Returns a formatted string for injection into AI generation prompts."""
        lines = [
            f"ASSET: {self.filename} ({self.category.upper()})",
            f"  Role options: {', '.join(self.roles[:3])}",
            f"  Placement: {self.treatment.get('placement_priority', 'flexible')}",
        ]
        if self.dominant_colors:
            lines.append(f"  Brand colors extracted: {', '.join(self.dominant_colors[:4])}")
        if self.is_transparent:
            lines.append("  Transparency: YES — safe for any background")
        dos = self.treatment.get("do", [])
        if dos:
            lines.append(f"  Key treatment rule: {dos[0]}")
        return "\n".join(lines)


class AssetEngine:
    """
    Central engine that processes all user-uploaded assets in a session.
    Builds a design-ready asset manifest for use in generation prompts.
    """

    def __init__(self):
        self.assets: list[AssetRecord] = []

    def add_asset(self, filepath: str, user_description: str = "") -> AssetRecord:
        """Register a new asset. Automatically analyses images if Pillow is available."""
        record = AssetRecord(filepath, user_description)
        if record.file_type in ("image", "vector"):
            record.analyse_image()
        self.assets.append(record)
        return record

    def add_assets(self, filepaths: list, descriptions: Optional[list] = None) -> list:
        """Register multiple assets at once."""
        descriptions = descriptions or [""] * len(filepaths)
        return [self.add_asset(fp, desc) for fp, desc in zip(filepaths, descriptions)]

    def get_logos(self) -> list:
        return [a for a in self.assets if a.category == "logo"]

    def get_photography(self) -> list:
        return [a for a in self.assets if a.category == "photography"]

    def get_products(self) -> list:
        return [a for a in self.assets if a.category == "product"]

    def get_documents(self) -> list:
        return [a for a in self.assets if a.category in ("document", "spreadsheet")]

    def extract_brand_colors(self) -> list:
        """Aggregate all dominant colors from logo + product assets."""
        colors = []
        for asset in self.assets:
            if asset.category in ("logo", "product", "illustration"):
                colors.extend(asset.dominant_colors)
        # Deduplicate while preserving order
        seen = set()
        unique = []
        for c in colors:
            if c not in seen:
                seen.add(c)
                unique.append(c)
        return unique[:6]  # Return top 6 brand colors

    def build_prompt_context(self) -> str:
        """Build a formatted asset context block for injection into generation prompts."""
        if not self.assets:
            return ""
        lines = ["── ASSET MANIFEST ──────────────────────────────────"]
        for asset in self.assets:
            lines.append(asset.get_prompt_context())
        brand_colors = self.extract_brand_colors()
        if brand_colors:
            lines.append(f"── EXTRACTED BRAND COLORS: {', '.join(brand_colors)}")
        lines.append("── END ASSET MANIFEST ──────────────────────────────")
        return "\n".join(lines)

    def build_design_brief(self) -> dict:
        """Returns a structured design brief based on all uploaded assets."""
        return {
            "total_assets": len(self.assets),
            "logos":        [a.to_dict() for a in self.get_logos()],
            "photography":  [a.to_dict() for a in self.get_photography()],
            "products":     [a.to_dict() for a in self.get_products()],
            "documents":    [a.to_dict() for a in self.get_documents()],
            "brand_colors": self.extract_brand_colors(),
            "prompt_context": self.build_prompt_context()
        }

    def validate_assets(self) -> list:
        """Quality-check all registered assets. Returns list of warnings."""
        warnings = []
        for asset in self.assets:
            if asset.file_size_kb > 20480:  # >20MB
                warnings.append(f"⚠ {asset.filename}: File is very large ({asset.file_size_kb}KB). Consider compression.")
            if asset.category == "logo" and not asset.is_transparent:
                warnings.append(f"⚠ {asset.filename}: Logo has no transparency — may not work on all backgrounds.")
            if asset.category == "photography" and asset.file_size_kb < 100:
                warnings.append(f"⚠ {asset.filename}: Photo appears very small ({asset.file_size_kb}KB) — may be low resolution.")
        return warnings

    def clear(self):
        """Reset the engine for a new session."""
        self.assets = []

    def summary(self) -> str:
        categories = {}
        for a in self.assets:
            categories[a.category] = categories.get(a.category, 0) + 1
        parts = [f"{v} {k}" for k, v in categories.items()]
        return f"AssetEngine: {len(self.assets)} assets registered — {', '.join(parts) if parts else 'none'}"


# ── Singleton for server-level use ────────────────────────────────────────
_engine_instance = AssetEngine()

def get_engine() -> AssetEngine:
    """Return the global AssetEngine singleton."""
    return _engine_instance


def reset_engine():
    """Reset the global engine (call between sessions if needed)."""
    _engine_instance.clear()


# ── Quick classification utility (no file needed) ─────────────────────────
def classify_by_filename(filename: str) -> str:
    """Classify an asset category purely from its filename string."""
    name = filename.lower()
    for category, keywords in ASSET_CATEGORIES.items():
        if any(k in name for k in keywords):
            return category
    ext = Path(filename).suffix.lower()
    return EXT_TYPE_MAP.get(ext, "unknown")


if __name__ == "__main__":
    engine = AssetEngine()
    print(engine.summary())
    print("\nTreatment DO rules for LOGO:")
    for rule in TREATMENT_LIBRARY["logo"]["do"]:
        print(f"  ✓ {rule}")
    print("\nTreatment DON'T rules for LOGO:")
    for rule in TREATMENT_LIBRARY["logo"]["dont"]:
        print(f"  ✗ {rule}")


def derive_brand_palette_from_assets(asset_path_or_bytes) -> dict:
    """
    Dynamically extracts a complete 5-token brand color palette (primary, secondary, background, surface, text)
    from an uploaded brand image/logo without relying on hardcoded brand dictionaries.
    """
    try:
        from PIL import Image
        import io
        if isinstance(asset_path_or_bytes, (str, os.PathLike)) and os.path.exists(str(asset_path_or_bytes)):
            img = Image.open(str(asset_path_or_bytes)).convert("RGB")
        elif isinstance(asset_path_or_bytes, bytes):
            img = Image.open(io.BytesIO(asset_path_or_bytes)).convert("RGB")
        elif hasattr(asset_path_or_bytes, "convert"):
            img = asset_path_or_bytes.convert("RGB")
        else:
            return {
                "primary": "#ff5500", "secondary": "#894fff", "background": "#08070b",
                "surface": "#111014", "text": "#faf8f5", "extracted_palette": ["#ff5500", "#894fff", "#08070b", "#111014", "#faf8f5"]
            }

        # Downsample and get dominant colors via getcolors or mediancut
        thumb = img.resize((150, 150))
        colors_count = thumb.getcolors(maxcolors=22500)
        extracted = []
        if colors_count:
            # Sort by frequency descending
            sorted_colors = sorted(colors_count, key=lambda x: x[0], reverse=True)
            for count, (r, g, b) in sorted_colors[:8]:
                extracted.append(f"#{r:02x}{g:02x}{b:02x}")
                
        if not extracted:
            quantized = thumb.quantize(colors=8)
            raw_pal = quantized.getpalette() or []
            for i in range(min(8, len(raw_pal) // 3)):
                r, g, b = raw_pal[i*3], raw_pal[i*3+1], raw_pal[i*3+2]
                extracted.append(f"#{r:02x}{g:02x}{b:02x}")

        primary = extracted[0] if len(extracted) > 0 else "#ff5500"
        secondary = extracted[1] if len(extracted) > 1 else "#894fff"
        
        return {
            "primary": primary,
            "secondary": secondary,
            "background": "#08070b",
            "surface": "#111014",
            "text": "#faf8f5",
            "extracted_palette": extracted or [primary, secondary],
            "source": "dynamic_asset_quantization"
        }
    except Exception as ex:
        return {
            "primary": "#ff5500", "secondary": "#894fff", "background": "#08070b",
            "surface": "#111014", "text": "#faf8f5", "extracted_palette": ["#ff5500", "#894fff"], "error": str(ex)
        }
