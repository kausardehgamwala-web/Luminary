"""
luminary_design_systems.py  —  Luminary V13 Design System Library
==================================================================
20 premium website design systems | 20 animation presets
7 page transitions | 10 visual effects | 5 typography systems | 9 color palettes
Design compatibility engine | Prompt-to-system mapper
Pure Python stdlib — no external dependencies.
"""

# ── MOTION TOKENS ──────────────────────────────────────────────────────────
MOTION_TOKENS = {
    "duration": {
        "instant": "0.1s", "fast": "0.2s", "normal": "0.35s",
        "medium": "0.5s", "slow": "0.7s", "cinematic": "1.0s"
    },
    "easing": {
        "linear":      "linear",
        "ease":        "ease",
        "ease_out":    "cubic-bezier(0.16, 1, 0.3, 1)",
        "ease_in_out": "cubic-bezier(0.4, 0, 0.2, 1)",
        "spring":      "cubic-bezier(0.34, 1.56, 0.64, 1)",
        "expo_out":    "cubic-bezier(0.19, 1, 0.22, 1)",
        "expo_in":     "cubic-bezier(0.86, 0, 0.07, 1)",
        "premium":     "cubic-bezier(0.25, 1, 0.5, 1)",
        "cinematic":   "cubic-bezier(0.77, 0, 0.175, 1)"
    },
    "stagger_delay": {"tight": "0.04s", "normal": "0.08s", "loose": "0.14s"}
}

# ── DESIGN TOKENS ──────────────────────────────────────────────────────────
DESIGN_TOKENS = {
    "spacing": {
        "xs": "4px", "sm": "8px", "md": "16px", "lg": "24px",
        "xl": "32px", "xxl": "48px", "xxxl": "64px", "section": "90px"
    },
    "border_radius": {
        "none": "0px", "sm": "4px", "md": "8px", "lg": "12px",
        "xl": "18px", "xxl": "28px", "xxxl": "40px", "circle": "50%"
    },
    "shadows": {
        "flat":         "none",
        "sm":           "0 2px 8px rgba(0,0,0,0.06)",
        "md":           "0 8px 24px rgba(0,0,0,0.12)",
        "lg":           "0 16px 40px rgba(0,0,0,0.18)",
        "xl":           "0 24px 64px rgba(0,0,0,0.25)",
        "luxury_glow":  "0 12px 30px rgba(197,168,128,0.18)",
        "orange_glow":  "0 12px 30px rgba(255,85,0,0.22)",
        "tech_glow":    "0 0 40px rgba(137,79,255,0.18)"
    },
    "container_widths": {
        "xs": "440px", "sm": "680px", "md": "960px",
        "lg": "1140px", "xl": "1360px", "full": "100%"
    },
    "breakpoints": {
        "mobile": "480px", "tablet": "768px",
        "laptop": "1024px", "desktop": "1280px"
    }
}

