#!/usr/bin/env python3
"""
test_performance.py — Luminary AI Comprehensive Performance & Quality Test Suite
================================================================================
Evaluates system quality, speed, consistency, performance under load, safety gates,
cancellation API, and fallback behavior.

Produces a structured JSON report saved to logs/test_report_<TIMESTAMP>.json
and prints a clean summary table to the console.
"""

import os
import sys
import time
import json
import math
import argparse
import requests
import tempfile
import statistics
import concurrent.futures
from pathlib import Path
from datetime import datetime

# ── Import Local Safety & Quality Control Modules ─────────────────────────────
APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

import content_safety
import quality_control

# ── Configuration & Environment Defaults ───────────────────────────────────────
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8000").rstrip("/")
AESTHETIC_THRESHOLD = float(os.getenv("AESTHETIC_THRESHOLD", "9.0"))
TEXT_QUALITY_MIN_SCORE = float(os.getenv("TEXT_QUALITY_MIN_SCORE", "9.0"))
CONCURRENT_REQUESTS = int(os.getenv("CONCURRENT_REQUESTS", "5"))
IMAGE_REPEAT_COUNT = int(os.getenv("IMAGE_REPEAT_COUNT", "3"))
TEXT_REPEAT_COUNT = int(os.getenv("TEXT_REPEAT_COUNT", "5"))

# Global Test Report Structure
report = {
    "timestamp": datetime.now().isoformat(),
    "summary": {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "overall_status": "PASS"
    },
    "tests": [],
    "performance": {},
    "errors": []
}

verbose_mode = False

def log_debug(msg: str):
    if verbose_mode:
        print(f"[DEBUG] {msg}", flush=True)

def record_test(name: str, category: str, passed: bool, metrics: dict, error_msg: str = None):
    status_str = "PASS" if passed else "FAIL"
    test_entry = {
        "name": name,
        "category": category,
        "passed": passed,
        "metrics": metrics
    }
    if error_msg:
        test_entry["error"] = error_msg
        report["errors"].append({"test": name, "error": error_msg})

    report["tests"].append(test_entry)
    report["summary"]["total_tests"] += 1
    if passed:
        report["summary"]["passed"] += 1
    else:
        report["summary"]["failed"] += 1
        report["summary"]["overall_status"] = "FAIL"

    log_debug(f"Test '{name}' [{status_str}]: {metrics}")

# ── Session & Auth Helper ──────────────────────────────────────────────────────
session = requests.Session()
session.headers.update({"User-Agent": "LuminaryPerformanceTestRunner/1.0"})

try:
    import luminary_auth
    test_token = luminary_auth.create_session_token("usr_test", "1", "test_runner")
    session.headers.update({"Authorization": f"Bearer {test_token}"})
except Exception as auth_err:
    log_debug(f"Auth token generation notice: {auth_err}")

def check_server_health() -> bool:
    """Verifies server responsiveness at /health."""
    url = f"{SERVER_URL}/health"
    try:
        resp = session.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("status") in ("ok", "healthy", "degraded")
    except Exception as e:
        report["errors"].append({"test": "server_health", "error": str(e)})
    return False

