"""
sd15_model_registry.py
======================
Central registry of curated, highly optimized SD 1.5 checkpoints and LoRAs.
Specifically designed for 16GB RAM + Iris Xe Intel systems to avoid memory bloat.
Each category defines the ideal checkpoint and compatible LoRA combinations.
"""

SD15_MODELS = {
    "product_advertising": {
        "checkpoint": "SG161222/Realistic_Vision_V6.0_B1_noVAE",
        "checkpoint_type": "sd15",
        "description": "High fidelity photorealism for e-commerce and product shots.",
        "loras": [
            {"name": "productPhotography_v10", "weight": 0.6, "trigger": "product photography, studio setup"}
        ],
        "default_cfg": 6.5,
        "default_steps": 25,
        "negative_prompt": "cartoon, illustration, 3d render, poor lighting, floating objects, blurry, watermark"
    },
    "luxury_beauty": {
        "checkpoint": "SG161222/Realistic_Vision_V6.0_B1_noVAE",
        "checkpoint_type": "sd15",
        "description": "Clean, high-end skin textures and luxury aesthetics.",
        "loras": [
            {"name": "skinTexture_lora", "weight": 0.45, "trigger": "detailed skin texture, macro beauty"}
        ],
        "default_cfg": 5.0,
        "default_steps": 25,
        "negative_prompt": "plastic skin, oversaturated, harsh shadows, low quality, deformed anatomy"
    },
    "automotive": {
        "checkpoint": "Lykon/DreamShaper",
        "checkpoint_type": "sd15",
        "description": "Excellent hard-surface reflections and cinematic lighting.",
        "loras": [
            {"name": "automotiveDetail_lora", "weight": 0.7, "trigger": "automotive photography, car"}
        ],
        "default_cfg": 7.0,
        "default_steps": 30,
        "negative_prompt": "distorted wheels, asymmetrical, damaged paint, flat lighting, unrealistic reflections"
    },
    "food": {
        "checkpoint": "SG161222/Realistic_Vision_V6.0_B1_noVAE",
        "checkpoint_type": "sd15",
        "description": "Rich colors, accurate organic textures, realistic depth of field.",
        "loras": [
            {"name": "foodPhotography_v2", "weight": 0.55, "trigger": "appetizing food, macro culinary"}
        ],
        "default_cfg": 6.0,
        "default_steps": 20,
        "negative_prompt": "plastic food, weird colors, unappetizing, chaotic background"
    },
    "fashion": {
        "checkpoint": "emilianJR/epiCRealism",
        "checkpoint_type": "sd15",
        "description": "High end fashion editorial and accurate clothing drape.",
        "loras": [
            {"name": "fashionEditorial_lora", "weight": 0.65, "trigger": "editorial fashion photography, lookbook"}
        ],
        "default_cfg": 5.5,
        "default_steps": 25,
        "negative_prompt": "extra limbs, deformed anatomy, bad hands, flat lighting, ugly clothes"
    },
    "architecture": {
        "checkpoint": "Lykon/DreamShaper",
        "checkpoint_type": "sd15",
        "description": "Precise geometric structures, clean lines, arch-viz.",
        "loras": [
            {"name": "architectural_v1", "weight": 0.7, "trigger": "architectural visualization, clean geometry"}
        ],
        "default_cfg": 7.5,
        "default_steps": 30,
        "negative_prompt": "crooked lines, impossible geometry, blurry, warped perspective"
    },
    "cinematic": {
        "checkpoint": "Lykon/DreamShaper",
        "checkpoint_type": "sd15",
        "description": "Moody, highly stylized dramatic lighting, bokeh.",
        "loras": [],
        "default_cfg": 6.0,
        "default_steps": 25,
        "negative_prompt": "flat lighting, overexposed, boring composition, amateur photography"
    },
    "default": {
        "checkpoint": "SG161222/Realistic_Vision_V6.0_B1_noVAE",
        "checkpoint_type": "sd15",
        "description": "Standard photorealism.",
        "loras": [],
        "default_cfg": 7.0,
        "default_steps": 20,
        "negative_prompt": "ugly, blurry, deformed, watermark, low quality, bad anatomy"
    }
}

def get_model_routing(category: str) -> dict:
    return SD15_MODELS.get(category.lower(), SD15_MODELS["default"])