# ── 20 ANIMATION PRESETS ───────────────────────────────────────────────────
ANIMATION_LIBRARY = {
    "fade_up": {
        "label": "Fade Up", "type": "entrance",
        "duration": "0.5s", "easing": "cubic-bezier(0.25, 1, 0.5, 1)",
        "css_from": "opacity:0; transform:translateY(24px)",
        "css_to":   "opacity:1; transform:translateY(0)"
    },
    "fade_down": {
        "label": "Fade Down", "type": "entrance",
        "duration": "0.5s", "easing": "cubic-bezier(0.25, 1, 0.5, 1)",
        "css_from": "opacity:0; transform:translateY(-24px)",
        "css_to":   "opacity:1; transform:translateY(0)"
    },
    "fade_in": {
        "label": "Fade In", "type": "entrance",
        "duration": "0.35s", "easing": "cubic-bezier(0.16, 1, 0.3, 1)",
        "css_from": "opacity:0", "css_to": "opacity:1"
    },
    "scale_in": {
        "label": "Scale In (Spring)", "type": "entrance",
        "duration": "0.5s", "easing": "cubic-bezier(0.34, 1.56, 0.64, 1)",
        "css_from": "opacity:0; transform:scale(0.94)",
        "css_to":   "opacity:1; transform:scale(1)"
    },
    "scale_out": {
        "label": "Scale Out (From Large)", "type": "entrance",
        "duration": "0.5s", "easing": "cubic-bezier(0.4, 0, 0.2, 1)",
        "css_from": "opacity:0; transform:scale(1.06)",
        "css_to":   "opacity:1; transform:scale(1)"
    },
    "slide_in": {
        "label": "Slide In from Left", "type": "entrance",
        "duration": "0.7s", "easing": "cubic-bezier(0.19, 1, 0.22, 1)",
        "css_from": "opacity:0; transform:translateX(-32px)",
        "css_to":   "opacity:1; transform:translateX(0)"
    },
    "image_reveal": {
        "label": "Image Reveal (Bottom Up)", "type": "mask",
        "duration": "0.7s", "easing": "cubic-bezier(0.77, 0, 0.175, 1)",
        "css_from": "clip-path:inset(100% 0 0 0)",
        "css_to":   "clip-path:inset(0 0 0 0)"
    },
    "mask_reveal": {
        "label": "Mask Reveal (Left to Right)", "type": "mask",
        "duration": "1.0s", "easing": "cubic-bezier(0.86, 0, 0.07, 1)",
        "css_from": "clip-path:polygon(0 0,0 0,0 100%,0 100%)",
        "css_to":   "clip-path:polygon(0 0,100% 0,100% 100%,0 100%)"
    },
    "text_reveal": {
        "label": "Text Line Reveal", "type": "text",
        "duration": "0.7s", "easing": "cubic-bezier(0.19, 1, 0.22, 1)",
        "css_from": "transform:translateY(105%)",
        "css_to":   "transform:translateY(0)",
        "note":     "Wrap each line in overflow:hidden parent"
    },
    "staggered_text": {
        "label": "Staggered Word/Letter Reveal", "type": "stagger",
        "duration": "0.35s", "delay_factor": "0.04s",
        "easing": "cubic-bezier(0.16, 1, 0.3, 1)"
    },
    "staggered_cards": {
        "label": "Staggered Card Entrances", "type": "stagger",
        "duration": "0.5s", "delay_factor": "0.08s",
        "easing": "cubic-bezier(0.25, 1, 0.5, 1)",
        "css_from": "opacity:0; transform:translateY(16px)",
        "css_to":   "opacity:1; transform:translateY(0)"
    },
    "scroll_parallax": {
        "label": "Scroll Parallax", "type": "scroll",
        "factor": 0.15, "axis": "y",
        "note": "Background moves at 15% of scroll velocity"
    },
    "horizontal_scroll": {
        "label": "Horizontal Scroll Section", "type": "scroll_trigger",
        "direction": "horizontal", "trigger": "viewport_center",
        "note": "Pin parent; translate child strip horizontally on scroll"
    },
    "sticky_transform": {
        "label": "Sticky Scale on Scroll", "type": "scroll_trigger",
        "css_from": "transform:scale(1); border-radius:0",
        "css_to":   "transform:scale(0.94); border-radius:24px",
        "trigger": "viewport_top"
    },
    "magnetic_button": {
        "label": "Magnetic Hover Button", "type": "interaction",
        "radius": "40px", "strength": 0.35,
        "note": "JS: track mouse proximity; offset element by delta * strength"
    },
    "cursor_interaction": {
        "label": "Custom Cursor + Blend Mode", "type": "interaction",
        "lag": "0.1s", "blend_mode": "difference",
        "size_default": "12px", "size_hover": "40px"
    },
    "hover_lift": {
        "label": "Card Hover Lift", "type": "hover",
        "duration": "0.2s", "easing": "cubic-bezier(0.16, 1, 0.3, 1)",
        "css_to": "transform:translateY(-6px); box-shadow:0 24px 48px rgba(0,0,0,0.22)"
    },
    "image_zoom": {
        "label": "Hover Image Zoom", "type": "hover",
        "duration": "0.5s", "easing": "cubic-bezier(0.4, 0, 0.2, 1)",
        "css_to": "transform:scale(1.06)",
        "note": "Apply to img inside overflow:hidden container"
    },
    "tilt_3d": {
        "label": "3D Perspective Tilt on Hover", "type": "interaction",
        "max_angle": "12deg", "perspective": "1000px",
        "note": "JS: track mouse in element; apply rotateX/rotateY via transform"
    },
    "smooth_page_transition": {
        "label": "Smooth Fullscreen Page Transition", "type": "transition",
        "duration": "1.0s", "easing": "cubic-bezier(0.77, 0, 0.175, 1)",
        "exit":  "opacity:1->0; transform:translateY(-8px)",
        "enter": "opacity:0->1; transform:translateY(8px)->translateY(0)"
    }
}

