"""
local_image_generator.py — Luminary Local AI Image Generation Engine
======================================================================
Provides offline, CPU/Iris Xe accelerated local image generation
using SDXL Turbo and OpenVINO runtime.
"""

import time
import re
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent

import sd15_pipeline
import sd15_model_registry
import luminary_creative_director

def generate_local_image(prompt: str, width: int = 512, height: int = 512, num_steps: int = 25) -> str:
    """
    Generates an image locally using SD 1.5 pipeline optimized for 16GB RAM / Iris Xe.
    """
    # 1. Analyze creative parameters
    params = luminary_creative_director.analyze_creative_parameters(prompt)
    
    # 2. Extract specific category if defined in prompt, else default to 'product_advertising'
    category_match = "default"
    for cat in sd15_model_registry.SD15_MODELS.keys():
        if cat.lower() in prompt.lower():
            category_match = cat
            break
            
    # 3. Model routing
    routing = sd15_model_registry.get_model_routing(category_match)
    
    # 4. Generate
    return sd15_pipeline.generate_sd15_image(
        prompt=prompt,
        negative_prompt=routing["negative_prompt"],
        width=width,
        height=height,
        checkpoint=routing["checkpoint"],
        loras=routing["loras"],
        num_steps=routing.get("default_steps", num_steps),
        cfg_scale=routing.get("default_cfg", 7.0)
    )
    
    # Removing the old SDXL Turbo implementation


    # Safe PIL Fallback Graphic if model is loading
    try:
        from PIL import Image, ImageDraw
        clean_title = re.sub(r"[^a-zA-Z0-9 ]", "", prompt)[:30] or "Luminary Image AI"
        img = Image.new("RGB", (width, height), color=(12, 10, 16))
        draw = ImageDraw.Draw(img)

        cx, cy = width // 2, height // 2
        draw.rectangle([(20, 20), (width - 20, height - 20)], outline=(255, 85, 0), width=3)
        draw.polygon([(cx, cy - 40), (cx + 40, cy + 20), (cx - 40, cy + 20)], fill=(255, 85, 0))
        draw.text((cx, cy + 50), clean_title.upper(), fill=(250, 248, 245), anchor="ms")
        draw.text((cx, cy + 80), "LUMINARY LOCAL AI GENERATED", fill=(255, 140, 64), anchor="ms")
        
        img.save(out_file, "JPEG", quality=92)
        return f"/generated/{filename}?v={int(time.time())}"
    except Exception as err:
        print(f"[Local Image AI] PIL Fallback failed: {err}")
        return ""
