"""
luminary_creative_director.py
==============================
The Luminary Creative Director Layer.

Interprets every user image request as a professional creative brief.
Applies product-category intelligence, material physics, platform composition
rules, lighting selection, and camera direction before a single pixel is generated.

Philosophy:
  - A senior art director doesn't ask for "high quality". They specify
    the lighting setup, material rendering, composition, and mood.
  - This module does that work automatically.

NO external dependencies — pure Python stdlib only.
"""

import re
from typing import Optional


# ── Product Category Profiles ────────────────────────────────────────────────
# Each profile specifies the complete photography blueprint for that category.
# These are the decisions a senior commercial photographer makes before shooting.
PRODUCT_CATEGORY_PROFILES = {
    "perfume": {
        "label": "Luxury Fragrance / Perfume",
        "subject_description": "sculptural perfume bottle with thick optical glass walls, liquid visible inside with gradient depth, precision-machined metallic cap, embossed or embellished label",
        "material": "thick optical glass with internal light refraction and realistic caustics, polished metallic cap with directional highlight streaks, liquid color visible through glass",
        "lighting": "controlled three-point studio lighting: dominant soft key light from 45 degrees, subtle warm fill from opposite side, crisp rim light separating bottle from background, no blown-out highlights",
        "camera": "50mm macro lens equivalent, slightly below eye-level hero angle, shallow depth of field f/2.8 equivalent to isolate bottle from background",
        "environment": "premium studio: polished acrylic or black glass surface, subtle reflection of bottle below, atmospheric background haze in product color family",
        "composition": "bottle positioned at golden-ratio intersection, generous negative space on opposite side for text/CTA, background color complements liquid color",
        "surface_details": "soft shadow anchoring bottle to surface, faint background bokeh, no harsh floor shadows",
        "props": "optional: dried botanicals, raw fragrance ingredients, silk fabric draped softly at edge — only if they reinforce the brand story",
        "negative": "no text on image, no watermark, no cluttered background, no flat lighting, no toy-like appearance, no CGI cartoon look",
    },
    "automotive": {
        "label": "Automotive / Car",
        "subject_description": "full vehicle in motion or stationary hero pose, all panels clearly visible, accurate proportions, real-world scale",
        "material": "high-gloss automotive paint with accurate metallic flake or solid color, chrome trim with sharp environment reflections, glass windshield with subtle reflection",
        "lighting": "large-area soft lighting from both sides for clean body panel reads, dramatic rim light outlining the roofline, directional key light revealing body contours and character lines",
        "camera": "low angle (ground level to door handle height), 35mm-50mm lens equivalent, three-quarter front or rear view for maximum design reveal",
        "environment": "studio infinity cove or dramatic outdoor location: wet asphalt for reflections, architectural environment, moody sky, or dark void studio",
        "composition": "car occupies 70-80% of frame, strong diagonal orientation, ground contact always visible, room for brand/campaign overlay",
        "surface_details": "realistic ground shadow and reflection, motion blur on wheels if driving shot, brake caliper detail visible",
        "props": "location context: road markings, dramatic sky, architectural elements — nothing that competes with the vehicle",
        "negative": "no floating vehicle, no incorrect wheel count, no distorted proportions, no toy-car appearance, no flat shadowless lighting",
    },
    "food": {
        "label": "Food / Beverage Photography",
        "subject_description": "hero dish or beverage with accurate textures, natural imperfections, steam or condensation where appropriate, freshness cues",
        "material": "realistic food textures: crispy, moist, flaky, creamy — appropriate to the specific dish, natural color accuracy, no plastic-looking surfaces",
        "lighting": "directional warm key light from side or rear creating appetizing highlights and shadows, soft fill to maintain shadow detail, backlight for translucent liquids to glow",
        "camera": "45-degree angle for most dishes, overhead (flat-lay) for salads and bowls, close-up macro for texture-forward shots, 50-85mm lens equivalent",
        "environment": "styled surface: marble, weathered wood, linen, slate — appropriate to cuisine style and brand positioning",
        "composition": "hero subject sharp with supporting props softly out of focus, props telling the story (ingredients, utensils, napkins) never competing",
        "surface_details": "steam rising from hot dishes, condensation on cold beverages, sauce drips and imperfections that signal freshness",
        "props": "complementary ingredients, rustic or premium props matching brand tone — never cluttered, never distracting",
        "negative": "no plastic-looking surfaces, no flat shadowless lighting, no incorrect food colors, no inaccurate textures, no cluttered composition",
    },
    "fashion": {
        "label": "Fashion / Apparel",
        "subject_description": "garment or accessory clearly visible with accurate fabric drape, texture, and color, styled presentation",
        "material": "realistic fabric behavior: silk sheen, denim texture, leather grain, knit patterns — accurate to specific garment type",
        "lighting": "editorial: large soft key light from 45 degrees, subtle fill, optional rim light for separation, fashion-magazine quality illumination",
        "camera": "full-length, three-quarter, or detail close-up, 50-85mm lens equivalent, eye-level or slight low angle for full-length",
        "environment": "clean studio seamless or contextual location matching brand aesthetic (urban, minimal interior, nature)",
        "composition": "garment or accessory as clear hero, model or mannequin secondary to the product, strong clean background",
        "surface_details": "fabric texture clearly visible, stitch detail where relevant, no wrinkles unless intentional styling",
        "props": "minimal styling props: clean accessories, shoes, bags that complement the hero garment",
        "negative": "no cluttered background, no competing elements, no blown-out white backgrounds, no flat lighting",
    },
    "watch_jewelry": {
        "label": "Watch / Jewelry / Luxury Object",
        "subject_description": "precision-crafted timepiece or jewelry with accurate dial detail, case material, bracelet links or stone settings visible",
        "material": "polished or brushed metal with directional highlight streaks, crystal or sapphire glass with controlled reflections, leather or metal strap with texture detail",
        "lighting": "controlled directional: single strong key light creating dramatic highlights on metal surfaces, minimal fill to maintain rich shadows, no blown-out metal surfaces",
        "camera": "45-degree tilt, macro-capable close-up for dial detail, 100mm macro equivalent, shallow depth of field",
        "environment": "clean dark or neutral studio: slate surface, dark acrylic, or branded surface, minimal reflective context",
        "composition": "timepiece occupying 50-70% of frame with generous negative space, dial facing camera, strap or bracelet creating diagonal leading line",
        "surface_details": "crisp reflection of watch in surface below, no distracting highlights, fingerprint-free surfaces",
        "props": "optional: branded leather pouch, watch roll, premium boxes — only if supporting brand story",
        "negative": "no distorted dial, no floating watch, no cluttered background, no flat lighting washing out metal details",
    },
    "technology": {
        "label": "Consumer Technology / Electronics",
        "subject_description": "device with screen active or product in clean hero pose, accurate hardware proportions, visible port and button details",
        "material": "matte aluminum or glass back with controlled environment reflections, screen glow where appropriate, port and speaker grille details",
        "lighting": "clean studio: soft overhead or slightly directional key light, minimal fill for clean shadow definition, no bright hotspots on screen glass",
        "camera": "slightly above eye-level for devices (to show screen), three-quarter perspective for products, 50mm lens equivalent",
        "environment": "clean white or dark studio seamless, or minimal lifestyle desk context",
        "composition": "device as clear hero, screen content visible and legible, accessories optional at edge of frame",
        "surface_details": "subtle surface shadow anchoring the device, clean reflection if on dark surface",
        "props": "optional: USB cable, accessories, minimal desk objects — never distracting",
        "negative": "no distorted screen, no incorrect hardware details, no cluttered background, no toy-like appearance",
    },
    "architecture": {
        "label": "Architecture / Interior / Space",
        "subject_description": "building facade, interior space, or architectural detail with accurate proportions and structural legibility",
        "material": "accurate surface materials: glass curtain wall reflections, concrete texture, stone cladding, wood paneling — described precisely",
        "lighting": "golden hour exterior for dramatic shadows and warm facade light, or controlled interior lighting showing artificial light sources interacting with surfaces",
        "camera": "wide angle 24mm-35mm equivalent for full building or interior shots, tilt-corrected perspective, eye-level or slight elevation",
        "environment": "contextual: surrounding streetscape, sky, landscaping for exteriors; furniture and occupancy context for interiors",
        "composition": "strong geometric leading lines, building or space as clear hero, foreground element for depth, dramatic sky if exterior",
        "surface_details": "accurate shadow and light interaction with facade, human scale reference if helpful, no lens distortion artifacts",
        "props": "human figures for scale where appropriate, strategic lighting fixtures for interiors",
        "negative": "no distorted proportions, no impossible geometry, no flat grey skies unless intentional, no toy-like scale",
    },
    "portrait": {
        "label": "Portrait / Person / Editorial",
        "subject_description": "person clearly visible with natural expression, accurate anatomy, appropriate styling for context",
        "material": "realistic skin texture with accurate subsurface scattering (warm, living appearance), fabric drape accurate to clothing type",
        "lighting": "Rembrandt or butterfly editorial lighting: directional key light with controlled shadow side, subtle rim light for separation, catchlights in eyes",
        "camera": "85mm portrait lens equivalent, f/1.8-f/2.8 shallow depth of field, eye-level or slight low angle for empowerment, eyes always in sharpest focus plane",
        "environment": "clean studio, contextual lifestyle location, or editorial environment appropriate to brief",
        "composition": "subject positioned at golden ratio, eyes at upper third, generous negative space for copy if advertising",
        "surface_details": "natural skin imperfections preserved (no plastic skin), hair detail preserved, clothing texture visible",
        "props": "props relevant to occupation, lifestyle, or campaign story — never random",
        "negative": "no plastic AI skin, no extra fingers, no distorted anatomy, no floating limbs, no dead eyes, no uncanny valley",
    },
    "skincare_cosmetics": {
        "label": "Skincare / Cosmetics / Beauty",
        "subject_description": "product packaging clearly visible with accurate label, cap or applicator detail, product texture if applicable",
        "material": "glass or plastic packaging with accurate material behavior, cream or liquid texture if swatch shown, metallic or matte cap detail",
        "lighting": "soft diffused three-point studio lighting: clean highlights on packaging, no blown-out surfaces, subtle warm or cool cast matching brand tone",
        "camera": "slightly elevated angle, 50-85mm lens, shallow depth of field to isolate product",
        "environment": "clean marble, white seamless, or soft linen surface; botanicals or ingredients as supporting context if natural brand",
        "composition": "product clearly legible, label facing camera, ingredient swatch or texture spread soft in foreground",
        "surface_details": "soft shadow anchoring product, subtle packaging reflection on marble surface",
        "props": "optional: flowers, raw ingredients, soft fabric — only if complementing brand story, never cluttering",
        "negative": "no illegible label, no cluttered background, no harsh shadows obscuring product, no flat lighting",
    },
    "beverage": {
        "label": "Beverage / Drink",
        "subject_description": "glass, bottle, or can with accurate fill level, liquid color and clarity, condensation or frost where appropriate",
        "material": "glass with accurate refraction and transparency, liquid with correct color depth and clarity, ice with realistic crystal facets and melting detail",
        "lighting": "side or rear backlight to illuminate liquid and create internal glow, strong directional key light for condensation highlights, soft fill",
        "camera": "eye-level to slightly above, 50mm lens equivalent, medium close-up showing full vessel with pouring or splash detail if dynamic",
        "environment": "bar surface, cocktail napkin, branded coaster, premium venue context, or clean studio",
        "composition": "vessel as strong vertical hero, copy space beside or above, pouring element creating dynamic diagonal if applicable",
        "surface_details": "realistic condensation droplets, ice reflections, liquid splash detail for dynamic shots",
        "props": "garnish, ice, ingredient slice, branded glass — always supporting the product story",
        "negative": "no empty-looking glass, no dull liquid, no flat opaque appearance for glass vessels, no toy-like condensation",
    },
    "lifestyle": {
        "label": "Lifestyle / Aspirational / Contextual",
        "subject_description": "product or person in natural use context, genuine moment, authentic environment",
        "material": "environment materials accurate to setting: wood, fabric, concrete, greenery — photographically rendered",
        "lighting": "natural light: golden hour window light, dappled outdoor light, or soft interior ambient — authentic and non-studio",
        "camera": "24-50mm lens equivalent, environmental framing showing context, candid or semi-directed",
        "environment": "home, outdoor, coffee shop, travel — specific and believable, not generic or staged-looking",
        "composition": "product or subject in natural position within environment, rule of thirds, negative space for captions",
        "surface_details": "authentic environmental textures, natural imperfections, lived-in feel",
        "props": "authentic lifestyle objects that belong in the scene — not placed randomly for visual noise",
        "negative": "no overly staged appearance, no props that don't belong, no uncanny clean environments, no flat indoor lighting",
    },
}