# ── PAGE TRANSITIONS ───────────────────────────────────────────────────────
TRANSITIONS = {
    "fade":             {"exit": "opacity:1->0", "entrance": "opacity:0->1", "duration": "0.35s"},
    "crossfade":        {"exit": "opacity:1->0", "entrance": "opacity:0->1", "duration": "0.7s", "overlap": True},
    "morph":            {"type": "shared_element", "duration": "0.7s", "easing": "cubic-bezier(0.4,0,0.2,1)"},
    "slide":            {"exit": "translateX(0)->translateX(-100%)", "entrance": "translateX(100%)->translateX(0)", "duration": "0.5s"},
    "clip_reveal":      {"type": "clip", "direction": "bottom_to_top", "css": "clip-path:inset(100% 0 0 0)->inset(0)", "duration": "0.7s"},
    "mask_transition":  {"type": "mask", "shape": "circle", "css": "clip-path:circle(0% at 50% 50%)->circle(150% at 50% 50%)", "duration": "1.0s"},
    "scale_transition": {"exit": "scale(1)->scale(0.94),opacity->0", "entrance": "scale(1.04)->scale(1),opacity->1", "duration": "0.7s"}
}

# ── VISUAL EFFECTS ─────────────────────────────────────────────────────────
EFFECT_LIBRARY = {
    "gradient_mesh":    {"css": "background:radial-gradient(at 15% 15%,#ff5500 0,transparent 50%),radial-gradient(at 85% 85%,#894fff 0,transparent 50%)", "perf": "high"},
    "glass":            {"css": "background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);backdrop-filter:blur(18px)", "perf": "medium"},
    "frosted_glass":    {"css": "background:rgba(10,9,13,0.7);border:1px solid rgba(255,255,255,0.05);backdrop-filter:blur(30px)", "perf": "medium"},
    "soft_glow":        {"css": "filter:drop-shadow(0 0 16px rgba(255,85,0,0.35))", "perf": "high"},
    "grain":            {"css": "::after pseudo SVG noise at 0.025 opacity, pointer-events:none", "perf": "very_high"},
    "technical_grid":   {"css": "background-image:linear-gradient(rgba(255,255,255,0.025) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,0.025) 1px,transparent 1px);background-size:24px 24px", "perf": "very_high"},
    "depth_blur":       {"css": "backdrop-filter:blur(10px);mask-image:linear-gradient(to bottom,black 60%,transparent 100%)", "perf": "medium"},
    "spotlight":        {"css": "radial-gradient(circle 120px at var(--mx) var(--my),rgba(255,255,255,0.06),transparent) — JS mousemove required", "perf": "high"},
    "aurora":           {"css": "background:linear-gradient(135deg,rgba(0,240,255,0.2),rgba(137,79,255,0.2),rgba(255,85,0,0.2));filter:blur(80px);animation:aurora 6s ease infinite", "perf": "medium"},
    "metallic_gradient":{"css": "background:linear-gradient(135deg,#f5f5f5 0%,#999 40%,#f5f5f5 60%,#888 100%);-webkit-background-clip:text", "perf": "very_high"}
}

# ── TYPOGRAPHY SYSTEMS ─────────────────────────────────────────────────────
TYPOGRAPHY_SYSTEMS = {
    "luxury": {
        "label": "Luxury & Fashion",
        "display": {"family": "'Playfair Display', serif",   "weight": "400", "letter_spacing": "-0.01em"},
        "heading": {"family": "'Playfair Display', serif",   "weight": "700", "letter_spacing": "-0.02em"},
        "body":    {"family": "'Outfit', sans-serif",         "weight": "300", "letter_spacing": "0.03em"},
        "caption": {"family": "'Outfit', sans-serif",         "weight": "400", "letter_spacing": "0.08em", "text_transform": "uppercase"},
        "google_fonts": "Playfair+Display:ital,wght@0,400;0,700;1,400&family=Outfit:wght@300;400"
    },
    "technology": {
        "label": "Technology & SaaS",
        "display": {"family": "'Outfit', sans-serif", "weight": "700", "letter_spacing": "-0.04em"},
        "heading": {"family": "'Outfit', sans-serif", "weight": "600", "letter_spacing": "-0.03em"},
        "body":    {"family": "'Outfit', sans-serif", "weight": "400", "letter_spacing": "0.01em"},
        "caption": {"family": "'Outfit', sans-serif", "weight": "400", "letter_spacing": "0.04em"},
        "google_fonts": "Outfit:wght@300;400;500;600;700"
    },
    "corporate": {
        "label": "Corporate & Finance",
        "display": {"family": "'Outfit', sans-serif", "weight": "700", "letter_spacing": "-0.025em"},
        "heading": {"family": "'Outfit', sans-serif", "weight": "600", "letter_spacing": "-0.02em"},
        "body":    {"family": "'Outfit', sans-serif", "weight": "400", "letter_spacing": "0.015em"},
        "caption": {"family": "'Outfit', sans-serif", "weight": "400", "letter_spacing": "0.05em"},
        "google_fonts": "Outfit:wght@400;500;600;700"
    },
    "editorial": {
        "label": "Editorial & Photography",
        "display": {"family": "'Lora', serif",        "weight": "500", "letter_spacing": "-0.02em"},
        "heading": {"family": "'Lora', serif",        "weight": "700", "letter_spacing": "-0.02em"},
        "body":    {"family": "'Lora', serif",        "weight": "400", "letter_spacing": "0.04em"},
        "caption": {"family": "'Outfit', sans-serif", "weight": "400", "letter_spacing": "0.06em", "text_transform": "uppercase"},
        "google_fonts": "Lora:ital,wght@0,400;0,500;0,700;1,400&family=Outfit:wght@400;500"
    },
    "futuristic": {
        "label": "Futuristic & Experimental",
        "display": {"family": "'Space Grotesk', sans-serif", "weight": "700", "letter_spacing": "-0.05em"},
        "heading": {"family": "'Space Grotesk', sans-serif", "weight": "600", "letter_spacing": "-0.04em"},
        "body":    {"family": "'Space Grotesk', sans-serif", "weight": "400", "letter_spacing": "0.02em"},
        "caption": {"family": "'Space Grotesk', sans-serif", "weight": "400", "letter_spacing": "0.08em"},
        "google_fonts": "Space+Grotesk:wght@300;400;600;700"
    }
}

