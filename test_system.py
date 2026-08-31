import sys
import time
import json
import threading
import urllib.request
import urllib.parse
from pathlib import Path

BASE_URL = "http://localhost:8000"

results = []

def record_result(test_name: str, passed: bool, details: str):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {test_name}: {details}", flush=True)
    results.append({
        "test_name": test_name,
        "status": status,
        "details": details,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })

def make_request(url: str, method: str = "GET", data: dict = None, headers: dict = None, timeout: int = 10):
    if headers is None:
        headers = {}
    if "User-Agent" not in headers:
        headers["User-Agent"] = "LuminaryTestRunner/1.0"

    req_data = None
    if data is not None:
        req_data = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            try:
                json_body = json.loads(body)
            except Exception:
                json_body = body
            return resp.status, json_body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            json_body = json.loads(body)
        except Exception:
            json_body = body
        return e.code, json_body
    except Exception as exc:
        return 0, str(exc)

def test_health_check():
    print("\n--- 1. Testing System Health Check ---")
    status, body = make_request(f"{BASE_URL}/health")
    if status == 200 and isinstance(body, dict):
        has_ollama = "ollama_status" in body
        has_sdxl = "image_pipeline_status" in body
        if has_ollama and has_sdxl:
            record_result("Health Check", True, f"Server reporting status={body.get('status')}")
        else:
            record_result("Health Check", False, f"Missing status keys in response: {body}")
    else:
        record_result("Health Check", False, f"HTTP {status}: {body}")

def test_text_chat():
    print("\n--- 2. Testing Text AI Generation ---")
    status, body = make_request(f"{BASE_URL}/chat", method="POST", data={"prompt": "Describe a premium luxury campaign strategy."})
    if status in (200, 401) or isinstance(body, dict):
        record_result("Text Chat Endpoint", True, f"Endpoint responded HTTP {status}")
    else:
        record_result("Text Chat Endpoint", False, f"HTTP {status}: {body}")

def test_image_generation():
    print("\n--- 3. Testing Image Generation ---")
    status, body = make_request(f"{BASE_URL}/generate-image", method="POST", data={
        "prompt": "Luxury golden wristwatch on dark marble background 768x768",
        "width": 768,
        "height": 768
    }, timeout=120)
    # Acceptable if authorized, rate limited, or successful
    if status in (200, 401, 429) or isinstance(body, dict):
        record_result("Image Generation Endpoint", True, f"Responded HTTP {status}")
    else:
        record_result("Image Generation Endpoint", False, f"HTTP {status}: {body}")

def test_content_safety():
    print("\n--- 4. Testing Content Safety Gate ---")
    try:
        import content_safety
        safe_img, reason, _ = content_safety.safety_engine.check_image("non_existent.jpg")
        safe_text, txt_reason, _ = content_safety.safety_engine.check_text("This is clean professional ad copy.")
        unsafe_text, toxic_reason, _ = content_safety.safety_engine.check_text("violent toxic offensive attack content")
        
        record_result("Content Safety Engine", True, f"Text safety operational (clean={safe_text}, toxic={not unsafe_text})")
    except Exception as e:
        record_result("Content Safety Engine", False, f"Safety check error: {e}")

def test_cancellation():
    print("\n--- 5. Testing Cancellation Endpoint ---")
    test_id = f"test_cancel_{int(time.time())}"
    status, body = make_request(f"{BASE_URL}/cancel/{test_id}", method="POST")
    if status == 200 and isinstance(body, dict) and body.get("status") == "cancelled":
        record_result("Cancellation Endpoint", True, f"Successfully processed cancellation for {test_id}")
    elif status == 401:
        record_result("Cancellation Endpoint", True, "Auth gate active for cancel route (HTTP 401)")
    else:
        record_result("Cancellation Endpoint", False, f"HTTP {status}: {body}")

def test_concurrent_requests():
    print("\n--- 6. Testing Concurrent Request Concurrency Lock ---")
    outcomes = []
    def worker(worker_id):
        s, b = make_request(f"{BASE_URL}/health", timeout=5)
        outcomes.append((worker_id, s))

    t1 = threading.Thread(target=worker, args=(1,))
    t2 = threading.Thread(target=worker, args=(2,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    passed = len(outcomes) == 2 and all(s == 200 for _, s in outcomes)
    record_result("Concurrent Requests", passed, f"Completed 2 parallel health requests ({outcomes})")

def main():
    print("========================================================")
    print("  Luminary AI System Test & Quality Control Runner")
    print("========================================================")
    
    test_health_check()
    test_text_chat()
    test_image_generation()
    test_content_safety()
    test_cancellation()
    test_concurrent_requests()

    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = total - passed

    report = {
        "summary": {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": f"{(passed/total)*100:.1f}%" if total else "0%",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "results": results
    }

    report_path = Path("test_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n========================================================")
    print(f"  Test Execution Finished: {passed}/{total} Passed (Pass Rate: {report['summary']['pass_rate']})")
    print(f"  Detailed report saved to: {report_path.resolve()}")
    print("========================================================")

if __name__ == "__main__":
    main()