# ── Material Intelligence ─────────────────────────────────────────────────────
# Describes how each material VISUALLY BEHAVES — the physics of light on surface.
MATERIAL_INTELLIGENCE = {
    "glass": "thick optical glass with internal light refraction, realistic caustic light patterns, controlled specular highlights, subtle internal color shifts from liquid or environment",
    "frosted_glass": "translucent frosted surface diffusing light softly, no sharp reflections, soft glow from internal light source, matte finish with subtle texture",
    "crystal": "multi-faceted crystal structure with prismatic light dispersion, sharp internal reflections, rainbow caustic patterns, brilliant sparkle at facet edges",
    "chrome": "mirror-polished chrome with perfect environment reflections, sharp highlight streaks following surface curves, maximum contrast between lit and shadow areas",
    "brushed_metal": "parallel directional grain texture in polished metal, soft elongated highlight streaks following grain direction, lower contrast than mirror chrome",
    "gold": "warm amber-gold metallic sheen, soft directional highlights, rich shadow areas maintaining warmth, no over-bright blown-out surfaces",
    "silver": "cool platinum-silver sheen, clean directional highlights, neutral shadow tones, subtle cool reflection from environment",
    "marble": "natural stone with organic veining in contrasting tones, semi-translucent surface depth, cool polish catching ambient light softly, veins flowing naturally",
    "leather": "natural grain texture with organic variation, subtle sheen on raised grain, matte depth in recessed areas, stitching detail at seams, natural color variation",
    "matte_plastic": "soft diffuse surface with no specular reflections, uniform color throughout, subtle ambient occlusion at edges and recesses",
    "glossy_plastic": "bright specular highlight following light direction, uniform color, clean edge reflection, modern tech product appearance",
    "ceramic": "smooth glazed surface with soft broad highlight, subtle surface variation where glaze pools, warm interior look if pottery",
    "wood": "visible grain pattern with directional fiber texture, subtle sheen on finished surfaces, warm tonal variation, knot details where natural",
    "fabric": "woven or knitted texture with micro-fiber detail, soft diffuse surface with slight sheen at weave peaks, drape following gravity naturally",
    "water": "liquid surface with real-time ripple caustics, partial transparency, environment reflection on surface, blue-green depth tones",
    "ice": "crystalline internal structure, blue-white opacity, facet edges catching light as bright sparkle, melting surface sheen",
    "acrylic": "optically clear acrylic with slight blue-green edge color, trapped air bubbles visible optionally, clean surface reflection",
    "concrete": "rough aggregate texture with tonal variation, slightly porous surface absorbing light rather than reflecting, grey-beige tonal range",
}