# ── COLOR PALETTE SUITE ────────────────────────────────────────────────────
COLOR_SUITE = {
    "luminary_dark":   {"bg": "#08070b", "surface": "#111014", "text": "#faf8f5", "muted": "rgba(250,248,245,0.6)",  "primary": "#ff5500", "accent": "#894fff"},
    "luxury_noir":     {"bg": "#050406", "surface": "#0d0c0e", "text": "#f5f3f0", "muted": "rgba(245,243,240,0.55)", "primary": "#c5a880", "accent": "#e6d5c3"},
    "tech_indigo":     {"bg": "#060608", "surface": "#0f0f15", "text": "#f1f1f5", "muted": "rgba(241,241,245,0.55)", "primary": "#00f0ff", "accent": "#894fff"},
    "automotive_dark": {"bg": "#050505", "surface": "#0e0e0e", "text": "#ffffff",  "muted": "rgba(255,255,255,0.5)",  "primary": "#e60000", "accent": "#cccccc"},
    "cream_luxury":    {"bg": "#faf4ee", "surface": "#ffffff",  "text": "#2d241e", "muted": "rgba(45,36,30,0.55)",   "primary": "#c3a58e", "accent": "#e07a5f"},
    "editorial_white": {"bg": "#f9f8f6", "surface": "#ffffff",  "text": "#1a1618", "muted": "rgba(26,22,24,0.55)",   "primary": "#1a1618", "accent": "#ff5500"},
    "fintech_dark":    {"bg": "#040306", "surface": "#0c0a10", "text": "#f9f9fb", "muted": "rgba(249,249,251,0.5)",  "primary": "#00d17e", "accent": "#ff5500"},
    "medical_clean":   {"bg": "#ffffff",  "surface": "#f0f4f8", "text": "#102a43", "muted": "rgba(16,42,67,0.55)",   "primary": "#0044ff", "accent": "#00ffd0"},
    "experimental":    {"bg": "#000000",  "surface": "#111111", "text": "#ffffff",  "muted": "rgba(255,255,255,0.5)", "primary": "#ff007f", "accent": "#00f0ff"}
}

