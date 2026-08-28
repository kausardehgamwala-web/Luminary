"""
luminary_client_translator.py
=============================
Translates casual/ambiguous client terminology (e.g., "make it pop", "clean", "premium", "like Apple", "like Nike")
into precise, actionable design constraints and prompt instructions.
"""

import re

CLIENT_DICTIONARY = {
    "premium": {
        "visual_directives": [
            "Use luxury editorial photography styling",
            "Incorporate a restrained color palette (max 3 colors, high contrast)",
            "Ensure generous negative space and whitespace (minimum 35% empty space)",
            "Specify high-end materials: brushed metal, matte carbon fiber, crystal glass, polished chrome, fine grain leather",
            "Use clean, sophisticated typography (serif for heritage, geometric sans-serif for modern)"
        ],
        "image_modifiers": "shot on Hasselblad H6D, luxury advertising campaign, high fashion editorial, premium surface finishes"
    },
    "make it pop": {
        "visual_directives": [
            "Boost local contrast dramatically",
            "Strengthen the visual focal point through high contrast illumination",
            "Use volumetric backlighting to separate the subject from the background",
            "Incorporate vibrant accent highlights while keeping base tones rich and deep"
        ],
        "image_modifiers": "dramatic backlighting, volumetric light rays, rim lighting, vibrant color accents, high dynamic range (HDR)"
    },
    "clean": {
        "visual_directives": [
            "Keep layout strictly minimalist",
            "Eliminate all non-essential visual elements, decorative patterns, and clutter",
            "Ensure precise alignment (use a clean grid system)",
            "Ensure light, neutral backgrounds (solid white, light grey, or soft studio gradients)"
        ],
        "image_modifiers": "minimalist studio photography, clean white background, soft shadow, clinical precision focus"
    },
    "modern": {
        "visual_directives": [
            "Use contemporary asymmetrical layouts",
            "Apply clean, light-weight sans-serif typography (e.g. Helvetica Neue, Futura)",
            "Incorporate modern color palettes (cool greys, vibrant electric blue/orange accents)",
            "Include sleek architectural glass, clean lines, and geometric compositions"
        ],
        "image_modifiers": "sleek contemporary design, geometric composition, modern architectural styling, high-tech aesthetics"
    },
    "professional": {
        "visual_directives": [
            "Maintain strict grid alignment across all elements",
            "Use authoritative, business-appropriate colors (navy blue, slate gray, subtle warm white)",
            "Ensure clear, logical visual hierarchy (heading size vs body text size)",
            "Avoid garish gradients, excessive icons, or amateur clipart"
        ],
        "image_modifiers": "corporate commercial shoot, clean corporate lighting, sharp focus, professional art direction"
    },
    "classy": {
        "visual_directives": [
            "Use classical typography (Didot, Garamond, Bodoni)",
            "Incorporate rich, understated colors (burgundy, forest green, navy, brass)",
            "Focus on texture and craftsmanship details rather than bold shapes"
        ],
        "image_modifiers": "elegant classic styling, soft Rembrandt lighting, heritage aesthetic, refined material textures"
    },
    "sleek": {
        "visual_directives": [
            "Incorporate aerodynamic curves and polished surfaces",
            "Use highly reflective textures with sharp highlight glints",
            "Ensure ultra-thin bezels or borders",
            "Apply a clean metallic or dark carbon palette"
        ],
        "image_modifiers": "aerodynamic form, polished metallic surfaces, razor sharp highlights, minimalist high-end rendering"
    },
    "bold": {
        "visual_directives": [
            "Use high-contrast block layouts",
            "Apply heavy, high-weight typography (e.g. Impact, Arial Black, heavy sans)",
            "Incorporate saturated, high-energy primary colors",
            "Create a single massive, undeniable focal point"
        ],
        "image_modifiers": "striking high contrast composition, bold primary color palette, massive visual scale, powerful presence"
    },
    "futuristic": {
        "visual_directives": [
            "Use cybernetic or neon accent lighting (cyan, magenta, amber)",
            "Incorporate holographic displays, HUD interfaces, or glowing circuits",
            "Apply sleek synthetic materials (carbon composite, glossy polymers)",
            "Create a high-tech sci-fi or cyberpunk atmosphere"
        ],
        "image_modifiers": "cyberpunk style, neon luminescence, futuristic technology elements, holographic highlights, dark sci-fi mood"
    },
    "natural": {
        "visual_directives": [
            "Use organic, earthy color palettes (greens, beige, brown, soft sky blue)",
            "Avoid synthetic shapes or hard mechanical lines",
            "Incorporate raw, untreated materials (wood, stone, linen, clay)",
            "Use soft, diffused natural daylight"
        ],
        "image_modifiers": "shot in natural daylight, soft diffused sun, organic textures, earthy tones, raw natural materials"
    },
    "aesthetic": {
        "visual_directives": [
            "Ensure strict balance and harmony in composition",
            "Use trending, cohesive palettes (e.g. pastel gradients, muted earth tones)",
            "Incorporate rule-of-thirds framing with elegant negative space"
        ],
        "image_modifiers": "aesthetic photography, clean pastel tones, rule of thirds, beautiful color harmony, soft focus background"
    },
    "expensive-looking": {
        "visual_directives": [
            "Use luxury materials, fine details, and custom typography",
            "Ensure absolute visual restraint (less is always more)",
            "Incorporate soft, expensive studio lighting (shallow depth of field)"
        ],
        "image_modifiers": "high-end luxury advertising, shot on medium format camera, flawless studio lighting, gold and platinum accents"
    },
    "luxurious": {
        "visual_directives": [
            "Use an extremely elegant, high-end editorial aesthetic",
            "Restrain colors to rich, deep tones (e.g., deep burgundy, emerald, navy) accented with gold or platinum",
            "Emphasize premium textures (brushed metal, polished stone, velvet, fine leather)",
            "Focus on clean spacing and elite typography to establish hierarchy"
        ],
        "image_modifiers": "luxurious editorial shoot, high-end luxury advertising, premium textures, sophisticated soft focus, medium format photography"
    },
    "like apple": {
        "visual_directives": [
            "Emphasize radical simplicity, clean layouts, and generous white space (minimum 40% empty space)",
            "Put all focus directly on the product or central message, eliminating secondary clutter",
            "Use neutral backgrounds (matte white, light gray, or dark space gray)",
            "Utilize elegant, clean typography with high contrast (sans-serif, precise weight variance)"
        ],
        "image_modifiers": "Apple-style industrial design product photography, clean white background, soft studio lighting, soft shadows, macro detail"
    },
    "like nike": {
        "visual_directives": [
            "Create high-energy, dynamic, and dramatic athletic compositions",
            "Incorporate motion, high contrast, and deep shadows",
            "Apply bold, heavy, impact-driven typography",
            "Establish an emotional, heroic, and inspiring narrative focus"
        ],
        "image_modifiers": "Nike advertising style, motion blur, dramatic sports lighting, high contrast, energetic action shot, raw emotion"
    },
    "like a top agency": {
        "visual_directives": [
            "Use standard marketing agency grids, professional typography systems, and high contrast",
            "Establish a clear target audience visual hierarchy",
            "Incorporate strategic frameworks (e.g., SWOT, target persona values) in document layouts",
            "Maintain pixel-perfect alignment and consistent spacing throughout"
        ],
        "image_modifiers": "professional agency portfolio style, commercial grade art direction, pristine studio setup, award-winning creative direction"
    },
    "eye-catching": {
        "visual_directives": [
            "Establish a massive, undeniable visual focal point using high contrast",
            "Use vibrant primary accents or complementary color theory",
            "Apply clear visual hierarchy to guide the viewer's eye from the focal point to the CTA",
            "Avoid flat, low-contrast, or overly busy compositions"
        ],
        "image_modifiers": "striking visual hook, high contrast, vivid color accents, dynamic composition, dramatic studio lighting"
    },
    "minimal": {
        "visual_directives": [
            "Strip away all decorative elements, borders, and unnecessary background textures",
            "Ensure ample breathing room and whitespace around key content",
            "Use a single, clean font family with maximum 2 weights",
            "Keep color palette strictly limited to 2-3 clean, harmonious shades"
        ],
        "image_modifiers": "minimalist aesthetic, soft diffuse lighting, ample negative space, clean lines, solid color background"
    },
    "cinematic": {
        "visual_directives": [
            "Use anamorphic widescreen composition and dramatic lighting",
            "Incorporate atmospheric elements (e.g. light fog, haze, lens flare)",
            "Use a color grading scheme with rich shadows (teal & orange style)",
            "Apply deep focus on the subject with cinematic background separation"
        ],
        "image_modifiers": "cinematic movie scene, 35mm film look, anamorphic lens flare, dramatic color grading, volumetric lighting"
    },
    "realistic": {
        "visual_directives": [
            "Avoid stylized rendering, cartoons, CGI looks, or digital paintings",
            "Use accurate real-world textures, lighting reflections, and physically plausible shadows",
            "Ensure proportions and perspective match photographic reality",
            "Provide realistic depth of field and authentic lens parameters"
        ],
        "image_modifiers": "authentic photo, raw unedited capture, realistic lighting, natural reflections, photorealistic textures"
    },
    "pinterest style": {
        "visual_directives": [
            "Optimise for a vertical 2:3 layout containing clear, highly legible text overlays",
            "Incorporate inspiring, aspirational lifestyle imagery",
            "Use warm, high-energy colors (terracotta, warm gold, pastel blush)",
            "Ensure the creative serves as a clear solution, tutorial, or lookbook pin"
        ],
        "image_modifiers": "Pinterest lifestyle photography, warm tones, high dynamic range, soft styling, inspirational lookbook style"
    },
    "instagram worthy": {
        "visual_directives": [
            "Optimise for a square 1:1 or portrait 4:5 frame",
            "Apply trendy color grading (pastel pinks, muted sages, warm sands, deep teals)",
            "Ensure a strong aesthetic balance, polished details, and high visual energy",
            "Place focus on key lifestyle details or highly desirable consumer goods"
        ],
        "image_modifiers": "Instagram feed aesthetic, trendy color grading, golden hour light, polished product styling, high-end lifestyle photography"
    },
    "tiktok ready": {
        "visual_directives": [
            "Use a vertical 9:16 layout optimized for mobile screens",
            "Place the primary subject in the central safe zone to avoid UI overlay crop",
            "Incorporate high contrast, vibrant lighting, and high action framing",
            "Establish a raw, authentic, user-generated feel rather than overly corporate styling"
        ],
        "image_modifiers": "vertical 9:16 video frame, raw smartphone look, vibrant ring light illumination, high energy close-up"
    },
    "make it street": {
        "visual_directives": [
            "Incorporate urban background textures (concrete, asphalt, neon, graffiti)",
            "Apply bold, heavy, grit-infused typography",
            "Use high-contrast directional lighting like streetlights or raw sunlight",
            "Establish a raw, candid, streetwear-editorial atmosphere"
        ],
        "image_modifiers": "candid street photography, gritty urban background, neon light reflections, harsh street shadows, raw candid composition"
    },
    "agency-grade": {
        "visual_directives": [
            "Adhere strictly to professional creative layouts, alignment, and spacing rules",
            "Use curated typographic systems (clean geometric headings + readable body)",
            "Integrate brand assets or cohesive marketing-campaign styles",
            "Maintain professional contrast levels and a polished execution standard"
        ],
        "image_modifiers": "award-winning advertising creative, agency portfolio quality, clean studio setup, elite art direction"
    },
    "magazine quality": {
        "visual_directives": [
            "Use luxury editorial grid layouts with elegant margin spacing",
            "Utilize classic high-end serif typography for titles",
            "Incorporate professional-studio or location-fashion photography rules",
            "Deliver a highly polished, clean finish suitable for print"
        ],
        "image_modifiers": "editorial magazine spread, high fashion location photography, soft styling, flawless lighting, premium print aesthetic"
    },
    "make it expensive": {
        "visual_directives": [
            "Apply luxury editorial photography styling",
            "Incorporate a restrained color palette (maximum 3 colors, high contrast)",
            "Specify high-end materials: brushed metal, crystal glass, fine leather"
        ],
        "image_modifiers": "luxury advertising campaign, shot on medium format camera, premium surface finishes"
    },
    "looks flat": {
        "visual_directives": [
            "Boost local contrast and spatial shadow density",
            "Use volumetric or dramatic side lighting to emphasize form",
            "Incorporate layered foreground and background elements for depth"
        ],
        "image_modifiers": "dramatic directional lighting, volumetric light rays, deep shadows, strong depth of field"
    },
    "less ai": {
        "visual_directives": [
            "Avoid perfect symmetry and digital cleanliness",
            "Introduce natural imperfections, subtle texture grains, and realistic lighting refractions",
            "Use organic locations and natural daylight configurations"
        ],
        "image_modifiers": "photographic realism, natural micro-imperfections, authentic light behavior, raw unedited capture"
    },
    "instagram ready": {
        "visual_directives": [
            "Optimize framing for portrait 4:5 or square 1:1 safe-margins",
            "Apply high-contrast scroll-stopping colors and clear center focus",
            "Leave clear copy space or breathing room for captions"
        ],
        "image_modifiers": "optimized for Instagram 4:5 feed, bold scroll-stopping composition, vibrant contrast"
    },
    "make it cleaner": {
        "visual_directives": [
            "Strip away all secondary visual clutter and background noise",
            "Maximize negative space (at least 40% blank area)",
            "Use simple grid alignment and high-contrast typography hierarchy"
        ],
        "image_modifiers": "minimalist studio photography, clean background, ample breathing room"
    },
    "more eye catching": {
        "visual_directives": [
            "Create a single massive, undeniable visual hook",
            "Use energetic lighting highlights and color-complementary accents",
            "Deepen surrounding shadow tones to separate the hero subject"
        ],
        "image_modifiers": "striking visual hook, maximum contrast, high energy key lighting"
    },
    "more premium": {
        "visual_directives": [
            "Adhere to strict visual restraint and elegant spacing",
            "Specify premium textures: polished stone, brushed titanium, optical glass",
            "Use soft, controlled, low-key lighting setups"
        ],
        "image_modifiers": "premium luxury brand look, flawless art direction, minimal high-end render"
    }
}


def translate_client_terms(prompt: str) -> dict:
    """
    Scans the prompt for client slang terms and extracts direct design guidelines
    and prompt modifiers to enrich the system context.
    """
    pl = prompt.lower()
    directives = []
    modifiers = []

    for term, mapping in CLIENT_DICTIONARY.items():
        # Match word boundaries for the client terms
        if re.search(r'\b' + re.escape(term) + r'\b', pl):
            directives.extend(mapping["visual_directives"])
            modifiers.append(mapping["image_modifiers"])

    # Fallback to general best practices if no slang terms match
    if not directives:
        directives.append("Ensure clear visual hierarchy, balanced whitespace, and alignment.")

    return {
        "directives": directives,
        "modifiers": ", ".join(modifiers)
    }


def get_client_translation_summary() -> str:
    """Returns a module identifier."""
    return "luminary_client_translator v2.0 — client slang term dictionary and translator (30+ terms)"