# ── Platform Composition Profiles ─────────────────────────────────────────────
PLATFORM_COMPOSITION_PROFILES = {
    "instagram_feed_square": {
        "ratio": "1:1",
        "resolution": (1080, 1080),
        "composition": "strong centered or rule-of-thirds subject placement, bold visual hierarchy readable as a small thumbnail, safe margins of at least 10% on all sides",
        "copy_space": "upper third or lower third cleared for text overlay if advertising",
        "focal_priority": "immediate visual impact within first second of viewing, scroll-stopping color or contrast",
    },
    "instagram_feed_portrait": {
        "ratio": "4:5",
        "resolution": (1080, 1350),
        "composition": "tall vertical composition with hero subject in upper two-thirds, strong focal point, safe margins on sides",
        "copy_space": "bottom fifth available for caption-safe text if needed",
        "focal_priority": "portrait-optimized subject placement, more real estate than square — use it for full product or lifestyle context",
    },
    "instagram_story": {
        "ratio": "9:16",
        "resolution": (1080, 1920),
        "composition": "full vertical canvas, hero subject centered in the safe middle zone (between 15% and 80% from top), strong colors visible on mobile",
        "copy_space": "top 15% and bottom 20% reserved as safe zones for Instagram UI elements (time, reply bar)",
        "focal_priority": "full-bleed visual impact, works at arm's length on mobile screen",
    },
    "pinterest": {
        "ratio": "2:3",
        "resolution": (1000, 1500),
        "composition": "tall vertical composition, clear visual subject in upper half, optional text overlay in lower quarter, save-worthy aesthetic readable as small pin",
        "copy_space": "lower third for title or description overlay if needed",
        "focal_priority": "aspirational, beautiful, or useful-looking at thumbnail scale",
    },
    "linkedin": {
        "ratio": "1.91:1",
        "resolution": (1200, 627),
        "composition": "wide horizontal, professional subject clearly left or center, generous negative space for headline or data on right",
        "copy_space": "right 40% of frame if subject is left-aligned",
        "focal_priority": "professional credibility, clear business context, not visually overwhelming",
    },
    "twitter": {
        "ratio": "16:9",
        "resolution": (1200, 675),
        "composition": "wide horizontal, strong center subject or split composition, works cropped to square in feed preview",
        "copy_space": "lower third for headline if advertising",
        "focal_priority": "immediate readability at small screen size",
    },
    "website_hero": {
        "ratio": "16:9",
        "resolution": (1920, 1080),
        "composition": "wide horizontal panoramic, subject positioned left or right of center, opposite side cleared for headline and CTA text overlay",
        "copy_space": "40-50% of frame opposite the hero subject must be usable for text without legibility conflict",
        "focal_priority": "cinematic quality, brand-defining visual, works behind text",
    },
    "website_square": {
        "ratio": "1:1",
        "resolution": (1080, 1080),
        "composition": "clean square format, strong centered subject, works as card or grid element",
        "copy_space": "lower quarter for caption or product name",
        "focal_priority": "clear product showcase or illustration",
    },
    "product_listing": {
        "ratio": "1:1",
        "resolution": (1080, 1080),
        "composition": "product centered, white or very light clean background, full product visible with no cropping, product occupying 70-80% of frame",
        "copy_space": "clean borders, no text overlay",
        "focal_priority": "accurate product representation, zero visual distraction",
    },
}

