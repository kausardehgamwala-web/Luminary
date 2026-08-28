"""
benchmark_tests.py
==================
Suite of 20 benchmark test cases for Luminary AI Master Intelligence.
Tests: text extraction, resolution mapping, image prompting, compliance check.

Run to verify the system performance.
"""

import sys
from pathlib import Path

# Add project root to path
APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

try:
    import luminary_intelligence
    print("[OK] Successfully imported luminary_intelligence")
except ImportError:
    print("[ERROR] Failed to import luminary_intelligence")
    sys.exit(1)


# 20 Test Cases: Prompt -> Expected Specs
TEST_CASES = [
    # ── Text / Writing ────────────────────────────────────────────────────────
    {
        "id": "TXT_01",
        "prompt": "Write a 500 word marketing blog article about electric SUVs",
        "expected": {"output_type": "docx", "word_count": 500, "subjects": ["electric SUVs"]},
    },
    {
        "id": "TXT_02",
        "prompt": "Create a detailed competitive research report on Apple vs Samsung 2025 revenue",
        "expected": {"output_type": "docx", "needs_web_search": True, "subjects": ["Apple", "Samsung"]},
    },
    {
        "id": "TXT_03",
        "prompt": "Draft a short luxury watch email newsletter",
        "expected": {"output_type": "docx", "style": "luxury"},
    },
    {
        "id": "TXT_04",
        "prompt": "Analyze the latest social media market trends for Nike with SWOT analysis",
        "expected": {"needs_web_search": True, "needs_research": True, "subjects": ["Nike"]},
    },
    {
        "id": "TXT_05",
        "prompt": "Write a professional business proposal for a new website launch",
        "expected": {"output_type": "docx", "style": "corporate"},
    },

    # ── Images ────────────────────────────────────────────────────────────────
    {
        "id": "IMG_01",
        "prompt": "Generate a 1080p photorealistic image of a red Ferrari SF90 on a racetrack",
        "expected": {"output_type": "image", "resolution": (1920, 1080), "style": "photorealistic", "subjects": ["Ferrari"]},
    },
    {
        "id": "IMG_02",
        "prompt": "Create 3 images of a black Porsche 911 at golden hour, landscape aspect",
        "expected": {"output_type": "image", "quantity": 3, "resolution": (1920, 1080), "subjects": ["Porsche"]},
    },
    {
        "id": "IMG_03",
        "prompt": "Draw a square animated style icon of an orange lightbulb, no background",
        "expected": {"output_type": "image", "resolution": (1080, 1080), "style": "animated", "negative": ["background"]},
    },
    {
        "id": "IMG_04",
        "prompt": "Generate a cinematic 2K portrait shot of two business executives in a boardroom",
        "expected": {"output_type": "image", "resolution": (2560, 1440), "style": "cinematic", "quantity": 2},
    },
    {
        "id": "IMG_05",
        "prompt": "Produce a luxury editorial shoot of a Rolex watch on a marble table, 4K resolution",
        "expected": {"output_type": "image", "resolution": (3840, 2160), "style": "luxury", "subjects": ["Rolex"]},
    },

    # ── Presentations ─────────────────────────────────────────────────────────
    {
        "id": "PPT_01",
        "prompt": "Create a 5-slide presentation on social media ROI",
        "expected": {"output_type": "pptx", "slide_count": 5},
    },
    {
        "id": "PPT_02",
        "prompt": "Generate a McKinsey style corporate deck about AI automation",
        "expected": {"output_type": "pptx", "style": "corporate"},
    },
    {
        "id": "PPT_03",
        "prompt": "Create an investor pitch deck for a startup, ten slides",
        "expected": {"output_type": "pptx", "slide_count": 10},
    },
    {
        "id": "PPT_04",
        "prompt": "Build a marketing presentation on Ferrari branding strategy",
        "expected": {"output_type": "pptx", "subjects": ["Ferrari"]},
    },
    {
        "id": "PPT_05",
        "prompt": "Design a 3-slide product launch deck for Apple's next product",
        "expected": {"output_type": "pptx", "slide_count": 3, "subjects": ["Apple"]},
    },

    # ── Spreadsheets ──────────────────────────────────────────────────────────
    {
        "id": "XLS_01",
        "prompt": "Build a monthly budget spreadsheet table with SUM formulas",
        "expected": {"output_type": "xlsx"},
    },
    {
        "id": "XLS_02",
        "prompt": "Create an Excel sheet mapping sales metrics for 12 months",
        "expected": {"output_type": "xlsx"},
    },
    {
        "id": "XLS_03",
        "prompt": "Generate a CSV data table showing website traffic and bounce rates",
        "expected": {"output_type": "xlsx"},
    },
    {
        "id": "XLS_04",
        "prompt": "Create a startup financial projection model spreadsheet",
        "expected": {"output_type": "xlsx"},
    },
    {
        "id": "XLS_05",
        "prompt": "Build a marketing campaign performance sheet for Facebook ads",
        "expected": {"output_type": "xlsx"},
    },
]