# ── 20 WEBSITE DESIGN SYSTEMS ──────────────────────────────────────────────
WEBSITE_DESIGN_SYSTEMS = {
    "ai_saas": {
        "title": "AI SaaS Platform", "industry": "Technology",
        "typography": TYPOGRAPHY_SYSTEMS["technology"], "color_system": COLOR_SUITE["tech_indigo"],
        "animation": ["staggered_cards", "fade_up", "text_reveal"], "transition": "morph",
        "effects": ["glass", "technical_grid", "aurora"], "graphics": ["isometric_grid"],
        "interaction_density": "medium",
        "avoid_effects": ["grain", "metallic_gradient"], "avoid_animation": ["tilt_3d"],
        "image_style": "UI screenshots in device frames, abstract 3D renders"
    },
    "ai_marketing_agency": {
        "title": "AI Marketing Agency", "industry": "Marketing",
        "typography": TYPOGRAPHY_SYSTEMS["technology"], "color_system": COLOR_SUITE["luminary_dark"],
        "animation": ["fade_up", "staggered_cards", "image_reveal"], "transition": "crossfade",
        "effects": ["gradient_mesh", "frosted_glass"], "graphics": ["gradient_blobs"],
        "interaction_density": "high",
        "avoid_effects": ["technical_grid"], "avoid_animation": [],
        "image_style": "Bold campaign photography, abstract motion"
    },
    "creative_agency": {
        "title": "Creative Agency Portfolio", "industry": "Design",
        "typography": TYPOGRAPHY_SYSTEMS["editorial"], "color_system": COLOR_SUITE["editorial_white"],
        "animation": ["magnetic_button", "cursor_interaction", "mask_reveal"], "transition": "scale_transition",
        "effects": [], "graphics": ["geometric_masks"],
        "interaction_density": "high",
        "avoid_effects": ["glass", "aurora"], "avoid_animation": ["fade_in"],
        "image_style": "Large editorial photography, high-contrast"
    },
    "premium_product": {
        "title": "Premium Product Showcase", "industry": "Consumer Goods",
        "typography": TYPOGRAPHY_SYSTEMS["luxury"], "color_system": COLOR_SUITE["luminary_dark"],
        "animation": ["image_zoom", "image_reveal", "scroll_parallax"], "transition": "clip_reveal",
        "effects": ["spotlight", "soft_glow"], "graphics": ["abstract_waves"],
        "interaction_density": "medium",
        "avoid_effects": ["technical_grid", "aurora"], "avoid_animation": ["tilt_3d", "magnetic_button"],
        "image_style": "Product still-life photography, close-up detail"
    },
    "luxury_brand": {
        "title": "Luxury Brand Campaign", "industry": "Luxury / Fashion",
        "typography": TYPOGRAPHY_SYSTEMS["luxury"], "color_system": COLOR_SUITE["luxury_noir"],
        "animation": ["image_reveal", "mask_reveal", "scroll_parallax"], "transition": "crossfade",
        "effects": ["soft_glow", "grain"], "graphics": ["geometric_masks"],
        "interaction_density": "low",
        "avoid_effects": ["technical_grid", "aurora", "glass"], "avoid_animation": ["magnetic_button", "staggered_cards"],
        "image_style": "Editorial campaign photography, cinematic"
    },
    "technology_startup": {
        "title": "Technology Startup Landing", "industry": "Startup",
        "typography": TYPOGRAPHY_SYSTEMS["technology"], "color_system": COLOR_SUITE["tech_indigo"],
        "animation": ["scroll_parallax", "staggered_cards", "fade_up"], "transition": "morph",
        "effects": ["technical_grid", "glass"], "graphics": ["technical_lines", "isometric_grid"],
        "interaction_density": "medium",
        "avoid_effects": ["grain", "metallic_gradient"], "avoid_animation": ["tilt_3d"],
        "image_style": "Dashboard screenshots, abstract renders, team photography"
    },
    "fintech": {
        "title": "Fintech & Financial Platform", "industry": "Finance",
        "typography": TYPOGRAPHY_SYSTEMS["corporate"], "color_system": COLOR_SUITE["fintech_dark"],
        "animation": ["staggered_cards", "fade_up"], "transition": "slide",
        "effects": ["glass"], "graphics": ["isometric_grid", "technical_lines"],
        "interaction_density": "low",
        "avoid_effects": ["grain", "aurora", "metallic_gradient"], "avoid_animation": ["cursor_interaction", "tilt_3d"],
        "image_style": "Data charts, product UI, abstract financial graphics"
    },
    "ecommerce": {
        "title": "Premium E-commerce Store", "industry": "E-commerce",
        "typography": TYPOGRAPHY_SYSTEMS["corporate"], "color_system": COLOR_SUITE["editorial_white"],
        "animation": ["hover_lift", "image_zoom", "fade_in"], "transition": "fade",
        "effects": [], "graphics": [],
        "interaction_density": "medium",
        "avoid_effects": ["gradient_mesh", "aurora"], "avoid_animation": ["cursor_interaction", "horizontal_scroll"],
        "image_style": "Clean product photography on white, lifestyle photography"
    },
    "portfolio": {
        "title": "Creative Designer Portfolio", "industry": "Personal Branding",
        "typography": TYPOGRAPHY_SYSTEMS["editorial"], "color_system": COLOR_SUITE["luminary_dark"],
        "animation": ["text_reveal", "mask_reveal", "smooth_page_transition"], "transition": "smooth_page_transition",
        "effects": ["frosted_glass"], "graphics": ["geometric_masks"],
        "interaction_density": "high",
        "avoid_effects": ["technical_grid"], "avoid_animation": ["scroll_parallax"],
        "image_style": "Project case study imagery, process documentation"
    },
    "architecture": {
        "title": "Architecture & Interior Design Studio", "industry": "Architecture",
        "typography": TYPOGRAPHY_SYSTEMS["luxury"],
        "color_system": {"bg": "#f5f5f5", "surface": "#ffffff", "text": "#111111", "muted": "rgba(17,17,17,0.5)", "primary": "#111111", "accent": "#e5e5e5"},
        "animation": ["mask_reveal", "image_reveal"], "transition": "clip_reveal",
        "effects": [], "graphics": ["technical_lines"],
        "interaction_density": "low",
        "avoid_effects": ["aurora", "gradient_mesh", "grain"], "avoid_animation": ["magnetic_button", "cursor_interaction"],
        "image_style": "Architectural photography, structural detail, large scale"
    },
    "automotive": {
        "title": "Automotive Experience Platform", "industry": "Automotive",
        "typography": TYPOGRAPHY_SYSTEMS["futuristic"], "color_system": COLOR_SUITE["automotive_dark"],
        "animation": ["image_zoom", "scroll_parallax", "sticky_transform"], "transition": "scale_transition",
        "effects": ["soft_glow", "spotlight", "metallic_gradient"], "graphics": ["isometric_grid"],
        "interaction_density": "medium",
        "avoid_effects": ["grain", "aurora"], "avoid_animation": ["fade_in"],
        "image_style": "High gloss automotive photography, speed blur, studio render"
    },
    "fashion": {
        "title": "High Fashion Brand Campaign", "industry": "Fashion",
        "typography": TYPOGRAPHY_SYSTEMS["editorial"],
        "color_system": {"bg": "#ffffff", "surface": "#fafafa", "text": "#000000", "muted": "rgba(0,0,0,0.45)", "primary": "#000000", "accent": "#ff5500"},
        "animation": ["image_reveal", "text_reveal", "mask_reveal"], "transition": "crossfade",
        "effects": ["grain"], "graphics": [],
        "interaction_density": "low",
        "avoid_effects": ["glass", "aurora", "technical_grid"], "avoid_animation": ["tilt_3d", "magnetic_button"],
        "image_style": "Editorial fashion photography, high-contrast, dramatic lighting"
    },
    "beauty": {
        "title": "Organic Beauty & Skincare", "industry": "Beauty",
        "typography": TYPOGRAPHY_SYSTEMS["luxury"], "color_system": COLOR_SUITE["cream_luxury"],
        "animation": ["fade_in", "fade_up", "hover_lift"], "transition": "crossfade",
        "effects": ["frosted_glass"], "graphics": ["abstract_waves"],
        "interaction_density": "low",
        "avoid_effects": ["technical_grid", "metallic_gradient"], "avoid_animation": ["cursor_interaction", "tilt_3d"],
        "image_style": "Soft lifestyle photography, skincare close-up, botanical"
    },
    "restaurant": {
        "title": "Artisanal Restaurant & Dining", "industry": "Food",
        "typography": TYPOGRAPHY_SYSTEMS["editorial"],
        "color_system": {"bg": "#120f0e", "surface": "#1d1917", "text": "#f6f3f0", "muted": "rgba(246,243,240,0.55)", "primary": "#e07a5f", "accent": "#f4f1de"},
        "animation": ["hover_lift", "image_reveal", "fade_up"], "transition": "fade",
        "effects": ["grain"], "graphics": [],
        "interaction_density": "low",
        "avoid_effects": ["technical_grid", "glass", "aurora"], "avoid_animation": ["cursor_interaction", "horizontal_scroll"],
        "image_style": "Editorial food photography, warm candlelight, dark moody tones"
    },
    "hospitality": {
        "title": "Bespoke Hospitality & Retreats", "industry": "Travel",
        "typography": TYPOGRAPHY_SYSTEMS["luxury"], "color_system": COLOR_SUITE["cream_luxury"],
        "animation": ["fade_up", "scroll_parallax"], "transition": "crossfade",
        "effects": ["grain"], "graphics": ["abstract_waves"],
        "interaction_density": "low",
        "avoid_effects": ["aurora", "technical_grid", "glass"], "avoid_animation": ["magnetic_button", "tilt_3d"],
        "image_style": "Wide landscape photography, property hero shots, warm natural light"
    },
    "education": {
        "title": "Modern Education & Training Hub", "industry": "Education",
        "typography": TYPOGRAPHY_SYSTEMS["corporate"],
        "color_system": {"bg": "#ffffff", "surface": "#f8f9fa", "text": "#212529", "muted": "rgba(33,37,41,0.55)", "primary": "#0056b3", "accent": "#ffc107"},
        "animation": ["fade_in", "staggered_cards"], "transition": "slide",
        "effects": [], "graphics": [],
        "interaction_density": "low",
        "avoid_effects": ["grain", "aurora", "gradient_mesh"], "avoid_animation": ["cursor_interaction", "tilt_3d"],
        "image_style": "Clear instructional photography, diverse learners, clean backgrounds"
    },
    "consulting": {
        "title": "Elite Consulting & Strategy Group", "industry": "Consulting",
        "typography": TYPOGRAPHY_SYSTEMS["corporate"],
        "color_system": {"bg": "#fcfcfd", "surface": "#ffffff", "text": "#1e293b", "muted": "rgba(30,41,59,0.5)", "primary": "#0f172a", "accent": "#3b82f6"},
        "animation": ["fade_up", "fade_in"], "transition": "slide",
        "effects": [], "graphics": ["technical_lines"],
        "interaction_density": "low",
        "avoid_effects": ["aurora", "grain", "gradient_mesh"], "avoid_animation": ["tilt_3d", "cursor_interaction", "magnetic_button"],
        "image_style": "Professional team photography, data visualization, boardroom"
    },
    "healthcare": {
        "title": "Advanced Healthcare & Research", "industry": "Healthcare",
        "typography": TYPOGRAPHY_SYSTEMS["corporate"], "color_system": COLOR_SUITE["medical_clean"],
        "animation": ["fade_in"], "transition": "fade",
        "effects": [], "graphics": [],
        "interaction_density": "minimal",
        "avoid_effects": ["grain", "aurora", "gradient_mesh", "glass"], "avoid_animation": ["cursor_interaction", "tilt_3d", "magnetic_button"],
        "image_style": "Medical photography, research labs, professional clean environments"
    },
    "real_estate": {
        "title": "Premium Real Estate Platform", "industry": "Real Estate",
        "typography": TYPOGRAPHY_SYSTEMS["luxury"],
        "color_system": {"bg": "#fcfbfc", "surface": "#ffffff", "text": "#1e1b1d", "muted": "rgba(30,27,29,0.5)", "primary": "#8d5b4c", "accent": "#eae6ea"},
        "animation": ["mask_reveal", "image_zoom", "fade_up"], "transition": "clip_reveal",
        "effects": [], "graphics": [],
        "interaction_density": "low",
        "avoid_effects": ["aurora", "technical_grid", "metallic_gradient"], "avoid_animation": ["tilt_3d", "cursor_interaction"],
        "image_style": "Architectural property photography, interior lifestyle, warm tones"
    },
    "creative_experimental": {
        "title": "Experimental Art Direction Space", "industry": "Art",
        "typography": TYPOGRAPHY_SYSTEMS["futuristic"], "color_system": COLOR_SUITE["experimental"],
        "animation": ["tilt_3d", "cursor_interaction", "magnetic_button", "smooth_page_transition"], "transition": "smooth_page_transition",
        "effects": ["gradient_mesh", "soft_glow"], "graphics": ["isometric_grid", "gradient_blobs"],
        "interaction_density": "extreme",
        "avoid_effects": ["grain"], "avoid_animation": ["fade_in"],
        "image_style": "Conceptual art direction, bold abstract photography, distortion"
    }
}