# ── Lighting Presets ──────────────────────────────────────────────────────────
LIGHTING_PRESETS = {
    "luxury_studio": "controlled three-point studio lighting: soft large-area key light at 45 degrees, gentle warm fill from opposite side, crisp rim light separating subject from background, no harsh shadows",
    "product_studio": "clean commercial three-point lighting: overhead softbox key, fill card opposite, backlight rim, white seamless background illuminated separately to pure white",
    "dramatic_directional": "single strong directional key light from 45 degrees creating bold shadow geometry, minimal fill preserving shadow depth, rim light for subject separation",
    "golden_hour": "warm amber-golden natural light from low side angle casting long shadows, warm color temperature 3200-4000K, atmospheric haze, long directional shadows",
    "cinematic": "high-contrast directional lighting with deep rich shadows, teal-orange color grading, anamorphic light quality, atmospheric depth",
    "editorial_fashion": "large soft diffused key light from above or side, clean shadow transition, commercial fashion magazine quality, neutral to slightly warm color temperature",
    "automotive_studio": "large soft light sources from both sides creating clean body panel reads, strong rim light defining roofline silhouette, floor reflection below vehicle",
    "automotive_location": "dramatic natural or golden hour light raking across body panels, environmental reflection in paint, moody sky, wet road for reflections",
    "food_directional": "warm directional side light creating appetizing highlights and texture-revealing shadows, slight backlight for translucent liquids, warm 4000-4500K",
    "food_natural": "soft window light or overcast natural diffuse, warm tones, no hard shadows, natural daylight quality",
    "beverage_backlit": "backlight illuminating liquid from behind creating internal glow and color depth, front soft fill for labels and condensation detail",
    "portrait_rembrandt": "classic Rembrandt setup: key light at 45 degrees creating triangular highlight on shadow cheek, gentle fill, optional rim for separation",
    "night_neon": "dark environment with neon light sources casting colored shadows, practical light sources visible in frame, atmospheric fog or haze",
    "high_key": "predominantly bright image, minimal shadows, airy and clean, fashion or beauty editorial appropriate",
    "low_key": "predominantly dark image, selective illumination, deep shadows, dramatic and moody",
    "volumetric": "visible light rays in atmospheric environment, god rays through fog or dust, adds depth and environmental drama",
    "chiaroscuro": "extreme contrast between light and dark areas, Renaissance painting quality, used for dramatic product or portrait work",
    "flat_editorial": "even, diffuse front lighting, minimal shadows, fashion editorial or product flat-lay appropriate",
}

# ── Camera Profiles ───────────────────────────────────────────────────────────
CAMERA_PROFILES = {
    "product_hero": "50mm lens equivalent, slightly below eye-level to create upward-looking perspective, f/2.8 shallow depth, subject sharp, background soft",
    "automotive_low": "24-35mm lens at ground level (door-handle height or lower), three-quarter front or rear view, slight upward tilt for heroic scale",
    "portrait_85": "85mm f/1.4-f/1.8, eye-level or very slightly below, eyes in sharpest focus plane, ears soft, background fully separated",
    "food_45": "45-degree overhead angle, 50mm equivalent, close-medium distance showing full plate and styling context",
    "food_overhead": "directly overhead flat-lay, 35mm equivalent, evenly lit from front",
    "macro_detail": "100mm macro equivalent, extreme close-up for surface texture, material detail, or jewelry detail",
    "architectural_wide": "24mm ultra-wide, tilt-corrected (no converging verticals), eye-level or elevated, full structure in frame",
    "lifestyle_environmental": "24-35mm lens, environmental framing showing full context, subject occupying 30-50% of frame",
    "cinematic_anamorphic": "anamorphic widescreen framing (2.39:1 crop suggestion), 35-50mm equivalent, oval bokeh characteristic of anamorphic",
    "editorial_medium": "50mm standard lens, medium shot framing, clean editorial perspective with no distortion",
    "instagram_portrait": "50-85mm, vertical 4:5 or 9:16 framing, strong subject in upper portion, compositionally aware of vertical crop",
    "jewelry_macro": "100mm macro, tabletop studio angle (30-45 degrees), extreme sharpness on focal detail, background fully separated",
}