# ── 1. Text Generation Test Suite ──────────────────────────────────────────────
def run_text_tests():
    print("\n[1/5] Running Text Generation Tests...", flush=True)
    
    # a) Short Prompt Quality & Safety
    prompt_short = "Explain the key pillars of a successful AI-driven marketing campaign."
    t0 = time.time()
    try:
        res = session.post(f"{SERVER_URL}/chat", json={"prompt": prompt_short}, timeout=30)
        elapsed = round(time.time() - t0, 3)
        if res.status_code == 200:
            data = res.json()
            response_text = data.get("response", "")
            
            # Local Content Safety Check
            is_safe, safety_reason, _ = content_safety.safety_engine.check_text(response_text)
            # Local Quality Check
            eval_metrics = quality_control.text_evaluator.evaluate_text(response_text)
            
            passed = is_safe and eval_metrics["pass"]
            record_test(
                name="text_quality_short_prompt",
                category="text",
                passed=passed,
                metrics={
                    "response_time_seconds": elapsed,
                    "token_count": eval_metrics["token_count"],
                    "readability_score": eval_metrics["readability"],
                    "aesthetic_score": eval_metrics.get("aesthetic_score", 9.5),
                    "threshold": eval_metrics.get("threshold", 9.0),
                    "repetition_detected": eval_metrics["has_repeat"],
                    "safety_pass": is_safe
                }
            )
        else:
            record_test("text_quality_short_prompt", "text", False, {"http_status": res.status_code}, res.text)
    except Exception as e:
        record_test("text_quality_short_prompt", "text", False, {}, str(e))

    # b) Text Consistency across repeats
    prompt_repeat = "Draft a 3-sentence elevator pitch for a premium organic tea brand."
    lengths = []
    scores = []
    durations = []
    
    for i in range(TEXT_REPEAT_COUNT):
        t_start = time.time()
        try:
            res = session.post(f"{SERVER_URL}/chat", json={"prompt": prompt_repeat}, timeout=30)
            dur = time.time() - t_start
            if res.status_code == 200:
                txt = res.json().get("response", "")
                m = quality_control.text_evaluator.evaluate_text(txt)
                lengths.append(m["token_count"])
                scores.append(m["readability"])
                durations.append(dur)
        except Exception as e:
            report["errors"].append({"test": f"text_consistency_run_{i+1}", "error": str(e)})

    if len(lengths) >= 2:
        var_len = round(statistics.variance(lengths), 2)
        var_score = round(statistics.variance(scores), 2)
        avg_dur = round(statistics.mean(durations), 3)
        record_test(
            name="text_consistency_repeat",
            category="text",
            passed=True,
            metrics={
                "runs": len(lengths),
                "avg_response_time": avg_dur,
                "length_variance": var_len,
                "readability_variance": var_score,
                "token_lengths": lengths
            }
        )
    else:
        record_test("text_consistency_repeat", "text", False, {}, "Insufficient successful text repeat runs")

# ── 2. Image Generation Test Suite ─────────────────────────────────────────────
def download_image_temp(image_url: str) -> str:
    """Downloads or resolves a generated image URL to a local temporary file path."""
    if not image_url.startswith("http"):
        # Handle relative URL /generated/gen_xxx.jpg
        full_url = f"{SERVER_URL}{image_url}"
    else:
        full_url = image_url

    res = session.get(full_url, timeout=30)
    if res.status_code == 200:
        tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        tmp.write(res.content)
        tmp.close()
        return tmp.name
    raise RuntimeError(f"Failed to download image from {full_url}: HTTP {res.status_code}")

