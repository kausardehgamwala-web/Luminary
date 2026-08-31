import logging
import json
from transformers import pipeline
from typing import Tuple

logger = logging.getLogger(__name__)

class SafetyEngine:
    """Unified safety engine for both image and text content.
    Loads two lightweight HuggingFace classifiers:
    * Image: microsoft/NSFW-detector (binary safe/unsafe)
    * Text : unitary/toxic-bert (binary safe/unsafe)
    """

    def __init__(self):
        self.image_classifier = None
        self.text_classifier = None
        self._load_models()

    def _load_models(self):
        try:
            logger.info("[SafetyEngine] Loading image NSFW detector model...")
            try:
                self.image_classifier = pipeline(
                    "image-classification",
                    model="microsoft/NSFW-detector",
                    device=0 if self._has_cuda() else -1,
                )
            except Exception:
                self.image_classifier = pipeline(
                    "image-classification",
                    model="Falconsai/nsfw_image_detection",
                    device=0 if self._has_cuda() else -1,
                )
            logger.info("[SafetyEngine] Image safety model loaded.")
        except Exception as e:
            logger.error(f"[SafetyEngine] Failed to load image safety model: {e}")
            self.image_classifier = None
        try:
            logger.info("[SafetyEngine] Loading text toxicity model...")
            self.text_classifier = pipeline(
                "text-classification",
                model="unitary/toxic-bert",
                truncation=True,
                device=0 if self._has_cuda() else -1,
            )
            logger.info("[SafetyEngine] Text safety model loaded.")
        except Exception as e:
            logger.error(f"[SafetyEngine] Failed to load text safety model: {e}")
            self.text_classifier = None

    def _has_cuda(self) -> bool:
        try:
            import torch
            return torch.cuda.is_available()
        except Exception:
            return False

    def check_image(self, image_path: str) -> Tuple[bool, str, float]:
        """Classify an image for safety.
        Returns (is_safe, reason, confidence).
        """
        if not self.image_classifier:
            return True, "no_classifier", 1.0
        try:
            result = self.image_classifier(image_path)[0]
            label = result["label"].lower()
            score = float(result["score"])
            if "nsfw" in label or "unsafe" in label:
                return False, f"NSFW detected ({label})", score
            return True, "safe", score
        except Exception as e:
            logger.error(f"[SafetyEngine] Image safety check error: {e}")
            return True, "error_fallback", 1.0

    def check_text(self, text: str) -> Tuple[bool, str, float]:
        """Classify a piece of text for toxicity.
        Returns (is_safe, reason, confidence).
        """
        if not self.text_classifier:
            return True, "no_classifier", 1.0
        try:
            result = self.text_classifier(text)[0]
            label = result["label"].lower()
            score = float(result["score"])
            if "toxic" in label or "unsafe" in label:
                return False, f"Toxic content detected ({label})", score
            return True, "safe", score
        except Exception as e:
            logger.error(f"[SafetyEngine] Text safety check error: {e}")
            return True, "error_fallback", 1.0

# Singleton instance for the service
safety_engine = SafetyEngine()