def run_tests():
    passed_count = 0
    total_count = len(TEST_CASES)

    print("=" * 60)
    print("           LUMINARY AI MASTER SPEC PARSER BENCHMARK")
    print("=" * 60)

    for tc in TEST_CASES:
        p = tc["prompt"]
        expected = tc["expected"]
        actual = luminary_intelligence.parse_prompt_specs(p)

        failed = []

        # Check Output Type
        if "output_type" in expected and expected["output_type"] != actual["output_type"]:
            failed.append(f"output_type: expected {expected['output_type']}, got {actual['output_type']}")

        # Check Resolution
        if "resolution" in expected and expected["resolution"] != actual["resolution"]:
            failed.append(f"resolution: expected {expected['resolution']}, got {actual['resolution']}")

        # Check Quantity
        if "quantity" in expected and expected["quantity"] != actual["quantity"]:
            failed.append(f"quantity: expected {expected['quantity']}, got {actual['quantity']}")

        # Check Slide Count
        if "slide_count" in expected and expected["slide_count"] != actual["slide_count"]:
            failed.append(f"slide_count: expected {expected['slide_count']}, got {actual['slide_count']}")

        # Check Word Count
        if "word_count" in expected and expected["word_count"] != actual["word_count"]:
            failed.append(f"word_count: expected {expected['word_count']}, got {actual['word_count']}")

        # Check Style
        if "style" in expected and expected["style"] != actual["style"]:
            failed.append(f"style: expected {expected['style']}, got {actual['style']}")

        # Check Subjects
        if "subjects" in expected:
            for s in expected["subjects"]:
                # case insensitive check
                if not any(s.lower() in act.lower() for act in actual["subjects"]):
                    failed.append(f"missing expected subject: '{s}' (got {actual['subjects']})")

        # Check Search
        if "needs_web_search" in expected and expected["needs_web_search"] != actual["needs_web_search"]:
            failed.append(f"needs_web_search: expected {expected['needs_web_search']}, got {actual['needs_web_search']}")

        # Check Negative
        if "negative" in expected:
            for n in expected["negative"]:
                if not any(n.lower() in act.lower() for act in actual["negative"]):
                    failed.append(f"missing negative constraint: '{n}' (got {actual['negative']})")

        if not failed:
            print(f"[{tc['id']}] PASS: \"{p[:45]}...\"")
            passed_count += 1
        else:
            print(f"[{tc['id']}] FAIL: \"{p[:45]}...\"")
            for f in failed:
                print(f"   - {f}")

    print("=" * 60)
    success_rate = (passed_count / total_count) * 100
    print(f"BENCHMARK RESULTS: {passed_count}/{total_count} PASSED ({success_rate:.1f}%)")
    print("=" * 60)

    if passed_count == total_count:
        print("[SUCCESS] System passed all core intelligence benchmarks!")
        return True
    else:
        print("[FAIL] System has benchmark failures. Please refine spec extraction rules.")
        return False


if __name__ == "__main__":
    run_tests()