# ── DESIGN COMPATIBILITY ENGINE ────────────────────────────────────────────
BAD_COMBINATIONS = [
    {"combo": ("futuristic", "grain"),           "reason": "Futuristic tech conflicts with analog film grain."},
    {"combo": ("luxury", "technical_grid"),      "reason": "Technical grids destroy luxury editorial elegance."},
    {"combo": ("luxury", "aurora"),              "reason": "Neon aurora effects are incompatible with restrained luxury."},
    {"combo": ("editorial", "tilt_3d"),          "reason": "3D tilt is too gimmicky for refined editorial design."},
    {"combo": ("healthcare", "gradient_mesh"),   "reason": "Gradient meshes undermine clinical trust and clarity."},
    {"combo": ("education", "cursor_interaction"), "reason": "Custom cursors distract from readability in education."},
]

GOOD_COMBINATIONS = [
    {"industry": "luxury_brand",    "combo": ("grain", "soft_glow", "image_reveal"),        "reason": "Controlled grain + glow create premium cinematic depth."},
    {"industry": "ai_saas",         "combo": ("glass", "technical_grid", "staggered_cards"), "reason": "Glassmorphism + grids communicate technical precision."},
    {"industry": "automotive",      "combo": ("metallic_gradient", "spotlight", "image_zoom"),"reason": "Metallic text + spotlight create visceral campaign energy."},
    {"industry": "creative_agency", "combo": ("cursor_interaction", "mask_reveal"),          "reason": "Bold interactive motion communicates design confidence."},
]