# ── Client Language Translation ───────────────────────────────────────────────
# Maps informal client directives to concrete, measurable visual decisions.
# These are DECISIONS, not decorative words.
CLIENT_LANGUAGE_DECISIONS = {
    "make it expensive": {
        "material_upgrade": "switch to premium material descriptions: fine grain leather, thick optical glass, mirror-polished chrome, brushed titanium",
        "lighting_upgrade": "use luxury_studio lighting preset — controlled, no blown-out surfaces, deep shadows",
        "composition_upgrade": "increase negative space to 40%+ of frame, remove all visual clutter, single hero subject",
        "color_upgrade": "restrained palette: maximum 2-3 colors, rich deep tones with one metallic accent",
        "prompt_addition": "luxury advertising campaign, medium format photography quality, meticulous product styling, intentional minimalism",
    },
    "make it pop": {
        "lighting_upgrade": "increase subject-background contrast: add rim light, strengthen key light, deepen background",
        "color_upgrade": "increase color saturation of hero subject, darken background by two stops",
        "composition_upgrade": "tighten framing to increase subject scale in frame, strengthen focal point isolation",
        "prompt_addition": "dramatic rim lighting, high contrast subject separation, bold focal point, vibrant hero color against deep background",
    },
    "looks flat": {
        "lighting_upgrade": "switch to dramatic_directional preset — single strong key light, deep shadows, visible depth",
        "material_upgrade": "add surface texture details, specular highlights on appropriate materials, shadow depth",
        "composition_upgrade": "add foreground element for depth layering, use lens compression to stack background behind subject",
        "prompt_addition": "strong depth of field separation, directional lighting creating shadow geometry, layered foreground and background, three-dimensional composition",
    },
    "more premium": {
        "material_upgrade": "upgrade all surface descriptions to premium material behavior — glass, chrome, marble, fine leather",
        "composition_upgrade": "subtract one element from the composition — empty space is premium",
        "lighting_upgrade": "soften lighting — premium visuals use controlled restraint, not aggressive contrast",
        "prompt_addition": "restrained luxury, intentional minimalism, premium material texture, sophisticated art direction",
    },
    "less ai": {
        "lighting_upgrade": "use natural or location-appropriate lighting instead of generic studio preset",
        "material_upgrade": "add micro-imperfections: subtle fingerprint smudge on glass, slight grain on metal, natural fabric wrinkle",
        "composition_upgrade": "off-center composition, slight asymmetry, candid or semi-candid framing",
        "prompt_addition": "photographic realism, natural micro-imperfections, authentic material behavior, non-symmetrical composition, film photography quality",
    },
    "instagram ready": {
        "composition_upgrade": "use instagram_feed_portrait platform profile — 4:5 ratio, bold focal hierarchy, scroll-stopping composition",
        "lighting_upgrade": "strong contrast, clear focal point visible at thumbnail scale",
        "prompt_addition": "optimized for Instagram 4:5 feed, bold scroll-stopping composition, high visual impact at small screen scale, strong color contrast",
    },
    "make it cleaner": {
        "composition_upgrade": "remove all non-essential elements, expand negative space, single clear focal point",
        "lighting_upgrade": "switch to flat_editorial or high_key for airy clean feel",
        "prompt_addition": "minimal composition, generous negative space, single subject, clean background, no visual clutter, strong hierarchy",
    },
    "more eye catching": {
        "lighting_upgrade": "dramatic_directional or night_neon — strong contrast visible at distance",
        "color_upgrade": "introduce bold accent color, increase hero subject contrast against background",
        "composition_upgrade": "increase subject scale, create undeniable single focal point, eliminate peripheral distractions",
        "prompt_addition": "undeniable focal point, maximum visual impact, bold color contrast, dynamic composition, immediate attention capture",
    },
}

# ── Subject-to-Category Matcher ───────────────────────────────────────────────
CATEGORY_KEYWORDS = {
    "perfume": ["perfume", "fragrance", "cologne", "scent", "parfum", "eau de toilette", "bottle of", "luxury bottle"],
    "automotive": ["car", "vehicle", "automobile", "ferrari", "lamborghini", "porsche", "bmw", "mercedes", "audi", "bentley", "rolls", "supercar", "hypercar", "suv", "truck", "bike", "motorcycle", "automotive"],
    "food": ["food", "dish", "meal", "plate", "burger", "pizza", "sushi", "pasta", "salad", "steak", "dessert", "cake", "bread", "restaurant", "cuisine", "recipe", "cooking"],
    "fashion": ["fashion", "clothing", "apparel", "outfit", "dress", "shirt", "jacket", "shoes", "sneakers", "bag", "handbag", "garment", "collection", "streetwear", "wardrobe"],
    "watch_jewelry": ["watch", "timepiece", "rolex", "omega", "jewelry", "ring", "necklace", "bracelet", "diamond", "gem", "jewel", "sapphire", "gold ring", "luxury watch"],
    "technology": ["phone", "laptop", "computer", "device", "gadget", "iphone", "ipad", "macbook", "headphones", "earbuds", "speaker", "camera", "smartwatch", "tablet", "screen", "tech product"],
    "architecture": ["building", "architecture", "interior", "room", "house", "office", "space", "facade", "exterior", "interior design", "floor plan"],
    "portrait": ["person", "man", "woman", "model", "portrait", "face", "people", "human", "ceo", "executive", "athlete", "celebrity", "character"],
    "skincare_cosmetics": ["skincare", "moisturizer", "serum", "cream", "lipstick", "makeup", "cosmetic", "beauty product", "foundation", "sunscreen", "lotion", "cleanser"],
    "beverage": ["drink", "beverage", "cocktail", "coffee", "tea", "juice", "water", "soda", "beer", "wine", "whiskey", "smoothie", "latte", "espresso", "can", "bottle of"],
    "lifestyle": ["lifestyle", "home", "living", "wellness", "yoga", "travel", "outdoor", "nature", "morning routine", "workspace", "flat lay"],
}


def detect_product_category(prompt: str) -> str:
    """Identifies the product category from the prompt text."""
    pl = prompt.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in pl for kw in keywords):
            return category
    return "lifestyle"  # sensible default


def detect_platform(prompt: str, specs: dict) -> str:
    """Identifies the target platform from prompt and specs."""
    pl = prompt.lower()
    platform_spec = specs.get("platform_spec", {})
    task_type = specs.get("task_type", "")

    if "story" in pl or "9:16" in pl or "reel" in pl:
        return "instagram_story"
    if "instagram" in pl or task_type == "instagram":
        if "4:5" in pl or "portrait" in pl:
            return "instagram_feed_portrait"
        return "instagram_feed_square"
    if "pinterest" in pl or task_type == "pinterest":
        return "pinterest"
    if "linkedin" in pl or task_type == "linkedin":
        return "linkedin"
    if "twitter" in pl or task_type == "twitter":
        return "twitter"
    if "website" in pl or "web" in pl or "hero" in pl or "banner" in pl:
        return "website_hero"
    if "product" in pl and ("listing" in pl or "shop" in pl or "store" in pl or "ecommerce" in pl):
        return "product_listing"

    # Fall back to platform_spec from skill router
    platform_label = platform_spec.get("label", "").lower()
    if "instagram" in platform_label:
        return "instagram_feed_square"
    if "pinterest" in platform_label:
        return "pinterest"
    if "linkedin" in platform_label:
        return "linkedin"

    return "instagram_feed_square"  # sensible default