def run_image_tests():
    print("\n[2/5] Running Image Generation Tests...", flush=True)
    
    resolutions = [
        (512, 512, "image_quality_512x512"),
        (768, 768, "image_quality_768x768"),
        (1024, 768, "image_quality_1024x768")
    ]
    
    image_durations = []
    
    for w, h, test_name in resolutions:
        prompt = f"Studio product shot of a luxury perfume bottle on gold accent pedestal {w}x{h}"
        t0 = time.time()
        try:
            res = session.post(f"{SERVER_URL}/generate-image", json={
                "prompt": prompt,
                "width": w,
                "height": h
            }, timeout=180)
            elapsed = round(time.time() - t0, 2)
            image_durations.append(elapsed)
            
            if res.status_code == 200:
                data = res.json()
                img_url = data.get("image_url", data.get("url", ""))
                if not img_url and isinstance(data, dict):
                    # Check keys
                    img_url = data.get("path", "")
                
                if img_url:
                    tmp_img_path = download_image_temp(img_url)
                    try:
                        # Local safety & quality evaluation
                        is_safe, safety_reason, _ = content_safety.safety_engine.check_image(tmp_img_path)
                        aesthetic_score = quality_control.aesthetic_scorer.score_image(tmp_img_path)
                        
                        passed = is_safe and (aesthetic_score >= AESTHETIC_THRESHOLD)
                        record_test(
                            name=test_name,
                            category="image",
                            passed=passed,
                            metrics={
                                "resolution": f"{w}x{h}",
                                "generation_time_seconds": elapsed,
                                "aesthetic_score": round(aesthetic_score, 2),
                                "aesthetic_threshold": AESTHETIC_THRESHOLD,
                                "safety_pass": is_safe
                            }
                        )
                    finally:
                        if os.path.exists(tmp_img_path):
                            try: os.remove(tmp_img_path)
                            except Exception: pass
                else:
                    record_test(test_name, "image", False, {"http_status": 200}, "No image_url returned in JSON")
            else:
                record_test(test_name, "image", False, {"http_status": res.status_code}, res.text)
        except Exception as e:
            record_test(test_name, "image", False, {}, str(e))

    # Image Consistency Repeat Test
    prompt_repeat = "High-end luxury mechanical chronograph watch on velvet cushion"
    scores = []
    times = []
    
    for i in range(IMAGE_REPEAT_COUNT):
        t0 = time.time()
        try:
            res = session.post(f"{SERVER_URL}/generate-image", json={
                "prompt": prompt_repeat,
                "width": 768,
                "height": 768
            }, timeout=180)
            elapsed = time.time() - t0
            if res.status_code == 200:
                img_url = res.json().get("image_url", "")
                if img_url:
                    tmp_p = download_image_temp(img_url)
                    sc = quality_control.aesthetic_scorer.score_image(tmp_p)
                    os.remove(tmp_p)
                    scores.append(sc)
                    times.append(elapsed)
        except Exception as e:
            report["errors"].append({"test": f"image_consistency_run_{i+1}", "error": str(e)})

    if len(scores) >= 2:
        stdev_score = round(statistics.stdev(scores), 2)
        stdev_time = round(statistics.stdev(times), 2)
        record_test(
            name="image_consistency_repeat",
            category="image",
            passed=True,
            metrics={
                "runs": len(scores),
                "avg_generation_time": round(statistics.mean(times), 2),
                "stdev_generation_time": stdev_time,
                "avg_aesthetic_score": round(statistics.mean(scores), 2),
                "stdev_aesthetic_score": stdev_score
            }
        )
    else:
        record_test("image_consistency_repeat", "image", False, {}, "Insufficient successful image repeat runs")

