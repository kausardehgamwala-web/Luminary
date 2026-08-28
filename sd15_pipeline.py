"""
sd15_pipeline.py / sdxl_pipeline.py
====================================
Real Local SDXL inference pipeline with IP-Adapter product conditioning,
8-16GB VRAM memory offload, and local super-resolution print upscaler.
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from PIL import Image

APP_ROOT = Path(__file__).resolve().parent

import local_sdxl_service
import luminary_image_engine

def generate_sd15_image(
    prompt: str, 
    negative_prompt: str = "",
    width: int = 1024, 
    height: int = 1024, 
    checkpoint: str = "stabilityai/stable-diffusion-xl-base-1.0", 
    loras: Optional[List[Dict[str, Any]]] = None,
    num_steps: int = 35,
    cfg_scale: float = 7.5,
    reference_image_path: Optional[str] = None,
    category: str = "product"
) -> str:
    """
    Generates an image via real persistent local SDXL inference service.
    """
    filename = f"local_sdxl_{int(time.time())}.jpg"
    out_dir = APP_ROOT / "generated"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / filename

    # 1. Parse resolution & print requirements
    target_w, target_h, is_print = luminary_image_engine.parse_target_resolution(prompt, (width, height))
    
    # SDXL native generation size
    native_w = min(1536, max(768, target_w))
    native_h = min(1536, max(768, target_h))

    # 2. Reference image path
    ref_obj = Path(reference_image_path) if reference_image_path and Path(reference_image_path).exists() else None

    # 3. Call local SDXL service under concurrency lock
    try:
        gen_img = local_sdxl_service.sdxl_service.generate(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=native_w,
            height=native_h,
            num_inference_steps=num_steps,
            guidance_scale=cfg_scale,
            reference_image_path=ref_obj,
            loras=loras
        )
    except Exception as err:
        print(f"[SDXL Pipeline Notice] Local inference error: {err}")
        # Fallback to local image engine
        img_bytes, _ = luminary_image_engine.engine.generate_image(
            prompt=prompt,
            width=native_w,
            height=native_h,
            negative_prompt=negative_prompt,
            reference_image_path=ref_obj,
            category=category,
            is_print=is_print
        )
        out_file.write_bytes(img_bytes)
        gen_img = Image.open(out_file)

    # 4. If print resolution was requested (e.g. A4 2480x3508), apply local AI upscaling
    if is_print and (target_w > native_w or target_h > native_h):
        gen_img = local_sdxl_service.upscale_image_for_print(gen_img, target_w, target_h)

    # 5. If reference product photo was uploaded, composite exact product into scene
    if ref_obj:
        gen_img.save(out_file, "JPEG", quality=95)
        luminary_image_engine.composite_real_product_into_scene(
            product_image_path=ref_obj,
            scene_background_path=out_file,
            output_path=out_file,
            position="center_bottom"
        )
        gen_img = Image.open(out_file)

    # 6. Apply subject-aware post processing and 300 DPI metadata
    gen_img.save(out_file, "JPEG", quality=96, dpi=(300, 300) if is_print else (144, 144))
    profile_name = luminary_image_engine.detect_post_process_profile(prompt, category)
    luminary_image_engine.apply_subject_aware_post_processing(out_file, profile_name=profile_name, is_print=is_print)

    print(f"[SDXL Pipeline] Saved deliverable to {out_file} (Resolution: {gen_img.size[0]}x{gen_img.size[1]})")
    return f"/generated/{filename}?v={int(time.time())}"
