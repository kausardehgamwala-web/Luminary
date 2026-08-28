"""
local_image_generator.py — Luminary Local SDXL Image Generator
==============================================================
Provides offline local image generation using SDXL with 8-16GB VRAM memory offload,
IP-Adapter product conditioning, and subject-aware post-processing.
"""

import time
from pathlib import Path
from typing import Optional

APP_ROOT = Path(__file__).resolve().parent

import sd15_pipeline
import sd15_model_registry
import luminary_creative_director

def generate_local_image(
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    num_steps: int = 35,
    reference_image_path: Optional[str] = None,
    category: str = "product"
) -> str:
    """
    Generates an image locally using the SDXL pipeline with IP-Adapter product conditioning.
    """
    # 1. Match category
    category_match = "default"
    for cat in sd15_model_registry.SD15_MODELS.keys():
        if cat.lower() in prompt.lower():
            category_match = cat
            break
            
    # 2. Model routing
    routing = sd15_model_registry.get_model_routing(category_match)
    
    # 3. Generate via persistent SDXL pipeline
    return sd15_pipeline.generate_sd15_image(
        prompt=prompt,
        negative_prompt=routing.get("negative_prompt", ""),
        width=width,
        height=height,
        checkpoint=routing.get("checkpoint", "stabilityai/stable-diffusion-xl-base-1.0"),
        loras=routing.get("loras", []),
        num_steps=routing.get("default_steps", num_steps),
        cfg_scale=routing.get("default_cfg", 7.5),
        reference_image_path=reference_image_path,
        category=category
    )