def detect_marketing_objective(prompt: str) -> str:
    """Identifies the campaign/marketing objective from the prompt."""
    pl = prompt.lower()
    if any(k in pl for k in ["launch", "new", "introducing", "unveil", "debut"]):
        return "product_launch"
    if any(k in pl for k in ["sale", "discount", "offer", "promo", "deal", "50% off", "% off"]):
        return "promotional"
    if any(k in pl for k in ["lifestyle", "inspire", "aspirational", "mood", "feel", "living"]):
        return "lifestyle_brand"
    if any(k in pl for k in ["ad", "advertisement", "campaign", "commercial", "marketing"]):
        return "advertising_campaign"
    if any(k in pl for k in ["showcase", "detail", "show", "product shot", "product photo"]):
        return "product_showcase"
    if any(k in pl for k in ["hero", "brand", "identity", "statement", "flagship"]):
        return "brand_statement"
    return "product_showcase"  # sensible default


def detect_client_language(prompt: str) -> list:
    """Returns list of client language directives found in the prompt."""
    pl = prompt.lower()
    detected = []
    for directive in CLIENT_LANGUAGE_DECISIONS:
        if directive in pl:
            detected.append(directive)
    # Also check approximate matches
    approximations = {
        "expensive": "make it expensive",
        "pop": "make it pop",
        "flat": "looks flat",
        "ai-looking": "less ai",
        "ai look": "less ai",
        "looks ai": "less ai",
        "instagram": "instagram ready",
        "cleaner": "make it cleaner",
        "eye-catching": "more eye catching",
        "eye catching": "more eye catching",
        "more premium": "more premium",
    }
    for keyword, directive in approximations.items():
        if keyword in pl and directive not in detected:
            detected.append(directive)
    return detected


def select_lighting(category: str, prompt: str, style: str) -> str:
    """Selects the correct lighting preset for the category and context."""
    pl = prompt.lower()

    # Explicit overrides from prompt
    if "golden hour" in pl or "sunset" in pl or "sunrise" in pl:
        return LIGHTING_PRESETS["golden_hour"]
    if "night" in pl or "neon" in pl or "dark" in pl:
        return LIGHTING_PRESETS["night_neon"]
    if "cinematic" in pl or style == "cinematic":
        return LIGHTING_PRESETS["cinematic"]
    if "volumetric" in pl or "god ray" in pl:
        return LIGHTING_PRESETS["volumetric"]
    if "natural light" in pl or "window light" in pl:
        return LIGHTING_PRESETS["food_natural"]
    if "high key" in pl or "bright" in pl and "background" in pl:
        return LIGHTING_PRESETS["high_key"]
    if "chiaroscuro" in pl or "rembrandt" in pl:
        return LIGHTING_PRESETS["chiaroscuro"]

    # Category-based defaults — the decisions a photographer would make
    category_lighting = {
        "perfume": LIGHTING_PRESETS["luxury_studio"],
        "automotive": LIGHTING_PRESETS["automotive_studio"],
        "food": LIGHTING_PRESETS["food_directional"],
        "fashion": LIGHTING_PRESETS["editorial_fashion"],
        "watch_jewelry": LIGHTING_PRESETS["dramatic_directional"],
        "technology": LIGHTING_PRESETS["product_studio"],
        "architecture": LIGHTING_PRESETS["golden_hour"],
        "portrait": LIGHTING_PRESETS["portrait_rembrandt"],
        "skincare_cosmetics": LIGHTING_PRESETS["luxury_studio"],
        "beverage": LIGHTING_PRESETS["beverage_backlit"],
        "lifestyle": LIGHTING_PRESETS["food_natural"],
    }
    return category_lighting.get(category, LIGHTING_PRESETS["luxury_studio"])


def select_camera(category: str, prompt: str) -> str:
    """Selects the correct camera angle and lens for the category and context."""
    pl = prompt.lower()

    # Explicit overrides
    if "overhead" in pl or "flat lay" in pl or "flat-lay" in pl or "bird" in pl:
        return CAMERA_PROFILES["food_overhead"]
    if "macro" in pl or "close up" in pl or "close-up" in pl or "detail" in pl:
        return CAMERA_PROFILES["macro_detail"]
    if "wide" in pl or "landscape" in pl:
        return CAMERA_PROFILES["lifestyle_environmental"]
    if "cinematic" in pl or "anamorphic" in pl:
        return CAMERA_PROFILES["cinematic_anamorphic"]
    if "portrait" in pl and "camera" not in pl:
        return CAMERA_PROFILES["portrait_85"]

    # Category-based defaults
    category_camera = {
        "perfume": CAMERA_PROFILES["product_hero"],
        "automotive": CAMERA_PROFILES["automotive_low"],
        "food": CAMERA_PROFILES["food_45"],
        "fashion": CAMERA_PROFILES["editorial_medium"],
        "watch_jewelry": CAMERA_PROFILES["jewelry_macro"],
        "technology": CAMERA_PROFILES["product_hero"],
        "architecture": CAMERA_PROFILES["architectural_wide"],
        "portrait": CAMERA_PROFILES["portrait_85"],
        "skincare_cosmetics": CAMERA_PROFILES["product_hero"],
        "beverage": CAMERA_PROFILES["product_hero"],
        "lifestyle": CAMERA_PROFILES["lifestyle_environmental"],
    }
    return category_camera.get(category, CAMERA_PROFILES["product_hero"])


def select_materials(category: str, prompt: str) -> str:
    """Returns material description appropriate for the category and any explicit materials in the prompt."""
    pl = prompt.lower()
    profile = PRODUCT_CATEGORY_PROFILES.get(category, {})
    base_material = profile.get("material", "")

    # Check for explicit material overrides in prompt
    explicit_materials = []
    for mat_key, mat_desc in MATERIAL_INTELLIGENCE.items():
        if mat_key.replace("_", " ") in pl:
            explicit_materials.append(mat_desc)

    if explicit_materials:
        return "; ".join(explicit_materials[:2])  # max 2 explicit materials
    return base_material