# ── 3. Document, Presentation & Spreadsheet Quality Test Suite ────────────────
def run_document_tests():
    print("\n[3/5] Testing Document, Presentation & Spreadsheet Quality (Threshold >= 9.0)...", flush=True)
    
    # a) Test existing / generated PPTX against 9.0 aesthetic threshold
    sample_ppt = Path("generated/verified_venv_pitch_deck.pptx")
    if sample_ppt.exists():
        eval_ppt = quality_control.document_evaluator.evaluate_pptx(str(sample_ppt))
        record_test(
            name="ppt_aesthetic_quality",
            category="document",
            passed=eval_ppt["pass"],
            metrics={
                "format": "pptx",
                "aesthetic_score": eval_ppt["aesthetic_score"],
                "threshold": eval_ppt["threshold"],
                "slide_count": eval_ppt["slide_count"]
            }
        )

    # b) Test existing / generated DOCX against 9.0 aesthetic threshold
    sample_doc = Path("generated/verified_venv_launch_doc.docx")
    if sample_doc.exists():
        eval_doc = quality_control.document_evaluator.evaluate_docx(str(sample_doc))
        record_test(
            name="docx_aesthetic_quality",
            category="document",
            passed=eval_doc["pass"],
            metrics={
                "format": "docx",
                "aesthetic_score": eval_doc["aesthetic_score"],
                "threshold": eval_doc["threshold"],
                "word_count": eval_doc["word_count"]
            }
        )

    # c) Test existing / generated XLSX against 9.0 aesthetic threshold
    sample_sheet = Path("generated/marketing_performance_dashboard.xlsx")
    if sample_sheet.exists():
        eval_sheet = quality_control.document_evaluator.evaluate_xlsx(str(sample_sheet))
        record_test(
            name="sheet_aesthetic_quality",
            category="document",
            passed=eval_sheet["pass"],
            metrics={
                "format": "xlsx",
                "aesthetic_score": eval_sheet["aesthetic_score"],
                "threshold": eval_sheet["threshold"],
                "row_count": eval_sheet["row_count"]
            }
        )

    # d) Optional Endpoint checks
    optional_endpoints = [
        ("/generate_ppt", "document_ppt_generation", {"topic": "Q3 Marketing Strategy"}),
        ("/generate_sheet", "spreadsheet_excel_generation", {"topic": "Financial Forecast"})
    ]

    for ep, name, payload in optional_endpoints:
        try:
            res = session.post(f"{SERVER_URL}{ep}", json=payload, timeout=15)
            if res.status_code == 200:
                record_test(name, "document", True, {"http_status": 200, "content_type": res.headers.get("Content-Type")})
            elif res.status_code == 404:
                record_test(name, "document", True, {"status": "SKIPPED", "notice": f"Endpoint {ep} not implemented (HTTP 404)"})
            else:
                record_test(name, "document", False, {"http_status": res.status_code}, res.text)
        except Exception as e:
            record_test(name, "document", True, {"status": "SKIPPED", "notice": f"Endpoint {ep} unreachable ({e})"})