# ── PUBLIC API ─────────────────────────────────────────────────────────────
def get_design_system_by_prompt(prompt: str) -> dict:
    """Maps a user prompt to the best matching design system."""
    pl = prompt.lower()
    mapping = [
        ("ai_saas",              ["saas", "platform", "software", "api", "ai tool", "dashboard", "subscription"]),
        ("ai_marketing_agency",  ["agency", "marketing", "campaign", "ads", "advertisement", "digital agency"]),
        ("creative_agency",      ["creative portfolio", "studio", "creative agency", "design firm", "art studio"]),
        ("premium_product",      ["product showcase", "perfume", "watch", "jewelry", "bottle", "product launch"]),
        ("luxury_brand",         ["luxury", "premium brand", "exclusive", "haute couture", "prestige"]),
        ("technology_startup",   ["startup", "seed round", "venture", "next gen tech", "mvp"]),
        ("fintech",              ["fintech", "finance", "banking", "trading", "crypto", "wealth", "investment"]),
        ("ecommerce",            ["ecommerce", "shop", "store", "buy", "cart", "product catalog", "marketplace"]),
        ("portfolio",            ["portfolio", "resume", "cv", "personal site", "biography", "my work"]),
        ("architecture",         ["architecture", "interior design", "architect", "space design"]),
        ("automotive",           ["car", "automotive", "ferrari", "lamborghini", "porsche", "tesla", "supercar", "vehicle"]),
        ("fashion",              ["fashion", "clothing", "streetwear", "apparel", "wardrobe", "garment"]),
        ("beauty",               ["beauty", "skincare", "skin", "cosmetics", "makeup", "serum", "moisturizer"]),
        ("restaurant",           ["restaurant", "food", "dining", "menu", "cafe", "culinary", "bistro"]),
        ("hospitality",          ["hospitality", "hotel", "retreat", "resort", "lodging", "spa", "villa"]),
        ("education",            ["education", "academy", "training", "school", "course", "learn", "university"]),
        ("consulting",           ["consulting", "strategy", "advisor", "advisory", "management consulting"]),
        ("healthcare",           ["healthcare", "medical", "hospital", "patient", "clinical", "doctor", "pharma"]),
        ("real_estate",          ["real estate", "property", "house", "villa", "apartment", "realty", "land"]),
        ("creative_experimental",["experimental", "art direction", "indie", "brutalist", "avant-garde"]),
    ]
    for sys_id, keywords in mapping:
        if any(k in pl for k in keywords):
            return WEBSITE_DESIGN_SYSTEMS.get(sys_id, WEBSITE_DESIGN_SYSTEMS["creative_agency"])
    return WEBSITE_DESIGN_SYSTEMS["creative_agency"]