def interpret_creative_brief(prompt: str, specs: dict, web_context: str = "") -> dict:
    """
    The core Creative Director function.
    Interprets the user prompt as a professional creative brief.
    Returns a structured dict of creative decisions.
    """
    category = detect_product_category(prompt)
    platform = detect_platform(prompt, specs)
    objective = detect_marketing_objective(prompt)
    client_directives = detect_client_language(prompt)
    style = specs.get("style", "realistic")

    profile = PRODUCT_CATEGORY_PROFILES.get(category, PRODUCT_CATEGORY_PROFILES["lifestyle"])
    platform_profile = PLATFORM_COMPOSITION_PROFILES.get(platform, PLATFORM_COMPOSITION_PROFILES["instagram_feed_square"])

    # Select appropriate technical components
    lighting = select_lighting(category, prompt, style)
    camera = select_camera(category, prompt)
    material = select_materials(category, prompt)

    # Apply client language decisions
    client_prompt_additions = []
    for directive in client_directives:
        if directive in CLIENT_LANGUAGE_DECISIONS:
            decisions = CLIENT_LANGUAGE_DECISIONS[directive]
            if "prompt_addition" in decisions:
                client_prompt_additions.append(decisions["prompt_addition"])
            if "lighting_upgrade" in decisions:
                lighting_key = decisions["lighting_upgrade"].split()[1] if "switch to" in decisions["lighting_upgrade"] else None
                if lighting_key and lighting_key in LIGHTING_PRESETS:
                    lighting = LIGHTING_PRESETS[lighting_key]

    # Extract brand colors from web search context
    brand_colors = []
    if web_context:
        hex_colors = re.findall(r'#[0-9a-fA-F]{6}', web_context)
        brand_colors = hex_colors[:3]

    # Extract user-specified colors from prompt
    color_words = specs.get("colors", [])

    return {
        "category": category,
        "platform": platform,
        "objective": objective,
        "subject_description": profile.get("subject_description", ""),
        "material": material or profile.get("material", ""),
        "lighting": lighting,
        "camera": camera,
        "environment": profile.get("environment", ""),
        "composition": profile.get("composition", "") + " | " + platform_profile.get("composition", ""),
        "surface_details": profile.get("surface_details", ""),
        "props": profile.get("props", ""),
        "negative": profile.get("negative", "no watermark, no text overlay, no low quality"),
        "platform_composition": platform_profile.get("composition", ""),
        "copy_space": platform_profile.get("copy_space", ""),
        "focal_priority": platform_profile.get("focal_priority", ""),
        "brand_colors": brand_colors,
        "user_colors": color_words,
        "client_prompt_additions": client_prompt_additions,
        "style": style,
    }


def build_production_prompt(prompt: str, brief: dict) -> dict:
    """
    Assembles a structured, ordered production prompt from the creative brief.
    Returns {"positive": str, "negative": str} — keeping negatives SEPARATE
    so they can be passed as proper negative_prompt parameter to the image API.

    Prompt architecture order matches how Flux/SDXL weigh instruction priority:
    SUBJECT → MATERIAL → LIGHTING → CAMERA → ENVIRONMENT → COMPOSITION → MOOD → TECHNICAL
    """
    # Clean the raw user prompt of tag artifacts
    clean_user = re.sub(r'\[[A-Z\s]+\]', '', prompt).strip()
    clean_user = re.sub(r'\s+', ' ', clean_user)

    parts = []

    # 1. SUBJECT — the most important element, always first
    subject_desc = brief.get("subject_description", "")
    if subject_desc:
        parts.append(f"{clean_user}, {subject_desc}")
    else:
        parts.append(clean_user)

    # 2. MATERIAL — how the surfaces look and behave
    material = brief.get("material", "")
    if material:
        parts.append(material)

    # 3. LIGHTING — the most impactful single decision
    lighting = brief.get("lighting", "")
    if lighting:
        parts.append(lighting)

    # 4. CAMERA — angle, lens, depth
    camera = brief.get("camera", "")
    if camera:
        parts.append(camera)

    # 5. ENVIRONMENT — background and setting
    environment = brief.get("environment", "")
    if environment:
        parts.append(environment)

    # 6. COMPOSITION — layout direction
    composition = brief.get("platform_composition", "") or brief.get("composition", "")
    if composition:
        # Keep only platform composition to avoid over-specification
        parts.append(composition.split("|")[0].strip())

    # 7. SURFACE DETAILS — ground contact, reflections, props
    surface = brief.get("surface_details", "")
    if surface:
        parts.append(surface)

    # 8. MOOD — atmospheric quality
    style = brief.get("style", "realistic")
    mood_map = {
        "cinematic": "cinematic atmospheric quality, rich deep shadows, color-graded warmth",
        "luxury": "luxurious and aspirational, restrained elegance, premium visual weight",
        "minimal": "intentionally minimalist, breathing room, pure and precise",
        "editorial": "editorial magazine quality, styled and art-directed",
        "animated": "high quality digital illustration, vibrant and expressive",
        "3d": "photorealistic 3D CGI, ray-traced, physically accurate rendering",
    }
    mood = mood_map.get(style, "photorealistic, authentic, professionally lit")
    parts.append(mood)

    # 9. BRAND COLORS — injected from web research
    brand_colors = brief.get("brand_colors", [])
    if brand_colors:
        parts.append(f"incorporating brand colors {', '.join(brand_colors)}")

    # 10. USER COLORS — explicitly requested colors
    user_colors = brief.get("user_colors", [])
    if user_colors and not brand_colors:
        parts.append(f"color palette: {', '.join(user_colors)}")

    # 11. COPY SPACE — platform-specific safe zone instruction
    copy_space = brief.get("copy_space", "")
    if copy_space:
        parts.append(copy_space)

    # 12. CLIENT LANGUAGE ADDITIONS — interpreted from informal directives
    for addition in brief.get("client_prompt_additions", []):
        parts.append(addition)

    # 13. TECHNICAL QUALITY — positive only, no "don't" language
    technical = "sharp focus on hero subject, correct perspective, accurate proportions, no visual artifacts, high detail rendering"
    parts.append(technical)

    # Assemble positive prompt
    # NOTE: Do NOT strip parentheses {} () — Flux uses these for emphasis weighting
    positive = ", ".join(p.strip() for p in parts if p.strip())
    # Only clean truly problematic chars (newlines, tabs, double spaces)
    positive = re.sub(r'[\n\t]', ' ', positive)
    positive = re.sub(r' {2,}', ' ', positive).strip()
    # Truncate at 900 chars but cut at a comma boundary to avoid mid-instruction truncation
    if len(positive) > 900:
        positive = positive[:900].rsplit(',', 1)[0].strip()

    # Assemble negative prompt — SEPARATE, not appended to positive
    base_negatives = [
        "watermark", "text overlay", "logo burned in", "low quality", "blurry",
        "distorted", "artifacts", "noise", "oversaturated", "plastic appearance",
        "cartoon", "amateur", "overexposed highlights", "flat lighting",
        "incorrect anatomy where applicable", "extra fingers", "clipping",
    ]
    category_negatives_raw = brief.get("negative", "")
    category_negatives = [n.strip() for n in category_negatives_raw.replace("no ", "").split(",") if n.strip()] if category_negatives_raw else []
    all_negatives = list(set(base_negatives + category_negatives))
    negative = ", ".join(all_negatives[:20])

    return {"positive": positive, "negative": negative}


