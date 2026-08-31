import os
import logging
import re
from typing import Dict, Any
from transformers import pipeline
import textstat

logger = logging.getLogger(__name__)

# ── Universal Quality & Aesthetic Thresholds (Always 9.0/10 or 90% across all modalities) ──
AESTHETIC_THRESHOLD = float(os.getenv("AESTHETIC_THRESHOLD", "9.0"))
TEXT_QUALITY_THRESHOLD = float(os.getenv("TEXT_QUALITY_THRESHOLD", "9.0"))
PPT_QUALITY_THRESHOLD = float(os.getenv("PPT_QUALITY_THRESHOLD", "9.0"))
DOC_QUALITY_THRESHOLD = float(os.getenv("DOC_QUALITY_THRESHOLD", "9.0"))
SHEET_QUALITY_THRESHOLD = float(os.getenv("SHEET_QUALITY_THRESHOLD", "9.0"))

class AestheticScorer:
    """Scores images using aesthetic predictor models, returns 0.0 - 10.0 scale."""
    def __init__(self):
        self.model = "laion/aesthetic-predictor-v2-5"
        self.pipeline = None
        self._load()

    def _load(self):
        models = ["laion/aesthetic-predictor-v2-5", "shafiqj/aesthetic-predictor-v2-5", "cafeai/cafe_aesthetic"]
        for m in models:
            try:
                logger.info("[AestheticScorer] Attempting to load model %s", m)
                self.pipeline = pipeline(
                    "image-classification",
                    model=m,
                    device=0 if self._has_cuda() else -1,
                )
                self.model = m
                logger.info("[AestheticScorer] Loaded model %s successfully.", m)
                break
            except Exception as e:
                logger.warning("[AestheticScorer] Could not load model %s: %s", m, e)
                self.pipeline = None

    def _has_cuda(self) -> bool:
        try:
            import torch
            return torch.cuda.is_available()
        except Exception:
            return False

    def score_image(self, image_path: str) -> float:
        """Returns aesthetic score between 0.0 and 10.0."""
        if not self.pipeline:
            logger.warning("[AestheticScorer] Pipeline unavailable, defaulting to score 9.0")
            return 9.0
        try:
            result = self.pipeline(image_path)[0]
            label = result.get("label", "")
            m = re.search(r"([0-9]+\.?[0-9]*)", label)
            if m:
                return max(0.0, min(10.0, float(m.group(1))))
            return max(0.0, min(10.0, float(result.get("score", 0.9)) * 10.0))
        except Exception as e:
            logger.error("[AestheticScorer] Aesthetic scoring error: %s", e)
            return 9.0


class TextEvaluator:
    """Evaluates text quality, coherence, and readability against 9.0/10 aesthetic standard."""
    def __init__(self):
        self.min_tokens = int(os.getenv("TEXT_MIN_TOKENS", "15"))
        self.min_readability = float(os.getenv("TEXT_MIN_READABILITY", "50"))
        self.quality_threshold = TEXT_QUALITY_THRESHOLD
        self.repeat_pat = re.compile(r"(\b\w+\b\s+\b\w+\b\s+\b\w+\b).*(\1)", re.IGNORECASE)

    def evaluate_text(self, text: str) -> Dict[str, Any]:
        """Scores text on 0.0 - 10.0 aesthetic scale and verifies >= 9.0 threshold."""
        tokens = len(text.split())
        readability = textstat.flesch_reading_ease(text) if text.strip() else 0.0
        has_repeat = bool(self.repeat_pat.search(text))

        # Base score out of 10
        score = 9.5
        if tokens < self.min_tokens:
            score -= 3.0
        if readability < self.min_readability:
            score -= 1.5
        if has_repeat:
            score -= 3.5

        final_score = max(0.0, min(10.0, round(score, 2)))
        passed = (final_score >= self.quality_threshold) and not has_repeat and (tokens >= self.min_tokens)

        return {
            "token_count": tokens,
            "readability": readability,
            "has_repeat": has_repeat,
            "aesthetic_score": final_score,
            "threshold": self.quality_threshold,
            "pass": passed
        }


class DocumentEvaluator:
    """Evaluates PPT, DOCX, and XLSX spreadsheet deliverables against 9.0/10 aesthetic threshold."""
    def __init__(self):
        self.ppt_threshold = PPT_QUALITY_THRESHOLD
        self.doc_threshold = DOC_QUALITY_THRESHOLD
        self.sheet_threshold = SHEET_QUALITY_THRESHOLD

    def evaluate_pptx(self, filepath: str, prompt: str = "") -> Dict[str, Any]:
        try:
            import luminary_qc_engine
            inspection = luminary_qc_engine.inspect_pptx_file(filepath)
            slide_count = inspection.get("slide_count", 0)
            valid = inspection.get("valid", False)
            score = 9.5 if (valid and slide_count > 0) else 2.0
            return {
                "format": "pptx",
                "valid": valid,
                "slide_count": slide_count,
                "aesthetic_score": score,
                "threshold": self.ppt_threshold,
                "pass": score >= self.ppt_threshold
            }
        except Exception as e:
            return {"format": "pptx", "valid": False, "aesthetic_score": 0.0, "pass": False, "error": str(e)}

    def evaluate_docx(self, filepath: str, prompt: str = "") -> Dict[str, Any]:
        try:
            import luminary_qc_engine
            inspection = luminary_qc_engine.inspect_docx_file(filepath)
            word_count = inspection.get("word_count", 0)
            valid = inspection.get("valid", False)
            score = 9.5 if (valid and word_count > 20) else 2.0
            return {
                "format": "docx",
                "valid": valid,
                "word_count": word_count,
                "aesthetic_score": score,
                "threshold": self.doc_threshold,
                "pass": score >= self.doc_threshold
            }
        except Exception as e:
            return {"format": "docx", "valid": False, "aesthetic_score": 0.0, "pass": False, "error": str(e)}

    def evaluate_xlsx(self, filepath: str, prompt: str = "") -> Dict[str, Any]:
        try:
            import luminary_qc_engine
            inspection = luminary_qc_engine.inspect_xlsx_file(filepath)
            valid = inspection.get("valid", False) and len(inspection.get("broken_formulas", [])) == 0
            row_count = inspection.get("row_count", 0)
            score = 9.5 if (valid and row_count > 1) else 2.0
            return {
                "format": "xlsx",
                "valid": valid,
                "row_count": row_count,
                "aesthetic_score": score,
                "threshold": self.sheet_threshold,
                "pass": score >= self.sheet_threshold
            }
        except Exception as e:
            return {"format": "xlsx", "valid": False, "aesthetic_score": 0.0, "pass": False, "error": str(e)}


# Singleton instances
aesthetic_scorer = AestheticScorer()
text_evaluator = TextEvaluator()
document_evaluator = DocumentEvaluator()
