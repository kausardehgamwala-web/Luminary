"""
luminary_workflows.py
========================
Dynamic Workflow Engine & Learning System for Luminary AI.
Implements strict SOPs for common marketing tasks (Docs, PPTs, Sheets, Images, Posting).
Includes a self-learning / fallback system that explicitly asks the client for details if unknown.
"""

import json
from pathlib import Path

WORKFLOWS_DB_FILE = Path(__file__).resolve().parent / "luminary_learned_workflows.json"

# Core Standard Operating Procedures
CORE_WORKFLOWS = {
    "ppt": (
        "[Strict PPT Workflow]\n"
        "1. STRATEGY: Define presentation goal, target audience, and core message.\n"
        "2. ARCHITECTURE: Draft a strict slide-by-slide outline (Title, Hook, Body, Conclusion, CTA).\n"
        "3. CONTENT: Limit bullets to 3-5 per slide. Use high-impact headers. Provide exact data points.\n"
        "4. VISUALS: Assign specific, high-resolution image generation prompts to each slide where appropriate.\n"
        "5. QC: Review against Luminary premium standards (no overwhelming text, strong contrast)."
    ),
    "docs": (
        "[Strict Document Workflow]\n"
        "1. EXECUTIVE SUMMARY: Write a powerful 1-paragraph TL;DR.\n"
        "2. STRUCTURE: Use clear H1, H2, H3 headings. Break up walls of text with bullet points.\n"
        "3. DATA INTEGRATION: Include actionable metrics, dates, and KPIs.\n"
        "4. TONE: Professional, authoritative, agency-grade.\n"
        "5. QC: Ensure logical flow and completeness of all requested topics."
    ),
    "sheets": (
        "[Strict Spreadsheet Workflow]\n"
        "1. DATA STRUCTURE: Define columns, rows, and headers clearly.\n"
        "2. CALCULATIONS: Specify exact formulas to be used (e.g., SUM, ROI, CTR calculations).\n"
        "3. FORMATTING: Use currency, percentage, and date formats properly.\n"
        "4. DASHBOARD: Provide a summary row or a high-level metrics view.\n"
        "5. QC: Check for math logic and data consistency."
    ),
    "image": (
        "[Strict Image Workflow]\n"
        "1. PROMPT ANALYSIS: Extract exactly what the user wants. Do NOT hallucinate off-topic subjects.\n"
        "2. ART DIRECTION: Apply premium photography/3D rules (lighting, camera model, textures).\n"
        "3. RESOLUTION: Target 1080p minimum (1920x1080, 1080x1080, etc.).\n"
        "4. NEGATIVE PROMPTING: Remove text, logos, blur, and artifacts.\n"
        "5. QC: Validate that the prompt specifically matches the user's explicit request."
    ),
    "posting": (
        "[Strict Social Posting Workflow]\n"
        "1. PLATFORM OPTIMIZATION: Tailor caption length, tone, and format to the specific platform (X, IG, FB, YT, Pinterest).\n"
        "2. HOOK: Start with a strong, engaging opening sentence.\n"
        "3. MEDIA ATTACHMENT: Ensure an image/video is selected. If unsupported document (e.g. .doc), ABORT and warn user.\n"
        "4. TAGS/HASHTAGS: Add relevant, high-traffic tags.\n"
        "5. CTA: End with a clear call-to-action."
    ),
    "strategy": (
        "[Strict Marketing Strategy Workflow]\n"
        "1. FRAMEWORK: Select an appropriate marketing framework (SWOT, 4Ps, AIDA, Porter's).\n"
        "2. AUDIENCE: Define the exact target persona.\n"
        "3. TACTICS: List actionable, step-by-step implementation tactics.\n"
        "4. BUDGET & TIMELINE: Provide estimated allocations and phases.\n"
        "5. QC: Ensure the strategy is realistic and actionable, not just buzzwords."
    ),
    "qna": (
        "[Strict Q&A Workflow]\n"
        "1. DIRECT ANSWER: Provide the answer immediately in the first sentence.\n"
        "2. CONTEXT/EVIDENCE: Back it up with data, facts, or strategic reasoning.\n"
        "3. ADVICE: Provide a proactive 'next step' or professional recommendation."
    )
}

def load_learned_workflows():
    if WORKFLOWS_DB_FILE.exists():
        try:
            with open(WORKFLOWS_DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_learned_workflow(task_name, workflow_steps):
    data = load_learned_workflows()
    data[task_name.lower()] = workflow_steps
    with open(WORKFLOWS_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def determine_task_category(prompt: str) -> str:
    p = prompt.lower()
    if any(w in p for w in ["slide", "presentation", "ppt", "deck"]): return "ppt"
    if any(w in p for w in ["doc", "report", "article", "blog", "write"]): return "docs"
    if any(w in p for w in ["sheet", "excel", "csv", "table", "data", "budget"]): return "sheets"
    if any(w in p for w in ["image", "picture", "photo", "render", "generate"]): return "image"
    if any(w in p for w in ["post", "publish", "tweet", "instagram", "facebook"]): return "posting"
    if any(w in p for w in ["strategy", "campaign", "plan", "funnel", "seo"]): return "strategy"
    if any(w in p for w in ["how", "what", "why", "when", "explain", "question"]): return "qna"
    return "unknown"

def get_workflow_for_prompt(prompt: str) -> str:
    """
    Returns the strict CoT workflow for the given prompt.
    If the task is completely unknown, it invokes the fallback protocol.
    """
    p = prompt.lower()
    # Check if budget/campaign/strategy is requested but lacks numbers, specifics, or details
    if any(w in p for w in ["budget", "campaign", "strategy", "plan"]) and not any(char.isdigit() for char in prompt) and len(p.split()) < 10:
        return (
            "[CRITICAL INSTRUCTION - CLARIFICATION REQUIRED]\n"
            "The client has asked for a complex marketing task ('budget', 'campaign', or 'strategy') but has provided NO specifics (no budget figures, no brand details, no products, no channels).\n"
            "DO NOT guess, make up numbers, or output a generic mock response.\n"
            "STOP immediately and reply by asking the user for these specific inputs:\n"
            "1. What is the total budget or target amount?\n"
            "2. What is the business/brand name and industry?\n"
            "3. Who is the target audience?\n"
            "4. What are the preferred marketing channels?"
        )

    category = determine_task_category(prompt)
    
    if category in CORE_WORKFLOWS:
        return CORE_WORKFLOWS[category]
        
    # Check learned workflows
    learned = load_learned_workflows()
    for kw, wf in learned.items():
        if kw in prompt.lower():
            return f"[Learned Workflow for {kw}]\n{wf}"
            
    # UNKNOWN TASK FALLBACK / CLIENT QUERY
    return (
        "[UNKNOWN TASK PROTOCOL - STRICT]\n"
        "The user has requested a complex task that does not map to a standard workflow.\n"
        "CRITICAL INSTRUCTION: You must NOT guess. You must NOT hallucinate numbers, budgets, or strategies if context is missing.\n"
        "Action Plan:\n"
        "1. Identify the core objective of the user's request.\n"
        "2. If crucial information (e.g., budget size, target demographics, specific platforms, brand details) is missing, STOP and write a message explicitly asking the user for those details.\n"
        "3. If sufficient information exists, utilize your internal knowledge (Internet simulated training) to construct a professional step-by-step workflow for this novel task.\n"
        "4. Formulate the response outlining the new proposed workflow/strategy clearly, so it can be learned for the future."
    )