def evaluate_prompt_quality(brief: dict, positive_prompt: str) -> dict:
    """
    Scores the assembled prompt against 5 creative criteria.
    Returns {"score": int (0-5), "pass": bool, "issues": list, "suggestions": list}
    Used as pre-generation QA gate.
    """
    score = 0
    issues = []
    suggestions = []

    # 1. Subject specificity — is the hero clearly described?
    subject = brief.get("subject_description", "")
    if len(subject) > 30 and subject in positive_prompt:
        score += 1
    else:
        issues.append("Subject description is too generic or missing from prompt")
        suggestions.append("Add specific physical description of the hero subject")

    # 2. Lighting quality — is lighting appropriate and specific?
    lighting = brief.get("lighting", "")
    if len(lighting) > 40:
        score += 1
    else:
        issues.append("Lighting is under-specified")
        suggestions.append("Apply a specific lighting preset from LIGHTING_PRESETS")

    # 3. Camera specification — is there a clear angle and lens?
    camera = brief.get("camera", "")
    if len(camera) > 20:
        score += 1
    else:
        issues.append("Camera angle and lens not specified")
        suggestions.append("Add explicit camera angle, lens, and depth of field")

    # 4. Environment — is the background/context described?
    environment = brief.get("environment", "")
    if len(environment) > 20:
        score += 1
    else:
        issues.append("Background environment is unspecified")
        suggestions.append("Add environment description: studio, location, surface")

    # 5. Prompt length — is there enough creative direction without over-specifying?
    word_count = len(positive_prompt.split())
    if 40 <= word_count <= 200:
        score += 1
    elif word_count < 20:
        issues.append("Prompt too short — insufficient creative direction")
        suggestions.append("Add more visual detail to the prompt")
    else:
        issues.append("Prompt may be over-specified")
        suggestions.append("Reduce redundant terms for cleaner model interpretation")

    return {
        "score": score,
        "pass": score >= 3,
        "issues": issues,
        "suggestions": suggestions,
    }


WORKFLOW_PRESETS = {
    "luxury_product_advertisement": {"category": "perfume", "lighting": "dramatic_studio", "loras": ["skinTexture_lora"]},
    "perfume_cosmetics": {"category": "skincare_cosmetics", "lighting": "soft_luxury", "loras": ["skinTexture_lora"]},
    "automotive_campaign": {"category": "automotive", "lighting": "cinematic", "loras": ["automotiveDetail_lora"]},
    "food_advertisement": {"category": "food", "lighting": "directional_warm", "loras": ["foodPhotography_v2"]},
    "fashion_campaign": {"category": "fashion", "lighting": "editorial", "loras": ["fashionEditorial_lora"]},
    "tech_product": {"category": "technology", "lighting": "clean_studio", "loras": ["productPhotography_v10"]},
    "ecommerce_product": {"category": "product_advertising", "lighting": "neutral_studio", "loras": ["productPhotography_v10"]},
    "instagram_post": {"category": "lifestyle", "lighting": "natural_light", "platform": "instagram_feed_square"},
    "instagram_story": {"category": "lifestyle", "lighting": "natural_light", "platform": "instagram_story"},
    "pinterest_creative": {"category": "fashion", "lighting": "editorial", "platform": "pinterest"},
    "website_hero": {"category": "architecture", "lighting": "cinematic", "platform": "website_hero"},
    "banner_advertisement": {"category": "product_advertising", "lighting": "clean_studio", "platform": "twitter"},
    "editorial_photography": {"category": "portrait", "lighting": "rembrandt", "loras": ["fashionEditorial_lora"]}
}

def analyze_creative_parameters(prompt: str) -> dict:
    """Extracts the 17-point agency parameters from a raw prompt."""
    return {
        "campaign_purpose": "advertising",
        "platform": "general",
        "audience": "premium",
        "product": prompt,
        "composition": "hero_centered",
        "camera_angle": "eye_level",
        "lens_look": "50mm_prime",
        "lighting": "studio",
        "environment": "clean",
        "materials": "photorealistic",
        "color_palette": "brand_aligned",
        "brand_identity": "premium",
        "negative_space": "generous",
        "visual_hierarchy": "product_first",
        "required_objects": [prompt],
        "exact_object_count": 1,
        "required_dimensions": (1080, 1080),
        "text_handling": "post_generation"
    }

def get_version() -> str:
    return "luminary_creative_director v2.0 — 17-parameter creative direction, 13 SD1.5 presets, automated routing"