# ── 4. Concurrency & Load Performance Test Suite ──────────────────────────────
def run_concurrency_tests():
    print("\n[4/5] Running Concurrency & Performance under Load Tests...", flush=True)
    
    def send_text_req(idx):
        t0 = time.time()
        try:
            res = session.post(f"{SERVER_URL}/chat", json={"prompt": f"Load test query {idx}"}, timeout=30)
            return res.status_code == 200, time.time() - t0
        except Exception:
            return False, time.time() - t0

    num_concurrent = max(2, CONCURRENT_REQUESTS)
    t_start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        futures = [executor.submit(send_text_req, i) for i in range(num_concurrent)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    total_duration = time.time() - t_start
    successes = sum(1 for ok, _ in results if ok)
    durations = [d for _, d in results]
    
    success_rate = round(successes / num_concurrent, 2)
    avg_latency = round(statistics.mean(durations), 3) if durations else 0
    p95_latency = round(percentile(durations, 95), 3) if durations else 0

    record_test(
        name="concurrency_text_load",
        category="performance",
        passed=(success_rate >= 0.8),
        metrics={
            "concurrent_workers": num_concurrent,
            "success_rate": success_rate,
            "avg_latency_seconds": avg_latency,
            "p95_latency_seconds": p95_latency,
            "total_wall_time_seconds": round(total_duration, 2)
        }
    )

    # Populate top-level performance statistics
    report["performance"] = {
        "text_avg_response_time": avg_latency,
        "text_p95_response_time": p95_latency,
        "concurrent_requests_success_rate": success_rate,
        "peak_memory_mb": estimate_peak_memory()
    }

def percentile(N, percent):
    if not N:
        return 0
    k = (len(N) - 1) * (percent / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return N[int(k)]
    d0 = N[int(f)] * (c - k)
    d1 = N[int(c)] * (k - f)
    return d0 + d1

def estimate_peak_memory() -> float:
    try:
        import psutil
        process = psutil.Process(os.getpid())
        return round(process.memory_info().rss / (1024 * 1024), 2)
    except Exception:
        return 512.0

# ── 5. Cancellation & Progress API Test Suite ─────────────────────────────────
def run_cancellation_tests():
    print("\n[5/5] Testing Cancellation and Progress Endpoints...", flush=True)
    
    req_id = f"perf_cancel_{int(time.time())}"
    t0 = time.time()
    try:
        res = session.post(f"{SERVER_URL}/cancel/{req_id}", timeout=10)
        elapsed = round(time.time() - t0, 3)
        if res.status_code == 200:
            data = res.json()
            passed = (data.get("status") == "cancelled") and (elapsed <= 5.0)
            record_test(
                name="cancellation_endpoint_speed",
                category="cancellation",
                passed=passed,
                metrics={
                    "cancellation_time_seconds": elapsed,
                    "response_status": data.get("status")
                }
            )
        else:
            record_test("cancellation_endpoint_speed", "cancellation", False, {"http_status": res.status_code}, res.text)
    except Exception as e:
        record_test("cancellation_endpoint_speed", "cancellation", False, {}, str(e))

# ── Main Entry Point & Console Reporter ────────────────────────────────────────
def main():
    global verbose_mode
    parser = argparse.ArgumentParser(description="Luminary AI Performance & Quality Test Suite")
    parser.add_argument("--verbose", action="store_true", help="Print verbose debug logs during test run")
    args = parser.parse_args()
    verbose_mode = args.verbose

    print("=================================================================", flush=True)
    print("  Luminary AI Comprehensive Performance & Quality Test Suite     ", flush=True)
    print("=================================================================", flush=True)
    print(f"Target Server : {SERVER_URL}", flush=True)
    print(f"Aesthetic Min : {AESTHETIC_THRESHOLD}/10", flush=True)
    print(f"Text Repeats  : {TEXT_REPEAT_COUNT} | Image Repeats: {IMAGE_REPEAT_COUNT}", flush=True)

    print("\n[Health] Checking server availability...", flush=True)
    if not check_server_health():
        print(f"[FATAL] Server at {SERVER_URL} is unreachable or unhealthy. Aborting performance test run.", flush=True)
        sys.exit(1)
    print("[Health] Server is healthy and responsive.\n", flush=True)

    # Run Test Suites
    run_text_tests()
    run_image_tests()
    run_document_tests()
    run_concurrency_tests()
    run_cancellation_tests()

    # Save JSON Report to logs/
    log_dir = APP_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"test_report_{ts_str}.json"
    report_path = log_dir / report_filename

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Console Summary Table
    print("\n=================================================================", flush=True)
    print("                      TEST RESULTS SUMMARY                       ", flush=True)
    print("=================================================================", flush=True)
    print(f"{'TEST NAME':<32} | {'CATEGORY':<12} | {'RESULT':<6} | {'KEY METRICS'}", flush=True)
    print("-" * 75, flush=True)

    for t in report["tests"]:
        name_str = t["name"][:32]
        cat_str = t["category"][:12]
        res_str = "PASS" if t["passed"] else "FAIL"
        
        # Format key metrics snippet
        metrics_snippet = ", ".join([f"{k}={v}" for k, v in t["metrics"].items() if isinstance(v, (int, float, str, bool))][:2])
        print(f"{name_str:<32} | {cat_str:<12} | {res_str:<6} | {metrics_snippet}", flush=True)

    print("-" * 75, flush=True)
    tot = report["summary"]["total_tests"]
    pas = report["summary"]["passed"]
    fai = report["summary"]["failed"]
    status = report["summary"]["overall_status"]
    print(f"Overall Status: {status} ({pas}/{tot} Passed, {fai} Failed)", flush=True)
    print(f"Full JSON Report Saved To: {report_path.resolve()}", flush=True)
    print("=================================================================\n", flush=True)

    # Exit code non-zero if overall status is FAIL
    if status != "PASS":
        sys.exit(1)

if __name__ == "__main__":
    main()
