# Luminary AI â€” Quality Control, Content Safety & System Testing Specification

## 1. Overview

This document outlines the production-grade **Quality Control (QC)**, **Content Safety**, **Adaptive Watchdog**, **Logging**, and **Automated Testing** architecture for Luminary AI V13+.

---

## 2. Content Safety Engine (`content_safety.py`)

Luminary AI provides a unified, zero-cloud singleton safety gate (`SafetyEngine`) for both image and text content:

- **Image Safety Classifier**: Uses `microsoft/NSFW-detector` (lightweight ONNX/PyTorch binary classifier) to screen both generated image outputs and uploaded product reference photos.
- **Text Toxicity Classifier**: Uses `unitary/toxic-bert` (truncated to max tokens) to inspect text generation output prior to serving.
- **Safety Violation Action**: Returns clean HTTP `403 Forbidden` / structured safety warnings; avoids serving inappropriate material or burning broken images.

---

## 3. Image Quality Control & Retry System (`quality_control.py`)

- **Aesthetic Predictor**: Uses `laion/aesthetic-predictor-v2-5` to compute aesthetic quality scores (scale `0.0` to `10.0`).
- **Configurable Threshold**: Exposed via environment variable `AESTHETIC_THRESHOLD` (default: `6.0`).
- **Configurable Retries**: Controlled via `IMAGE_RETRY_COUNT` (default: `2`). If a generated image scores below the threshold, the engine automatically prepends a quality-enhancement modifier (`"high quality, professional, sharp, detailed, "`) and retries generation.

---

## 4. Text Quality Evaluator

- **Repeat-Phrase Detection**: Uses regex matching (`(\b\w+\b\s+\b\w+\b\s+\b\w+\b).*(\1)`) to detect repetitive phrases.
- **Token Count & Readability**: Measures word count against `TEXT_MIN_TOKENS` (default: `15`) and computes Flesch Reading Ease score via `textstat`.
- **Auto Re-Query**: Automatically re-queries the LLM with instructions to elaborate if text fails quality standards.

---

## 5. Adaptive Time Limits, Inactivity Watchdog & Cancellation

- **Thread-Safe Concurrency Lock**: `_INFERENCE_LOCK` serializes diffusion passes to protect CPU / RAM.
- **5-Minute Inactivity Watchdog**: Monitors step elapsed times. If step generation stalls for > 300 seconds, the step count is dynamically reduced from 10 to 6.
- **Cancellation Endpoint**:
  - `POST /cancel/<request_id>`
  - Triggers `sdxl_service.cancel()`, flipping a thread-safe flag checked at each step.
- **SSE Real-Time Progress Endpoint**:
  - `GET /progress/<request_id>`
  - Streams real-time step events formatted as Server-Sent Events (`text/event-stream`).

---

## 6. Structured JSON Log Rotation (`luminary_logging.py`)

- **File Destination**: `logs/luminary.log`
- **Rotation Configuration**: `RotatingFileHandler` with 10 MB maximum file size and 5 rolling backup files.
- **Event Schema**:
  ```json
  {
    "timestamp": "2026-08-30 18:25:00",
    "request_id": "req_12345",
    "type": "image",
    "prompt": "high quality ad concept...",
    "model": "local_sdxl",
    "resolution": "768x768",
    "steps": 10,
    "duration": 42.15,
    "aesthetic_score": 7.8,
    "safety_pass": true
  }
  ```

---

## 7. System Test Runner (`test_system.py`)

Run tests via the batch script shortcut:
```cmd
workSTART_LUMINARY_BACKEND.bat test
```
or directly:
```bash
python test_system.py
```

Generates a JSON test execution summary in `test_report.json` covering:
1. Health check & dependency probing.
2. Text chat endpoint responsiveness.
3. Image generation endpoint execution.
4. Content safety classification.
5. Cancellation request handling.
6. Parallel request concurrency lock validation.
---

## 8. Token Limits Configuration

The Luminary server exposes environment variables to govern maximum **output** generation tokens per endpoint.

> [!NOTE]
> These environment variables control **output** tokens only. The input context is determined by each model's native context window (e.g., 8,192 tokens for Ollama models) and does not require manual configuration.

| Environment Variable | Default | Description |
|---|---|---|
| `CHAT_OUTPUT_TOKENS` | `2048` | Max output tokens for general `/chat` completions. |
| `DOC_OUTPUT_TOKENS` | `4096` | Max output tokens for generated DOCX articles and strategy guides. |
| `PPT_OUTPUT_TOKENS` | `4096` | Max output tokens for generated PPTX presentation decks. |
| `SHEET_OUTPUT_TOKENS` | `4096` | Max output tokens for generated XLSX financial and tabular datasets. |
| `PROMPT_BUILDER_MAX_TOKENS` | `1024` | Max tokens for creative brief formulation and prompt expansion. |
| `SDXL_PROMPT_MAX_TOKENS` | `77` | Fixed SDXL CLIP tokenizer prompt limit (hard-capped at 77 tokens). |
| `FALLBACK_CAP` | `1024` | Hard ceiling for `distilgpt2` fallback generation when primary models are offline. |

All limits are logged to stdout at startup:
```text
[Token Limits] CHAT_OUTPUT_TOKENS=2048 DOC_OUTPUT_TOKENS=4096 PPT_OUTPUT_TOKENS=4096 SHEET_OUTPUT_TOKENS=4096 PROMPT_BUILDER_MAX_TOKENS=1024 SDXL_PROMPT_MAX_TOKENS=77 FALLBACK_MAX_TOKENS=1024
```
And inspectable dynamically via `GET /token_limits`.