def validate_design_combination(system_id: str, effects: list, animations: list) -> list:
    """Returns list of incompatibility warnings for a given system + effects + animations."""
    system = WEBSITE_DESIGN_SYSTEMS.get(system_id, {})
    warnings = []
    for e in effects:
        if e in system.get("avoid_effects", []):
            warnings.append(f"INCOMPATIBLE EFFECT '{e}' — conflicts with '{system_id}' design language.")
    for a in animations:
        if a in system.get("avoid_animation", []):
            warnings.append(f"INCOMPATIBLE ANIMATION '{a}' — conflicts with '{system_id}' design language.")
    return warnings


def get_module_summary() -> str:
    return (
        f"luminary_design_systems v1.0 | "
        f"{len(WEBSITE_DESIGN_SYSTEMS)} design systems | "
        f"{len(ANIMATION_LIBRARY)} animations | "
        f"{len(TRANSITIONS)} transitions | "
        f"{len(EFFECT_LIBRARY)} effects | "
        f"{len(TYPOGRAPHY_SYSTEMS)} typography systems | "
        f"{len(COLOR_SUITE)} color palettes"
    )


if __name__ == "__main__":
    print(get_module_summary())
    sys = get_design_system_by_prompt("luxury brand perfume campaign")
    print(f"Matched system: {sys['title']}")
    warnings = validate_design_combination("luxury_brand", ["technical_grid", "aurora"], ["staggered_cards"])
    for w in warnings:
        print(f"  ⚠ {w}")
