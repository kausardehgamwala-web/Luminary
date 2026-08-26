"""
adversarial_test_runner.py
==========================
Adversarial stress-testing script designed to expose flaws in Luminary's
intelligence layers, prompt compliance, quality grading, and formatting.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path("C:/Users/Kausar/OneDrive/Documents/IM")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import luminary_intelligence
import luminary_skill_router

def run_adversarial_tests():
    print("============================================================")
    print("        RUNNING ADVERSARIAL STRESS-TESTS FOR LUMINARY")
    print("============================================================")

    failures = []

    # ──── TEST 1: Extreme Subject Count Enforcement (Adversarial) ────
    # Requesting 5 subjects but outputting only 2.
    prompt_1 = "Create a graphic showing a Ferrari, a Lamborghini, a Porsche, a BMW, and a Mercedes."
    specs_1 = luminary_intelligence.parse_prompt_specs(prompt_1)
    # Output missing 3 brands
    output_1 = "Here is a stunning photo featuring a Ferrari and a Lamborghini driving side-by-side at sunset."
    score_1 = luminary_intelligence.build_quality_score(output_1, specs_1)
    
    print(f"Test 1 Score: {score_1['total']}/100. Issues: {score_1['issues']}")
    # Under a strict agency model, missing 3 out of 5 subjects should drop accuracy score heavily.
    # Currently it might pass because accuracy only deducts 3 points per missing subject.
    if score_1["total"] >= 85:
        failures.append({
            "id": "F02",
            "test": "Missing major subjects",
            "score": score_1["total"],
            "issues": score_1["issues"],
            "reason": "Passed despite missing 3 out of 5 requested subjects."
        })

    # ──── TEST 2: Word Count Proportional Scaling Check (Adversarial) ────
    # Prompt asks for 500 words, output is only 45 words.
    prompt_2 = "Write a 500 word article about AI scaling limits."
    specs_2 = luminary_intelligence.parse_prompt_specs(prompt_2)
    output_2 = "AI scaling limits are hot topic. Standard transformer models require exponential computational resources. This is a critical challenge."
    score_2 = luminary_intelligence.build_quality_score(output_2, specs_2)
    
    print(f"Test 2 Score: {score_2['total']}/100. Issues: {score_2['issues']}")
    if score_2["total"] >= 85:
        failures.append({
            "id": "F01",
            "test": "Proportional word count limit",
            "score": score_2["total"],
            "issues": score_2["issues"],
            "reason": "Passed despite outputting only 9% of requested word count."
        })

    # ──── TEST 3: Slide Count Strictness Check (Adversarial) ────
    # Prompt asks for 10 slides, output only has 3 slides.
    prompt_3 = "Create a 10 slide deck about Ferrari marketing strategy."
    specs_3 = luminary_intelligence.parse_prompt_specs(prompt_3)
    output_3 = (
        "### Slide 1: Cover\n- Key Takeaway: Ferrari is a luxury brand\n\n"
        "### Slide 2: Market\n- Key Takeaway: Target market is ultra-wealthy\n\n"
        "### Slide 3: Conclusion\n- Key Takeaway: Growth target reached\n"
    )
    score_3 = luminary_intelligence.build_quality_score(output_3, specs_3)
    
    print(f"Test 3 Score: {score_3['total']}/100. Issues: {score_3['issues']}")
    if score_3["total"] >= 85:
        failures.append({
            "id": "F03",
            "test": "Slide count strictness",
            "score": score_3["total"],
            "issues": score_3["issues"],
            "reason": "Passed despite slide count mismatch (got 3, expected 10)."
        })

    # ──── TEST 4: Pinterest Aspect Ratio Validation (Adversarial) ────
    # Prompt is for Pinterest, but output specifies horizontal 1920x1080 resolution.
    prompt_4 = "Make a Ferrari post for Pinterest at 1920x1080 landscape."
    specs_4 = luminary_intelligence.parse_prompt_specs(prompt_4)
    # The output type is image. Check quality score.
    # Currently quality score doesn't verify if Pinterest posts are vertical 2:3.
    # Let's inspect the resolution.
    res = specs_4.get("resolution")
    print(f"Test 4 Resolution parsed: {res}. Platform aspect: {specs_4.get('platform_spec', {}).get('aspect_ratio')}")
    # Under agency rules, this is a layout conflict since Pinterest posts MUST be vertical.
    # The scorer should flag and deduct points for aspect ratio mismatch if Pinterest is requested with landscape dims.
    # Let's see if scorer detected any platform/resolution conflict:
    has_res_conflict_issue = any("resolution" in issue.lower() or "aspect" in issue.lower() for issue in score_3["issues"])
    # Let's write a mock output and check score
    output_4 = "Here is a 1920x1080 landscape image of a Ferrari."
    score_4 = luminary_intelligence.build_quality_score(output_4, specs_4)
    print(f"Test 4 Score: {score_4['total']}/100. Issues: {score_4['issues']}")
    if score_4["total"] >= 85:
        failures.append({
            "id": "F05",
            "test": "Pinterest landscape aspect mismatch",
            "score": score_4["total"],
            "issues": score_4["issues"],
            "reason": "Failed to penalise landscape dimensions for Pinterest post (which requires vertical 2:3 ratio)."
        })

    # ──── TEST 5: SEO Quality Scoring (Adversarial) ────
    # Prompt is a blog post SEO task, but output has NO meta description, NO H1, NO CTA.
    prompt_5 = "Write an SEO-optimized blog post about sustainable fashion trends."
    specs_5 = luminary_intelligence.parse_prompt_specs(prompt_5)
    output_5 = "Sustainable fashion is a growing trend. Brands are using eco-friendly materials. Consumers are more conscious about their buying choices. This is good for the planet."
    score_5 = luminary_intelligence.build_quality_score(output_5, specs_5)
    
    print(f"Test 5 Score: {score_5['total']}/100. Issues: {score_5['issues']}")
    if score_5["total"] >= 85:
        failures.append({
            "id": "F06",
            "test": "SEO output missing key elements",
            "score": score_5["total"],
            "issues": score_5["issues"],
            "reason": "Passed despite missing meta description, H1 structure, keywords and CTA in SEO blog output."
        })
    
    # ──── TEST 6: AIDA Copywriting Framework (Adversarial) ────
    # Prompt is an ad caption, but output has no attention hook, no desire, no action.
    prompt_6 = "Write an ad caption for a luxury watch brand."
    specs_6 = luminary_intelligence.parse_prompt_specs(prompt_6)
    output_6 = "Our watches are made from premium materials. We have been crafting timepieces for 50 years."
    score_6 = luminary_intelligence.build_quality_score(output_6, specs_6)
    
    print(f"Test 6 Score: {score_6['total']}/100. Issues: {score_6['issues']}")
    print(f"Test 6 Copywriting Frameworks Detected: {specs_6.get('copywriting_frameworks', [])}")
    if score_6["total"] >= 85:
        failures.append({
            "id": "F07",
            "test": "AIDA framework missing in ad copy",
            "score": score_6["total"],
            "issues": score_6["issues"],
            "reason": "Passed despite ad copy missing Attention hook, Desire, and Action CTA."
        })
    
    # ──── TEST 7: Code Output Type Detection (Adversarial) ────
    # Prompt is a website build request. Should be classified as 'code', not 'text' or 'image'.
    prompt_7 = "Build a landing page website with HTML and CSS for a fitness app."
    specs_7 = luminary_intelligence.parse_prompt_specs(prompt_7)
    print(f"Test 7 Output Type: '{specs_7.get('output_type')}'. Expected: 'code'")
    if specs_7.get("output_type") != "code":
        failures.append({
            "id": "F08",
            "test": "Website/HTML task not classified as code output",
            "score": 0,
            "issues": [f"Got output_type='{specs_7.get('output_type')}', expected 'code'"],
            "reason": "Website building prompt should classify output_type as 'code', not 'text'."
        })

    # ──── SUMMARY ────

    print("============================================================")
    if failures:
        print(f"STRESS TEST COMPLETE: FOUND {len(failures)} INTEL LOGIC FAILURES.")
        for f in failures:
            print(f"- [{f['id']}] {f['test']}: Score={f['score']}, Reason: {f['reason']}")
    else:
        print("SUCCESS: ALL STRESS-TESTS PASSED WITH 100% EXCELLENCE!")
    print("============================================================")

    return len(failures) == 0

if __name__ == "__main__":
    success = run_adversarial_tests()
    sys.exit(0 if success else 1)
